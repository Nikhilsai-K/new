import os
from typing import Dict, List, Any
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class LLMService:
    """AI service for intelligent data cleaning suggestions using LangChain"""

    def __init__(self):
        self.llm = None
        api_key = os.getenv("GOOGLE_API_KEY")

        if api_key:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=api_key,
                    temperature=0.3,
                    convert_system_message_to_human=True
                )
            except Exception as e:
                print(f"Failed to initialize LLM: {e}")

    async def get_cleaning_suggestions(
        self,
        original_df: pd.DataFrame,
        cleaned_df: pd.DataFrame,
        cleaning_report: Dict[str, Any]
    ) -> List[str]:
        """Get AI suggestions based on cleaning results"""
        if not self.llm:
            return ["AI service not available. Configure GOOGLE_API_KEY to enable."]

        try:
            prompt = PromptTemplate(
                input_variables=["report", "columns", "sample_data"],
                template="""You are a data quality expert. Based on the cleaning report below, provide 3-5 brief, actionable suggestions to further improve data quality.

Cleaning Report:
{report}

Columns: {columns}

Sample Data (first 3 rows):
{sample_data}

Provide concise, bullet-point suggestions focusing on:
1. Additional cleaning steps
2. Data validation rules to implement
3. Potential data enrichment opportunities

Format as a simple numbered list."""
            )

            chain = prompt | self.llm

            # Prepare data
            sample_data = cleaned_df.head(3).to_dict(orient='records')

            response = await chain.ainvoke({
                "report": str(cleaning_report),
                "columns": ", ".join(cleaned_df.columns.tolist()),
                "sample_data": str(sample_data)
            })

            # Extract suggestions
            suggestions_text = response.content if hasattr(response, 'content') else str(response)
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip() and len(s.strip()) > 5]

            return suggestions[:5]  # Limit to 5 suggestions

        except Exception as e:
            return [f"Error generating AI suggestions: {str(e)}"]

    async def get_smart_suggestions(
        self,
        df: pd.DataFrame,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get smart AI-powered suggestions for data quality issues"""
        if not self.llm:
            return [{
                "type": "info",
                "message": "AI service not available. Configure GOOGLE_API_KEY to enable smart suggestions."
            }]

        try:
            prompt = PromptTemplate(
                input_variables=["analysis", "columns", "sample"],
                template="""You are a data cleaning AI assistant. Analyze this dataset and provide specific, actionable cleaning recommendations.

Data Analysis:
- Total rows: {analysis[total_rows]}
- Total columns: {analysis[total_columns]}
- Quality score: {analysis[quality_score]}/100

Issues found:
{analysis[issues]}

Columns: {columns}

Sample data:
{sample}

Provide 5-7 specific recommendations in this exact JSON-like format:
1. [Action Type] - Brief description of what to do
2. [Action Type] - Brief description of what to do

Focus on:
- Data validation rules
- Format standardization
- Missing value strategies
- Duplicate handling
- Data type conversions

Be specific and actionable."""
            )

            chain = prompt | self.llm

            sample = df.head(5).to_string()

            response = await chain.ainvoke({
                "analysis": analysis,
                "columns": ", ".join(df.columns.tolist()),
                "sample": sample
            })

            # Parse response
            suggestions_text = response.content if hasattr(response, 'content') else str(response)

            suggestions = []
            for line in suggestions_text.split('\n'):
                line = line.strip()
                if line and len(line) > 10:
                    # Extract action type and message
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
