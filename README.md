# Wafer Detection Agent 🔬

**Production-ready AI-powered semiconductor wafer defect detection system** with multi-agent architecture, intelligent copilot, and full-stack dashboard.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15.5-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Model Performance](#-model-performance)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

---

## 🎯 Features

### 1. **Dual Model Support** 🤖
#### Image Classification (ResNet18)
- **99.98% Accuracy** on wafer images (.jpg, .png)
- ImageNet-normalized preprocessing for optimal performance
- Detects 9 defect classes with high confidence
- Real-time inference with GPU/CPU support

#### NPY Wafer Map Analysis (Ensemble Model)
- Processes .npy wafer map files (26×26 grids)
- Ensemble of k_cross_CNN.pt (PyTorch) + my_model.weights.h5 (TensorFlow)
- Separate class mappings for backward compatibility
- Handles both binary and multi-class wafer maps

**Supported Defect Classes:**
- Center
- Donut  
- Edge_Loc
- Edge_Ring
- Loc
- Near_Full
- Normal (good wafer)
- Random
- Scratch

### 2. **Multi-Agent System** 🤝
Six specialized agents working in sequence:

#### **Ingestion Agent** 📥
- File validation and format detection
- Image preprocessing (resize, normalize, tensor conversion)
- NPY wafer map processing
- Automatic format detection (.jpg, .png, .npy)

#### **ML Agent** 🧠
- Model loading and inference
- Supports ResNet18 for images
- Ensemble model for NPY files
- Probability distribution calculation
- Confidence scoring

#### **Analysis Agent** 📊
- Probability distribution analysis
- Consistency checking
- Severity assessment (High/Medium/Low/None)
- Major issue identification
- Quality recommendations

#### **Validation Agent** ✅
- Model confidence validation
- Cross-checks predictions
- Verdict determination (PASS/FAIL)
- Quality metrics calculation

#### **Trend Agent** 📈
- Lot-level defect analysis
- Pattern detection across batches
- Systematic issue identification
- Tool-wise failure tracking

#### **Explanation Agent** 💬
- Natural language explanations
- Root cause suggestions
- Actionable recommendations
- Context-aware descriptions

### 3. **AI Copilot** 🤖💡
Intelligent assistant for wafer data analysis:

**Capabilities:**
- Natural language queries about your fab data
- Real-time statistics from database (last 100 wafers)
- Query-specific intelligent responses
- Follow-up suggestion generation

**Query Types Supported:**
- **Yield Analysis**: "What's the current yield rate?"
  - Shows pass/fail breakdown
  - Identifies top failure reasons
  - Highlights problematic tools
  
- **Tool Performance**: "Which tool has the most defects?"
  - Ranks tools by failure count
  - Drill-down on specific tools
  - Defect pattern by tool
  
- **Defect Patterns**: "Show me scratch defects"
  - Defect distribution analysis
  - Specific defect type focus
  - Tool correlation

- **Trend Analysis**: "Show recent trends"
  - Time-based analysis
  - Quality assessment
  - Recent activity summary

**Powered by:** Google ADK (Agentic Development Kit)

### 4. **Full-Stack Dashboard** 🖥️
Modern Next.js 15 frontend with:

#### **Main Dashboard**
- Live wafer analysis interface
- Drag & drop file upload
- Real-time agent execution display
- 3-card agent result view (ML, Analysis, Validation)
- Confidence visualization
- Defect probability charts

#### **Scan History** 📜
- Searchable history of all analyzed wafers
- Filter by Tool ID, Chamber ID, Date
- Pagination support
- Detailed result cards
- Export capabilities

#### **Analytics** 📊
- Defect distribution pie charts
- Tool-wise performance metrics
- Time-series trend graphs
- Quality metrics dashboard

#### **SPC Charts** 📉
- Statistical Process Control monitoring
- Western Electric Rules violation detection
- Upper/Lower control limits
- Mean tracking
- Trend indicators

#### **Root Cause Analysis (RCA)** 🔍
- 5-Why analysis framework
- Fishbone diagram support
- Tool/Process correlation
- Actionable recommendations

#### **Parameters** ⚙️
- System configuration
- Model parameters
- Threshold adjustments
- Quality gates

#### **AI Copilot Chat** 💬
- Interactive chat interface
- Scrollable conversation history
- Suggestion chips for common queries
- Real-time data integration

### 5. **Database & Persistence** 💾
- SQLite database (`wafer_analysis.db`)
- Stores all analysis results
- Scan history tracking
- Defect distribution tracking
- Auto-created on first run

### 6. **Production-Ready Backend** 🚀
- **FastAPI** server with async support
- CORS middleware for frontend integration
- File upload handling (multipart/form-data)
- Batch processing support
- Error handling and logging
- Health check endpoint

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 15)                │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐            │
│  │Dashboard │  │  History  │  │ Copilot  │  ...       │
│  └──────────┘  └───────────┘  └──────────┘            │
└─────────────────────────────────────────────────────────┘
                        │ HTTP/REST API
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI + Python)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │              API Endpoints                        │  │
│  │  /analyze  /analyze-lot  /history  /copilot     │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                │
│  ┌─────────────────────┴──────────────────────┐       │
│  ▼                                              ▼       │
│  Multi-Agent System                    AI Copilot      │
│  ┌─────────────┐  ┌──────────────┐   ┌──────────┐    │
│  │ Ingestion   │→ │  ML Agent    │→  │ Analysis │    │
│  │   Agent     │  │ (ResNet18)   │   │  Agent   │    │
│  └─────────────┘  │ (Ensemble)   │   └──────────┘    │
│                    └──────────────┘         │          │
│                           │                  ▼          │
│                           │          ┌──────────────┐  │
│                           │          │ Validation   │  │
│                           │          │   Agent      │  │
│                           │          └──────────────┘  │
│                           │                  │          │
│                           ▼                  ▼          │
│                    ┌────────────────────────────┐      │
│                    │   Database (SQLite)        │      │
│                    │  - Wafer records           │      │
│                    │  - Scan history            │      │
│                    │  - Defect distributions    │      │
│                    └────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

**Key Technologies:**
- **Backend**: Python 3.11, FastAPI, PyTorch, TensorFlow, SQLAlchemy
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, Shadcn UI
- **AI**: Google ADK, ResNet18, Custom CNN ensemble
- **Database**: SQLite with SQLAlchemy ORM

---

## 📦 Installation

### Prerequisites
- **Python** 3.11 or higher
- **Node.js** 18+ and npm/pnpm
- **Git** for version control
- **CUDA** (optional, for GPU acceleration)

### Step 1: Clone the Repository
```bash
git clone https://github.com/saad-latheef/wafer_detection_agent.git
cd wafer_detection_agent
```

### Step 2: Backend Setup

#### Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Required packages include:**
- fastapi
- uvicorn
- torch
- torchvision
- tensorflow
- pillow
- numpy
- sqlalchemy
- python-multipart

#### Download Model Files
**⚠️ Important:** Model files are excluded from the repository due to size (300+ MB).

You need to obtain/place the following model files in the project root:
- `best_model.pt` - ResNet18 model for image classification
- `k_cross_CNN.pt` - PyTorch CNN for NPY wafer maps
- `my_model.weights.h5` - TensorFlow model for NPY ensemble

**Options:**
1. Train your own models using your wafer datasets
2. Download pre-trained models (if available)
3. Use Git LFS to store and retrieve large files

#### Configure Environment (Optional)
Create a `.env` file for API keys:
```bash
# For AI Copilot (optional)
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Step 3: Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Return to project root
cd ..
```

### Step 4: Start the Application

#### Option A: Start Both Servers Separately

**Terminal 1 - Backend:**
```bash
# Using the helper script (sets PYTHONPATH correctly)
python start_backend.py

# OR manually with uvicorn
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### Option B: Using Process Manager (Production)
```bash
# Install PM2 globally
npm install -g pm2

# Start backend
pm2 start "python start_backend.py" --name wafer-backend

# Start frontend
pm2 start "npm run dev" --name wafer-frontend --cwd frontend

# View logs
pm2 logs
```

### Step 5: Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🚀 Usage

### Basic Workflow

#### 1. Upload & Analyze a Wafer
```bash
# Using curl
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@path/to/wafer.jpg"

# Using Python
import requests
files = {'file': open('wafer.jpg', 'rb')}
response = requests.post('http://localhost:8000/api/analyze', files=files)
print(response.json())
```

#### 2. View Results in Dashboard
1. Navigate to http://localhost:3000
2. Upload wafer image or .npy file
3. Watch real-time agent execution
4. View 3-card result display
5. Check confidence scores and verdict

#### 3. Query AI Copilot
Navigate to AI Copilot page and ask:
- "What's the current yield rate?"
- "Which tool has the highest defect rate?"
- "Show me scratch defects from TOOL-3"
- "What's the trend for edge-ring defects?"

#### 4. Review Scan History
- Click "Scan History" in sidebar
- Filter by Tool ID, Chamber ID, or date
- View detailed analysis results
- Export data as needed

#### 5. Monitor SPC Compliance
- Navigate to SPC Charts
- Check for Western Electric Rules violations
- Monitor process stability
- Identify trends requiring intervention

### Batch Processing
```bash
# Analyze multiple wafers
curl -X POST http://localhost:8000/api/analyze-lot \
  -F "files=@wafer1.jpg" \
  -F "files=@wafer2.jpg" \
  -F "files=@wafer3.jpg"
```

---

## 📡 API Reference

### Endpoints

#### `POST /api/analyze`
Analyze a single wafer file (image or NPY).

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image or .npy)

**Response:**
```json
{
  "waferId": "wafer_1234567890",
  "predictedClass": "Scratch",
  "confidence": 0.9823,
  "verdict": "FAIL",
  "severity": "High",
  "agentResults": [
    {
      "agent": "ML Model",
      "topPattern": "Scratch",
      "confidence": 0.9823,
      "description": "..."
    },
    ...
  ]
}
```

#### `POST /api/analyze-lot`
Batch analyze multiple wafers.

**Request:**
- Content-Type: `multipart/form-data`  
- Body: `files[]` (multiple files)

**Response:**
```json
{
  "results": [...],
  "lotId": "lot_1234567890",
  "trendAnalysis": "..."
}
```

#### `GET /api/history`
Get wafer analysis history.

**Query Parameters:**
- `limit` (int): Number of records (default: 50)
- `tool_id` (str): Filter by tool ID
- `chamber_id` (str): Filter by chamber

**Response:**
```json
{
  "total": 150,
  "wafers": [...]
}
```

#### `POST /api/copilot/query`
Query the AI copilot.

**Request:**
```json
{
  "query": "What's the current yield rate?"
}
```

**Response:**
```json
{
  "response": "📊 **Yield Analysis** ...",
  "suggestions": ["Which tool is causing failures?", ...],
  "powered_by": "Wafer Analytics Engine"
}
```

#### `GET /api/spc`
Get SPC chart data.

**Query Parameters:**
- `days` (int): Time range in days
- `tool_id` (str): Filter by tool

**Response:**
```json
{
  "data": [...],
  "controlLimits": {...},
  "violations": [...]
}
```

---

## 📊 Model Performance

### ResNet18 (Image Classification)
- **Accuracy**: 99.98%
- **Training**: Pre-trained on ImageNet, fine-tuned on wafer dataset
- **Input**: 224×224 RGB images
- **Preprocessing**: ImageNet normalization (critical!)
  - Mean: [0.485, 0.456, 0.406]
  - Std: [0.229, 0.224, 0.225]

### Ensemble Model (NPY Maps)
- **Architecture**: k_cross_CNN (PyTorch) + my_model (TensorFlow)
- **Input**: 26×26 wafer maps (3 channels)
- **Ensemble**: Best confidence selection
- **Classes**: 9 defect types with separate mapping

### Class Mapping Fix
⚠️ **Critical**: Separate class name lists for different models:
- `IMAGE_CLASS_NAMES` for ResNet18 (underscores: Edge_Loc)
- `NPY_CLASS_NAMES` for ensemble (hyphens: Edge-Loc, "none" for normal)

---

## 📁 Project Structure

```
wafer_detection_agent/
├── api/
│   └── server.py              # FastAPI application
├── agents/
│   ├── ingestion_agent.py     # File processing
│   ├── ml_agent.py            # Model inference
│   ├── analysis_agent.py      # Result analysis
│   ├── validation_agent.py    # Quality validation
│   ├── trend_agent.py         # Batch analysis
│   └── explanation_agent.py   # Natural language generation
├── backend/
│   ├── models.py              # SQLAlchemy models
│   ├── database.py            # Database configuration
│   ├── adk_copilot.py         # AI Copilot implementation
│   └── copilot_utils.py       # Legacy copilot (deprecated)
├── shared/
│   └── context.py             # Shared agent context
├── frontend/
│   ├── app/                   # Next.js 15 app directory
│   │   ├── (dashboard)/
│   │   │   ├── page.tsx       # Main dashboard
│   │   │   ├── history/       # Scan history
│   │   │   ├── analytics/     # Analytics charts
│   │   │   ├── spc/           # SPC charts
│   │   │   ├── rca/           # Root cause analysis
│   │   │   ├── parameters/    # Configuration
│   │   │   └── copilot/       # AI Copilot chat
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── ui/                # Shadcn UI components
│   │   └── layout/            # Layout components
│   ├── lib/                   # Utilities
│   └── package.json
├── google/
│   └── adk/                   # Google ADK (local)
├── Datasets/                  # Training/test data (excluded)
├── best_model.pt             # ResNet18 (excluded - 100MB+)
├── k_cross_CNN.pt            # CNN model (excluded - 100MB+)
├── my_model.weights.h5       # TensorFlow (excluded - 100MB+)
├── wafer_analysis.db         # SQLite database (excluded)
├── requirements.txt          # Python dependencies
├── start_backend.py          # Backend startup helper
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

**Note**: Large files (.pt, .h5, datasets, database) are excluded from Git. See Installation section for setup.

---

## 🔧 Configuration

### Backend Configuration
Edit `api/server.py` for:
- CORS origins
- Upload file size limits
- Database path
- Model paths

### Frontend Configuration
Edit `frontend/next.config.mjs` for:
- API endpoint URLs
- Build settings
- Image optimization

### Model Configuration
- ResNet18: `agents/ml_agent.py` lines 36-48 (class names)
- Ensemble: `agents/ml_agent.py` lines 240-290 (model loading)

---

## 🐛 Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: google.adk
**Solution**: Use `start_backend.py` which sets PYTHONPATH correctly
```bash
python start_backend.py
```

#### 2. Model file not found
**Solution**: Ensure model files are in project root
```bash
ls -la *.pt *.h5
```

#### 3. Frontend can't connect to backend
**Solution**: Check CORS settings in `api/server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    ...
)
```

#### 4. Database locked error
**Solution**: Stop backend server and delete lock file
```bash
rm wafer_analysis.db
# Restart backend
```

#### 5. NPY files predict wrong class
**Solution**: Verify NPY_CLASS_NAMES are used (fixed in this version)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google ADK** for agentic framework
- **PyTorch** and **TensorFlow** for ML frameworks
- **Next.js** team for the amazing frontend framework
- **FastAPI** for the high-performance backend
- **Shadcn UI** for beautiful components

---

## 📞 Support

For issues, questions, or contributions:
- **GitHub Issues**: https://github.com/saad-latheef/wafer_detection_agent/issues
- **Pull Requests**: https://github.com/saad-latheef/wafer_detection_agent/pulls

---

## 🗺️ Roadmap

- [ ] Git LFS setup for model files
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests
- [ ] Real-time WebSocket updates
- [ ] Advanced SPC rules
- [ ] Model retraining pipeline
- [ ] Multi-user authentication
- [ ] Cloud storage integration
- [ ] Grafana dashboards
- [ ] Automated testing suite

---

**Built with ❤️ for semiconductor manufacturing quality control**
