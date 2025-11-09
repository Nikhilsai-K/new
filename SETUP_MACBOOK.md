# 🚀 Setup Guide for MacBook Air (16GB RAM)

## Perfect Models for Your Hardware

Your MacBook Air M1/M2 with 16GB RAM can run these excellent models:

### ⭐ RECOMMENDED (Best Quality/Speed Balance)

```bash
# Install Ollama first
brew install ollama

# Start Ollama service
ollama serve

# Pull the BEST model for your hardware (in another terminal)
ollama pull qwen2.5:14b
```

**Qwen 2.5 14B** - Perfect balance of quality and speed for 16GB RAM
- Excellent analytical reasoning
- Fast on Mac Silicon
- Great for data analysis

### 🎯 Alternative Options

**Option 1: Fastest (Still High Quality)**
```bash
ollama pull llama3.1:8b
```
- Very fast responses (2-5 seconds)
- Good quality
- Uses only 6GB RAM

**Option 2: Best Quality (Slower)**
```bash
ollama pull qwen2.5:32b-instruct-q4_K_M
```
- Highest quality for 16GB RAM
- Quantized to fit in memory
- Slower but more accurate (10-20 seconds)

**Option 3: Specialized for Data**
```bash
ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M
```
- Optimized for structured data tasks
- Great for code generation
- Medium speed

## 🎯 My Recommendation

Start with **Qwen 2.5 14B**:

```bash
# 1. Install Ollama
/bin/bash -c "$(curl -fsSL https://ollama.com/install.sh)"

# 2. Pull model (downloads ~8GB)
ollama pull qwen2.5:14b

# 3. Verify it works
ollama run qwen2.5:14b "Analyze this data: Name: John, Age: 25, Salary: 50000"
```

## 🔧 Integration with Your App

Your backend will **automatically detect** and use the best available model!

1. Start Ollama: `ollama serve`
2. Start backend: `cd backend && python -m uvicorn app.main:app --reload`
3. Upload a file - the LLM will analyze it!

## ⚡ Performance Expectations

| Model | Speed | Quality | RAM Usage |
|-------|-------|---------|-----------|
| Qwen 2.5 14B | ⭐⭐⭐⭐ (5-10s) | ⭐⭐⭐⭐⭐ | ~10GB |
| Llama 3.1 8B | ⭐⭐⭐⭐⭐ (2-5s) | ⭐⭐⭐⭐ | ~6GB |
| Qwen 32B (Q4) | ⭐⭐⭐ (10-20s) | ⭐⭐⭐⭐⭐ | ~14GB |

## 🎨 What You Get

Your local LLM will:
- ✅ Analyze data quality with expert-level reasoning
- ✅ Provide specific, actionable recommendations
- ✅ Suggest optimal cleaning strategies (median/mode/etc.)
- ✅ Understand domain context (knows data cleaning best practices)
- ✅ Self-verify for accuracy
- ✅ Run 100% offline (no internet needed)
- ✅ Zero cost forever!

## 🐛 Troubleshooting

**Ollama not starting?**
```bash
# Check if running
ps aux | grep ollama

# Restart
killall ollama
ollama serve
```

**Model too slow?**
```bash
# Switch to faster model
ollama pull llama3.1:8b
```

**Out of memory?**
```bash
# Use quantized version
ollama pull qwen2.5:14b-instruct-q4_K_M
```

## 🚀 Quick Start Commands

```bash
# Complete setup in 3 commands
brew install ollama
ollama pull qwen2.5:14b
ollama serve
```

That's it! Your industrial-grade local LLM is ready! 🎉
