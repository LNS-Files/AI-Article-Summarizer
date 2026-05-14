# AI Article Summarizer

A polished Streamlit app that summarizes articles using **Claude AI** (Anthropic).  
Paste text directly or drop in a URL — Claude handles the rest.

## Features

- **Two input modes** — paste article text or fetch directly from a URL
- **4 summary styles** — Paragraph, Bullet Points, Key Insights, Executive Summary
- **3 length options** — Brief, Detailed, Comprehensive
- **Live stats** — word count, character count, estimated reading time
- **Compression badge** — shows how much shorter the summary is vs the original
- **Download summary** as a `.txt` file
- **Session history** — all summaries from the current session in the sidebar
- **Dark UI** with a purple/indigo gradient theme

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your API key

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Get a key at [console.anthropic.com](https://console.anthropic.com).

### 3. Run the app

```bash
streamlit run app.py
```

## Project structure

```
AI-Article-Summarizer/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Dark theme config
├── .env                    # API key (not committed)
└── .gitignore
```
