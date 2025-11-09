# Advanced Visualization & Dashboard Features

## Overview
Added professional-grade data visualization and analytics dashboard capabilities to the AI Data Cleaner application, similar to Tableau and Power BI.

## New Pages & Features

### 1. Advanced Visualization Page (`/visualize`)
**Location:** `/frontend/app/visualize/page.tsx`

#### Features:
- **Two-Column Selection**: Choose X and Y columns for comparison
- **Smart Chart Type Selection**: Automatically recommends chart types based on data types
- **Interactive Plotly Charts**: Professional, interactive visualizations with:
  - Scatter plots (numeric vs numeric)
  - Line charts (numeric vs numeric)
  - Bubble charts (numeric vs numeric)
  - Bar charts (numeric vs categorical)
  - Box plots (distribution analysis)
  - Violin plots (detailed distributions)
  - Pie charts (categorical)
  - Stacked bar charts (categorical vs categorical)
  - Heatmaps (correlation and categorical)

#### Smart Chart Type Detection:
```
Numeric vs Numeric → scatter, line, bubble, correlation heatmap
Numeric vs Categorical → bar, box, violin
Categorical vs Numeric → bar, box, violin  
Categorical vs Categorical → stacked_bar, heatmap
Single Numeric → histogram, box plot
Single Categorical → bar, pie
```

#### User Experience:
- Upload CSV or Excel file
- Real-time column metadata display
- Live statistics for selected columns
- Download charts as PNG images
- Responsive design with dark theme

---

### 2. Analytics Dashboard Page (`/dashboard`)
**Location:** `/frontend/app/dashboard/page.tsx`

#### Features:
- **Auto-Generated Visualizations**: Automatically creates 8+ charts from uploaded file
- **Summary Statistics**: Shows total rows, columns, numeric vs categorical breakdown
- **Multi-Chart Grid Layout**: 2-column responsive grid
- **Automatic Chart Selection**:
  - Numeric columns → Histograms (distribution analysis)
  - Categorical columns → Bar charts (frequency)
  - Correlation matrix → Auto-generated from numeric columns
  - Relationships → Numeric vs categorical box plots

#### Tableau/Power BI Style Features:
- Professional color scheme
- Summary cards with key metrics
- Responsive grid layout
- Export functionality
- File management

---

## Backend Implementation

### New Service: VisualizationService
**Location:** `/backend/app/services/visualization_service.py`

#### Core Methods:
1. **get_column_info()** - Returns metadata about all columns
2. **generate_chart_data()** - Generates data for specific chart types
3. **generate_dashboard_data()** - Creates complete dashboard with multiple charts

#### Chart Generation Methods:
- `_scatter_plot()` - Scatter plot with color gradient
- `_line_chart()` - Line plots with trend visualization
- `_bubble_chart()` - Bubble charts with sized markers
- `_bar_chart_by_category()` - Grouped bar charts with error bars
- `_box_plot()` - Box plots for distribution analysis
- `_violin_plot()` - Violin plots for detailed distributions
- `_histogram()` - Distribution histograms with statistics
- `_pie_chart()` - Pie charts for categorical data
- `_stacked_bar_chart()` - Stacked bar charts for two categoricals
- `_categorical_heatmap()` - Heatmaps for categorical relationships
- `_correlation_heatmap()` - Correlation matrices for numeric columns

#### Features:
- Automatic data type detection
- Missing value handling
- Outlier-aware scaling
- Statistical calculations
- JSON serialization ready

### New API Endpoints

```
POST /api/visualize/columns
- Input: CSV/Excel file
- Output: Column metadata and type information
- Use: Populate column selectors in frontend

POST /api/visualize/chart
- Input: File + x_column + y_column + chart_type (optional)
- Output: Plotly-ready chart data
- Use: Generate interactive charts on demand

POST /api/visualize/dashboard
- Input: CSV/Excel file
- Output: Complete dashboard with 8+ charts
- Use: Auto-generate comprehensive dashboard
```

---

## Technology Stack

### Frontend
- **Plotly.js** - Interactive charting library
- **React** - UI framework
- **Tailwind CSS** - Styling
- **TypeScript** - Type safety

### Backend
- **FastAPI** - REST API framework
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **SciPy** - Statistical functions

### Dependencies Added:
```
Frontend: plotly.js, react-plotly.js, recharts
Backend: scipy==1.11.4
```

---

## Chart Capabilities

### Data Type Combinations Supported:
1. **Numeric + Numeric** (5 chart types)
   - Scatter with gradient coloring
   - Time series line charts
   - Bubble charts with size encoding
   - Correlation heatmap
   - Statistical overlays

2. **Numeric + Categorical** (3 chart types)
   - Grouped bar charts with error bars
   - Box plots with outliers
   - Violin plots with distribution

3. **Categorical + Categorical** (2 chart types)
   - Stacked bar charts
   - Heatmaps with frequency

4. **Single Column Analysis** (2-3 chart types)
   - Histograms with distribution stats
   - Box plots with quartiles
   - Pie charts for categories

### Statistical Information Displayed:
- Mean, Median, Standard Deviation
- Min, Max, Range
- Quartiles (Q1, Q3)
- IQR (Interquartile Range)
- Correlation coefficients
- Group counts and percentages

---

## Navigation Integration

### Updated Main Page Header
Added two new navigation buttons:
- **Visualize** button → `/visualize` page
- **Dashboard** button → `/dashboard` page
- Links available from all pages

### Navigation Flow:
```
Home (/clean)
├─→ Visualize (/visualize)
│   └─→ Dashboard (/dashboard)
└─→ Dashboard (/dashboard)
    └─→ Visualize (/visualize)
```

---

## Performance Optimizations

1. **Data Limits**: 
   - Categories limited to prevent overcrowding
   - Top 20 categories displayed for large datasets
   - Efficient grouping and aggregation

2. **Memory Management**:
   - Stream processing where possible
   - Lazy loading of charts
   - Efficient JSON serialization

3. **API Efficiency**:
   - Single file upload per request
   - Smart caching of column metadata
   - Optimized aggregations

---

## Visual Design

### Dark Theme Consistency:
- Matches existing navy-blue color scheme
- Purple gradient accents (#8B5CF6)
- White text on dark backgrounds
- Smooth animations and transitions

### Responsive Layout:
- Mobile-friendly grid layouts
- Adaptive chart sizing
- Collapsible controls
- Touch-friendly buttons

---

## Example Use Cases

1. **Sales Analysis**: 
   - Scatter plot of Revenue vs Quantity
   - Box plot of Sales by Region
   - Dashboard showing all product categories

2. **HR Analytics**:
   - Salary distribution by department
   - Employee count by location
   - Heatmap of department vs status

3. **Customer Data**:
   - Purchase frequency vs order value
   - Customer lifetime value distribution
   - Geographic distribution heatmap

---

## Testing

All endpoints have been tested with sample data:
- ✅ Column metadata retrieval
- ✅ Chart generation for all types
- ✅ Dashboard auto-generation
- ✅ Edge cases (missing values, empty categories)
- ✅ Large datasets (500+ records)

---

## Files Modified/Created

### New Files:
- `/backend/app/services/visualization_service.py` (850+ lines)
- `/frontend/app/visualize/page.tsx` (350+ lines)
- `/frontend/app/dashboard/page.tsx` (250+ lines)

### Modified Files:
- `/backend/app/main.py` - Added 3 new API endpoints
- `/backend/requirements.txt` - Added scipy
- `/frontend/app/page.tsx` - Added navigation links
- `/frontend/package.json` - Added plotly dependencies

---

## Future Enhancements

Potential additions for even more power:
- Interactive dashboard builder (drag-drop charts)
- Custom color schemes and themes
- Advanced filters and drill-down
- Time series forecasting
- ML-powered anomaly detection
- Export to PDF/PowerPoint
- Shared dashboards and reports
- Real-time data updates

