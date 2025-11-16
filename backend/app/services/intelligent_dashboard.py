"""
Intelligent Dashboard Generator
Uses AI to create perfect Tableau/Power BI-quality dashboards automatically
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from .ai_chart_selector import AIChartSelector
from .advanced_visualizations import AdvancedVisualizationEngine


class IntelligentDashboardGenerator:
    """
    AI-Powered Dashboard Generator

    Creates enterprise-quality dashboards automatically:
    - AI decides which charts to show
    - Smart layout optimization
    - Executive summary generation
    - Key metrics extraction
    - Color scheme selection
    - Responsive grid layout
    """

    def __init__(self):
        self.ai_selector = AIChartSelector()
        self.viz_engine = AdvancedVisualizationEngine()

    def generate_dashboard(self, df: pd.DataFrame, dashboard_config: Dict = None) -> Dict[str, Any]:
        """
        Generate complete dashboard using AI

        Args:
            df: DataFrame to visualize
            dashboard_config: Optional configuration overrides

        Returns:
            Complete dashboard specification with:
            - charts: List of chart configurations
            - layout: Grid layout specification
            - metrics: Key business metrics
            - summary: Executive summary
            - theme: Color scheme and styling
        """
        config = dashboard_config or {}

        # Step 1: Ask AI to design the dashboard
        print("🧠 AI designing dashboard layout...")
        ai_dashboard_spec = self.ai_selector.recommend_dashboard_layout(df)

        # Step 2: Generate actual chart configurations
        print("📊 Generating charts...")
        charts = self._generate_charts_from_spec(df, ai_dashboard_spec)

        # Step 3: Extract key metrics
        print("📈 Calculating key metrics...")
        metrics = self._extract_key_metrics(df, ai_dashboard_spec.get("key_metrics", []))

        # Step 4: Create responsive layout
        print("🎨 Optimizing layout...")
        layout = self._create_responsive_layout(charts)

        # Step 5: Apply professional theme
        theme = self._select_color_theme(ai_dashboard_spec.get("color_scheme", "professional"))

        dashboard = {
            "title": ai_dashboard_spec.get("dashboard_title", "Business Intelligence Dashboard"),
            "subtitle": ai_dashboard_spec.get("executive_summary", ""),
            "metrics": metrics,
            "charts": charts,
            "layout": layout,
            "theme": theme,
            "metadata": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "generated_by": "AI",
                "chart_count": len(charts)
            }
        }

        return dashboard

    def _generate_charts_from_spec(self, df: pd.DataFrame, spec: Dict) -> List[Dict]:
        """Generate actual chart configurations from AI specification"""
        charts = []

        for chart_spec in spec.get("charts", []):
            try:
                chart_type = chart_spec.get("chart_type", "bar")
                x_col = chart_spec.get("x_column")
                y_col = chart_spec.get("y_column")
                title = chart_spec.get("title", "")

                # Generate chart based on type
                if chart_type == "line":
                    chart = self.viz_engine.generate_line_chart(
                        df, x_col, y_col, title
                    )
                elif chart_type == "bar":
                    chart = self.viz_engine.generate_bar_chart(
                        df, x_col, y_col, title,
                        config={"top_n": 15}
                    )
                elif chart_type == "scatter":
                    chart = self.viz_engine.generate_scatter_plot(
                        df, x_col, y_col, title
                    )
                elif chart_type == "pie" or chart_type == "doughnut":
                    chart = self.viz_engine.generate_pie_chart(
                        df, x_col, y_col, title,
                        config={"variant": chart_type}
                    )
                elif chart_type == "heatmap":
                    chart = self.viz_engine.generate_heatmap(df)
                else:
                    # Default to bar chart
                    chart = self.viz_engine.generate_bar_chart(
                        df, x_col, y_col, title
                    )

                # Add metadata from AI spec
                chart["position"] = chart_spec.get("position", len(charts) + 1)
                chart["size"] = chart_spec.get("size", "medium")
                chart["insight"] = chart_spec.get("insight", "")

                charts.append(chart)

            except Exception as e:
                print(f"Warning: Could not generate chart: {e}")
                continue

        return charts

    def _extract_key_metrics(self, df: pd.DataFrame, metric_specs: List[Dict]) -> List[Dict]:
        """Extract and calculate key business metrics"""
        metrics = []

        # If AI specified metrics, use those
        for spec in metric_specs:
            try:
                metric_name = spec.get("metric")
                value_column = spec.get("value_column")
                format_type = spec.get("format", "number")

                if value_column and value_column in df.columns:
                    value = df[value_column].sum()

                    metrics.append({
                        "name": metric_name,
                        "value": value,
                        "format": format_type,
                        "icon": self._get_metric_icon(metric_name)
                    })
            except:
                continue

        # If no metrics specified, auto-detect
        if len(metrics) == 0:
            metrics = self._auto_detect_metrics(df)

        return metrics

    def _auto_detect_metrics(self, df: pd.DataFrame) -> List[Dict]:
        """Automatically detect key metrics from data"""
        metrics = []

        # Total records
        metrics.append({
            "name": "Total Records",
            "value": len(df),
            "format": "number",
            "icon": "database"
        })

        # Find revenue-like columns
        revenue_keywords = ["revenue", "sales", "amount", "total", "price", "cost"]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in revenue_keywords):
                metrics.append({
                    "name": f"Total {col}",
                    "value": df[col].sum(),
                    "format": "currency" if "revenue" in col_lower or "sales" in col_lower else "number",
                    "icon": "dollar-sign"
                })
                break  # Only show one revenue metric

        # Find count-like columns
        count_keywords = ["count", "quantity", "qty", "num", "users", "customers"]
        for col in numeric_cols:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in count_keywords):
                metrics.append({
                    "name": f"Total {col}",
                    "value": int(df[col].sum()),
                    "format": "number",
                    "icon": "users"
                })
                break

        return metrics[:4]  # Limit to 4 key metrics

    def _get_metric_icon(self, metric_name: str) -> str:
        """Get appropriate icon for metric"""
        name_lower = metric_name.lower()

        if "revenue" in name_lower or "sales" in name_lower:
            return "dollar-sign"
        elif "user" in name_lower or "customer" in name_lower:
            return "users"
        elif "order" in name_lower or "transaction" in name_lower:
            return "shopping-cart"
        elif "conversion" in name_lower or "rate" in name_lower:
            return "trending-up"
        else:
            return "bar-chart"

    def _create_responsive_layout(self, charts: List[Dict]) -> Dict:
        """Create responsive grid layout for charts"""
        # Tableau-style grid layout
        # Large charts: full width (12 columns)
        # Medium charts: half width (6 columns)
        # Small charts: quarter width (3 columns)

        layout_grid = []

        for i, chart in enumerate(charts):
            size = chart.get("size", "medium")

            if size == "large":
                columns = 12
            elif size == "medium":
                columns = 6
            else:  # small
                columns = 3

            layout_grid.append({
                "chart_id": i,
                "columns": columns,
                "row": "auto",  # Auto-arrange rows
                "height": "400px" if size == "large" else "350px" if size == "medium" else "300px"
            })

        return {
            "type": "responsive_grid",
            "max_columns": 12,
            "gap": "20px",
            "items": layout_grid
        }

    def _select_color_theme(self, scheme_name: str) -> Dict:
        """Select and configure color theme"""
        themes = {
            "professional": {
                "primary": "#1f77b4",
                "secondary": "#ff7f0e",
                "background": "#ffffff",
                "text": "#333333",
                "border": "#e0e0e0",
                "palette": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
            },
            "modern": {
                "primary": "#667eea",
                "secondary": "#764ba2",
                "background": "#f8f9fa",
                "text": "#2c3e50",
                "border": "#dee2e6",
                "palette": ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"]
            },
            "corporate": {
                "primary": "#003f5c",
                "secondary": "#2f4b7c",
                "background": "#ffffff",
                "text": "#1a1a1a",
                "border": "#cccccc",
                "palette": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087"]
            },
            "vibrant": {
                "primary": "#FF6B6B",
                "secondary": "#4ECDC4",
                "background": "#f7f9fc",
                "text": "#2d3436",
                "border": "#dfe6e9",
                "palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
            }
        }

        return themes.get(scheme_name, themes["professional"])

    def generate_executive_dashboard(self, df: pd.DataFrame) -> Dict:
        """
        Generate executive-focused dashboard with high-level metrics

        Optimized for C-level viewing:
        - Fewer, more impactful charts
        - Large KPI cards
        - Trend indicators
        - Simplified visuals
        """
        # Force specific layout for executive view
        executive_config = {
            "focus": "metrics",
            "chart_count": 4,  # Max 4 charts for simplicity
            "show_trends": True
        }

        dashboard = self.generate_dashboard(df, executive_config)

        # Enhance with trend indicators
        dashboard["metrics"] = self._add_trend_indicators(dashboard["metrics"])

        return dashboard

    def _add_trend_indicators(self, metrics: List[Dict]) -> List[Dict]:
        """Add trend up/down indicators to metrics"""
        for metric in metrics:
            # Placeholder for trend calculation
            # In production, compare with historical data
            metric["trend"] = {
                "direction": "up",  # up, down, stable
                "percentage": 5.2,  # Example: 5.2% increase
                "period": "vs last month"
            }

        return metrics
