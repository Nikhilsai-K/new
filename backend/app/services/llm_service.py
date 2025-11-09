import os
from typing import Dict, List, Any
import pandas as pd
import google.generativeai as genai


class LLMService:
    """AI service for intelligent data cleaning suggestions using Google Generative AI"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    async def get_cleaning_suggestions(
        self,
        original_df: pd.DataFrame,
        cleaned_df: pd.DataFrame,
        cleaning_report: Dict[str, Any]
    ) -> List[str]:
        """Get AI suggestions based on cleaning results"""
        if not self.api_key:
            return ["AI service not available. Configure GOOGLE_API_KEY to enable."]

        try:
            prompt = f"""You are a data quality expert. Based on the cleaning report below, provide 3-5 brief, actionable suggestions to further improve data quality.

Cleaning Report:
{str(cleaning_report)}

Columns: {", ".join(cleaned_df.columns.tolist())}

Sample Data (first 3 rows):
{str(cleaned_df.head(3).to_dict(orient='records'))}

Provide concise, bullet-point suggestions focusing on:
1. Additional cleaning steps
2. Data validation rules to implement
3. Potential data enrichment opportunities

Format as a simple numbered list."""

            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)

            suggestions_text = response.text
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip() and len(s.strip()) > 5]

            return suggestions[:5]

        except Exception as e:
            return [f"Error generating AI suggestions: {str(e)}"]

    async def get_smart_suggestions(
        self,
        df: pd.DataFrame,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get smart AI-powered suggestions for data quality issues"""
        if not self.api_key:
            return [{
                "type": "info",
                "message": "AI service not available. Configure GOOGLE_API_KEY to enable smart suggestions."
            }]

        try:
            prompt = f"""You are a data cleaning AI assistant. Analyze this dataset and provide specific, actionable cleaning recommendations.

Data Analysis:
- Total rows: {analysis.get('total_rows', 0)}
- Total columns: {analysis.get('total_columns', 0)}
- Quality score: {analysis.get('quality_score', 0)}/100

Issues found:
{analysis.get('issues', 'None')}

Columns: {", ".join(df.columns.tolist())}

Sample data:
{df.head(5).to_string()}

Provide 5-7 specific recommendations in this exact format:
1. [Action Type] - Brief description of what to do
2. [Action Type] - Brief description of what to do

Focus on:
- Data validation rules
- Format standardization
- Missing value strategies
- Duplicate handling
- Data type conversions

Be specific and actionable."""

            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)

            suggestions_text = response.text

            suggestions = []
            for line in suggestions_text.split('\n'):
                line = line.strip()
                if line and len(line) > 10:
                    if '[' in line and ']' in line:
                        action_type = line[line.find('[')+1:line.find(']')]
                        message = line[line.find(']')+1:].strip(' -').strip()
                        suggestions.append({
                            "type": action_type.lower(),
                            "message": message
                        })
                    else:
                        suggestions.append({
                            "type": "general",
                            "message": line.lstrip('0123456789.- ')
                        })

            return suggestions[:7]

        except Exception as e:
            return [{
                "type": "error",
                "message": f"Error generating suggestions: {str(e)}"
            }]

    def analyze_column_semantics(self, column_data: pd.Series) -> Dict[str, Any]:
        """Analyze what a column likely represents using AI"""
        # Placeholder for future enhancement
        return {
            "likely_type": "unknown",
            "confidence": 0.0,
            "suggestions": []
        }
