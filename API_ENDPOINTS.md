# AI Data Cleaner API - Complete Documentation

## Overview
This API provides comprehensive data quality analysis, cleaning, and visualization capabilities powered by local ML-based analytics and optional Google AI integration for enhanced suggestions.

---

## Core Analysis Endpoints

### 1. **POST /api/local-analysis/quality**
Advanced data quality analysis using local ML-powered analytics engine.

**Purpose**: Returns comprehensive data quality assessment

**Returns**:
- Missing data patterns (MCAR, MNAR detection)
- Duplicate detection (exact, partial, fuzzy)
- Outlier detection (3-method ensemble: IQR, Z-score, Modified Z-score)
- Type consistency validation
- Entropy and distribution analysis
- Cardinality assessment
- Statistical anomalies
- Quality metrics and scores

**Request**:
```bash
curl -X POST http://localhost:8001/api/local-analysis/quality \
  -F "file=@data.csv"
```

**Response**:
```json
{
  "overall_quality_score": 85.5,
  "missing_value_analysis": {
    "total_missing": 42,
    "columns_with_missing": ["age", "email"],
    "mcar_score": 0.8,
    "mnar_score": 0.2
  },
  "duplicate_analysis": {
    "exact_duplicates": 5,
    "partial_duplicates": 12,
    "duplicate_percentage": 2.1
  },
  "outlier_analysis": {
    "numeric_outliers": {
      "salary": 3,
      "age": 1
    },
    "total_outliers": 4
  },
  "entropy_analysis": {
    "high_entropy_columns": ["id", "email"],
    "low_entropy_columns": ["is_active"]
  },
  "cardinality_analysis": {
    "ultra_high": ["id"],
    "very_high": ["email"],
    "high": ["age"],
    "moderate": ["department"],
    "low": ["is_active"]
  },
  "metrics": {
    "completeness_score": 92.3,
    "consistency_score": 88.5,
    "validity_score": 95.0,
    "uniqueness_score": 98.0,
    "timeliness_score": 85.0
  },
  "recommendations": [
    {
      "issue": "Missing values in age column",
      "priority": "high",
      "action": "Fill with median (35 years)",
      "impact": "Increases completeness by 2.1%"
    }
  ]
}
```

---

### 2. **POST /api/local-analysis/strategies**
Get smart cleaning strategies using local analytics.

**Purpose**: Returns prioritized cleaning strategies based on data quality issues

**Returns**:
- Prioritized cleaning strategies
- Summary with critical/warning/info counts
- Data quality issues identified
- Risk assessments
- Best practices

**Request**:
```bash
curl -X POST http://localhost:8001/api/local-analysis/strategies \
  -F "file=@data.csv"
```

**Response**:
```json
{
  "success": true,
  "strategies": [
    {
      "issue": "Exact duplicates detected",
      "priority": "high",
      "action": "Remove 5 duplicate rows",
      "impact": "Improves data uniqueness"
    },
    {
      "issue": "Missing values in email",
      "priority": "medium",
      "action": "Verify with source or mark as invalid",
      "impact": "Improves completeness"
    }
  ],
  "summary": {
    "total_issues": 12,
    "critical": 3,
    "warnings": 5,
    "info": 4
  }
}
```

---

### 3. **POST /api/local-analysis/insights**
Get analytical insights about the dataset.

**Purpose**: Returns insights including statistics, correlations, anomalies, and recommendations

**Returns**:
- Dataset overview
- Quality metrics
- Issue summary
- Actionable recommendations (top 5)

**Request**:
```bash
curl -X POST http://localhost:8001/api/local-analysis/insights \
  -F "file=@data.csv"
```

**Response**:
```json
{
  "success": true,
  "dataset_overview": {
    "total_rows": 10000,
    "total_columns": 15,
    "columns": ["id", "name", "email", ...],
    "dtypes": {
      "id": "int64",
      "name": "object",
      "email": "object",
      ...
    }
  },
  "quality_metrics": {
    "completeness": 92.3,
    "consistency": 88.5,
    "validity": 95.0,
    "uniqueness": 98.0,
    "timeliness": 85.0
  },
  "issue_summary": {
    "missing_values": 75,
    "duplicates": 5,
    "outliers": 12,
    "type_mismatches": 3
  },
  "recommendations": [
    {
      "issue": "Missing values in age column",
      "priority": "high",
      "action": "Fill with median (35 years)",
      "impact": "Increases completeness by 2.1%"
    }
  ]
}
```

---

### 4. **POST /api/local-analysis/report**
Generate a comprehensive data analysis report.

**Purpose**: Returns a detailed report with executive summary and detailed findings

**Returns**:
- Executive summary
- Dataset information
- Detailed analysis results
- Comprehensive recommendations
- Next steps

**Request**:
```bash
curl -X POST http://localhost:8001/api/local-analysis/report \
  -F "file=@data.csv"
```

**Response**:
```json
{
  "success": true,
  "report_title": "Comprehensive Data Quality Report",
  "dataset_info": {
    "filename": "data.csv",
    "rows": 10000,
    "columns": 15,
    "size_mb": 2.5
  },
  "executive_summary": {
    "overall_quality_score": 85.5,
    "total_issues": 12,
    "high_priority": 3,
    "data_completeness": "92.3%"
  },
  "detailed_analysis": {
    "missing_value_analysis": {...},
    "duplicate_analysis": {...},
    "outlier_analysis": {...},
    "type_consistency": {...},
    "entropy_analysis": {...},
    "cardinality_analysis": {...}
  },
  "recommendations": [...],
  "next_steps": [
    "Review high-priority issues first",
    "Validate recommended cleaning strategies",
    "Perform data profiling on critical columns",
    "Document any data transformations",
    "Implement data validation rules for future ingestion"
  ]
}
```

---

## Traditional Endpoints (Backward Compatible)

### 5. **POST /api/analyze**
Analyze uploaded file and return data quality issues.

**Purpose**: Legacy analysis endpoint - returns basic data quality metrics

**Request**:
```bash
curl -X POST http://localhost:8001/api/analyze \
  -F "file=@data.csv"
```

---

### 6. **POST /api/ai-suggestions**
Get AI-powered cleaning suggestions without cleaning.

**Purpose**: Returns smart suggestions using local ML-powered analytics engine
- Uses LocalAnalyticsLLM for secure, on-premise analysis
- Optionally uses Google API for enhanced suggestions if configured

**Request**:
```bash
curl -X POST http://localhost:8001/api/ai-suggestions \
  -F "file=@data.csv"
```

**Response**:
```json
{
  "success": true,
  "source": "local_ml_analytics",
  "suggestions": [...],
  "analysis": {...}
}
```

---

### 7. **POST /api/clean**
Clean the uploaded file based on options.

**Parameters**:
- `remove_duplicates` (bool): Remove exact duplicate rows
- `fill_missing` (bool): Fill missing values intelligently
- `standardize_formats` (bool): Normalize dates, emails, phone numbers
- `use_ai` (bool): Use AI for advanced cleaning suggestions

**Request**:
```bash
curl -X POST "http://localhost:8001/api/clean?remove_duplicates=true&fill_missing=true&standardize_formats=true&use_ai=false" \
  -F "file=@data.csv"
```

---

## Visualization Endpoints

### 8. **POST /api/visualize/columns**
Get column information for visualization selection.

**Purpose**: Returns column metadata for chart selection

---

### 9. **POST /api/visualize/chart**
Generate chart data for specified columns.

**Parameters**:
- `x_column` (string): X-axis column
- `y_column` (string, optional): Y-axis column
- `chart_type` (string, optional): Chart type (scatter, bar, line, etc.)

**Request**:
```bash
curl -X POST "http://localhost:8001/api/visualize/chart?x_column=age&y_column=salary&chart_type=scatter" \
  -F "file=@data.csv"
```

---

### 10. **POST /api/visualize/recommended-charts**
Get recommended chart types for columns.

**Parameters**:
- `x_column` (string): X-axis column
- `y_column` (string, optional): Y-axis column

**Request**:
```bash
curl -X POST "http://localhost:8001/api/visualize/recommended-charts?x_column=age&y_column=salary" \
  -F "file=@data.csv"
```

---

### 11. **POST /api/visualize/dashboard**
Generate smart dashboard with intelligent chart selection.

**Purpose**: Auto-generates multiple visualizations for the dataset

**Request**:
```bash
curl -X POST http://localhost:8001/api/visualize/dashboard \
  -F "file=@data.csv"
```

---

## Health & Status

### 12. **GET /health**
Health check endpoint.

**Request**:
```bash
curl http://localhost:8001/health
```

**Response**:
```json
{
  "status": "healthy"
}
```

---

### 13. **GET /**
API information.

**Request**:
```bash
curl http://localhost:8001/
```

**Response**:
```json
{
  "message": "AI Data Cleaner API",
  "status": "running",
  "version": "1.0.0"
}
```

---

## Advanced Analytics Engine Features

### LocalAnalyticsLLM Capabilities

The integrated LocalAnalyticsLLM service provides enterprise-grade data quality analysis with:

#### 1. **Missing Data Pattern Detection**
- MCAR (Missing Completely At Random) detection
- MNAR (Missing Not At Random) detection
- Missing value correlation analysis
- Per-column missing statistics

#### 2. **Duplicate Detection**
- Exact duplicate rows
- Partial duplicates across numeric columns
- Fuzzy matching for text columns
- Duplicate percentage and impact metrics

#### 3. **Advanced Outlier Detection**
- **IQR Method**: Traditional interquartile range (1.5x multiplier)
- **Z-Score Method**: Standard deviation-based detection (±3σ)
- **Modified Z-Score (MAD)**: Median Absolute Deviation-based, robust to extreme values
- **Consensus Voting**: Identifies outliers flagged by multiple methods

#### 4. **Distribution & Entropy Analysis**
- Shannon entropy calculation (normalized 0-1 scale)
- Distribution shape assessment
- Entropy-based uniformity metrics
- Data concentration analysis

#### 5. **Cardinality Classification**
Five-level classification:
- **Ultra High**: >50% unique values
- **Very High**: 20-50% unique values
- **High**: 10-20% unique values
- **Moderate**: 5-10% unique values
- **Low**: <5% unique values

#### 6. **Statistical Normality Testing**
- Shapiro-Wilk test with p-values
- Distribution shape analysis
- Normality assessment

#### 7. **Type Consistency Validation**
- Detection of mistyped numeric data (stored as text)
- Datetime format consistency
- Email format validation
- Phone number pattern matching

---

## Configuration

### Environment Variables

```env
GOOGLE_API_KEY=your_api_key_here  # Optional: for enhanced AI suggestions
NEXT_PUBLIC_API_URL=http://localhost:8001  # Frontend API URL
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad request (missing parameters, unsupported format)
- **413**: Payload too large (>500MB)
- **500**: Server error
- **503**: Service unavailable (e.g., Google API not configured)

---

## File Format Support

- **CSV** (.csv)
- **Excel** (.xlsx, .xls)
- Maximum file size: **500MB**

---

## Security Notes

✅ **On-Premise Analysis**: LocalAnalyticsLLM runs entirely on-premise with no external API calls
✅ **Data Privacy**: No data is sent to external services unless explicitly configured
✅ **Optional Cloud Integration**: Google API integration is optional and can be disabled

---

## Performance Characteristics

| Dataset Size | Analysis Time | Memory Usage |
|---|---|---|
| <1MB | <100ms | <50MB |
| 1-10MB | 100-500ms | 50-200MB |
| 10-100MB | 500ms-2s | 200-500MB |
| 100-500MB | 2-10s | 500MB-2GB |

---

## Usage Examples

### Example 1: Quick Data Quality Check
```bash
curl -X POST http://localhost:8001/api/local-analysis/quality \
  -F "file=@sales_data.csv" | jq '.metrics'
```

### Example 2: Get Cleaning Strategies
```bash
curl -X POST http://localhost:8001/api/local-analysis/strategies \
  -F "file=@customer_data.csv" | jq '.strategies[0:3]'
```

### Example 3: Generate Comprehensive Report
```bash
curl -X POST http://localhost:8001/api/local-analysis/report \
  -F "file=@employee_data.xlsx" > report.json
```

### Example 4: Create Dashboard with Visualizations
```bash
curl -X POST http://localhost:8001/api/visualize/dashboard \
  -F "file=@analytics_data.csv" > dashboard_data.json
```

---

## Integration with Frontend

The API is fully integrated with the Next.js frontend application:

- **Home Page** (`/`): File upload and basic cleaning
- **Visualize Page** (`/visualize`): Advanced chart creation
- **Dashboard Page** (`/dashboard`): Auto-generated dashboard

---

## Version History

- **v1.0.0**: Initial release with LocalAnalyticsLLM integration
  - 4 new local analysis endpoints
  - Enhanced `/api/ai-suggestions` with fallback logic
  - Complete data quality assessment suite
  - 25+ chart types support

