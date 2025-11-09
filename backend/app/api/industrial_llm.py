"""
Industrial LLM API Endpoints
Provides access to powerful local LLMs for data analysis
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import io
import json

router = APIRouter(prefix="/api/industrial-llm", tags=["Industrial LLM"])

# Custom JSON encoder
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

MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB


@router.get("/models")
async def get_available_models():
    """Get list of available LLM models on this system"""
    from app.services.industrial_llm_engine import IndustrialLLMEngine

    engine = IndustrialLLMEngine()

    return {
        "available_models": [
            {
                "name": m.name,
                "model_id": m.model_id,
                "min_ram_gb": m.min_ram_gb,
                "strength": m.strength
            }
            for m in engine.available_models
        ],
        "best_model": {
            "name": engine.best_model.name,
            "model_id": engine.best_model.model_id,
            "strength": engine.best_model.strength
        } if engine.best_model else None,
        "ollama_status": "running" if engine.available_models else "not_running"
    }


@router.post("/analyze")
async def analyze_with_industrial_llm(file: UploadFile = File(...)):
    """
    Analyze data quality using industrial-grade local LLM

    Uses the most powerful LLM available on your system:
    - Qwen 2.5 (72B, 14B)
    - Llama 3.3 (70B)
    - DeepSeek Coder V2
    - Mixtral 8x7B
    - Llama 3.1 (8B)

    Features:
    - RAG-enhanced (domain knowledge about data cleaning)
    - Self-verification for accuracy
    - Expert-level reasoning
    - 100% offline, zero cost
    """
    from app.services.industrial_llm_engine import IndustrialLLMEngine

    try:
        contents = await file.read()

        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is 500MB"
            )

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Initialize industrial LLM engine
        engine = IndustrialLLMEngine()

        if not engine.best_model:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "No LLM available",
                    "message": "Please install Ollama and pull a model",
                    "instructions": "See SETUP_MACBOOK.md for setup instructions",
                    "quick_start": "brew install ollama && ollama pull qwen2.5:14b"
                }
            )

        # Perform industrial-grade analysis
        analysis = engine.analyze_data_quality_with_llm(df)

        # Add metadata
        analysis["model_used"] = engine.best_model.name
        analysis["model_id"] = engine.best_model.model_id
        analysis["analysis_type"] = "industrial_llm"

        return JSONResponse(
            content=json.loads(json.dumps(analysis, cls=NumpyEncoder))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/setup-guide")
async def get_setup_guide():
    """Get setup guide for MacBook or other hardware"""
    from app.services.industrial_llm_engine import get_model_recommendations

    return {
        "guide": get_model_recommendations(),
        "quick_setup": {
            "macbook_16gb": [
                "brew install ollama",
                "ollama pull qwen2.5:14b",
                "ollama serve"
            ],
            "linux_32gb": [
                "curl -fsSL https://ollama.com/install.sh | sh",
                "ollama pull qwen2.5:72b",
                "ollama serve"
            ],
            "any_cpu": [
                "Install Ollama from https://ollama.ai/",
                "ollama pull llama3.1:8b",
                "ollama serve"
            ]
        }
    }
