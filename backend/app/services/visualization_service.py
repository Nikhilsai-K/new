import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import json
from scipy import stats
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class VisualizationService:
    """Advanced visualization service with Tableau-like capabilities"""

    def __init__(self):
        self.max_categories = 15
        self.sample_size = 5000

    def get_column_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive metadata about columns"""
        columns_info = []
        numeric_cols = []
        categorical_cols = []

        for col in df.columns:
            col_type = self._infer_column_type(df[col])
            clean_data = df[col].dropna()

            info = {
                "name": col,
                "type": col_type,
                "unique_count": int(df[col].nunique()),
                "missing_count": int(df[col].isna().sum()),
                "missing_percent": round(df[col].isna().sum() / len(df) * 100, 2)
            }

            # Add numeric stats
            if col_type == "numeric" and len(clean_data) > 0:
                info["stats"] = {
                    "mean": float(clean_data.mean()),
                    "median": float(clean_data.median()),
                    "std": float(clean_data.std()),
                    "min": float(clean_data.min()),
                    "max": float(clean_data.max())
                }
                numeric_cols.append(col)

            # Add categorical info
            if col_type == "categorical":
                categorical_cols.append(col)
                top_values = clean_data.value_counts().head(5)
                info["top_values"] = {str(k): int(v) for k, v in top_values.items()}

            columns_info.append(info)

        # Smart recommendations
        recommendations = self._get_smart_recommendations(df, numeric_cols, categorical_cols)

        return {
            "columns": columns_info,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "recommendations": recommendations
        }

    def _get_smart_recommendations(self, df: pd.DataFrame, numeric_cols: List[str],
                                   categorical_cols: List[str]) -> Dict[str, Any]:
        """Get smart recommendations for visualizations"""
        recommendations = {
            "timeseries": [],
            "distributions": [],
            "comparisons": [],
            "correlations": [],
            "compositions": []
        }

        # Time series recommendations
        time_like = [col for col in df.columns if any(t in col.lower() for t in ['date', 'time', 'year', 'month'])]
        if time_like and numeric_cols:
            recommendations["timeseries"] = {
                "x_column": time_like[0],
                "y_column": numeric_cols[0],
                "suggested_charts": ["Line", "Area", "Column"]
            }

        # Distribution recommendations
        if numeric_cols:
            recommendations["distributions"] = {
                "column": numeric_cols[0],
                "suggested_charts": ["Histogram", "Density", "Box Plot"]
            }

        # Comparison recommendations
        if numeric_cols and categorical_cols:
            recommendations["comparisons"] = {
                "x_column": categorical_cols[0],
                "y_column": numeric_cols[0],
                "suggested_charts": ["Bar", "Column", "Violin", "Box Plot"]
            }

        # Correlation recommendations
        if len(numeric_cols) >= 2:
            recommendations["correlations"] = {
                "x_column": numeric_cols[0],
                "y_column": numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0],
                "suggested_charts": ["Scatter", "Bubble", "Heatmap"]
            }

        # Composition recommendations
        if categorical_cols:
            recommendations["compositions"] = {
                "column": categorical_cols[0],
                "suggested_charts": ["Pie", "Donut", "Treemap", "Stacked Bar"]
            }

        return recommendations

    def _infer_column_type(self, series: pd.Series) -> str:
        """Infer column type"""
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "date"
        else:
            try:
                clean_series = series.dropna()
                if len(clean_series) == 0:
                    return "categorical"
                pd.to_numeric(clean_series)
                return "numeric"
            except (ValueError, TypeError):
                return "categorical"

    def get_recommended_charts(self, df: pd.DataFrame, x_col: str, y_col: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recommended chart types for given columns"""
        x_type = self._infer_column_type(df[x_col])

        if y_col:
            y_type = self._infer_column_type(df[y_col])
        else:
            y_type = None

        charts = []

        if not y_col:
            # Single column
            if x_type == "numeric":
                charts = [
                    {"name": "Histogram", "type": "histogram"},
                    {"name": "Density Plot", "type": "density"},
                    {"name": "Box Plot", "type": "box_single"},
                    {"name": "Scatter Plot", "type": "scatter_single"},
                ]
            else:
                charts = [
                    {"name": "Bar Chart", "type": "bar"},
                    {"name": "Pie Chart", "type": "pie"},
                    {"name": "Donut Chart", "type": "donut"},
                    {"name": "Tree Map", "type": "treemap"},
                    {"name": "Stacked Bar", "type": "stacked_bar_single"},
                ]
        else:
            if x_type == "numeric" and y_type == "numeric":
                charts = [
                    {"name": "Scatter Plot", "type": "scatter"},
                    {"name": "Bubble Chart", "type": "bubble"},
                    {"name": "Line Chart", "type": "line"},
                    {"name": "Area Chart", "type": "area"},
                    {"name": "Hexbin Heatmap", "type": "hexbin"},
                    {"name": "2D Density", "type": "density_2d"},
                ]
            elif (x_type == "numeric" and y_type == "categorical") or (x_type == "categorical" and y_type == "numeric"):
                num_col = x_col if x_type == "numeric" else y_col
                cat_col = y_col if x_type == "numeric" else x_col
                charts = [
                    {"name": "Bar Chart", "type": "bar"},
                    {"name": "Column Chart", "type": "column"},
                    {"name": "Box Plot", "type": "box"},
                    {"name": "Violin Plot", "type": "violin"},
                    {"name": "Strip Plot", "type": "strip"},
                ]
            elif x_type == "categorical" and y_type == "categorical":
                charts = [
                    {"name": "Stacked Bar", "type": "stacked_bar"},
                    {"name": "Grouped Bar", "type": "grouped_bar"},
                    {"name": "Heatmap", "type": "heatmap"},
                    {"name": "Mosaic Plot", "type": "mosaic"},
                ]

        return charts

    def generate_chart_data(self, df: pd.DataFrame, x_column: str, y_column: Optional[str] = None,
                          chart_type: str = None) -> Dict[str, Any]:
        """Generate chart data for any combination"""

        if not chart_type:
            charts = self.get_recommended_charts(df, x_column, y_column)
            if charts:
                chart_type = charts[0]["type"]
            else:
                return {"error": "Could not determine chart type"}

        # Route to appropriate chart generator
        chart_methods = {
            # Single column
            "histogram": self._histogram,
            "density": self._density,
            "box_single": self._box_plot_single,
            "scatter_single": self._scatter_single,
            "bar": self._bar_chart,
            "pie": self._pie_chart,
            "donut": self._donut_chart,
            "treemap": self._treemap,
            "stacked_bar_single": self._stacked_bar_single,

            # Numeric vs Numeric
            "scatter": self._scatter_plot,
            "bubble": self._bubble_chart,
            "line": self._line_chart,
            "area": self._area_chart,
            "hexbin": self._hexbin_chart,
            "density_2d": self._density_2d,

            # Numeric vs Categorical
            "column": self._column_chart,
            "box": self._box_plot,
            "violin": self._violin_plot,
            "strip": self._strip_plot,

            # Categorical vs Categorical
            "stacked_bar": self._stacked_bar,
            "grouped_bar": self._grouped_bar,
            "heatmap": self._heatmap,
            "mosaic": self._mosaic_plot,
        }

        method = chart_methods.get(chart_type)
        if not method:
            return {"error": f"Chart type {chart_type} not supported"}

        try:
            if y_column:
                return method(df, x_column, y_column)
            else:
                return method(df, x_column)
        except Exception as e:
            return {"error": str(e)}

    # ============= SINGLE COLUMN CHARTS =============

    def _histogram(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate histogram"""
        clean_data = df[col].dropna()

        # Validate data
        if len(clean_data) == 0:
            return {"error": f"No data available for {col}"}

        if not pd.api.types.is_numeric_dtype(clean_data):
            return {"error": f"Column {col} must be numeric for histogram"}

        return {
            "type": "histogram",
            "title": f"Distribution of {col}",
            "data": {
                "x": clean_data.tolist(),
                "type": "histogram",
                "nbinsx": 30,
                "marker": {"color": "#8B5CF6", "opacity": 0.7}
            },
            "layout": {
                "title": f"Histogram: {col}",
                "xaxis": {"title": col},
                "yaxis": {"title": "Frequency"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            },
            "stats": {
                "mean": float(clean_data.mean()),
                "median": float(clean_data.median()),
                "std": float(clean_data.std()),
                "min": float(clean_data.min()),
                "max": float(clean_data.max())
            }
        }

    def _density(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate density plot"""
        clean_data = df[col].dropna()

        # Validate data
        if len(clean_data) == 0:
            return {"error": f"No data available for {col}"}

        if not pd.api.types.is_numeric_dtype(clean_data):
            return {"error": f"Column {col} must be numeric for density plot"}

        return {
            "type": "density",
            "title": f"Density Plot: {col}",
            "data": [{
                "x": clean_data.tolist(),
                "type": "histogram",
                "histnorm": "probability density",
                "marker": {"color": "#EC4899", "opacity": 0.6}
            }],
            "layout": {
                "title": f"Density Plot: {col}",
                "xaxis": {"title": col},
                "yaxis": {"title": "Density"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _box_plot_single(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate single box plot"""
        clean_data = df[col].dropna()

        # Validate data
        if len(clean_data) == 0:
            return {"error": f"No data available for {col}"}

        if not pd.api.types.is_numeric_dtype(clean_data):
            return {"error": f"Column {col} must be numeric for box plot"}

        return {
            "type": "box",
            "title": f"Box Plot: {col}",
            "data": [{
                "y": clean_data.tolist(),
                "name": col,
                "type": "box",
                "marker": {"color": "#06B6D4"},
                "boxmean": "sd"
            }],
            "layout": {
                "title": f"Box Plot: {col}",
                "yaxis": {"title": col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            },
            "stats": {
                "q1": float(clean_data.quantile(0.25)),
                "median": float(clean_data.median()),
                "q3": float(clean_data.quantile(0.75)),
                "iqr": float(clean_data.quantile(0.75) - clean_data.quantile(0.25))
            }
        }

    def _scatter_single(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate scatter plot for single column"""
        clean_data = df[col].dropna()

        # Validate data
        if len(clean_data) == 0:
            return {"error": f"No data available for {col}"}

        if not pd.api.types.is_numeric_dtype(clean_data):
            return {"error": f"Column {col} must be numeric for scatter plot"}

        indices = list(range(len(clean_data)))

        return {
            "type": "scatter",
            "title": f"Value Distribution: {col}",
            "data": {
                "x": indices,
                "y": clean_data.tolist(),
                "mode": "markers",
                "marker": {"color": "#F59E0B", "size": 6, "opacity": 0.6}
            },
            "layout": {
                "title": f"Scatter: {col}",
                "xaxis": {"title": "Index"},
                "yaxis": {"title": col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _bar_chart(self, df: pd.DataFrame, col: str = None, num_col: str = None) -> Dict[str, Any]:
        """Generate bar chart for categorical column or categorical vs numeric"""
        # Handle both single column and two column cases
        if col and num_col:
            # Two column case: categorical aggregation
            clean = df[[col, num_col]].dropna()
            if pd.api.types.is_numeric_dtype(clean[num_col]):
                grouped = clean.groupby(col)[num_col].count().sort_values(ascending=False).head(self.max_categories)
            else:
                grouped = pd.crosstab(clean[col], clean[num_col]).sum(axis=1).sort_values(ascending=False).head(self.max_categories)
        else:
            # Single column case
            col = col or num_col
            grouped = df[col].value_counts().head(self.max_categories)

        return {
            "type": "bar",
            "title": f"Bar Chart: {col}",
            "data": {
                "x": grouped.index.astype(str).tolist(),
                "y": grouped.values.tolist(),
                "type": "bar",
                "marker": {"color": "#8B5CF6"}
            },
            "layout": {
                "title": f"Bar Chart: {col}",
                "xaxis": {"title": col},
                "yaxis": {"title": "Count"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _pie_chart(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate pie chart"""
        value_counts = df[col].value_counts().head(10)

        # Validate data
        if len(value_counts) == 0:
            return {"error": f"No data available for {col}"}

        return {
            "type": "pie",
            "data": [{
                "labels": value_counts.index.astype(str).tolist(),
                "values": value_counts.values.tolist(),
                "type": "pie",
                "marker": {"line": {"color": "#16213e", "width": 2}},
                "textposition": "inside",
                "textinfo": "label+percent"
            }],
            "layout": {
                "title": f"Pie Chart: {col}",
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _donut_chart(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate donut chart"""
        value_counts = df[col].value_counts().head(10)

        # Validate data
        if len(value_counts) == 0:
            return {"error": f"No data available for {col}"}

        return {
            "type": "pie",
            "data": [{
                "labels": value_counts.index.astype(str).tolist(),
                "values": value_counts.values.tolist(),
                "type": "pie",
                "hole": 0.4,
                "marker": {"line": {"color": "#16213e", "width": 2}},
                "textposition": "inside",
                "textinfo": "label+percent"
            }],
            "layout": {
                "title": f"Donut Chart: {col}",
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _treemap(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate treemap"""
        value_counts = df[col].value_counts().head(15)

        # Validate data
        if len(value_counts) == 0:
            return {"error": f"No data available for {col}"}

        return {
            "type": "treemap",
            "data": [{
                "labels": value_counts.index.astype(str).tolist(),
                "parents": [""] * len(value_counts),
                "values": value_counts.values.tolist(),
                "type": "treemap",
                "marker": {"colors": value_counts.values.tolist(), "colorscale": "Viridis"}
            }],
            "layout": {
                "title": f"Tree Map: {col}",
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _stacked_bar_single(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Generate stacked bar for single column"""
        return self._bar_chart(df, col)

    # ============= TWO COLUMN CHARTS =============

    def _scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate scatter plot"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        if not pd.api.types.is_numeric_dtype(clean[x_col]):
            return {"error": f"Column {x_col} must be numeric for scatter plot"}

        if not pd.api.types.is_numeric_dtype(clean[y_col]):
            return {"error": f"Column {y_col} must be numeric for scatter plot"}

        return {
            "type": "scatter",
            "data": {
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "mode": "markers",
                "marker": {
                    "size": 8,
                    "color": clean[y_col].tolist(),
                    "colorscale": "Viridis",
                    "showscale": True,
                    "opacity": 0.7
                }
            },
            "layout": {
                "title": f"{x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _bubble_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate bubble chart"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        if not pd.api.types.is_numeric_dtype(clean[x_col]):
            return {"error": f"Column {x_col} must be numeric for bubble chart"}

        if not pd.api.types.is_numeric_dtype(clean[y_col]):
            return {"error": f"Column {y_col} must be numeric for bubble chart"}

        sizes = np.abs(clean[y_col] - clean[y_col].min()) + 1
        sizes = (sizes / sizes.max() * 40 + 5).tolist()

        return {
            "type": "scatter",
            "data": {
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "mode": "markers",
                "marker": {
                    "size": sizes,
                    "color": clean[y_col].tolist(),
                    "colorscale": "Plasma",
                    "showscale": True,
                    "opacity": 0.6
                }
            },
            "layout": {
                "title": f"Bubble Chart: {x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _line_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate line chart"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        if not pd.api.types.is_numeric_dtype(clean[y_col]):
            return {"error": f"Column {y_col} must be numeric for line chart"}

        if pd.api.types.is_numeric_dtype(clean[x_col]):
            clean = clean.sort_values(x_col)

        return {
            "type": "scatter",
            "data": {
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "mode": "lines+markers",
                "line": {"color": "#8B5CF6", "width": 3},
                "marker": {"size": 6}
            },
            "layout": {
                "title": f"Line Chart: {x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _area_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate area chart"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        if not pd.api.types.is_numeric_dtype(clean[y_col]):
            return {"error": f"Column {y_col} must be numeric for area chart"}

        if pd.api.types.is_numeric_dtype(clean[x_col]):
            clean = clean.sort_values(x_col)

        return {
            "type": "scatter",
            "data": {
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "fill": "tozeroy",
                "mode": "lines",
                "line": {"color": "#EC4899", "width": 2},
                "fillcolor": "rgba(236, 72, 153, 0.2)"
            },
            "layout": {
                "title": f"Area Chart: {x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _hexbin_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate 2D histogram (hexbin simulation)"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        if not pd.api.types.is_numeric_dtype(clean[x_col]):
            return {"error": f"Column {x_col} must be numeric for hexbin chart"}

        if not pd.api.types.is_numeric_dtype(clean[y_col]):
            return {"error": f"Column {y_col} must be numeric for hexbin chart"}

        return {
            "type": "histogram2d",
            "data": [{
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "colorscale": "Viridis",
                "type": "histogram2d",
                "nbinsx": 20,
                "nbinsy": 20
            }],
            "layout": {
                "title": f"Density Heatmap: {x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _density_2d(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate 2D density plot"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        if not pd.api.types.is_numeric_dtype(clean[x_col]):
            return {"error": f"Column {x_col} must be numeric for 2D density"}

        if not pd.api.types.is_numeric_dtype(clean[y_col]):
            return {"error": f"Column {y_col} must be numeric for 2D density"}

        return {
            "type": "scatter",
            "data": {
                "x": clean[x_col].tolist(),
                "y": clean[y_col].tolist(),
                "mode": "markers",
                "marker": {
                    "size": 4,
                    "color": "rgba(139, 92, 246, 0.3)"
                }
            },
            "layout": {
                "title": f"2D Density: {x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": y_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _column_chart(self, df: pd.DataFrame, cat_col: str, num_col: str) -> Dict[str, Any]:
        """Generate column chart (vertical bars)"""
        clean = df[[cat_col, num_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {cat_col} vs {num_col}"}

        # Only aggregate if num_col is numeric
        if pd.api.types.is_numeric_dtype(clean[num_col]):
            grouped = clean.groupby(cat_col)[num_col].mean().sort_values(ascending=False).head(15)
            is_numeric = True
        else:
            # If not numeric, just count occurrences
            grouped = clean[cat_col].value_counts().head(15)
            num_col = "Count"
            is_numeric = False

        # Validate grouped data
        if len(grouped) == 0:
            return {"error": f"No grouped data available"}

        # Safe type checking
        first_val = grouped.values[0] if len(grouped.values) > 0 else None
        is_numeric_val = isinstance(first_val, (int, float, np.integer, np.floating))

        return {
            "type": "bar",
            "data": {
                "x": grouped.index.astype(str).tolist(),
                "y": grouped.values.tolist(),
                "type": "bar",
                "marker": {"color": "#06B6D4"}
            },
            "layout": {
                "title": f"Average {num_col} by {cat_col}" if is_numeric_val else f"{cat_col} Distribution",
                "xaxis": {"title": cat_col},
                "yaxis": {"title": f"Average {num_col}" if is_numeric_val else "Count"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _box_plot(self, df: pd.DataFrame, cat_col: str, num_col: str) -> Dict[str, Any]:
        """Generate box plot"""
        clean = df[[cat_col, num_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {cat_col} vs {num_col}"}

        if not pd.api.types.is_numeric_dtype(clean[num_col]):
            return {"error": f"Column {num_col} must be numeric for box plot"}

        categories = clean[cat_col].unique()[:self.max_categories]

        data = []
        for cat in categories:
            values = clean[clean[cat_col] == cat][num_col].tolist()
            if len(values) > 0:
                data.append({
                    "y": values,
                    "name": str(cat),
                    "type": "box"
                })

        if len(data) == 0:
            return {"error": f"No valid data for box plot"}

        return {
            "type": "box",
            "data": data,
            "layout": {
                "title": f"Distribution of {num_col} by {cat_col}",
                "yaxis": {"title": num_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _violin_plot(self, df: pd.DataFrame, cat_col: str, num_col: str) -> Dict[str, Any]:
        """Generate violin plot"""
        clean = df[[cat_col, num_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {cat_col} vs {num_col}"}

        if not pd.api.types.is_numeric_dtype(clean[num_col]):
            return {"error": f"Column {num_col} must be numeric for violin plot"}

        categories = clean[cat_col].unique()[:self.max_categories]

        data = []
        for cat in categories:
            values = clean[clean[cat_col] == cat][num_col].tolist()
            if len(values) > 0:
                data.append({
                    "y": values,
                    "name": str(cat),
                    "type": "violin",
                    "meanline": {"visible": True},
                    "points": "outliers"
                })

        if len(data) == 0:
            return {"error": f"No valid data for violin plot"}

        return {
            "type": "violin",
            "data": data,
            "layout": {
                "title": f"Violin Plot: {num_col} by {cat_col}",
                "yaxis": {"title": num_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _strip_plot(self, df: pd.DataFrame, cat_col: str, num_col: str) -> Dict[str, Any]:
        """Generate strip plot (scatter with jitter)"""
        clean = df[[cat_col, num_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {cat_col} vs {num_col}"}

        if not pd.api.types.is_numeric_dtype(clean[num_col]):
            return {"error": f"Column {num_col} must be numeric for strip plot"}

        data = []
        for i, cat in enumerate(clean[cat_col].unique()[:self.max_categories]):
            values = clean[clean[cat_col] == cat][num_col].tolist()
            if len(values) > 0:
                x_jitter = [i + np.random.normal(0, 0.04) for _ in values]
                data.append({
                    "x": x_jitter,
                    "y": values,
                    "mode": "markers",
                    "name": str(cat),
                    "marker": {"size": 6, "opacity": 0.6}
                })

        if len(data) == 0:
            return {"error": f"No valid data for strip plot"}

        return {
            "type": "scatter",
            "data": data,
            "layout": {
                "title": f"Strip Plot: {num_col} by {cat_col}",
                "yaxis": {"title": num_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _stacked_bar(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate stacked bar chart"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        crosstab = pd.crosstab(clean[x_col], clean[y_col])

        # Validate crosstab
        if len(crosstab) == 0 or len(crosstab.columns) == 0:
            return {"error": f"No grouped data available"}

        data = []
        for col in crosstab.columns:
            data.append({
                "x": crosstab.index.astype(str).tolist(),
                "y": crosstab[col].tolist(),
                "name": str(col),
                "type": "bar"
            })

        return {
            "type": "bar",
            "data": data,
            "layout": {
                "barmode": "stack",
                "title": f"Stacked Bar: {x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": "Count"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _grouped_bar(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate grouped bar chart"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        crosstab = pd.crosstab(clean[x_col], clean[y_col])

        # Validate crosstab
        if len(crosstab) == 0 or len(crosstab.columns) == 0:
            return {"error": f"No grouped data available"}

        data = []
        for col in crosstab.columns:
            data.append({
                "x": crosstab.index.astype(str).tolist(),
                "y": crosstab[col].tolist(),
                "name": str(col),
                "type": "bar"
            })

        return {
            "type": "bar",
            "data": data,
            "layout": {
                "barmode": "group",
                "title": f"Grouped Bar: {x_col} vs {y_col}",
                "xaxis": {"title": x_col},
                "yaxis": {"title": "Count"},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _heatmap(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate heatmap"""
        clean = df[[x_col, y_col]].dropna()

        # Validate data
        if len(clean) == 0:
            return {"error": f"No data available for {x_col} vs {y_col}"}

        crosstab = pd.crosstab(clean[x_col], clean[y_col])

        # Validate crosstab
        if len(crosstab) == 0 or len(crosstab.columns) == 0:
            return {"error": f"No grouped data available"}

        return {
            "type": "heatmap",
            "data": [{
                "z": crosstab.values.tolist(),
                "x": crosstab.columns.astype(str).tolist(),
                "y": crosstab.index.astype(str).tolist(),
                "type": "heatmap",
                "colorscale": "Viridis"
            }],
            "layout": {
                "title": f"Heatmap: {x_col} vs {y_col}",
                "xaxis": {"title": y_col},
                "yaxis": {"title": x_col},
                "plot_bgcolor": "#1a1a2e",
                "paper_bgcolor": "#16213e",
                "font": {"color": "#ffffff"}
            }
        }

    def _mosaic_plot(self, df: pd.DataFrame, x_col: str, y_col: str) -> Dict[str, Any]:
        """Generate mosaic plot (as stacked bar with widths)"""
        return self._stacked_bar(df, x_col, y_col)

    def generate_smart_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate smart dashboard with intelligent chart selection"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        dashboard_data = {
            "summary": {
                "total_rows": int(len(df)),
                "total_columns": len(df.columns),
                "numeric_columns": len(numeric_cols),
                "categorical_columns": len(categorical_cols)
            },
            "charts": []
        }

        # Add distribution charts for numeric columns
        for col in numeric_cols[:3]:
            dashboard_data["charts"].append(
                self.generate_chart_data(df, col, chart_type="histogram")
            )

        # Add frequency charts for categorical
        for col in categorical_cols[:2]:
            dashboard_data["charts"].append(
                self.generate_chart_data(df, col, chart_type="bar")
            )

        # Add relationship charts
        if len(numeric_cols) >= 2:
            dashboard_data["charts"].append(
                self.generate_chart_data(df, numeric_cols[0], numeric_cols[1], chart_type="scatter")
            )

        if numeric_cols and categorical_cols:
            dashboard_data["charts"].append(
                self.generate_chart_data(df, categorical_cols[0], numeric_cols[0], chart_type="box")
            )

        return dashboard_data
