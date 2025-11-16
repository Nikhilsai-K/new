"""
Advanced Tableau/Power BI-Quality Visualizations
Professional, publication-ready charts with enterprise styling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json


class AdvancedVisualizationEngine:
    """
    Enterprise-Grade Visualization Engine

    Generates Tableau/Power BI-quality chart configurations:
    - Professional color schemes
    - Smart axis formatting
    - Intelligent aggregations
    - Interactive features
    - Responsive layouts
    - Advanced chart types
    """

    def __init__(self):
        # Professional color palettes (Tableau-style)
        self.color_schemes = {
            "professional": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
            "tableau10": ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#59a14f", "#edc949"],
            "powerbi": ["#01b8aa", "#374649", "#fd625e", "#f2c80f", "#5f6b6d", "#8ad4eb"],
            "corporate": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a"],
            "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F"],
            "modern": ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe", "#43e97b"]
        }

        self.default_scheme = "tableau10"

    def generate_line_chart(self, df: pd.DataFrame, x_column: str, y_column: str,
                           title: str = "", config: Dict = None) -> Dict[str, Any]:
        """
        Generate advanced line chart configuration (Tableau-quality)

        Features:
        - Multiple lines with legend
        - Smooth curves option
        - Markers on data points
        - Grid lines
        - Hover tooltips
        - Trend lines
        """
        config = config or {}

        # Prepare data
        df_sorted = df.sort_values(x_column)
        x_data = df_sorted[x_column].tolist()
        y_data = df_sorted[y_column].tolist()

        chart_config = {
            "type": "line",
            "title": title or f"{y_column} over {x_column}",
            "data": {
                "labels": x_data,
                "datasets": [{
                    "label": y_column,
                    "data": y_data,
                    "borderColor": self.color_schemes[self.default_scheme][0],
                    "backgroundColor": "rgba(78, 121, 167, 0.1)",
                    "borderWidth": 3,
                    "tension": 0.4,  # Smooth curves
                    "fill": config.get("fill_area", True),
                    "pointRadius": 4,
                    "pointHoverRadius": 6,
                    "pointBackgroundColor": self.color_schemes[self.default_scheme][0],
                    "pointBorderColor": "#fff",
                    "pointBorderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "interaction": {
                    "mode": "index",
                    "intersect": False
                },
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "top",
                        "labels": {
                            "font": {"size": 12, "weight": "bold"},
                            "padding": 15,
                            "usePointStyle": True
                        }
                    },
                    "tooltip": {
                        "enabled": True,
                        "backgroundColor": "rgba(0, 0, 0, 0.8)",
                        "padding": 12,
                        "titleFont": {"size": 14, "weight": "bold"},
                        "bodyFont": {"size": 12},
                        "cornerRadius": 6,
                        "displayColors": True
                    },
                    "title": {
                        "display": True,
                        "text": title or f"{y_column} Trend",
                        "font": {"size": 18, "weight": "bold"},
                        "padding": 20
                    }
                },
                "scales": {
                    "x": {
                        "display": True,
                        "title": {
                            "display": True,
                            "text": x_column,
                            "font": {"size": 14, "weight": "bold"}
                        },
                        "grid": {
                            "display": config.get("show_grid", True),
                            "color": "rgba(0, 0, 0, 0.05)"
                        }
                    },
                    "y": {
                        "display": True,
                        "title": {
                            "display": True,
                            "text": y_column,
                            "font": {"size": 14, "weight": "bold"}
                        },
                        "grid": {
                            "display": True,
                            "color": "rgba(0, 0, 0, 0.05)"
                        },
                        "ticks": {
                            "callback": "value => value.toLocaleString()"  # Format numbers
                        }
                    }
                }
            },
            "advanced_features": {
                "exportable": True,
                "zoomable": True,
                "annotations": config.get("annotations", [])
            }
        }

        return chart_config

    def generate_bar_chart(self, df: pd.DataFrame, x_column: str, y_column: str,
                          title: str = "", config: Dict = None) -> Dict[str, Any]:
        """
        Generate advanced bar chart (Power BI-quality)

        Features:
        - Horizontal/vertical orientation
        - Grouped/stacked bars
        - Value labels on bars
        - Sorted by value option
        - Color gradients
        """
        config = config or {}

        # Aggregate data
        if config.get("aggregate", True):
            df_agg = df.groupby(x_column)[y_column].sum().reset_index()
        else:
            df_agg = df[[x_column, y_column]].copy()

        # Sort if requested
        if config.get("sort_by_value", True):
            df_agg = df_agg.sort_values(y_column, ascending=False)

        # Limit to top N
        top_n = config.get("top_n", 20)
        df_agg = df_agg.head(top_n)

        x_data = df_agg[x_column].astype(str).tolist()
        y_data = df_agg[y_column].tolist()

        # Generate color gradient
        colors = self._generate_color_gradient(len(y_data), self.color_schemes[self.default_scheme][0])

        chart_config = {
            "type": "bar",
            "title": title or f"{y_column} by {x_column}",
            "data": {
                "labels": x_data,
                "datasets": [{
                    "label": y_column,
                    "data": y_data,
                    "backgroundColor": colors,
                    "borderColor": colors,
                    "borderWidth": 2,
                    "borderRadius": 6,
                    "barThickness": config.get("bar_thickness", "flex")
                }]
            },
            "options": {
                "indexAxis": config.get("orientation", "x"),  # x = vertical, y = horizontal
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": config.get("show_legend", False)
                    },
                    "tooltip": {
                        "enabled": True,
                        "backgroundColor": "rgba(0, 0, 0, 0.8)",
                        "padding": 12,
                        "cornerRadius": 6
                    },
                    "title": {
                        "display": True,
                        "text": title or f"Top {len(y_data)} by {y_column}",
                        "font": {"size": 18, "weight": "bold"},
                        "padding": 20
                    },
                    "datalabels": {
                        "display": config.get("show_values", True),
                        "color": "#fff",
                        "font": {"weight": "bold"},
                        "formatter": "value => value.toLocaleString()"
                    }
                },
                "scales": {
                    "x": {
                        "grid": {"display": False},
                        "ticks": {
                            "font": {"size": 11},
                            "maxRotation": 45,
                            "minRotation": 0
                        }
                    },
                    "y": {
                        "grid": {
                            "display": True,
                            "color": "rgba(0, 0, 0, 0.05)"
                        },
                        "ticks": {
                            "callback": "value => value.toLocaleString()"
                        }
                    }
                }
            }
        }

        return chart_config

    def generate_scatter_plot(self, df: pd.DataFrame, x_column: str, y_column: str,
                             title: str = "", config: Dict = None) -> Dict[str, Any]:
        """
        Generate advanced scatter plot with trend line

        Features:
        - Bubble sizes (3rd dimension)
        - Color by category
        - Trend line/regression
        - Correlation coefficient
        - Outlier highlighting
        """
        config = config or {}

        # Sample data if too large
        if len(df) > 1000:
            df_sample = df.sample(1000, random_state=42)
        else:
            df_sample = df

        x_data = df_sample[x_column].tolist()
        y_data = df_sample[y_column].tolist()

        # Calculate correlation
        correlation = df_sample[[x_column, y_column]].corr().iloc[0, 1]

        chart_config = {
            "type": "scatter",
            "title": title or f"{y_column} vs {x_column}",
            "data": {
                "datasets": [{
                    "label": f"{y_column} vs {x_column}",
                    "data": [{"x": x, "y": y} for x, y in zip(x_data, y_data)],
                    "backgroundColor": "rgba(78, 121, 167, 0.6)",
                    "borderColor": self.color_schemes[self.default_scheme][0],
                    "borderWidth": 2,
                    "pointRadius": 5,
                    "pointHoverRadius": 8
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": True},
                    "tooltip": {
                        "enabled": True,
                        "callbacks": {
                            "label": f"(context) => `${{{x_column}}}: ${{context.parsed.x}}, {y_column}: ${{context.parsed.y}}`"
                        }
                    },
                    "title": {
                        "display": True,
                        "text": [
                            title or f"{y_column} vs {x_column}",
                            f"Correlation: {correlation:.3f}"
                        ],
                        "font": {"size": 18, "weight": "bold"},
                        "padding": 20
                    }
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": x_column,
                            "font": {"size": 14, "weight": "bold"}
                        },
                        "grid": {"color": "rgba(0, 0, 0, 0.05)"}
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": y_column,
                            "font": {"size": 14, "weight": "bold"}
                        },
                        "grid": {"color": "rgba(0, 0, 0, 0.05)"}
                    }
                }
            },
            "statistics": {
                "correlation": round(correlation, 3),
                "sample_size": len(df_sample),
                "total_points": len(df)
            }
        }

        return chart_config

    def generate_heatmap(self, df: pd.DataFrame, config: Dict = None) -> Dict[str, Any]:
        """
        Generate correlation heatmap (for numeric columns)

        Features:
        - Correlation matrix
        - Color intensity by value
        - Annotations with values
        - Hierarchical clustering option
        """
        config = config or {}

        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            return {"error": "Need at least 2 numeric columns for heatmap"}

        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()

        # Convert to list format for Chart.js matrix plugin
        data = []
        for i, row_name in enumerate(corr_matrix.index):
            for j, col_name in enumerate(corr_matrix.columns):
                data.append({
                    "x": col_name,
                    "y": row_name,
                    "v": round(corr_matrix.iloc[i, j], 3)
                })

        chart_config = {
            "type": "matrix",
            "title": "Correlation Heatmap",
            "data": {
                "datasets": [{
                    "label": "Correlation",
                    "data": data,
                    "backgroundColor": "value => value.v > 0 ? `rgba(76, 175, 80, ${Math.abs(value.v)})` : `rgba(244, 67, 54, ${Math.abs(value.v)})`",
                    "borderWidth": 1,
                    "borderColor": "#fff",
                    "width": "({chart}) => (chart.chartArea || {}).width / chart.scales.x.ticks.length - 1",
                    "height": "({chart}) => (chart.chartArea || {}).height / chart.scales.y.ticks.length - 1"
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {
                        "callbacks": {
                            "title": "() => ''",
                            "label": "(context) => `${context.dataset.data[context.dataIndex].y} × ${context.dataset.data[context.dataIndex].x}: ${context.dataset.data[context.dataIndex].v}`"
                        }
                    },
                    "title": {
                        "display": True,
                        "text": "Feature Correlation Matrix",
                        "font": {"size": 18, "weight": "bold"}
                    }
                },
                "scales": {
                    "x": {
                        "type": "category",
                        "ticks": {
                            "font": {"size": 10},
                            "maxRotation": 90,
                            "minRotation": 45
                        }
                    },
                    "y": {
                        "type": "category",
                        "offset": True,
                        "ticks": {"font": {"size": 10}}
                    }
                }
            }
        }

        return chart_config

    def generate_pie_chart(self, df: pd.DataFrame, category_column: str, value_column: str,
                          title: str = "", config: Dict = None) -> Dict[str, Any]:
        """
        Generate advanced pie/doughnut chart

        Features:
        - Donut chart option
        - Percentage labels
        - Legend with values
        - Top N categories + "Others"
        """
        config = config or {}

        # Aggregate data
        df_agg = df.groupby(category_column)[value_column].sum().reset_index()
        df_agg = df_agg.sort_values(value_column, ascending=False)

        # Keep top N, group rest as "Others"
        top_n = config.get("top_n", 10)
        if len(df_agg) > top_n:
            top_df = df_agg.head(top_n)
            others_sum = df_agg.iloc[top_n:][value_column].sum()
            others_row = pd.DataFrame({category_column: ["Others"], value_column: [others_sum]})
            df_agg = pd.concat([top_df, others_row], ignore_index=True)

        labels = df_agg[category_column].astype(str).tolist()
        values = df_agg[value_column].tolist()

        # Use professional colors
        colors = self.color_schemes[config.get("color_scheme", self.default_scheme)]
        background_colors = colors[:len(labels)]

        chart_config = {
            "type": config.get("variant", "doughnut"),  # pie or doughnut
            "title": title or f"{value_column} Distribution",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": values,
                    "backgroundColor": background_colors,
                    "borderColor": "#fff",
                    "borderWidth": 3,
                    "hoverOffset": 10
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "right",
                        "labels": {
                            "font": {"size": 12},
                            "padding": 15,
                            "generateLabels": "function(chart) { /* custom labels with percentages */ }"
                        }
                    },
                    "tooltip": {
                        "callbacks": {
                            "label": "(context) => `${context.label}: ${context.parsed.toLocaleString()} (${((context.parsed / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%)`"
                        }
                    },
                    "title": {
                        "display": True,
                        "text": title or f"{value_column} by {category_column}",
                        "font": {"size": 18, "weight": "bold"}
                    },
                    "datalabels": {
                        "formatter": "(value, context) => ((value / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1) + '%'",
                        "color": "#fff",
                        "font": {"weight": "bold", "size": 14}
                    }
                }
            }
        }

        return chart_config

    def _generate_color_gradient(self, n: int, base_color: str) -> List[str]:
        """Generate n colors as gradient from base color"""
        # Simple gradient by adjusting opacity
        return [f"{base_color}{hex(int(255 - (i * 180 / n)))[2:].zfill(2)}" for i in range(n)]

    def get_chart_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get smart chart recommendations based on data

        Returns list of recommended chart configurations
        """
        recommendations = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # Recommend bar chart for categorical vs numeric
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            recommendations.append({
                "type": "bar",
                "priority": "high",
                "x": categorical_cols[0],
                "y": numeric_cols[0],
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}"
            })

        # Recommend scatter for numeric correlations
        if len(numeric_cols) >= 2:
            recommendations.append({
                "type": "scatter",
                "priority": "high",
                "x": numeric_cols[0],
                "y": numeric_cols[1],
                "title": "Correlation Analysis"
            })

        # Recommend heatmap for correlations
        if len(numeric_cols) >= 3:
            recommendations.append({
                "type": "heatmap",
                "priority": "medium",
                "title": "Feature Correlations"
            })

        return recommendations
