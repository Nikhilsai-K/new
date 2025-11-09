# Quick Start: Visualization & Dashboard Features

## 🚀 Getting Started

### Prerequisites
- Backend running on http://localhost:8001
- Frontend running on http://localhost:3002
- CSV or Excel file ready to analyze

### Running the Application

```bash
# Terminal 1: Start Backend
cd /Users/nikhilsai/new-main/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Start Frontend
cd /Users/nikhilsai/new-main/frontend
PORT=3002 npm run dev
```

Visit http://localhost:3002 in your browser

---

## 📊 Using Advanced Visualizations

### Step 1: Navigate to Visualize Page
1. Click **"Visualize"** button in header
2. Or go directly to: http://localhost:3002/visualize

### Step 2: Upload Your Data
- Click **"Select File"**
- Choose CSV or Excel file
- Wait for column metadata to load

### Step 3: Configure Visualization
1. **Select X Column**: Choose first variable to visualize
2. **Select Y Column** (Optional): Choose second variable for comparison
3. **Select Chart Type**: 
   - "Auto" for smart selection
   - Or manually choose from available types

### Step 4: Generate Chart
- Click **"Generate Chart"**
- Interactive chart appears below
- Statistics panel shows summary data

### Step 5: Explore Results
- Hover over chart for details
- Use Plotly tools (zoom, pan, download)
- See statistics table
- Download as PNG image

---

## 📈 Using Dashboard

### Method 1: From Main Page
1. Click **"Dashboard"** button in header
2. Or go directly to: http://localhost:3002/dashboard

### Method 2: Quick Dashboard
1. Upload file to dashboard page
2. Wait for auto-generation (5-10 seconds)
3. Browse all charts in grid layout

### Dashboard Includes:
- ✅ Summary statistics (rows, columns, types)
- ✅ All numeric column distributions
- ✅ All categorical column frequencies
- ✅ Correlation heatmap
- ✅ Numeric vs categorical relationships

---

## 📊 Chart Types Reference

### Numeric vs Numeric
| Chart | Best For | Example |
|-------|----------|---------|
| **Scatter** | Relationship patterns | Salary vs Experience |
| **Line** | Trend over time | Price vs Date |
| **Bubble** | 3-variable analysis | X, Y, and Size |
| **Correlation** | Relationships between all vars | Feature correlations |

### Numeric vs Categorical
| Chart | Best For | Example |
|-------|----------|---------|
| **Bar** | Average by group | Avg Salary by Department |
| **Box Plot** | Distribution by group | Revenue by Region |
| **Violin** | Detailed distribution | Price distribution by Category |

### Categorical vs Categorical
| Chart | Best For | Example |
|-------|----------|---------|
| **Stacked Bar** | Breakdown comparison | Product vs Color |
| **Heatmap** | Frequency patterns | Department vs Status |

### Single Column
| Chart | Best For | Example |
|-------|----------|---------|
| **Histogram** | Distribution shape | Salary distribution |
| **Box Plot** | Outliers & quartiles | Age quartiles |
| **Pie** | Part-to-whole ratio | Market share |

---

## 🎨 Visual Features

### Interactive Controls
- **Zoom**: Click and drag to zoom
- **Pan**: Double-click to reset
- **Hover**: See exact values
- **Download**: Save chart as PNG
- **Legend**: Toggle series on/off

### Color Schemes
- Scatter plots: Viridis gradient
- Most charts: Purple (#8B5CF6)
- Heatmaps: Viridis or RdBu
- Dark theme: Navy background

---

## 💡 Pro Tips

### Column Selection
- Start with numeric columns for most interesting charts
- Use categorical for grouping/comparison
- Mix numeric + categorical for distributions by group

### Best Practices
1. **Start with Dashboard** to get overview
2. **Then use Visualize** for deeper analysis
3. **Try different chart types** to find best view
4. **Export interesting charts** for presentations

### Data Considerations
- Missing values are automatically handled
- Outliers are preserved
- Large categories are limited to top 20
- Correlation matrix limited to 6 numeric columns

---

## 🔧 API Endpoints (For Developers)

### Get Column Info
```bash
curl -X POST http://localhost:8001/api/visualize/columns \
  -F "file=@your_file.csv"
```

Response:
```json
{
  "columns": [
    {
      "name": "Salary",
      "type": "numeric",
      "unique_count": 100,
      "missing_count": 2
    }
  ]
}
```

### Generate Chart
```bash
curl -X POST "http://localhost:8001/api/visualize/chart?x_column=Salary&y_column=Department&chart_type=bar" \
  -F "file=@your_file.csv"
```

### Generate Dashboard
```bash
curl -X POST http://localhost:8001/api/visualize/dashboard \
  -F "file=@your_file.csv"
```

---

## 📁 Project Structure

```
new-main/
├── backend/
│   ├── app/
│   │   ├── main.py (added 3 visualization endpoints)
│   │   ├── services/
│   │   │   ├── data_cleaner.py (existing)
│   │   │   ├── llm_service.py (existing)
│   │   │   └── visualization_service.py (NEW - 850+ lines)
│   │   └── ...
│   └── requirements.txt (added scipy)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx (updated with nav links)
│   │   ├── visualize/ (NEW)
│   │   │   └── page.tsx (visualization page)
│   │   └── dashboard/ (NEW)
│   │       └── page.tsx (dashboard page)
│   ├── components/
│   │   └── ... (existing components)
│   └── package.json (added plotly, recharts)
│
└── VISUALIZATION_FEATURES.md (comprehensive docs)
```

---

## 🐛 Troubleshooting

### "Backend is not running"
- Ensure backend is on http://localhost:8001
- Check if port 8001 is in use: `lsof -i :8001`

### Charts not loading
- Check browser console for errors
- Ensure file is CSV or Excel format
- Try with sample_data.csv first

### Slow chart generation
- Large files (>100MB) may take time
- Some chart types (violin, heatmap) compute intensive
- Browser may need more memory

### Columns not detecting correctly
- Data type inference happens on first 20 rows
- Some data may be mixed types
- Check data_cleaner.py for type detection logic

---

## ✨ What's New in This Release

### New Pages
- `/visualize` - Advanced interactive charts
- `/dashboard` - Auto-generated analytics

### New Services
- `VisualizationService` - 20+ chart generation methods
- Statistical calculations and metadata extraction

### New API Endpoints
- `POST /api/visualize/columns` - Get column metadata
- `POST /api/visualize/chart` - Generate specific chart
- `POST /api/visualize/dashboard` - Auto-generate dashboard

### New Dependencies
- plotly.js - Interactive charting
- react-plotly.js - React wrapper
- scipy - Statistics calculations

---

## 📞 Support

For issues or questions:
1. Check VISUALIZATION_FEATURES.md for detailed docs
2. Review chart types reference above
3. Check backend logs: `tail -f backend.log`
4. Check browser console: F12 → Console tab

---

**Happy Analyzing! 📊🚀**

