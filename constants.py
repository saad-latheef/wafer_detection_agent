"""
Constants for Wafer Detection Agent.
Centralizes all magic numbers and fixed values.
"""
from typing import Tuple

# Defect Pattern Classifications
DEFECT_PATTERNS = [
    "none",
    "Center",
    "Donut",
    "Edge-Loc",
    "Edge-Ring",
    "Loc",
    "Near-full",
    "Random",
    "Scratch"
]

# Severity Levels
SEVERITY_NONE = "None"
SEVERITY_LOW = "Low"
SEVERITY_MEDIUM = "Medium"
SEVERITY_HIGH = "High"
SEVERITY_CRITICAL = "Critical"

# Verdict Types
VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"

# Wafer Map Values
WAFER_MAP_NON_WAFER = 0
WAFER_MAP_NORMAL = 1
WAFER_MAP_DEFECT = 2

# RGB Color Mapping for Wafer Maps
WAFER_MAP_COLORS = {
    WAFER_MAP_NON_WAFER: (255, 0, 0),    # Red
    WAFER_MAP_NORMAL: (0, 255, 0),       # Green
    WAFER_MAP_DEFECT: (0, 0, 255),       # Blue
}

# Image Processing
IMAGE_SIZE: Tuple[int, int] = (56, 56)
IMAGE_CHANNELS = 3  # RGB
NORMALIZATION_FACTOR = 255.0

# SPC (Statistical Process Control)
SPC_SIGMA_MULTIPLIER = 3
SPC_RULE_1_SIGMA = 3  # Points beyond 3σ
SPC_RULE_2_SIGMA = 2  # Points beyond 2σ
SPC_RULE_2_OUT_OF_3 = 2  # 2 out of 3 consecutive points
SPC_RULE_4_CONSECUTIVE = 8  # 8 consecutive points on same side
SPC_ZONE_A = "A"  # Within ±1σ
SPC_ZONE_B = "B"  # Between ±1σ and ±2σ
SPC_ZONE_C = "C"  # Beyond ±2σ

# Process Stability Thresholds
STABILITY_THRESHOLD_UNSTABLE = 10.0  # >10% out of control
STABILITY_THRESHOLD_WARNING = 5.0    # >5% out of control
STABILITY_STATUS_STABLE = "stable"
STABILITY_STATUS_WARNING = "warning"
STABILITY_STATUS_UNSTABLE = "unstable"

# Analysis Consistency
CONSISTENCY_SCORE_PASS_THRESHOLD = 0.6
CONSISTENCY_PENALTY_LOW_CONFIDENCE = 0.3
CONSISTENCY_PENALTY_MODERATE_CONFIDENCE = 0.1
CONSISTENCY_PENALTY_MULTIPLE_DEFECTS = 0.2
CONSISTENCY_PENALTY_PREDICTION_MISMATCH = 0.3

# Root Cause Analysis
RCA_FISHBONE_CATEGORIES = ["man", "machine", "material", "method", "measurement", "environment"]
RCA_FIVE_WHYS_LEVELS = 5
RCA_CAPA_PRIORITY_CRITICAL = "Critical"
RCA_CAPA_PRIORITY_HIGH = "High"
RCA_CAPA_PRIORITY_MEDIUM = "Medium"
RCA_CAPA_PRIORITY_LOW = "Low"

# Notification/Alert Thresholds
ALERT_DEFECT_RATE_THRESHOLD = 15.0  # percent
ALERT_CONSECUTIVE_FAILS = 3

# Database
DB_QUERY_LIMIT_DEFAULT = 100
DB_QUERY_LIMIT_MAX = 1000

# File Types
SUPPORTED_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')
SUPPORTED_NPY_EXTENSION = '.npy'

# HTTP Status Messages
MSG_FILE_NOT_FOUND = "File not found"
MSG_INVALID_FILE_TYPE = "Invalid file type"
MSG_PROCESSING_ERROR = "Processing error occurred"
MSG_MODEL_NOT_AVAILABLE = "Model not available"
MSG_SUCCESS = "Operation successful"

# Agent Names
AGENT_INGESTION = "ingestion_agent"
AGENT_ML = "ml_agent"
AGENT_ANALYSIS = "analysis_agent"
AGENT_VALIDATION = "validation_agent"
AGENT_TRIGGER = "trigger_agent"
AGENT_EXPLANATION = "explanation_agent"
AGENT_TREND = "trend_agent"

# Model Names
MODEL_NAME_PYTORCH = "PyTorch CNN"
MODEL_NAME_VIT = "Keras ViT"
MODEL_NAME_CUSTOM = "Custom Keras"
MODEL_NAME_SIMULATED = "Simulated"
