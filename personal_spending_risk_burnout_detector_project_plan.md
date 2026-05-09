# 💡 Personal Spending Risk & Burnout Detector (Malaysia-Focused)

## 🎯 Core Value

A smart system that:

- Analyzes bank statements (PDF/CSV)
- Detects financial stress patterns
- Flags burnout-related spending behavior
- Provides actionable, localized advice (Malaysia context)

---

## 🧠 Why This Project Matters

Most finance tools only track spending. This project interprets behavior.

**Key Differentiators:**

- Behavioral + financial insights
- Malaysia-specific ecosystem (Grab, TNG, Shopee)
- AI-driven explanations

---

## 🏗️ System Overview

### Pipeline Flow

```
Upload → Parse → Clean → Categorize → Feature Extraction → Risk Scoring → Insights
```

---

## 🔄 Detailed Workflow

### 1. 📥 Data Ingestion Layer

**Inputs:**

- PDF bank statements
- CSV exports

**Tools:**

- pdfplumber (PDF)
- pandas (CSV)

**Standard Format:**

```json
{
  "date": "2026-04-01",
  "description": "GRAB FOOD",
  "amount": -23.50,
  "balance": 1200.00
}
```

**Strategy:**

- Modular parsers per bank

```
parsers/
  maybank_parser.py
  cimb_parser.py
```

---

### 2. 🧹 Data Cleaning

- Remove duplicates
- Normalize merchant names
- Standardize formats

---

### 3. 🏷️ Transaction Categorization

**Categories:**

- Food & Beverage
- Transport
- Shopping
- Bills
- Entertainment
- Income

**Approach:**

- Phase 1: Rule-based (keywords)
- Phase 2: ML classifier (optional)

---

### 4. 📊 Feature Engineering

**Spending Patterns:**

- Daily/weekly trends
- Spending growth

**Risk Indicators:**

- High food delivery frequency
- Late-night transactions
- Sudden spending spikes

**Burnout Signals:**

- Increased GrabFood usage
- Higher weekday spending
- Reduced savings rate

---

### 5. ⚠️ Risk Scoring Engine

**Financial Risk Score (0–100):**

- Spending vs income
- Balance trend
- Savings rate

**Burnout Score (0–100):**

- Behavioral anomalies
- Lifestyle spending

---

### 6. 🤖 Insight Generation

**Example Outputs:**

- "Food delivery spending increased 45%"
- "Higher weekday spending detected"
- "Savings dropped below recommended level"

---

### 7. 🇲🇾 Malaysia-Specific Features

- Recognize local merchants (Grab, Shopee, TNG)
- Provide contextual advice

---

### 8. 📊 Dashboard

**Views:**

- Spending breakdown
- Trend analysis
- Risk scores
- Insight cards

**Tech Options:**

- Streamlit (fast MVP)
- React + FastAPI (advanced)

---

## 🧱 Tech Stack

**Backend:**

- Python
- Pandas
- FastAPI

**Frontend:**

- Streamlit

**Storage:**

- SQLite / JSON

---

## 🚀 Development Phases

### Phase 1 (1–2 weeks)

- CSV parsing
- Basic categorization
- Simple dashboard

### Phase 2 (2–3 weeks)

- Risk scoring
- Burnout detection
- Insight engine

### Phase 3 (Optional)

- ML categorization
- UI improvements
- Multi-bank support

---

## ⚡ Efficiency Strategy

**Do:**

- Start with CSV only
- Use rule-based logic
- Build MVP quickly

**Avoid:**

- Overengineering early
- Supporting all banks at once
- Complex UI initially

---

## 🧪 Example Output

```
Burnout Risk: High

You are ordering more food at night,
which may indicate stress.

Suggestion:
Plan meals earlier or reduce late-night orders.
```

---

## 🧠 Career Value

This project demonstrates:

- Data engineering
- Feature engineering
- Applied ML thinking
- Product design mindset
- Real-world relevance

---

# 🤖 Prompt for Antigravity IDE

Use this prompt inside Antigravity IDE:

```
You are a senior software architect and Python engineer.

I want to build a project called "Personal Spending Risk & Burnout Detector (Malaysia-Focused)".

Your task is to generate a COMPLETE, PRODUCTION-READY development plan and code structure.

Requirements:

1. System Architecture
- Design modular backend system
- Separate parsing, processing, and analytics layers
- Ensure scalability and clean code structure

2. Features to Implement
- CSV bank statement ingestion
- PDF parsing (modular support)
- Transaction normalization
- Rule-based categorization system
- Feature engineering (spending trends, behavioral signals)
- Financial risk scoring (0–100)
- Burnout detection scoring (0–100)
- Insight generation engine (human-readable explanations)

3. Technical Stack
- Python (main language)
- Pandas for data processing
- FastAPI for backend APIs
- Streamlit for frontend dashboard
- SQLite for storage

4. Code Requirements
- Provide full folder structure
- Write clean, modular, production-quality code
- Include comments and docstrings
- Follow best practices

5. Output Requirements
- Step-by-step implementation plan
- Full backend code (parsers, services, scoring engine)
- Example dataset for testing
- Streamlit dashboard code
- Instructions to run locally

6. Optimization Goals
- Minimize complexity
- Avoid unnecessary ML in early stage
- Prioritize clarity and maintainability

7. Bonus (if possible)
- Add simple ML categorization upgrade path
- Add API endpoint for uploading files

Generate everything in a structured and developer-friendly format. Always check and troubleshoot the system and fix any error until the system is effient
```

---

**End of Document**

