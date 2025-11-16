"""
Exploratory Data Analysis (EDA) Service
Provides basic data analysis functions that data analysts commonly use
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import io


class EDAService:
    """Perform exploratory data analysis on datasets"""

    def __init__(self):
        pass

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive EDA on a DataFrame

        Returns dict with:
        - head: First 5-10 rows
        - tail: Last 5-10 rows
        - info: DataFrame info
        - describe: Statistical summary
        - nullCounts: Missing values per column
        - shape: {rows, columns}
        - dtypes: Data types per column
        - columns: List of column names
        - correlations: Correlation matrix for numeric columns
        - value_counts: Value counts for categorical columns (top 10)
        """

        result = {}

        # df.head() - First rows
        result['head'] = df.head(10).to_dict(orient='records')

        # df.tail() - Last rows
        result['tail'] = df.tail(10).to_dict(orient='records')

        # df.shape
        result['shape'] = {
            'rows': int(df.shape[0]),
            'columns': int(df.shape[1])
        }

        # df.columns
        result['columns'] = df.columns.tolist()

        # df.dtypes
        result['dtypes'] = {col: str(dtype) for col, dtype in df.dtypes.items()}

        # df.describe() - Statistical summary for numeric columns
        describe_df = df.describe(include='all')
        result['describe'] = describe_df.to_dict()

        # df.info() - Column information
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()

        result['info'] = {
            'summary': info_str,
            'memory_usage': df.memory_usage(deep=True).sum(),
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_details': [
                {
                    'column': col,
                    'dtype': str(df[col].dtype),
                    'non_null_count': int(df[col].count()),
                    'null_count': int(df[col].isnull().sum()),
                    'null_percentage': float(df[col].isnull().sum() / len(df) * 100)
                }
                for col in df.columns
            ]
        }

        # df.isnull().sum() - Missing values
        result['nullCounts'] = {
            col: {
                'count': int(df[col].isnull().sum()),
                'percentage': float(df[col].isnull().sum() / len(df) * 100)
            }
            for col in df.columns
        }

        # Correlation matrix for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            result['correlations'] = corr_matrix.to_dict()
        else:
            result['correlations'] = {}

        # Value counts for categorical columns (top 10)
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        result['value_counts'] = {}
        for col in categorical_cols[:10]:  # Limit to first 10 categorical columns
            value_counts = df[col].value_counts().head(10)
            result['value_counts'][col] = value_counts.to_dict()

        # Summary statistics
        result['summary'] = {
            'total_records': int(len(df)),
            'total_columns': int(len(df.columns)),
            'numeric_columns': len(numeric_cols),
            'categorical_columns': len(categorical_cols),
            'total_missing_values': int(df.isnull().sum().sum()),
            'missing_percentage': float(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100),
            'duplicate_rows': int(df.duplicated().sum()),
            'memory_usage_mb': float(df.memory_usage(deep=True).sum() / (1024 * 1024))
        }

        # Sample data (first 100 rows for preview)
        result['sample_data'] = df.head(100).to_dict(orient='records')

        return result

    def get_column_stats(self, df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific column"""

        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")

        col = df[column_name]
        stats = {
            'column_name': column_name,
            'dtype': str(col.dtype),
            'total_count': int(len(col)),
            'non_null_count': int(col.count()),
            'null_count': int(col.isnull().sum()),
            'null_percentage': float(col.isnull().sum() / len(col) * 100),
            'unique_count': int(col.nunique()),
            'unique_percentage': float(col.nunique() / len(col) * 100)
        }

        # Numeric column statistics
        if pd.api.types.is_numeric_dtype(col):
            stats.update({
                'mean': float(col.mean()) if not col.isnull().all() else None,
                'median': float(col.median()) if not col.isnull().all() else None,
                'mode': float(col.mode()[0]) if len(col.mode()) > 0 else None,
                'std': float(col.std()) if not col.isnull().all() else None,
                'min': float(col.min()) if not col.isnull().all() else None,
                'max': float(col.max()) if not col.isnull().all() else None,
                'q25': float(col.quantile(0.25)) if not col.isnull().all() else None,
                'q50': float(col.quantile(0.50)) if not col.isnull().all() else None,
                'q75': float(col.quantile(0.75)) if not col.isnull().all() else None,
                'skewness': float(col.skew()) if not col.isnull().all() else None,
                'kurtosis': float(col.kurt()) if not col.isnull().all() else None,
            })

        # Categorical column statistics
        elif pd.api.types.is_string_dtype(col) or pd.api.types.is_object_dtype(col):
            value_counts = col.value_counts().head(20)
            stats.update({
                'most_common': value_counts.to_dict(),
                'most_common_value': str(col.mode()[0]) if len(col.mode()) > 0 else None,
                'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'least_common_value': str(value_counts.index[-1]) if len(value_counts) > 0 else None,
                'least_common_count': int(value_counts.iloc[-1]) if len(value_counts) > 0 else 0,
            })

        return stats

    def get_data_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a comprehensive data quality report"""

        report = {
            'overall_quality_score': 0,
            'issues': [],
            'recommendations': []
        }

        # Check for missing values
        total_missing = df.isnull().sum().sum()
        missing_pct = (total_missing / (len(df) * len(df.columns))) * 100

        if missing_pct > 20:
            report['issues'].append({
                'severity': 'high',
                'type': 'missing_values',
                'message': f'{missing_pct:.1f}% of data is missing',
                'affected_columns': df.columns[df.isnull().sum() > 0].tolist()
            })
            report['recommendations'].append('Consider imputation or removal of columns with high missing values')
        elif missing_pct > 5:
            report['issues'].append({
                'severity': 'medium',
                'type': 'missing_values',
                'message': f'{missing_pct:.1f}% of data is missing'
            })

        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(df)) * 100
            severity = 'high' if dup_pct > 10 else 'medium' if dup_pct > 1 else 'low'
            report['issues'].append({
                'severity': severity,
                'type': 'duplicates',
                'message': f'{duplicates} duplicate rows found ({dup_pct:.1f}%)'
            })
            report['recommendations'].append('Remove duplicate rows to ensure data integrity')

        # Check for high cardinality
        for col in df.select_dtypes(include=['object', 'category']).columns:
            cardinality = df[col].nunique()
            if cardinality > len(df) * 0.9:
                report['issues'].append({
                    'severity': 'low',
                    'type': 'high_cardinality',
                    'message': f'Column "{col}" has very high cardinality ({cardinality} unique values)',
                    'column': col
                })

        # Calculate quality score (0-100)
        quality_score = 100
        quality_score -= min(missing_pct * 2, 40)  # Max 40 points deduction for missing values
        quality_score -= min((duplicates / len(df)) * 100, 30)  # Max 30 points deduction for duplicates
        quality_score = max(0, quality_score)

        report['overall_quality_score'] = round(quality_score, 1)

        return report
