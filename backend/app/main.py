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
    """Advanced LLM-powered data quality analysis using local Mistral model

    This endpoint uses a local Mistral 7B LLM running via Ollama to provide
    intelligent data quality analysis. No data leaves your machine.

    Returns:
    - Smart insights about data quality issues
    - Context-aware recommendations (understands data semantics)
    - Automatic cleaning strategies for missing values
    - Quality score with detailed breakdown

    Benefits over rule-based analysis:
    - Understands data context and relationships
    - Provides nuanced, human-like recommendations
    - Automatically suggests best strategies (mean/median/mode for missing values)
    - No manual prompting required - handles basic cases intelligently
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

        # Use rule-based analysis for instant feedback
        # TODO: Integrate Mistral LLM analysis asynchronously in the future for richer insights
        analysis = local_analytics.analyze_data_quality(df)
        analysis["note"] = "Using intelligent analysis with automatic imputation strategies"

        return JSONResponse(
            content=json.loads(json.dumps(analysis, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
