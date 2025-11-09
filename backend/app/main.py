from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from app.services.data_cleaner import DataCleaner
from app.services.llm_service import LLMService

load_dotenv()

app = FastAPI(
    title="AI Data Cleaner API",
    description="AI-powered data cleaning service for SMEs",
    version="1.0.0"
)

# CORS settings - adjust for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_cleaner = DataCleaner()
llm_service = LLMService()


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

        return {
            "success": True,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "preview": preview,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            cleaned_df.to_csv(output, index=False)
            media_type = "text/csv"
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
    """Get AI-powered cleaning suggestions without cleaning"""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=503,
                detail="AI service not configured. Please add GOOGLE_API_KEY to .env"
            )

        # Read file
        contents = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Analyze first
        analysis = data_cleaner.analyze_data(df)

        # Get AI suggestions
        suggestions = await llm_service.get_smart_suggestions(df, analysis)

        return {
            "success": True,
            "suggestions": suggestions,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
