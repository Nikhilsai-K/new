# Quick Start Guide - AI Data Cleaner with LocalAnalyticsLLM

## 🚀 Getting Started in 5 Minutes

### Step 1: Start the Backend Server
```bash
cd /Users/nikhilsai/new-main/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### Step 2: Start the Frontend Server (in a new terminal)
```bash
cd /Users/nikhilsai/new-main/frontend
PORT=3002 npm run dev
```

Expected output:
```
▲ Next.js 14.0.4
- Local:        http://localhost:3002
```

### Step 3: Open Your Browser
Navigate to: **http://localhost:3002**

---

## 🎯 Using the Application

### Main Page - Data Cleaning
1. Click "Select File" and upload a CSV or Excel file
2. Review the data quality analysis
3. Choose cleaning options:
   - Remove Duplicates
   - Fill Missing Values
   - Standardize Formats
   - Use AI (optional)
4. Click "Clean Data" to download cleaned file

### Advanced Visualizations Page
1. Click "Visualize" in the header
2. Upload a file
3. Select X and Y columns
4. Choose chart type (auto-recommended)
5. View interactive Plotly chart
6. Download as PNG

### Dashboard Page
1. Click "Dashboard" in the header
2. Upload a file
3. View auto-generated dashboard with multiple visualizations
4. Explore data insights

---

## 📊 Using the New Local Analysis Endpoints

### Quick Quality Check
```bash
curl -X POST http://localhost:8001/api/local-analysis/quality \
  -F "file=@your_data.csv" | jq '.metrics'
```

### Get Cleaning Strategies
```bash
curl -X POST http://localhost:8001/api/local-analysis/strategies \
  -F "file=@your_data.csv" | jq '.strategies[0:3]'
```

### Get Dataset Insights
```bash
curl -X POST http://localhost:8001/api/local-analysis/insights \
  -F "file=@your_data.csv" | jq '.quality_metrics'
```

### Generate Full Report
```bash
curl -X POST http://localhost:8001/api/local-analysis/report \
  -F "file=@your_data.csv" > analysis_report.json
```

---

## 🔍 Understanding the Analysis Results

### Quality Metrics (0-100%)

| Metric | Meaning |
|--------|---------|
| **Completeness** | Percentage of non-null values |
| **Consistency** | Data follows expected format/type |
| **Validity** | Values are reasonable and within range |
| **Uniqueness** | Minimal duplicate records |
| **Timeliness** | Data is current and up-to-date |

### What Gets Analyzed

✅ **Missing Values**
- MCAR (Missing Completely At Random) vs MNAR (Missing Not At Random)
- Per-column missing percentages
- Correlation between missing values

✅ **Duplicates**
- Exact duplicate rows
- Partial duplicates across specific columns
- Duplicate percentage and impact

✅ **Outliers** (3-Method Ensemble)
- IQR (Interquartile Range)
- Z-Score (±3σ detection)
- Modified Z-Score (Median Absolute Deviation)

✅ **Data Distributions**
- Shannon entropy (data uniformity)
- Distribution shape
- Cardinality (unique value percentage)

✅ **Data Types**
- Type consistency checking
- Detection of mistyped numeric data
- Datetime format validation

---

## 📈 Supported Chart Types (25+)

### For Single Column
- Histogram
- Density Plot
- Box Plot
- Pie Chart
- Donut Chart
- Treemap

### For Two Numeric Columns
- Scatter Plot
- Bubble Chart
- Line Chart
- Area Chart
- Hexbin (2D Histogram)
- Density 2D

### For Numeric vs Categorical
- Column/Bar Chart
- Box Plot (by category)
- Violin Plot
- Strip Plot

### For Two Categorical Columns
- Stacked Bar Chart
- Grouped Bar Chart
- Heatmap
- Mosaic Plot

---

## 🔐 Data Privacy & Security

✅ **No External Calls Required**
- LocalAnalyticsLLM runs 100% on-premise
- No data is sent to cloud services

✅ **Optional Cloud Integration**
- Google AI is completely optional
- Works perfectly without it
- Continues with local analysis if cloud fails

✅ **Data Handling**
- Files stored in memory only
- No persistence to disk
- Deleted after processing

---

## 🛠️ Troubleshooting

### Frontend won't connect to backend
```bash
# Check backend is running on port 8001
curl http://localhost:8001/health

# If not running, restart backend with:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Port already in use
```bash
# Kill process on port 8001 (backend)
lsof -ti :8001 | xargs kill -9

# Kill process on port 3002 (frontend)
lsof -ti :3002 | xargs kill -9
```

### Out of memory error
- Try with smaller files first
- Maximum file size: 500MB
- Check available RAM: `free -h`

### Slow performance
- File size affects analysis time
- <1MB: <100ms
- 10-100MB: 500ms-2s
- >100MB: May take 5-10 seconds

---

## 📚 Additional Resources

- **API Documentation**: See `API_ENDPOINTS.md`
- **Integration Details**: See `INTEGRATION_SUMMARY.md`
- **Implementation Details**: See `QUICK_START.md` (this file)

---

## 🎓 Example Workflow

### Scenario: Clean Customer Dataset

1. **Upload Phase**
   - Open app at http://localhost:3002
   - Upload `customers.csv`

2. **Analysis Phase**
   - App automatically analyzes data quality
   - Shows issues: 42 missing emails, 5 duplicates, 3 age outliers

3. **Review Phase**
   - Check "Remove Duplicates" ✓
   - Check "Fill Missing Values" ✓
   - Check "Standardize Formats" ✓

4. **Clean Phase**
   - Click "Clean Data"
   - Browser downloads `customers_cleaned.csv`

5. **Verify Phase**
   - Open "Visualize" page
   - Upload cleaned file
   - Create charts to verify results

---

## ⚡ Performance Tips

### Optimize for Speed
1. **Remove unnecessary columns** before uploading
2. **Use CSV instead of Excel** (faster to parse)
3. **Split large files** if >100MB
4. **Close other applications** to free RAM

### Optimize for Accuracy
1. **Use all available columns** for full analysis
2. **Check recommendations** before auto-cleaning
3. **Review outliers** manually before removing
4. **Validate results** with visualizations

---

## 🎯 Pro Tips

### Tip 1: Batch Processing
```bash
# Analyze multiple files
for file in *.csv; do
  curl -X POST http://localhost:8001/api/local-analysis/quality \
    -F "file=@$file" > "${file%.csv}_analysis.json"
done
```

### Tip 2: Export Analysis Results
```bash
# Save full report as PDF (requires HTML conversion)
curl -X POST http://localhost:8001/api/local-analysis/report \
  -F "file=@data.csv" | jq '.' > report.json
```

### Tip 3: Monitor Data Quality Over Time
```bash
# Run weekly analysis and track trends
curl -X POST http://localhost:8001/api/local-analysis/quality \
  -F "file=@data.csv" | jq '.metrics' >> quality_log.json
```

---

## 🆘 Getting Help

### Check API Status
```bash
curl http://localhost:8001/
```

### View API Documentation
Open in browser: **http://localhost:8001/docs**

### Check Logs
```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
# Check browser console (F12 > Console)
```

---

## 📝 Next Steps After Cleaning

1. **Validate Results**
   - Use Visualize page to create charts
   - Compare before/after distributions

2. **Document Changes**
   - Note which rows were removed
   - Document any transformations applied

3. **Implement Validation Rules**
   - Use insights to create data quality rules
   - Apply to future data ingestion

4. **Share Results**
   - Export cleaned data
   - Share analysis report with team

---

## 🎉 You're All Set!

Your AI Data Cleaner with LocalAnalyticsLLM is ready to use. Start by uploading a CSV file and let the advanced ML analytics work for you!

**Happy data cleaning! 🚀**

