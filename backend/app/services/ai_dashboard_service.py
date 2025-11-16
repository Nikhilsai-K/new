"""
AI-Powered Dashboard Service
Uses Llama 3.1 8B to intelligently select visualizations and create Tableau/Power BI-level dashboards.
100% local - no external APIs.

FEATURES:
- AI understands data semantics (e.g., "sales" vs "age" vs "category")
- Smart chart recommendations based on data relationships
- Tableau/Power BI-level advanced visualizations
- Context-aware dashboard generation
"""

import pandas as pd
import numpy as np
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class AIDashboardService:
    """
    AI-Powered Dashboard Generation using Llama 3.1 8B.

    Replaces rule-based chart selection with intelligent LLM analysis that:
    - Understands data semantics (revenue, dates, categories, etc.)
    - Recommends best visualization for each data relationship
    - Creates professional Tableau/Power BI-style dashboards
    - Considers best practices for data storytelling
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize with local Ollama connection"""
        self.ollama_url = ollama_url
        self.model = "llama3.1:8b"  # Fast and accurate
        self.timeout = 60
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

    def _call_llm(self, prompt: str) -> str:
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
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json().get("response", "")
        except requests.exceptions.Timeout:
            print(f"LLM request timed out after {self.timeout}s")
        except Exception as e:
            print(f"Error calling LLM: {e}")
        return ""

    def generate_ai_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate intelligent dashboard using AI to select charts.

        Returns:
            Dictionary with dashboard configuration and chart selections
        """
        if not self.is_available:
            return {
                "error": "Llama 3.1 8B not available. Install with: ollama pull llama3.1:8b",
                "fallback": "using_rule_based_charts"
            }

        # Step 1: Analyze dataset structure
        analysis = self._analyze_dataset_structure(df)

        # Step 2: Get AI recommendations for charts
        chart_recommendations = self._get_ai_chart_recommendations(df, analysis)

        # Step 3: Generate dashboard configuration
        dashboard = self._build_dashboard_config(df, chart_recommendations, analysis)

        return dashboard

    def _analyze_dataset_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze dataset to understand structure and semantics"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = []

        # Detect date-like columns
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['date', 'time', 'year', 'month', 'day']):
                date_cols.append(col)

        # Detect business metrics columns
        revenue_cols = [col for col in numeric_cols if any(k in col.lower() for k in ['revenue', 'sales', 'price', 'amount', 'total'])]
        count_cols = [col for col in numeric_cols if any(k in col.lower() for k in ['count', 'quantity', 'qty', 'number'])]
        rate_cols = [col for col in numeric_cols if any(k in col.lower() for k in ['rate', 'percentage', 'pct', '%'])]

        # Column statistics
        column_details = {}
        for col in df.columns:
            column_details[col] = {
                'dtype': str(df[col].dtype),
                'unique_count': int(df[col].nunique()),
                'missing_pct': float(df[col].isnull().sum() / len(df) * 100),
                'sample_values': df[col].dropna().head(3).tolist() if len(df[col].dropna()) > 0 else []
            }

        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'date_columns': date_cols,
            'revenue_columns': revenue_cols,
            'count_columns': count_cols,
            'rate_columns': rate_cols,
            'column_details': column_details
        }

    def _get_ai_chart_recommendations(self, df: pd.DataFrame, analysis: Dict) -> List[Dict]:
        """Use AI to recommend charts based on data semantics"""

        # Build prompt for LLM
        prompt = self._build_chart_recommendation_prompt(analysis)

        # Call LLM
        llm_response = self._call_llm(prompt)

        # Parse response
        recommendations = self._parse_chart_recommendations(llm_response, analysis)

        return recommendations

    def _build_chart_recommendation_prompt(self, analysis: Dict) -> str:
        """Build prompt for AI chart recommendations"""
        return f"""You are a data visualization expert. Analyze this dataset and recommend the BEST visualizations.

DATASET OVERVIEW:
- Total rows: {analysis['total_rows']:,}
- Total columns: {analysis['total_columns']}

COLUMNS:
Numeric columns: {', '.join(analysis['numeric_columns'][:10])}
Categorical columns: {', '.join(analysis['categorical_columns'][:10])}
Date columns: {', '.join(analysis['date_columns'])}

BUSINESS METRICS DETECTED:
Revenue/Sales columns: {', '.join(analysis['revenue_columns'])}
Count/Quantity columns: {', '.join(analysis['count_columns'])}
Rate/Percentage columns: {', '.join(analysis['rate_columns'])}

SAMPLE COLUMN VALUES:
{json.dumps({col: details['sample_values'] for col, details in list(analysis['column_details'].items())[:8]}, indent=2)}

TASK: Recommend 5-8 different visualizations for an executive dashboard. For each chart:
1. Identify the story it tells (trend, distribution, comparison, composition, relationship)
2. Choose the BEST chart type (line, bar, scatter, heatmap, pie, box, histogram, area, etc.)
3. Select columns to visualize
4. Explain why this chart is valuable

Return JSON format:
{{
  "charts": [
    {{
      "title": "Revenue Trend Over Time",
      "chart_type": "line",
      "x_column": "Date",
      "y_column": "Revenue",
      "story": "Shows revenue trend over time to identify growth patterns",
      "insight": "Useful for executives to see performance trajectory"
    }},
    ...
  ]
}}

Focus on:
- Business value and actionable insights
- Tableau/Power BI-level professional charts
- Diverse chart types (don't repeat same type)
- Clear storytelling"""

    def _parse_chart_recommendations(self, llm_response: str, analysis: Dict) -> List[Dict]:
        """Parse LLM response to extract chart recommendations"""
        try:
            # Extract JSON from response
            start = llm_response.find('{')
            end = -1
            brace_count = 0

            if start >= 0:
                for i in range(start, len(llm_response)):
                    if llm_response[i] == '{':
                        brace_count += 1
                    elif llm_response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break

            if start >= 0 and end > start:
                json_str = llm_response[start:end]
                parsed = json.loads(json_str)

                charts = parsed.get("charts", [])
                if charts:
                    return charts

        except Exception as e:
            print(f"Failed to parse AI recommendations: {e}")

        # Fallback to rule-based recommendations
        return self._get_fallback_recommendations(analysis)

    def _get_fallback_recommendations(self, analysis: Dict) -> List[Dict]:
        """Fallback rule-based recommendations if AI fails"""
        recommendations = []

        numeric_cols = analysis['numeric_columns']
        categorical_cols = analysis['categorical_columns']
        date_cols = analysis['date_columns']

        # Time series if date column exists
        if date_cols and numeric_cols:
            recommendations.append({
                "title": f"{numeric_cols[0]} Over Time",
                "chart_type": "line",
                "x_column": date_cols[0],
                "y_column": numeric_cols[0],
                "story": "Trend analysis over time",
                "insight": "Shows temporal patterns"
            })

        # Distribution of first numeric column
        if numeric_cols:
            recommendations.append({
                "title": f"Distribution of {numeric_cols[0]}",
                "chart_type": "histogram",
                "x_column": numeric_cols[0],
                "y_column": None,
                "story": "Value distribution analysis",
                "insight": "Understanding data spread"
            })

        # Categorical breakdown
        if categorical_cols:
            recommendations.append({
                "title": f"{categorical_cols[0]} Breakdown",
                "chart_type": "bar",
                "x_column": categorical_cols[0],
                "y_column": None,
                "story": "Categorical composition",
                "insight": "Comparing categories"
            })

        # Relationship between two numeric columns
        if len(numeric_cols) >= 2:
            recommendations.append({
                "title": f"{numeric_cols[0]} vs {numeric_cols[1]}",
                "chart_type": "scatter",
                "x_column": numeric_cols[0],
                "y_column": numeric_cols[1],
                "story": "Correlation analysis",
                "insight": "Relationship between variables"
            })

        # Categorical vs numeric
        if categorical_cols and numeric_cols:
            recommendations.append({
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                "chart_type": "box",
                "x_column": categorical_cols[0],
                "y_column": numeric_cols[0],
                "story": "Distribution across categories",
                "insight": "Comparing distributions"
            })

        return recommendations[:6]  # Limit to 6 charts

    def _build_dashboard_config(self, df: pd.DataFrame, recommendations: List[Dict], analysis: Dict) -> Dict[str, Any]:
        """Build complete dashboard configuration"""

        dashboard = {
            "success": True,
            "title": "AI-Generated Executive Dashboard",
            "source": "llama3.1_8b",
            "summary": {
                "total_rows": analysis['total_rows'],
                "total_columns": analysis['total_columns'],
                "numeric_columns": len(analysis['numeric_columns']),
                "categorical_columns": len(analysis['categorical_columns']),
                "chart_count": len(recommendations)
            },
            "charts": []
        }

        # Generate chart data for each recommendation
        for rec in recommendations:
            chart_type = rec.get('chart_type', 'bar')
            x_col = rec.get('x_column')
            y_col = rec.get('y_column')

            # Validate columns exist
            if x_col and x_col not in df.columns:
                continue
            if y_col and y_col not in df.columns:
                continue

            # Generate chart configuration
            chart_config = {
                "title": rec.get('title', 'Untitled Chart'),
                "chart_type": chart_type,
                "x_column": x_col,
                "y_column": y_col,
                "story": rec.get('story', ''),
                "insight": rec.get('insight', ''),
                "config": self._generate_chart_config(df, chart_type, x_col, y_col)
            }

            dashboard["charts"].append(chart_config)

        return dashboard

    def _generate_chart_config(self, df: pd.DataFrame, chart_type: str, x_col: str, y_col: Optional[str]) -> Dict:
        """Generate Plotly configuration for a chart"""

        try:
            if chart_type == "line":
                return self._line_chart_config(df, x_col, y_col)
            elif chart_type == "bar":
                return self._bar_chart_config(df, x_col, y_col)
            elif chart_type == "scatter":
                return self._scatter_chart_config(df, x_col, y_col)
            elif chart_type == "histogram":
                return self._histogram_config(df, x_col)
            elif chart_type == "box":
                return self._box_chart_config(df, x_col, y_col)
            elif chart_type == "pie":
                return self._pie_chart_config(df, x_col)
            elif chart_type == "heatmap":
                return self._heatmap_config(df, x_col, y_col)
            elif chart_type == "area":
                return self._area_chart_config(df, x_col, y_col)
            else:
                return self._bar_chart_config(df, x_col, y_col)
        except Exception as e:
            print(f"Error generating chart config: {e}")
            return {"error": str(e)}

    # ============= CHART CONFIGURATIONS =============

    def _line_chart_config(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict:
        """Generate line chart configuration"""
        clean = df[[x_col, y_col]].dropna()

        return {
            "data": [{
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"color": "#8B5CF6", "width": 3},
                "marker": {"size": 6, "color": "#8B5CF6"}
            }],
            "layout": {
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12},
                "hovermode": "x unified"
            }
        }

    def _bar_chart_config(self, df: pd.DataFrame, x_col: str, y_col: Optional[str]) -> Dict:
        """Generate bar chart configuration"""
        if y_col:
            # Grouped bar
            clean = df[[x_col, y_col]].dropna()
            grouped = clean.groupby(x_col)[y_col].mean().sort_values(ascending=False).head(15)
        else:
            # Value counts
            grouped = df[x_col].value_counts().head(15)

        return {
            "data": [{
                "x": grouped.index.astype(str).tolist(),
                "y": grouped.values.tolist(),
                "type": "bar",
                "marker": {
                    "color": "#06B6D4",
                    "line": {"color": "#0891B2", "width": 1.5}
                }
            }],
            "layout": {
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col if y_col else "Count"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12}
            }
        }

    def _scatter_chart_config(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict:
        """Generate scatter chart configuration"""
        clean = df[[x_col, y_col]].dropna()

        return {
            "data": [{
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "type": "scatter",
                "mode": "markers",
                "marker": {
                    "size": 8,
                    "color": clean[y_col].tolist(),
                    "colorscale": "Viridis",
                    "showscale": True,
                    "opacity": 0.7
                }
            }],
            "layout": {
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12}
            }
        }

    def _histogram_config(self, df: pd.DataFrame, x_col: str) -> Dict:
        """Generate histogram configuration"""
        clean = df[x_col].dropna()

        return {
            "data": [{
                "x": clean.tolist(),
                "type": "histogram",
                "nbinsx": 30,
                "marker": {"color": "#EC4899", "opacity": 0.7}
            }],
            "layout": {
                "xaxis": {"title": x_col},
                "yaxis": {"title": "Frequency"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12}
            }
        }

    def _box_chart_config(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict:
        """Generate box plot configuration"""
        clean = df[[x_col, y_col]].dropna()
        categories = clean[x_col].unique()[:15]

        data = []
        for cat in categories:
            values = clean[clean[x_col] == cat][y_col].tolist()
            if values:
                data.append({
                    "y": values,
                    "name": str(cat),
                    "type": "box",
                    "boxmean": "sd"
                })

        return {
            "data": data,
            "layout": {
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12}
            }
        }

    def _pie_chart_config(self, df: pd.DataFrame, x_col: str) -> Dict:
        """Generate pie chart configuration"""
        value_counts = df[x_col].value_counts().head(10)

        return {
            "data": [{
                "labels": value_counts.index.astype(str).tolist(),
                "values": value_counts.values.tolist(),
                "type": "pie",
                "marker": {"line": {"color": "#16213e", "width": 2}},
                "textposition": "inside",
                "textinfo": "label+percent"
            }],
            "layout": {
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12}
            }
        }

    def _heatmap_config(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict:
        """Generate heatmap configuration"""
        clean = df[[x_col, y_col]].dropna()
        crosstab = pd.crosstab(clean[x_col], clean[y_col])

        return {
            "data": [{
                "z": crosstab.values.tolist(),
                "x": crosstab.columns.astype(str).tolist(),
                "y": crosstab.index.astype(str).tolist(),
                "type": "heatmap",
                "colorscale": "Viridis"
            }],
            "layout": {
                "xaxis": {"title": y_col},
                "yaxis": {"title": x_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12}
            }
        }

    def _area_chart_config(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict:
        """Generate area chart configuration"""
        clean = df[[x_col, y_col]].dropna()

        if pd.api.types.is_numeric_dtype(clean[x_col]):
            clean = clean.sort_values(x_col)

        return {
            "data": [{
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "fill": "tozeroy",
                "type": "scatter",
                "mode": "lines",
                "line": {"color": "#F59E0B", "width": 2},
                "fillcolor": "rgba(245, 158, 11, 0.2)"
            }],
            "layout": {
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff", "size": 12}
            }
        }
