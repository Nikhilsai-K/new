from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import pandas as pd
import numpy as np
import io
import json
from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from app.services.data_cleaner import DataCleaner
from app.services.llm_service import LLMService
from app.services.visualization_service import VisualizationService
from app.services.local_analytics_llm import LocalAnalyticsLLM
from app.services.smart_llm_analyzer import SmartLLMAnalyzer
from app.services.smart_data_cleaner import SmartDataCleaner
from app.services.database_connector import DatabaseConnector
from app.services.eda_service import EDAService
from app.services.notebook_export import NotebookExporter
from app.services.ai_dashboard_service import AIDashboardService
from app.api.industrial_llm import router as industrial_llm_router

load_dotenv()

# Custom JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            if pd.isna(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

    def encode(self, o):
        result = super().encode(o)
        # Replace NaN and Infinity with null
        result = result.replace('NaN', 'null')
        result = result.replace('Infinity', 'null')
        result = result.replace('-Infinity', 'null')
        return result

# Set max upload size to 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB in bytes

app = FastAPI(
    title="AI Data Cleaner API",
    description="AI-powered data cleaning service for SMEs",
    version="1.0.0"
)

# CORS settings - adjust for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_cleaner = DataCleaner()
llm_service = LLMService()
visualization_service = VisualizationService()
local_analytics = LocalAnalyticsLLM()
smart_analyzer = SmartLLMAnalyzer()  # LLM-powered intelligent analysis
smart_cleaner = SmartDataCleaner()  # Applies LLM-recommended cleaning strategies
db_connector = DatabaseConnector()  # Database connectivity
eda_service = EDAService()  # Exploratory Data Analysis
notebook_exporter = NotebookExporter()  # Jupyter Notebook export
ai_dashboard = AIDashboardService()  # AI-powered dashboard generation

# Include API routers
app.include_router(industrial_llm_router)


class CleaningOptions(BaseModel):
    remove_duplicates: bool = True
    fill_missing: bool = True
    standardize_formats: bool = True
    use_ai: bool = False
    ai_suggestions_only: bool = False


@app.get("/")
async def root():
    return {
        "message": "AI Data Cleaner API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Analyze uploaded file and return data quality issues"""
    try:
        # Read file
        contents = await file.read()

        # Validate file size
        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        # Determine file type and read
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Analyze data
        analysis = data_cleaner.analyze_data(df)

        # Get preview (first 10 rows)
        preview = df.head(10).to_dict(orient='records')

        response_data = {
            "success": True,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "preview": preview,
            "analysis": analysis
        }

        # Use custom JSON encoder to handle numpy types
        return JSONResponse(
            content=json.loads(json.dumps(response_data, cls=NumpyEncoder))
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error: {str(e)}"}
        )


@app.post("/api/clean")
async def clean_file(
    file: UploadFile = File(...),
    remove_duplicates: bool = True,
    fill_missing: bool = True,
    standardize_formats: bool = True,
    use_ai: bool = False
):
    """Clean the uploaded file based on options"""
    try:
        # Read file
        contents = await file.read()

        # Validate file size
        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
            output_format = 'csv'
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
            output_format = 'excel'
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        original_rows = len(df)

        # Clean data
        cleaned_df, cleaning_report = data_cleaner.clean_data(
            df,
            remove_duplicates=remove_duplicates,
            fill_missing=fill_missing,
            standardize_formats=standardize_formats
        )

        # AI enhancement (if enabled)
        if use_ai and os.getenv("GOOGLE_API_KEY"):
            ai_suggestions = await llm_service.get_cleaning_suggestions(
                df,
                cleaned_df,
                cleaning_report
            )
            cleaning_report["ai_suggestions"] = ai_suggestions

        # Prepare file for download
        output = io.BytesIO()
        if output_format == 'csv':
            cleaned_df.to_csv(output, index=False, encoding='utf-8')
            media_type = "text/csv; charset=utf-8"
            filename = file.filename.replace('.csv', '_cleaned.csv')
        else:
            cleaned_df.to_excel(output, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = file.filename.replace('.xlsx', '_cleaned.xlsx').replace('.xls', '_cleaned.xlsx')

        output.seek(0)

        # Return cleaned file
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Cleaning-Report": str(cleaning_report)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai-suggestions")
async def get_ai_suggestions(file: UploadFile = File(...)):
    """Get AI-powered cleaning suggestions without cleaning

    Uses local ML-powered analytics engine for secure, on-premise analysis.
    Optionally uses Google API for enhanced suggestions if GOOGLE_API_KEY is configured.
    """
    try:
        # Read file
        contents = await file.read()

        # Validate file size
        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Use local analytics LLM for analysis (secure, on-premise)
        local_analysis = local_analytics.analyze_data_quality(df)
        local_suggestions = local_analysis.get("recommendations", [])

        result = {
            "success": True,
            "source": "local_ml_analytics",
            "suggestions": local_suggestions,
            "analysis": local_analysis
        }

        # If Google API is configured, enhance with remote suggestions
        if os.getenv("GOOGLE_API_KEY"):
            try:
                # Get legacy analysis for compatibility
                legacy_analysis = data_cleaner.analyze_data(df)

                # Get Google API suggestions
                google_suggestions = await llm_service.get_smart_suggestions(df, legacy_analysis)

                # Combine suggestions
                result["google_suggestions"] = google_suggestions
                result["source"] = "hybrid_local_and_cloud"
            except Exception as google_error:
                # If Google API fails, continue with local suggestions
                result["google_error"] = str(google_error)

        return JSONResponse(
            content=json.loads(json.dumps(result, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visualize/columns")
async def get_column_info(file: UploadFile = File(...)):
    """Get column information for visualization selection"""
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        column_info = visualization_service.get_column_info(df)

        return JSONResponse(
            content=json.loads(json.dumps(column_info, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visualize/chart")
async def generate_chart(
    file: UploadFile = File(...),
    x_column: str = None,
    y_column: str = None,
    chart_type: str = None
):
    """Generate chart data for specified columns"""
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if not x_column:
            raise HTTPException(status_code=400, detail="x_column parameter is required")

        chart_data = visualization_service.generate_chart_data(
            df,
            x_column,
            y_column=y_column,
            chart_type=chart_type
        )

        return JSONResponse(
            content=json.loads(json.dumps(chart_data, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visualize/recommended-charts")
async def get_recommended_charts(
    file: UploadFile = File(...),
    x_column: str = None,
    y_column: str = None
):
    """Get recommended chart types for columns"""
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if not x_column:
            raise HTTPException(status_code=400, detail="x_column parameter is required")

        charts = visualization_service.get_recommended_charts(df, x_column, y_column)

        return JSONResponse(
            content=json.loads(json.dumps({"charts": charts}, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visualize/dashboard")
async def generate_dashboard(file: UploadFile = File(...)):
    """Generate smart dashboard with intelligent chart selection"""
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        dashboard_data = visualization_service.generate_smart_dashboard(df)

        return JSONResponse(
            content=json.loads(json.dumps(dashboard_data, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/local-analysis/quality")
async def analyze_data_quality(file: UploadFile = File(...)):
    """Advanced data quality analysis using local ML-powered analytics engine

    Returns comprehensive data quality assessment including:
    - Missing data patterns (MCAR, MNAR detection)
    - Duplicate detection (exact, partial, fuzzy)
    - Outlier detection (3-method ensemble)
    - Type consistency validation
    - Entropy and distribution analysis
    - Cardinality assessment
    - Statistical anomalies
    """
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Perform advanced data quality analysis
        quality_report = local_analytics.analyze_data_quality(df)

        return JSONResponse(
            content=json.loads(json.dumps(quality_report, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/local-analysis/strategies")
async def get_cleaning_strategies(file: UploadFile = File(...)):
    """Get smart cleaning strategies using local analytics

    Returns prioritized cleaning strategies based on:
    - Data quality issues identified
    - Impact analysis
    - Risk assessment
    - Best practices
    """
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Analyze data quality and get recommendations
        quality_report = local_analytics.analyze_data_quality(df)

        # Extract recommendations from the report
        strategies = quality_report.get("recommendations", [])

        return JSONResponse(
            content=json.loads(json.dumps({
                "success": True,
                "strategies": strategies,
                "summary": {
                    "total_issues": len(strategies),
                    "critical": sum(1 for s in strategies if s.get("priority") == "high"),
                    "warnings": sum(1 for s in strategies if s.get("priority") == "medium"),
                    "info": sum(1 for s in strategies if s.get("priority") == "low")
                }
            }, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/local-analysis/insights")
async def get_analytical_insights(file: UploadFile = File(...)):
    """Get analytical insights about the dataset

    Returns insights including:
    - Column statistics and distributions
    - Correlation patterns
    - Anomalies and outliers
    - Data consistency metrics
    - Actionable recommendations
    """
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Get comprehensive analysis
        analysis = local_analytics.analyze_data_quality(df)

        insights = {
            "success": True,
            "dataset_overview": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict()
            },
            "quality_metrics": {
                "completeness": analysis.get("metrics", {}).get("completeness_score", 0),
                "consistency": analysis.get("metrics", {}).get("consistency_score", 0),
                "validity": analysis.get("metrics", {}).get("validity_score", 0),
                "uniqueness": analysis.get("metrics", {}).get("uniqueness_score", 0),
                "timeliness": analysis.get("metrics", {}).get("timeliness_score", 0)
            },
            "issue_summary": analysis.get("issue_summary", {}),
            "recommendations": analysis.get("recommendations", [])[:5]  # Top 5 recommendations
        }

        return JSONResponse(
            content=json.loads(json.dumps(insights, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/local-analysis/report")
async def generate_comprehensive_report(file: UploadFile = File(...)):
    """Generate a comprehensive data analysis report

    Returns a detailed report including:
    - Executive summary
    - Data quality assessment
    - Detailed findings
    - Cleaning recommendations
    - Risk analysis
    - Best practices
    """
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Generate comprehensive analysis
        analysis = local_analytics.analyze_data_quality(df)

        report = {
            "success": True,
            "report_title": "Comprehensive Data Quality Report",
            "dataset_info": {
                "filename": file.filename,
                "rows": len(df),
                "columns": len(df.columns),
                "size_mb": len(contents) / (1024 * 1024)
            },
            "executive_summary": {
                "overall_quality_score": analysis.get("overall_quality_score", 0),
                "total_issues": len(analysis.get("recommendations", [])),
                "high_priority": sum(1 for r in analysis.get("recommendations", []) if r.get("priority") == "high"),
                "data_completeness": f"{analysis.get('metrics', {}).get('completeness_score', 0):.1f}%"
            },
            "detailed_analysis": {
                "missing_value_analysis": analysis.get("missing_value_analysis", {}),
                "duplicate_analysis": analysis.get("duplicate_analysis", {}),
                "outlier_analysis": analysis.get("outlier_analysis", {}),
                "type_consistency": analysis.get("type_consistency_analysis", {}),
                "entropy_analysis": analysis.get("entropy_analysis", {}),
                "cardinality_analysis": analysis.get("cardinality_analysis", {})
            },
            "recommendations": analysis.get("recommendations", []),
            "next_steps": [
                "Review high-priority issues first",
                "Validate recommended cleaning strategies",
                "Perform data profiling on critical columns",
                "Document any data transformations",
                "Implement data validation rules for future ingestion"
            ]
        }

        return JSONResponse(
            content=json.loads(json.dumps(report, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/local-analysis/smart")
async def smart_data_analysis(file: UploadFile = File(...)):
    """Advanced LLM-powered data quality analysis using Llama 3.1 8B

    This endpoint uses Llama 3.1 8B running locally via Ollama for
    intelligent data quality analysis. Fast (2-5s) and accurate.
    No data leaves your machine.

    Returns:
    - Smart insights about data quality issues
    - Context-aware recommendations (understands data semantics)
    - Automatic cleaning strategies for missing values
    - Quality score with detailed breakdown

    Requires: ollama pull llama3.1:8b
    """
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Use Llama 3.1 8B LLM via Ollama for intelligent analysis (no fallback)
        analysis = smart_analyzer.analyze_data_quality(df)

        # Llama 3.1 is required - no fallback to rules
        if analysis.get("error"):
            raise HTTPException(
                status_code=503,
                detail=f"Llama 3.1 8B not available: {analysis.get('error')}. Install with: ollama pull llama3.1:8b"
            )

        analysis["note"] = "Using Llama 3.1 8B LLM for intelligent data quality analysis"

        return JSONResponse(
            content=json.loads(json.dumps(analysis, cls=NumpyEncoder))
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=str(e) or f"Internal error: {type(e).__name__}")


@app.post("/api/clean-data-smart")
async def clean_data_smart(
    file: UploadFile = File(...),
    analysis: Optional[str] = None
):
    """Apply LLM-recommended cleaning strategies to data

    Uses Llama 3.1 8B insights to intelligently clean data:
    - Missing value imputation (mean, median, mode based on column type)
    - Duplicate removal
    - Outlier handling
    - Data type consistency

    Accepts:
    - file: CSV/Excel file to clean
    - analysis: JSON string from /api/local-analysis/smart with cleaning_strategies

    Returns:
    - Cleaned data as CSV
    - Detailed cleaning report with statistics
    """
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB, got {len(contents) / (1024*1024):.2f}MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Parse LLM analysis if provided
        llm_analysis = {}
        if analysis:
            try:
                llm_analysis = json.loads(analysis)
            except json.JSONDecodeError:
                llm_analysis = {}

        # Apply smart cleaning using LLM-recommended strategies
        cleaning_result = smart_cleaner.clean_data(df, llm_analysis)

        if not cleaning_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Cleaning failed: {cleaning_result.get('error', 'Unknown error')}"
            )

        cleaned_df = cleaning_result["cleaned_data"]
        report = cleaning_result.get("report", {})

        # Convert cleaned data to CSV
        csv_buffer = io.StringIO()
        cleaned_df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()

        response_data = {
            "success": True,
            "filename": file.filename,
            "cleaned_csv": csv_content,
            "report": report,
            "data_summary": {
                "rows_before": report.get("original_rows", 0),
                "rows_after": report.get("cleaned_rows", 0),
                "rows_removed": report.get("rows_removed", 0),
                "columns": report.get("cleaned_cols", 0),
                "missing_values_remaining": report.get("missing_values_remaining", 0)
            },
            "steps_applied": report.get("steps_applied", [])
        }

        return JSONResponse(
            content=json.loads(json.dumps(response_data, cls=NumpyEncoder))
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleaning error: {str(e)}")


# ============ NEW DATABASE & EDA ENDPOINTS ============

class DatabaseConfig(BaseModel):
    source_type: str
    config: dict


@app.post("/api/database/connect")
async def connect_database(db_config: DatabaseConfig):
    """Connect to a database and return data with EDA"""
    try:
        # Connect to database
        df = db_connector.connect(db_config.source_type, db_config.config)

        # Perform EDA
        eda_results = eda_service.analyze(df)

        return JSONResponse(
            content=json.loads(json.dumps({
                "success": True,
                "eda": eda_results,
                "connection_info": {
                    "source_type": db_config.source_type,
                    "host": db_config.config.get('host'),
                    "database": db_config.config.get('database'),
                    "query": db_config.config.get('query')
                }
            }, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/eda/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Upload a file and perform EDA"""
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB"
            )

        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Perform EDA
        eda_results = eda_service.analyze(df)

        return JSONResponse(
            content=json.loads(json.dumps({
                "success": True,
                "eda": eda_results,
                "filename": file.filename
            }, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ExportRequest(BaseModel):
    analysis_data: dict


@app.post("/api/export/jupyter")
async def export_jupyter(request: ExportRequest):
    """Export analysis to Jupyter Notebook"""
    try:
        eda_results = request.analysis_data.get('eda', {})
        connection_info = request.analysis_data.get('connection_info')

        # Generate notebook
        notebook_json = notebook_exporter.export_to_ipynb(eda_results, connection_info)

        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(notebook_json.encode()),
            media_type="application/x-ipynb+json",
            headers={"Content-Disposition": "attachment; filename=analysis.ipynb"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/colab")
async def export_colab(request: ExportRequest):
    """Export analysis to Google Colab"""
    try:
        eda_results = request.analysis_data.get('eda', {})
        connection_info = request.analysis_data.get('connection_info')

        # Generate notebook
        notebook = notebook_exporter.create_notebook(eda_results, connection_info)

        # Generate Colab URL
        colab_url = notebook_exporter.generate_colab_url(notebook)

        return JSONResponse(
            content={
                "success": True,
                "colab_url": colab_url,
                "notebook": notebook
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/upload")
async def dashboard_upload(file: UploadFile = File(...)):
    """Upload file for business dashboard"""
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB"
            )

        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Calculate dashboard metrics
        total_records = len(df)
        total_revenue = 0
        active_users = 0
        conversion_rate = 0

        # Try to find common business metrics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            # Assume first numeric column might be revenue-related
            total_revenue = df[numeric_cols[0]].sum() if len(numeric_cols) > 0 else 0

        return JSONResponse(
            content=json.loads(json.dumps({
                "success": True,
                "total_records": total_records,
                "total_revenue": total_revenue,
                "active_users": active_users,
                "conversion_rate": conversion_rate,
                "columns": df.columns.tolist(),
                "sample_data": df.head(100).to_dict(orient='records')
            }, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/connect")
async def dashboard_connect(db_config: DatabaseConfig):
    """Connect database for business dashboard"""
    try:
        # Connect to database
        df = db_connector.connect(db_config.source_type, db_config.config)

        # Calculate dashboard metrics
        total_records = len(df)
        total_revenue = 0
        active_users = 0
        conversion_rate = 0

        # Try to find common business metrics
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            total_revenue = df[numeric_cols[0]].sum()

        return JSONResponse(
            content=json.loads(json.dumps({
                "success": True,
                "total_records": total_records,
                "total_revenue": total_revenue,
                "active_users": active_users,
                "conversion_rate": conversion_rate,
                "columns": df.columns.tolist(),
                "sample_data": df.head(100).to_dict(orient='records')
            }, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/database/list-tables")
async def list_database_tables(db_config: DatabaseConfig):
    """List all tables in the connected database (Tableau/Power BI-style table browser)"""
    try:
        tables = db_connector.list_tables(db_config.source_type, db_config.config)

        return JSONResponse(
            content={
                "success": True,
                "tables": tables,
                "count": len(tables)
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class TableSchemaRequest(BaseModel):
    source_type: str
    config: dict
    table_name: str


@app.post("/api/database/table-schema")
async def get_table_schema(request: TableSchemaRequest):
    """Get columns/schema for a specific table (Tableau/Power BI-style column selector)"""
    try:
        schema = db_connector.get_table_schema(
            request.source_type,
            request.config,
            request.table_name
        )

        return JSONResponse(
            content={
                "success": True,
                "schema": schema
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/ai-generate")
async def generate_ai_dashboard(file: UploadFile = File(...)):
    """Generate AI-powered Tableau/Power BI-style dashboard using Llama 3.1 8B

    This endpoint uses Llama 3.1 8B to:
    - Analyze data semantics (understand revenue, dates, categories, etc.)
    - Recommend best visualizations based on data relationships
    - Create professional dashboard with diverse chart types
    - Provide actionable insights and storytelling

    Returns:
    - Dashboard configuration with 5-8 intelligent chart recommendations
    - Each chart includes: title, type, columns, story, insight, and Plotly config
    - Source: llama3.1_8b for transparency

    Requires: ollama pull llama3.1:8b
    """
    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB"
            )

        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Generate AI-powered dashboard
        dashboard = ai_dashboard.generate_ai_dashboard(df)

        # Check if AI is available
        if dashboard.get("error"):
            raise HTTPException(
                status_code=503,
                detail=f"Llama 3.1 8B not available: {dashboard.get('error')}. Install with: ollama pull llama3.1:8b"
            )

        return JSONResponse(
            content=json.loads(json.dumps(dashboard, cls=NumpyEncoder))
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=str(e) or f"Internal error: {type(e).__name__}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
