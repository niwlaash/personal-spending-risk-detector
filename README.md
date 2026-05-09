# 💰 Personal Spending Risk & Burnout Detector

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0%2B-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25.0%2B-FF4B4B?logo=streamlit)

A smart system that analyzes bank statements, detects financial stress patterns, flags burnout-related spending behavior, and provides actionable Malaysia-contextualized advice. 

This tool is especially useful for understanding personal financial health by combining rule-based heuristics with machine learning analysis of spending categories and behaviors.

---

## 🚀 Features

- **CSV & PDF Parsing** — Upload bank statements from major Malaysian banks.
- **Smart Categorization** — Recognizes Grab, Shopee, TNG, and 50+ local merchants.
- **Risk Scoring** — Calculates Financial Risk (0–100) and Burnout Risk (0–100).
- **Behavioral Insights** — Flags late-night spending, food delivery patterns, and spending spikes.
- **Interactive Dashboard** — Streamlit-powered dashboard with interactive charts and recommendations.
- **RESTful API** — FastAPI backend for programmatic access and external integrations.

---

## 🛠️ Quick Start

### 1. Installation & Setup
Clone the repository and set up a virtual environment:

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Dashboard (Streamlit)
To launch the interactive web dashboard:
```bash
.\venv\Scripts\streamlit run dashboard.py
```

### 3. Run API Server (FastAPI)
To run the backend API for programmatic access:
```bash
.\venv\Scripts\uvicorn app.main:app --reload
```
Once running, visit `http://127.0.0.1:8000/docs` for the interactive API documentation.

### 4. Test with Sample Data
A sample CSV is included at `data/sample_statement.csv`. The Streamlit dashboard can load it automatically for demonstration.

---

## 📂 Project Structure

```text
├── app/
│   ├── config.py              # Configuration & constants
│   ├── models.py              # SQLAlchemy database models
│   ├── pipeline.py            # Orchestrator for full analysis
│   ├── main.py                # FastAPI application
│   ├── parsers/               # Statement parsers (CSV, PDF, Maybank, CIMB)
│   └── services/              # Core business logic (categorization, scoring)
├── data/
│   └── sample_statement.csv   # Example test data
├── dashboard.py               # Streamlit dashboard entrypoint
├── requirements.txt           # Project dependencies
└── README.md                  # This document
```

---

## 💻 Tech Stack

- **Data Processing**: Pandas
- **Backend API**: FastAPI
- **Frontend Dashboard**: Streamlit
- **Visualizations**: Plotly
- **Database**: SQLAlchemy + SQLite
- **Document Parsing**: pdfplumber

---

## 📄 License
This project is for personal use and side-project exploration.
