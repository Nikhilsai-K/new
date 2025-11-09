"""
Smart LLM-Based Data Analysis Service
Uses local Mistral LLM via Ollama for intelligent data quality analysis.
100% local - all data stays on your machine, no external API calls.
"""

import pandas as pd
import numpy as np
import requests
import json
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')


class SmartLLMAnalyzer:
    """
    LLM-Powered Data Quality Analyzer using Mistral 7B

    Features:
    - Intelligent missing value analysis with automatic strategy suggestion
    - Smart outlier detection and handling recommendations
    - Data quality scoring with detailed explanations
    - Automatic cleaning strategy generation
    - Context-aware recommendations (understands data semantics)
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize with local Ollama connection"""
        self.ollama_url = ollama_url
        self.model = "llama3.1:8b"  # Fast model: 2-5 seconds response time
        self.timeout = 20  # 20 seconds (Llama 3.1 responds in 2-5s, plenty of buffer)
        self.is_available = self._check_ollama_availability()

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is running and Llama 3.1 8B is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m["name"].startswith("llama3.1") for m in models)
        except:
            pass
        return False

    def _call_mistral(self, prompt: str) -> str:
        """Call Llama 3.1 8B LLM via Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get("response", "")
        except requests.exceptions.Timeout:
            print(f"Llama 3.1 8B request timed out after {self.timeout}s")
        except Exception as e:
            print(f"Error calling Llama 3.1 8B: {e}")
        return ""

    def analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive data quality analysis using Llama 3.1 8B LLM.
        No fallback - LLM analysis is required.
        """
        if not self.is_available:
            return {"error": "Llama 3.1 8B not available. Install with: ollama pull llama3.1:8b"}

        analysis = {
            "quality_score": 0,
            "insights": [],
            "recommendations": [],
            "cleaning_strategies": {},
            "metrics": {}
        }

        # Step 1: Prepare data summary for LLM
        data_summary = self._prepare_data_summary(df)

        # Step 2: Use LLM to analyze data quality
        quality_prompt = self._build_quality_analysis_prompt(data_summary)
        llm_analysis = self._call_mistral(quality_prompt)

        if not llm_analysis:
            return {"error": "Llama 3.1 8B analysis failed or timed out"}

        analysis.update(self._parse_llm_analysis(llm_analysis, df))

        # Step 3: Generate smart cleaning strategies
        cleaning_prompt = self._build_cleaning_strategy_prompt(data_summary, analysis)
        llm_strategies = self._call_mistral(cleaning_prompt)

        if llm_strategies:
            analysis["cleaning_strategies"] = self._parse_cleaning_strategies(llm_strategies)

        # Step 4: Calculate quality score
        analysis["quality_score"] = self._calculate_quality_score(analysis, df)

        return analysis

    def _prepare_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare a concise data summary for LLM analysis"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "missing_analysis": {},
            "duplicates": len(df) - len(df.drop_duplicates()),
            "column_details": {}
        }

        # Missing value analysis per column
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_percent = (missing_count / len(df)) * 100

            summary["missing_analysis"][col] = {
                "count": int(missing_count),
                "percentage": round(missing_percent, 2)
            }

            # Column type and stats
            if col in numeric_cols:
                try:
                    summary["column_details"][col] = {
                        "type": "numeric",
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "mean": float(df[col].mean()),
                        "std": float(df[col].std()),
                        "has_missing": bool(missing_count > 0)
                    }
                except:
                    summary["column_details"][col] = {"type": "numeric", "error": "Could not compute stats"}
            else:
                unique_count = df[col].nunique()
                summary["column_details"][col] = {
                    "type": "categorical",
                    "unique_values": int(unique_count),
                    "has_missing": bool(missing_count > 0)
                }

        return summary

    def _build_quality_analysis_prompt(self, summary: Dict) -> str:
        """Build a prompt for LLM to analyze data quality"""
        return f"""Analyze this dataset for data quality issues and provide insights and recommendations.

Dataset Summary:
- Total Rows: {summary['total_rows']}
- Total Columns: {summary['total_columns']}
- Numeric Columns: {summary['numeric_columns']}
- Categorical Columns: {summary['categorical_columns']}
- Duplicates: {summary['duplicates']}

Missing Values Analysis:
{json.dumps(summary['missing_analysis'], indent=2)}

Column Details:
{json.dumps(summary['column_details'], indent=2)}

Please provide:
1. A list of identified data quality issues (each as {{message, severity, column, percent, description}})
2. A list of recommendations (each as {{action, priority, impact, description}})

Format your response as JSON with "issues" and "recommendations" arrays.
Be specific about which columns have problems and why."""

    def _build_cleaning_strategy_prompt(self, summary: Dict, analysis: Dict) -> str:
        """Build a prompt to generate smart cleaning strategies"""
        return f"""Based on this data analysis, suggest intelligent cleaning strategies.

Dataset: {summary['total_rows']} rows, {summary['total_columns']} columns
Numeric Columns: {summary['numeric_columns']}
Categorical Columns: {summary['categorical_columns']}

Missing Values:
{json.dumps(summary['missing_analysis'], indent=2)}

Issues Identified:
{json.dumps(analysis.get('insights', [])[:5], indent=2)}

For columns with missing values, recommend the BEST approach:
- For numeric columns: suggest mean, median, or mode imputation based on distribution
- For categorical columns: suggest mode imputation or create 'Unknown' category
- For highly missing columns (>50%): suggest removal or 'missing' indicator column
- Consider data context and relationships between columns

Format as JSON with column-specific strategies. Example:
{{
  "column_name": {{
    "issue": "50% missing values",
    "recommended_strategy": "mean imputation (values follow normal distribution)",
    "implementation": "df['column'].fillna(df['column'].mean())",
    "rationale": "Mean imputation is suitable because..."
  }}
}}"""

    def _parse_llm_analysis(self, llm_response: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse LLM response and extract insights/recommendations"""
        try:
            # Try to extract JSON from response
            start = llm_response.find('{')
            end = llm_response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = llm_response[start:end]
                parsed = json.loads(json_str)

                return {
                    "insights": parsed.get("issues", []),
                    "recommendations": parsed.get("recommendations", [])
                }
        except:
            pass

        # Fallback: Extract insights from raw response
        insights = []
        recommendations = []

        for line in llm_response.split('\n'):
            if 'missing' in line.lower() and '%' in line:
                insights.append({
                    "message": line.strip(),
                    "severity": "high" if "high" in line.lower() else "medium",
                    "column": "various",
                    "description": line.strip()
                })
            elif 'recommend' in line.lower() or 'should' in line.lower():
                recommendations.append({
                    "action": line.strip(),
                    "priority": "medium",
                    "description": line.strip()
                })

        return {
            "insights": insights if insights else self._generate_basic_insights(df),
            "recommendations": recommendations if recommendations else self._generate_basic_recommendations(df)
        }

    def _parse_cleaning_strategies(self, llm_response: str) -> Dict[str, Any]:
        """Parse cleaning strategies from LLM response"""
        try:
            start = llm_response.find('{')
            end = llm_response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = llm_response[start:end]
                return json.loads(json_str)
        except:
            pass

        return {}

    def _generate_basic_insights(self, df: pd.DataFrame) -> List[Dict]:
        """Generate basic insights if LLM is unavailable"""
        insights = []

        # Check for missing values
        for col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                percent = (missing / len(df)) * 100
                insights.append({
                    "message": f"Column '{col}' has {percent:.1f}% missing values",
                    "severity": "high" if percent > 20 else "medium",
                    "column": col,
                    "percent": percent,
                    "description": f"Missing data detected - recommend imputation or removal"
                })

        # Check for duplicates
        dups = len(df) - len(df.drop_duplicates())
        if dups > 0:
            percent = (dups / len(df)) * 100
            insights.append({
                "message": f"Dataset contains {dups} duplicate rows ({percent:.1f}%)",
                "severity": "high",
                "column": "N/A",
                "percent": percent,
                "description": "Duplicates should be investigated and removed"
            })

        return insights

    def _generate_basic_recommendations(self, df: pd.DataFrame) -> List[Dict]:
        """Generate basic recommendations if LLM is unavailable"""
        recommendations = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        # Missing value recommendations
        for col in numeric_cols:
            missing = df[col].isnull().sum()
            if missing > 0:
                missing_percent = (missing / len(df)) * 100
                if missing_percent < 5:
                    strategy = "mean/median imputation"
                elif missing_percent < 20:
                    strategy = "forward fill or interpolation"
                else:
                    strategy = "remove or create missing indicator"

                recommendations.append({
                    "action": f"Fill missing values in '{col}'",
                    "priority": "high" if missing_percent > 10 else "medium",
                    "impact": "Data becomes complete and usable",
                    "description": f"Use {strategy} - {missing_percent:.1f}% missing"
                })

        for col in categorical_cols:
            missing = df[col].isnull().sum()
            if missing > 0:
                missing_percent = (missing / len(df)) * 100
                recommendations.append({
                    "action": f"Fill missing values in '{col}'",
                    "priority": "high" if missing_percent > 10 else "medium",
                    "impact": "Data becomes complete",
                    "description": f"Use mode (most frequent) imputation - {missing_percent:.1f}% missing"
                })

        # Duplicate recommendations
        dups = len(df) - len(df.drop_duplicates())
        if dups > 0:
            recommendations.append({
                "action": "Remove duplicate rows",
                "priority": "high",
                "impact": "Reduces data redundancy, improves quality",
                "description": f"{dups} exact duplicate rows detected"
            })

        return recommendations

    def _calculate_quality_score(self, analysis: Dict, df: pd.DataFrame) -> float:
        """Calculate overall data quality score (0-100)"""
        score = 100.0

        # Deduct for missing values
        for col in df.columns:
            missing_percent = (df[col].isnull().sum() / len(df)) * 100
            if missing_percent > 0:
                score -= min(missing_percent / 2, 10)  # Max 10 points for missing

        # Deduct for duplicates
        dup_percent = ((len(df) - len(df.drop_duplicates())) / len(df)) * 100
        score -= min(dup_percent / 2, 10)  # Max 10 points for duplicates

        # Deduct for number of issues
        num_issues = len(analysis.get("insights", []))
        score -= min(num_issues * 2, 20)  # Max 20 points for issues

        return max(0, min(100, round(score, 1)))
