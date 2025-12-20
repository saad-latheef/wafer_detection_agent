# 🏭 Wafer Detection Agentic System

An intelligent, multi-agent system designed for **automated wafer defect detection and analysis** in semiconductor manufacturing. This project leverages a custom CNN model combined with a robust agentic architecture to provide high-accuracy defect classification, root-cause analysis, and automated corrective actions.

---

## 🚀 Overview

In semiconductor manufacturing, detecting and classifying defect patterns on wafers is critical for maintaining high yields. This system moves beyond simple classification by employing a **Coordination-as-a-Service** model where multiple specialized agents collaborate:

1.  **Ingestion Agent**: Pre-processes raw `.npy` wafer maps and extracts key features.
2.  **ML Agent**: Executes a trained CNN (`k_cross_CNN.pt`) to detect defect patterns.
3.  **Analysis Agent**: Evaluates prediction confidence, consistency, and determines severity.
4.  **Validation Agent**: Performs quality checks and triggers retries if thresholds aren't met.
5.  **Explanation Agent**: Generates human-readable summaries and actionable insights.
6.  **Trigger Agent**: Executes downstream workflows (alerts, lot holds, etc.).

---

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, PyTorch (Inference)
-   **Frontend**: Next.js (React), Tailwind CSS, Lucide Icons, Recharts
-   **Agent Framework**: Google ADK (Agent Development Kit)
-   **Data Processing**: NumPy, OpenCV, Pandas

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or pnpm

### 1. Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd wafer_detection_agent

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate # On Windows: source .venv/bin/activate 

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

---

## 🏃 Running the Project

### Core Pipeline (CLI)
To run a sample analysis on the provided `wafer.npy`:
```bash
python main.py
```

### Backend API
Start the FastAPI server:
```bash
python api/server.py
```
The API will be available at `http://localhost:8000`. You can view the interactive documentation at `/docs`.

### Frontend Dashboard
Launch the Next.js development server:
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000` in your browser to access the dashboard.

---

## 📊 Sample Input & Output

### Input
A wafer map stored as a `.npy` file (e.g., `wafer.npy`). This is typically a 2D array where values represent different states:
- `0`: Background/Non-wafer
- `1`: Normal/Pass
- `2`: Defect/Fail

### Output
The system generates a comprehensive multi-agent analysis report. Below is an example of the structured API response:

```json
{
  "waferId": "W-4829",
  "finalVerdict": "FAIL",
  "detectedPattern": "Edge-Ring",
  "confidence": 98.5,
  "severity": "High",
  "analysisDetails": {
    "consistencyScore": 1.0,
    "recommendation": "FAIL",
    "issuesFound": []
  },
  "triggerAction": {
    "alertSent": true,
    "severity": "High",
    "actions": [
      "STOP production line for inspection",
      "Flag wafer for immediate review",
      "Notify Quality Control team"
    ]
  },
  "explanation": "The analysis detected a significant Edge-Ring defect pattern. This pattern is often associated with issues in the edge bead removal (EBR) process or spin coating non-uniformity..."
}
```

---

## 🏗️ Key Components

### 🧠 Multi-Agent Orchestration (`/agents`)
- **Coordinator Agent**: The brain of the system, managing the sequential execution of all sub-agents.
- **Detection Loop**: A sub-orchestrator that handles the repetitive process of detection, analysis, and validation.

### 🌐 Backend API (`/api`)
- Built with **FastAPI**, providing endpoints for wafer analysis and health monitoring.
- Bridges the gap between the Next.js frontend and the Python-based agent logic.

### 🖥️ Frontend Dashboard (`/frontend`)
- A modern, reactive dashboard built with **Next.js 14 and Tailwind CSS**.
- Features real-time analysis visualization, defect grouping, and detailed report generation.

### 🧪 Google ADK (`/google/adk`)
- A local implementation of the Google Agent Development Kit, enabling structured agent definitions, tool integration, and context management.

---

## 📁 Project Structure

```text
wafer_detection_agent/
├── agents/             # Multi-agent implementations
├── api/                # FastAPI server implementation
├── frontend/           # Next.js dashboard
├── google/adk/         # Google Agent Development Kit (Local implementation)
├── shared/             # Shared context and data models
├── tools/              # Utility tools for agents
├── k_cross_CNN.pt      # Pre-trained defect detection model
├── main.py             # CLI entry point
└── requirements.txt    # Python dependencies
```

---


