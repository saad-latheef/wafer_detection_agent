# 🏭 Wafer Detection Agentic System

An intelligent, multi-agent system designed for **automated wafer defect detection and analysis** in semiconductor manufacturing. This project leverages a custom CNN model combined with a robust agentic architecture to provide high-accuracy defect classification, statistical process control (SPC), and automated root-cause analysis (RCA).

---

## 🚀 Overview

In semiconductor manufacturing, detecting and classifying defect patterns on wafers is critical for maintaining high yields. This system moves beyond simple classification by employing a **Coordination-as-a-Service** model where multiple specialized agents collaborate:

1.  **Ingestion Agent**: Pre-processes raw `.npy` wafer maps and extracts key features.
2.  **ML Agent**: Executes a trained CNN (`k_cross_CNN.pt`) to detect defect patterns.
3.  **Analysis Agent**: Evaluates prediction confidence, consistency, and determines severity.
4.  **Validation Agent**: Performs quality checks and triggers retries if thresholds aren't met.
5.  **Explanation Agent**: Generates human-readable summaries and actionable insights.
6.  **Trigger Agent**: Executes downstream workflows (alerts, lot holds, reporting).

---

## 🛠️ Tech Stack

-   **Backend**: Python 3.9+, FastAPI, PyTorch (Inference), SQLAlchemy (SQLite)
-   **Frontend**: Next.js 14, Tailwind CSS, Framer Motion, Recharts, Lucide Icons
-   **Agent Framework**: Google ADK (Agent Development Kit)
-   **Data Processing**: NumPy, OpenCV, Pandas

---

## 📦 Detailed Setup

### Prerequisites
- Python 3.9+ installed and added to PATH
- Node.js 18+ and npm installed

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/R-Vaishnav-Raj/wafer_detection_agent
cd wafer_detection_agent

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate 

# Install dependencies
pip install -r requirements.txt
```

### 2. Database & Data Seeding
Before running the application, you must initialize the database and seed it with realistic data for the dashboard charts to function.

```bash
# Initialize database tables
python backend/init_db.py

# Seed database with 30 days of realistic SPC/Defect data
python backend/seed_spc_data.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

---

## 🏃 Running the Project

### Start Backend API
The backend provides the API for the dashboard and manages the agentic workflows.
```bash
# From the project root
uvicorn api.server:app --reload --port 8000
```
- **Documentation**: Access the Swagger UI at `http://localhost:8000/docs`

### Start Frontend Dashboard
Launch the modern, responsive Next.js dashboard.
```bash
cd frontend
npm run dev
```
- **Access**: Open `http://localhost:3000` in your browser.

---

## ✨ Dashboard Features

-   **Live Analysis**: Real-time wafer scan ingestion and multi-agent defect classification.
-   **SPC Charts**: Interactive control charts (Process Stability, Western Electric Rules detection).
-   **Automated RCA**: AI-driven Root Cause Analysis with 5-Why and Fishbone (Ishikawa) diagrams.
-   **AI Copilot**: Natural language interface to query fab data and yield trends.
-   **Global Transitions**: Fluid "Slide-Up & Fade" animations and a persistent sidebar for a premium SPA experience.

---

## 🏗️ Project Structure

```text
wafer_detection_agent/
├── agents/             # specialized agent implementations (Ingestion, ML, Analysis, etc.)
├── api/                # FastAPI server and endpoint definitions
├── backend/            # core utilities, database models, and seeding scripts
├── frontend/           # Next.js dashboard application
│   ├── app/            # Next.js 14 App Router (Persistent Layouts)
│   ├── components/     # UI components (Recharts, Framer Motion transitions)
├── google/adk/         # Google Agent Development Kit (Local implementation)
├── shared/             # shared context, schemas, and data models
├── k_cross_CNN.pt      # pre-trained defect detection model
├── main.py             # CLI entry point for batch analysis
└── requirements.txt    # Python dependencies
```

---
