import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import re
from datetime import datetime


class DataCleaner:
    """Core data cleaning service with rule-based cleaning"""

    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality and detect issues"""
        analysis = {
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "issues": [],
            "quality_score": 100,
            "column_analysis": {}
        }

        deductions = 0

        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            analysis["issues"].append({
                "type": "duplicates",
                "severity": "medium",
                "count": int(duplicate_count),
                "message": f"Found {duplicate_count} duplicate rows"
            })
            deductions += min(20, duplicate_count / len(df) * 100)

        # Analyze each column
        for col in df.columns:
            col_analysis = {
                "dtype": str(df[col].dtype),
                "missing_count": int(df[col].isna().sum()),
                "missing_percentage": round(df[col].isna().sum() / len(df) * 100, 2),
                "unique_count": int(df[col].nunique()),
                "issues": []
            }

            # Check for missing values
            if col_analysis["missing_count"] > 0:
                col_analysis["issues"].append({
                    "type": "missing_values",
                    "count": col_analysis["missing_count"],
                    "percentage": col_analysis["missing_percentage"]
                })
                deductions += min(10, col_analysis["missing_percentage"] / 10)

            # Check for potential data type issues
            if df[col].dtype == 'object':
                # Check for emails
                if self._is_email_column(df[col]):
                    invalid_emails = self._count_invalid_emails(df[col])
                    if invalid_emails > 0:
                        col_analysis["issues"].append({
                            "type": "invalid_emails",
                            "count": invalid_emails
                        })
                        deductions += min(5, invalid_emails / len(df) * 100)

                # Check for dates
                if self._is_date_column(df[col]):
                    col_analysis["potential_type"] = "date"

                # Check for phone numbers
                if self._is_phone_column(df[col]):
                    col_analysis["potential_type"] = "phone"

            analysis["column_analysis"][col] = col_analysis

        # Calculate final quality score
        analysis["quality_score"] = max(0, round(100 - deductions, 2))

        # Convert all numpy types to Python native types for JSON serialization
        analysis = self._convert_numpy_types(analysis)

        return analysis

    def _convert_numpy_types(self, obj: Any) -> Any:
        """Recursively convert numpy/pandas types to Python native types"""
        if isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return obj

    def clean_data(
        self,
        df: pd.DataFrame,
        remove_duplicates: bool = True,
        fill_missing: bool = True,
        standardize_formats: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Clean data based on options"""
        cleaned_df = df.copy()
        report = {
            "actions_taken": [],
            "rows_before": len(df),
            "rows_after": len(df),
            "changes": {}
        }

        # Remove duplicates
        if remove_duplicates:
            duplicates_count = cleaned_df.duplicated().sum()
            if duplicates_count > 0:
                cleaned_df = cleaned_df.drop_duplicates()
                report["actions_taken"].append(f"Removed {duplicates_count} duplicate rows")
                report["changes"]["duplicates_removed"] = int(duplicates_count)

        # Fill missing values
        if fill_missing:
            missing_filled = {}
            for col in cleaned_df.columns:
                missing_count = cleaned_df[col].isna().sum()
                if missing_count > 0:
                    # Fill based on data type
                    if cleaned_df[col].dtype in ['int64', 'float64']:
                        # Fill numeric with median
                        cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                        missing_filled[col] = f"{missing_count} values filled with median"
                    else:
                        # Fill categorical with mode or "Unknown"
                        mode_val = cleaned_df[col].mode()
                        if len(mode_val) > 0:
                            cleaned_df[col].fillna(mode_val[0], inplace=True)
                            missing_filled[col] = f"{missing_count} values filled with mode"
                        else:
                            cleaned_df[col].fillna("Unknown", inplace=True)
                            missing_filled[col] = f"{missing_count} values filled with 'Unknown'"

            if missing_filled:
                report["actions_taken"].append(f"Filled missing values in {len(missing_filled)} columns")
                report["changes"]["missing_filled"] = missing_filled

        # Standardize formats
        if standardize_formats:
            format_changes = {}
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':
                    # Standardize emails
                    if self._is_email_column(cleaned_df[col]):
                        cleaned_df[col] = cleaned_df[col].str.lower().str.strip()
                        format_changes[col] = "Standardized email format"

                    # Standardize phone numbers
                    elif self._is_phone_column(cleaned_df[col]):
                        cleaned_df[col] = cleaned_df[col].apply(self._standardize_phone)
                        format_changes[col] = "Standardized phone format"

                    # Try to parse dates
                    elif self._is_date_column(cleaned_df[col]):
                        try:
                            cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                            format_changes[col] = "Converted to datetime"
                        except:
                            pass

            if format_changes:
                report["actions_taken"].append(f"Standardized formats in {len(format_changes)} columns")
                report["changes"]["formats_standardized"] = format_changes

        report["rows_after"] = len(cleaned_df)

        return cleaned_df, report

    def _is_email_column(self, series: pd.Series) -> bool:
        """Check if column likely contains emails"""
        if series.dtype != 'object':
            return False
        sample = series.dropna().astype(str).head(20)
        if len(sample) == 0:
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        matches = sample.str.match(email_pattern).sum()
        return matches / len(sample) > 0.5

    def _count_invalid_emails(self, series: pd.Series) -> int:
        """Count invalid email addresses"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        valid = series.dropna().astype(str).str.match(email_pattern)
        return (~valid).sum()

    def _is_date_column(self, series: pd.Series) -> bool:
        """Check if column likely contains dates"""
        if series.dtype != 'object':
            return False
        sample = series.dropna().astype(str).head(10)
        if len(sample) == 0:
            return False
        try:
            parsed = pd.to_datetime(sample, errors='coerce')
            return parsed.notna().sum() / len(sample) > 0.5
        except:
            return False

    def _is_phone_column(self, series: pd.Series) -> bool:
        """Check if column likely contains phone numbers"""
        if series.dtype != 'object':
            return False
        sample = series.dropna().astype(str).head(20)
        if len(sample) == 0:
            return False
        # Check for patterns with digits, spaces, dashes, parentheses
        phone_pattern = r'[\d\s\-\(\)\+]{7,}'
        matches = sample.str.match(phone_pattern).sum()
        return matches / len(sample) > 0.5

    def _standardize_phone(self, phone: Any) -> str:
        """Standardize phone number format"""
        if pd.isna(phone):
            return phone
        # Remove all non-digit characters except +
        phone_str = str(phone)
        digits = re.sub(r'[^\d+]', '', phone_str)
        return digits
