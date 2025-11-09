# 🧹 AI Data Cleaner

> AI-powered data cleaning tool for SMEs. Upload CSV or Excel files and get clean, validated data instantly.

![Tech Stack](https://img.shields.io/badge/Next.js-14-black)
![Tech Stack](https://img.shields.io/badge/FastAPI-0.104-009688)
![Tech Stack](https://img.shields.io/badge/LangChain-Latest-blue)
![Tech Stack](https://img.shields.io/badge/Tailwind-3.3-38bdf8)

## 🎯 Market Opportunity

The global data cleaning market is expected to exceed **$2 billion by 2030**. Small and medium-sized enterprises (SMEs) suffer from "dirty data"—about **80% of operational data** is incomplete, duplicated, or inconsistent.

With over **3.5 million SMEs in Japan alone**, this represents a massive market opportunity for an affordable, AI-powered data cleaning solution.

## ✨ Features

### Core Cleaning
- ✅ **Remove Duplicates** - Automatically detect and remove duplicate rows
- 🔄 **Fill Missing Values** - Smart filling based on data patterns (median, mode, or intelligent defaults)
- 📋 **Standardize Formats** - Normalize dates, emails, phone numbers, and more
- 📊 **Data Quality Score** - Get instant feedback on your data quality (0-100)

### AI Enhancement (Optional)
- 🤖 **Smart Suggestions** - AI-powered recommendations for data improvement
- 🎯 **Context-Aware Cleaning** - LangChain-based intelligent decision making
- 💡 **Actionable Insights** - Specific steps to further improve your data

### User Experience
- 🎨 **Beautiful Dark UI** - Modern, professional interface with Tailwind CSS
- 📁 **Drag & Drop Upload** - Easy file uploads for CSV and Excel files
- 📥 **Instant Download** - Get your cleaned data immediately
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js 14 + Tailwind CSS)                  │
│  • Modern dark theme UI                                 │
│  • File upload & preview                                │
│  • Interactive data cleaning options                    │
│  • Real-time analysis display                           │
└─────────────────┬───────────────────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────────────────┐
│  Backend (FastAPI)                                      │
│  • /api/analyze - Analyze data quality                  │
│  • /api/clean - Clean and download data                 │
│  • /api/ai-suggestions - Get AI recommendations         │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼────────┐
│  Data Cleaner  │  │  LLM Service  │
│   (Pandas)     │  │  (LangChain)  │
│                │  │               │
│ • Duplicates   │  │ • Gemini API  │
│ • Missing vals │  │ • Ollama      │
│ • Validation   │  │   (local)     │
└────────────────┘  └───────────────┘
```

## 💰 Minimal Cost Setup (FREE!)

This project is designed to run with **$0 cost** during development:

| Component | Free Option | Cost |
|-----------|-------------|------|
| Frontend Hosting | Vercel | **FREE** |
| Backend Hosting | Railway/Render Free Tier | **FREE** |
| AI (Local) | Ollama (Llama 2) | **FREE** |
| AI (Cloud) | Google Gemini Free Tier | **FREE** (60 req/min) |
| Database | Not needed for MVP | **FREE** |

**Total: $0/month** 🎉

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### 1️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (optional, for AI features)
# Get free API key: https://makersuite.google.com/app/apikey

# Run the backend
python -m uvicorn app.main:app --reload
```

Backend will run on **http://localhost:8000**

### 2️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local

# Run the development server
npm run dev
```

Frontend will run on **http://localhost:3000**

### 3️⃣ Open Your Browser

Navigate to **http://localhost:3000** and start cleaning your data! 🎉

## 📖 Usage Guide

### Step 1: Upload Your File
- Drag & drop your CSV or Excel file
- Or click "Select File" to browse
- Supported formats: `.csv`, `.xlsx`, `.xls`
- Max file size: 10MB

### Step 2: Review Analysis
- View data quality score (0-100)
- See detected issues (duplicates, missing values, format problems)
- Preview your data (first 10 rows)

### Step 3: Choose Cleaning Options
- ✅ Remove duplicates
- ✅ Fill missing values
- ✅ Standardize formats
- ✅ Use AI suggestions (optional, requires API key)

### Step 4: Download Cleaned Data
- Click "Clean & Download"
- File automatically downloads with `_cleaned` suffix
- Review and use your cleaned data!

## 🤖 AI Integration (Optional)

### Using Google Gemini (Recommended for MVP)

1. Get free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `backend/.env`:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
3. Enable "Use AI" option in the UI

**Free Tier:** 60 requests/minute

### Using Ollama (100% Free, Local)

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama2
   ```
3. Update `backend/.env`:
   ```
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2
   ```
4. Modify `llm_service.py` to use Ollama instead of Gemini

## 📁 Project Structure

```
ai-data-cleaner/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── services/
│   │   │   ├── data_cleaner.py  # Core cleaning logic
│   │   │   └── llm_service.py   # AI/LangChain integration
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main application page
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── FileUploader.tsx
│   │   ├── DataPreview.tsx
│   │   ├── CleaningResults.tsx
│   │   └── ui/                 # Reusable UI components
│   ├── package.json
│   └── tailwind.config.ts
│
└── README.md
```

## 🔧 API Documentation

### `POST /api/analyze`

Analyze uploaded file and return data quality issues.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV or Excel)

**Response:**
```json
{
  "success": true,
  "filename": "data.csv",
  "rows": 1000,
  "columns": 5,
  "column_names": ["name", "email", "phone", "date", "amount"],
  "preview": [...],
  "analysis": {
    "quality_score": 75,
    "issues": [...]
  }
}
```

### `POST /api/clean`

Clean the uploaded file and return cleaned version.

**Query Parameters:**
- `remove_duplicates`: boolean
- `fill_missing`: boolean
- `standardize_formats`: boolean
- `use_ai`: boolean

**Response:** File download (CSV or Excel)

### `POST /api/ai-suggestions`

Get AI-powered cleaning suggestions.

**Request:** Same as `/api/analyze`

**Response:**
```json
{
  "success": true,
  "suggestions": [...],
  "analysis": {...}
}
```

## 🚀 Deployment

### Frontend (Vercel - FREE)

```bash
cd frontend
vercel deploy
```

### Backend (Railway - FREE)

1. Create account at https://railway.app
2. Create new project from GitHub
3. Select `backend` folder
4. Add environment variables
5. Deploy!

## 🛣️ Roadmap

### Phase 1 - MVP (Current)
- ✅ Basic data cleaning (duplicates, missing values, formats)
- ✅ Beautiful dark theme UI
- ✅ CSV and Excel support
- ✅ AI integration (optional)

### Phase 2 - Enhanced AI
- 🔄 Fuzzy duplicate detection
- 🔄 Auto-categorization
- 🔄 Data enrichment via APIs
- 🔄 Custom validation rules

### Phase 3 - SaaS Features
- 🔄 User authentication
- 🔄 Cloud storage integration (Google Sheets, Dropbox)
- 🔄 Scheduled cleaning jobs
- 🔄 Team collaboration
- 🔄 API access for developers

### Phase 4 - Enterprise
- 🔄 Database connectivity
- 🔄 Dashboard generation
- 🔄 Advanced analytics
- 🔄 White-label options

## 💼 Business Model (Future)

### Freemium Pricing
- **Free**: 10 files/month, 10MB max, basic cleaning
- **Pro** ($29/mo): Unlimited files, 100MB max, AI features
- **Business** ($99/mo): Team features, API access, priority support

### Target Market
- 3.5M+ SMEs in Japan
- Businesses using spreadsheets (accounting, HR, sales)
- Industries: Retail, Real Estate, Healthcare, Education

## 🤝 Contributing

Contributions are welcome! This is an open-source project in early development.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - feel free to use this project for learning or commercial purposes!

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- AI by [LangChain](https://langchain.com/) + [Google Gemini](https://ai.google.dev/)
- Styled with [Tailwind CSS](https://tailwindcss.com/)

## 📧 Contact

For questions or feedback, please open an issue on GitHub!

---

**Built with ❤️ for SMEs struggling with dirty data**