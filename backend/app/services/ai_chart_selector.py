"""
AI-Powered Chart Selector
Uses LLM to intelligently select the best visualization type for data
Much smarter than rule-based selection!
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import requests
import json


class AIChartSelector:
    """
    AI-Powered Intelligent Chart Selector

    Uses local LLM (Llama 3.1 8B) to understand data semantics and
    recommend the perfect visualization type - just like a data analyst would!

    Capabilities:
    - Semantic understanding of column names and data
    - Context-aware chart recommendations
    - Multi-chart dashboard layout suggestions
    - Tableau/Power BI-quality visualization planning
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.1:8b"  # Fast and smart
        self.timeout = 30

    def _call_llm(self, prompt: str) -> str:
        """Call Llama 3.1 8B for chart recommendations"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower for more consistent recommendations
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json().get("response", "")
        except:
            pass

        return ""

    def recommend_chart_for_columns(self, df: pd.DataFrame, x_column: str, y_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask AI to recommend the best chart type for given columns

        Returns:
            {
                "chart_type": "line" | "bar" | "scatter" | "heatmap" | etc,
                "reasoning": "why this chart is best",
                "alternatives": ["other", "options"],
                "title": "suggested chart title",
                "insights": ["key insights AI noticed"]
            }
        """

        # Prepare data summary for AI
        data_summary = self._prepare_data_summary(df, x_column, y_column)

        # Build prompt
        prompt = self._build_chart_recommendation_prompt(data_summary, x_column, y_column)

        # Get AI recommendation
        llm_response = self._call_llm(prompt)

        # Parse response
        recommendation = self._parse_chart_recommendation(llm_response)

        return recommendation

    def recommend_dashboard_layout(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Ask AI to design the perfect dashboard layout for this dataset

        Returns complete dashboard specification with:
        - Which charts to show
        - How to arrange them
        - What insights to highlight
        - Color schemes and styling
        """

        # Prepare comprehensive data summary
        data_summary = self._prepare_comprehensive_summary(df)

        # Build dashboard design prompt
        prompt = self._build_dashboard_design_prompt(data_summary)

        # Get AI dashboard design
        llm_response = self._call_llm(prompt)

        # Parse dashboard specification
        dashboard_spec = self._parse_dashboard_spec(llm_response)

        return dashboard_spec

    def _prepare_data_summary(self, df: pd.DataFrame, x_column: str, y_column: Optional[str]) -> Dict:
        """Prepare concise data summary for AI"""
        summary = {
            "total_rows": len(df),
            "x_column": {
                "name": x_column,
                "type": str(df[x_column].dtype),
                "unique_values": int(df[x_column].nunique()),
                "sample_values": df[x_column].dropna().head(5).tolist(),
                "has_nulls": bool(df[x_column].isna().any())
            }
        }

        # Add numeric stats if numeric
        if pd.api.types.is_numeric_dtype(df[x_column]):
            summary["x_column"]["stats"] = {
                "min": float(df[x_column].min()),
                "max": float(df[x_column].max()),
                "mean": float(df[x_column].mean()),
                "median": float(df[x_column].median())
            }

        # Add Y column info if provided
        if y_column and y_column in df.columns:
            summary["y_column"] = {
                "name": y_column,
                "type": str(df[y_column].dtype),
                "unique_values": int(df[y_column].nunique()),
                "sample_values": df[y_column].dropna().head(5).tolist(),
                "has_nulls": bool(df[y_column].isna().any())
            }

            if pd.api.types.is_numeric_dtype(df[y_column]):
                summary["y_column"]["stats"] = {
                    "min": float(df[y_column].min()),
                    "max": float(df[y_column].max()),
                    "mean": float(df[y_column].mean()),
                    "median": float(df[y_column].median())
                }

        return summary

    def _prepare_comprehensive_summary(self, df: pd.DataFrame) -> Dict:
        """Prepare comprehensive data summary for dashboard design"""
        summary = {
            "shape": {
                "rows": len(df),
                "columns": len(df.columns)
            },
            "columns": []
        }

        # Analyze each column
        for col in df.columns[:20]:  # Limit to first 20 columns for performance
            col_info = {
                "name": col,
                "type": str(df[col].dtype),
                "unique_count": int(df[col].nunique()),
                "null_count": int(df[col].isna().sum()),
                "sample_values": df[col].dropna().head(3).tolist()
            }

            # Add stats for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["stats"] = {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean())
                }

            summary["columns"].append(col_info)

        return summary

    def _build_chart_recommendation_prompt(self, data_summary: Dict, x_column: str, y_column: Optional[str]) -> str:
        """Build LLM prompt for chart recommendation"""
        y_info = ""
        if "y_column" in data_summary:
            y_info = f"""
Y Column: {data_summary['y_column']['name']}
- Type: {data_summary['y_column']['type']}
- Unique values: {data_summary['y_column']['unique_values']}
- Sample: {data_summary['y_column']['sample_values']}
"""

        prompt = f"""You are an expert data visualization consultant. Recommend the BEST chart type for this data.

DATA SUMMARY:
Total rows: {data_summary['total_rows']}

X Column: {data_summary['x_column']['name']}
- Type: {data_summary['x_column']['type']}
- Unique values: {data_summary['x_column']['unique_values']}
- Sample: {data_summary['x_column']['sample_values']}
{y_info}

TASK:
Recommend the single best chart type and explain why. Consider:
- What story does this data tell?
- What patterns should be highlighted?
- What would a Tableau/Power BI expert choose?

Respond in this EXACT JSON format:
{{
  "chart_type": "line|bar|scatter|heatmap|box|violin|area|pie|histogram|treemap",
  "reasoning": "why this is the best choice",
  "alternatives": ["second choice", "third choice"],
  "title": "Great chart title",
  "x_axis_label": "X axis label",
  "y_axis_label": "Y axis label",
  "insights": ["key insight 1", "key insight 2"]
}}

JSON response:"""

        return prompt

    def _build_dashboard_design_prompt(self, data_summary: Dict) -> str:
        """Build LLM prompt for complete dashboard design"""
        columns_info = "\n".join([
            f"- {col['name']} ({col['type']}): {col['unique_count']} unique values"
            for col in data_summary['columns']
        ])

        prompt = f"""You are an expert dashboard designer (Tableau/Power BI level). Design the perfect business intelligence dashboard for this dataset.

DATASET:
Rows: {data_summary['shape']['rows']:,}
Columns: {data_summary['shape']['columns']}

COLUMNS:
{columns_info}

TASK:
Design a professional BI dashboard with 4-6 charts that tell the complete story. Consider:
- What are the key business metrics?
- What trends should executives see?
- How would Tableau auto-generate this dashboard?

Respond in this EXACT JSON format:
{{
  "dashboard_title": "Executive Dashboard Title",
  "key_metrics": [
    {{"metric": "Total Revenue", "value_column": "column_name", "format": "currency"}}
  ],
  "charts": [
    {{
      "position": 1,
      "title": "Chart Title",
      "chart_type": "line|bar|pie|scatter|heatmap|area",
      "x_column": "column_name",
      "y_column": "column_name",
      "size": "large|medium|small",
      "insight": "What this chart reveals"
    }}
  ],
  "color_scheme": "professional|modern|vibrant|corporate",
  "executive_summary": "One sentence summary of key findings"
}}

Design 4-6 diverse, insightful charts. JSON response:"""

        return prompt

    def _parse_chart_recommendation(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM chart recommendation"""
        try:
            # Extract JSON from response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                recommendation = json.loads(json_str)

                # Validate required fields
                if "chart_type" in recommendation:
                    return recommendation
        except:
            pass

        # Fallback recommendation
        return {
            "chart_type": "bar",
            "reasoning": "Default bar chart (AI unavailable)",
            "alternatives": ["line", "scatter"],
            "title": "Data Visualization",
            "x_axis_label": "X Axis",
            "y_axis_label": "Y Axis",
            "insights": []
        }

    def _parse_dashboard_spec(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM dashboard specification"""
        try:
            # Extract JSON from response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                spec = json.loads(json_str)

                # Validate required fields
                if "charts" in spec and len(spec["charts"]) > 0:
                    return spec
        except:
            pass

        # Fallback dashboard
        return {
            "dashboard_title": "Business Dashboard",
            "key_metrics": [],
            "charts": [
                {
                    "position": 1,
                    "title": "Overview",
                    "chart_type": "bar",
                    "size": "large",
                    "insight": "Data overview"
                }
            ],
            "color_scheme": "professional",
            "executive_summary": "Dashboard summary"
        }

    def get_tableau_style_recommendation(self, df: pd.DataFrame, chart_context: str = "") -> Dict[str, Any]:
        """
        Get Tableau-style 'Show Me' recommendations

        chart_context: Optional context like "comparing categories" or "showing trend over time"
        """
        # Analyze data types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        recommendations = []

        # Time series charts
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            recommendations.append({
                "type": "line",
                "priority": "high",
                "use_case": "Show trends over time",
                "x": datetime_cols[0],
                "y": numeric_cols[0]
            })

        # Category comparisons
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            if df[categorical_cols[0]].nunique() <= 20:
                recommendations.append({
                    "type": "bar",
                    "priority": "high",
                    "use_case": "Compare categories",
                    "x": categorical_cols[0],
                    "y": numeric_cols[0]
                })

        # Correlations
        if len(numeric_cols) >= 2:
            recommendations.append({
                "type": "scatter",
                "priority": "medium",
                "use_case": "Find correlations",
                "x": numeric_cols[0],
                "y": numeric_cols[1]
            })

        # Distribution
        if len(numeric_cols) > 0:
            recommendations.append({
                "type": "histogram",
                "priority": "medium",
                "use_case": "See distribution",
                "x": numeric_cols[0]
            })

        return {
            "recommendations": recommendations,
            "data_profile": {
                "numeric_columns": len(numeric_cols),
                "categorical_columns": len(categorical_cols),
                "datetime_columns": len(datetime_cols)
            }
        }
