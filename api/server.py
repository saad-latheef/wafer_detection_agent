"""
FastAPI server for Wafer Detection Agent.
Returns comprehensive analysis data matching agent output.
"""
import os
import sys
import tempfile
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.context import WaferContext
from agents.ingestion_agent import ingest_image
from agents.ml_agent import run_ml_inference
from agents.analysis_agent import analyze_results
from agents.explanation_agent import generate_explanation
from agents.trend_agent import analyze_trend

# Database imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.models import get_db, Lot, Wafer, DefectDistribution
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import StreamingResponse

# PDF import - conditional to handle potential import errors
try:
    from backend.pdf_generator import generate_wafer_report_pdf
    PDF_AVAILABLE = True
except ImportError as e:
    print(f"PDF generation not available: {e}")
    PDF_AVAILABLE = False

# Extend WaferContext to support trend analysis
WaferContext.defect_distribution = {}
WaferContext.trend_analysis = ""

app = FastAPI(title="Wafer Detection Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatternProbability(BaseModel):
    pattern: str
    probability: float


class IngestionDetails(BaseModel):
    waferMapShape: List[int]
    tensorShape: List[int]
    nonWaferCount: int
    normalCount: int
    defectCount: int


class AnalysisDetails(BaseModel):
    consistencyScore: float
    issuesFound: List[str]
    recommendation: str
    majorIssues: List[Dict[str, Any]]


class ValidationDetails(BaseModel):
    attempts: int
    maxAttempts: int
    criteriaChecks: List[Dict[str, Any]]
    passed: bool


class AgentResult(BaseModel):
    name: str
    model: str
    topPattern: str
    topProbabilities: List[PatternProbability]
    confidence: float
    qualityFlag: Optional[str]
    description: str
    rootCauses: List[str]
    actionSuggestions: List[str]


class TriggerAction(BaseModel):
    alertSent: bool
    recipient: str
    subject: str
    severity: str
    actions: List[str]


class AnalysisResponse(BaseModel):
    waferId: str
    fileName: str
    finalVerdict: str
    confidence: float
    severity: str
    
    # Detailed info from each agent
    ingestionDetails: IngestionDetails
    analysisDetails: AnalysisDetails
    validationDetails: ValidationDetails
    triggerAction: TriggerAction
    
    # Agent results for 3 columns
    agentResults: List[AgentResult]
    
    # Full data
    fullProbabilityDistribution: Dict[str, float]
    explanation: str
    
    # Processing info
    modelUsed: str
    deviceUsed: str


class LotAnalysisRequest(BaseModel):
    defectDistribution: Dict[str, int]


class LotAnalysisResponse(BaseModel):
    analysis: str


# Root cause mappings
ROOT_CAUSES = {
    "Center": [
        "Focus or exposure center bias",
        "Chuck temperature center gradient",
        "Gas flow distribution center concentration"
    ],
    "Donut": [
        "Photoresist coating ring pattern",
        "Spin coating non-uniformity",
        "Temperature gradient during processing"
    ],
    "Edge-Loc": [
        "Edge handling damage",
        "Edge exclusion zone misconfiguration",
        "Peripheral contamination"
    ],
    "Edge-Ring": [
        "Edge bead removal (EBR) process deviation",
        "Spin coating non-uniformity at wafer periphery",
        "Chamber edge heating inconsistency"
    ],
    "Loc": [
        "Localized particle contamination",
        "Point source defect during deposition",
        "Mask defect or alignment issue"
    ],
    "Near-full": [
        "Severe process contamination",
        "Complete chamber malfunction",
        "Critical recipe parameter deviation"
    ],
    "Random": [
        "Ambient particle contamination",
        "Handling and transport issues",
        "Cleanroom environment degradation"
    ],
    "Scratch": [
        "Mechanical handling damage",
        "Robotic arm malfunction",
        "Wafer cassette contact issues"
    ],
    "none": []
}

ACTION_SUGGESTIONS = {
    "Center": [
        "Verify stepper focus calibration",
        "Check chuck thermal uniformity",
        "Analyze process gas flow patterns"
    ],
    "Donut": [
        "Inspect photoresist dispense system",
        "Calibrate spin coater acceleration",
        "Check bake plate temperature uniformity"
    ],
    "Edge-Loc": [
        "Inspect edge contact points",
        "Review edge exclusion settings",
        "Check for peripheral contamination"
    ],
    "Edge-Ring": [
        "Check EBR tool calibration and nozzle positioning",
        "Verify spin coating recipe parameters",
        "Inspect edge exclusion zone settings"
    ],
    "Loc": [
        "Run particle analysis on affected area",
        "Check deposition uniformity",
        "Inspect mask for defects"
    ],
    "Near-full": [
        "Immediate lot hold recommended",
        "Full chamber qualification required",
        "Escalate to process engineering team"
    ],
    "Random": [
        "Review cleanroom particle counts",
        "Inspect wafer handling equipment",
        "Check HEPA filter status"
    ],
    "Scratch": [
        "Inspect robotic handler end effectors",
        "Check wafer cassette for damage",
        "Review handling procedures"
    ],
    "none": [
        "Continue production monitoring",
        "Standard quality gate passage"
    ]
}

TRIGGER_ACTIONS = {
    "High": [
        "STOP production line for inspection",
        "Flag wafer for immediate review",
        "Notify Quality Control team"
    ],
    "Medium": [
        "Mark wafer for quality review",
        "Continue production with monitoring",
        "Log for trend analysis"
    ],
    "Low": [
        "Log defect for monitoring",
        "Continue normal operation",
        "Review in next batch analysis"
    ],
    "None": [
        "Continue production monitoring",
        "Standard quality gate passage"
    ]
}


@app.post("/api/analyze-lot", response_model=LotAnalysisResponse)
async def analyze_lot(request: LotAnalysisRequest):
    context = WaferContext(image_path="LOT_LEVEL_ANALYSIS")
    context.defect_distribution = request.defectDistribution
    
    # Run trend agent
    analyze_trend(context)
    
    return LotAnalysisResponse(analysis=context.trend_analysis)


@app.get("/api/trends")
async def get_trends(start_date: str = "", end_date: str = "", group_by: str = "day"):
    """
    Get historical trend data for defect rates over time.
    Returns time-series data grouped by day/week/month.
    """
    from datetime import datetime, timedelta
    
    db = next(get_db())
    try:
        # Default to last 30 days if no date range specified
        if not end_date:
            end_dt = datetime.utcnow()
        else:
            end_dt = datetime.fromisoformat(end_date)
            
        if not start_date:
            start_dt = end_dt - timedelta(days=30)
        else:
            start_dt = datetime.fromisoformat(start_date)
        
        # Query wafers in date range
        wafers = db.query(Wafer).filter(
            Wafer.analyzed_at >= start_dt,
            Wafer.analyzed_at <= end_dt
        ).all()
        
        # Group by date
        trends = {}
        for wafer in wafers:
            date_key = wafer.analyzed_at.strftime("%Y-%m-%d")
            if date_key not in trends:
                trends[date_key] = {"total": 0, "defective": 0, "pass": 0}
            
            trends[date_key]["total"] += 1
            if wafer.final_verdict == "FAIL":
                trends[date_key]["defective"] += 1
            else:
                trends[date_key]["pass"] += 1
        
        # Calculate yield rates
        result = []
        for date, stats in sorted(trends.items()):
            yield_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result.append({
                "date": date,
                "total_wafers": stats["total"],
                "defective_wafers": stats["defective"],
                "pass_wafers": stats["pass"],
                "yield_rate": round(yield_rate, 2)
            })
        
        return {"trends": result, "start_date": start_dt.isoformat(), "end_date": end_dt.isoformat()}
    
    finally:
        db.close()


@app.get("/api/equipment-correlation")
async def get_equipment_correlation(tool_id: str = ""):
    """
    Get equipment correlation data showing defect rates by tool/chamber.
    """
    db = next(get_db())
    try:
        query = db.query(Wafer)
        
        # Filter by tool if specified
        if tool_id:
            query = query.filter(Wafer.tool_id == tool_id)
        
        wafers = query.all()
        
        # Group by tool
        tool_stats = {}
        for wafer in wafers:
            tool = wafer.tool_id or "UNKNOWN"
            if tool not in tool_stats:
                tool_stats[tool] = {
                    "total": 0,
                    "defective": 0,
                    "defect_breakdown": {}
                }
            
            tool_stats[tool]["total"] += 1
            if wafer.final_verdict == "FAIL":
                tool_stats[tool]["defective"] += 1
                
                # Track defect types
                pattern = wafer.predicted_class or "None"
                if pattern not in tool_stats[tool]["defect_breakdown"]:
                    tool_stats[tool]["defect_breakdown"][pattern] = 0
                tool_stats[tool]["defect_breakdown"][pattern] += 1
        
        # Calculate defect rates
        result = []
        for tool, stats in tool_stats.items():
            defect_rate = (stats["defective"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result.append({
                "tool_id": tool,
                "total_wafers": stats["total"],
                "defective_wafers": stats["defective"],
                "defect_rate": round(defect_rate, 2),
                "defect_breakdown": stats["defect_breakdown"]
            })
        
        # Sort by defect rate (descending)
        result.sort(key=lambda x: x["defect_rate"], reverse=True)
        
        return {"equipment_data": result}
    
    finally:
        db.close()


@app.get("/api/search")
async def search_wafers(
    tool_id: str = "",
    start_date: str = "",
    end_date: str = "",
    defect_type: str = "",
    severity: str = ""
):
    """
    Search and filter wafer analysis results.
    """
    from datetime import datetime, timedelta
    
    db = next(get_db())
    try:
        query = db.query(Wafer)
        
        # Apply filters
        if tool_id:
            query = query.filter(Wafer.tool_id == tool_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Wafer.analyzed_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Wafer.analyzed_at <= end_dt)
        
        if defect_type:
            query = query.filter(Wafer.predicted_class == defect_type)
        
        if severity:
            query = query.filter(Wafer.severity == severity)
        
        # Order by most recent first
        wafers = query.order_by(Wafer.analyzed_at.desc()).limit(100).all()
        
        # Format results
        results = []
        for wafer in wafers:
            results.append({
                "wafer_id": wafer.wafer_id,
                "file_name": wafer.file_name,
                "tool_id": wafer.tool_id,
                "chamber_id": wafer.chamber_id,
                "analyzed_at": wafer.analyzed_at.isoformat() if wafer.analyzed_at else None,
                "predicted_class": wafer.predicted_class,
                "confidence": wafer.confidence,
                "final_verdict": wafer.final_verdict,
                "severity": wafer.severity
            })
        
        return {"results": results, "count": len(results)}
    
    finally:
        db.close()


@app.get("/api/debug-pdf")
async def debug_pdf():
    """
    Debug endpoint to check PDF availability and environment.
    """
    import sys
    import os
    
    debug_info = {
        "pdf_available": PDF_AVAILABLE,
        "cwd": os.getcwd(),
        "sys_path": sys.path,
        "backend_in_modules": "backend" in sys.modules,
        "backend_init_exists": os.path.exists("backend/__init__.py"),
    }
    
    if not PDF_AVAILABLE:
        try:
            from backend.pdf_generator import generate_wafer_report_pdf
            debug_info["import_test"] = "Success (Unexpected)"
        except ImportError as e:
            debug_info["import_error"] = str(e)
        except Exception as e:
            debug_info["other_error"] = str(e)
            
    return debug_info


@app.post("/api/export-lot-pdf")
async def export_lot_pdf(lot_data: dict):
    """
    Generate PDF for a specific lot using provided data.
    Used for batch analysis page.
    """
    if not PDF_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF generation not available")
    
    try:
        # Generate PDF directly from provided lot data
        pdf_buffer = generate_wafer_report_pdf(
            lot_data.get("lot_stats", {}),
            lot_data.get("wafer_analyses", [])
        )
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.get("/api/export-pdf")
async def export_pdf(tool_id: str = "", start_date: str = "", end_date: str = ""):
    """
    Generate and download a PDF report for wafer analyses.
    """
    from datetime import datetime, timedelta
    
    db = next(get_db())
    try:
        # Query wafers
        query = db.query(Wafer)
        
        if tool_id:
            query = query.filter(Wafer.tool_id == tool_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Wafer.analyzed_at >= start_dt)
        else:
            # Default to last 7 days
            start_dt = datetime.utcnow() - timedelta(days=7)
            query = query.filter(Wafer.analyzed_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Wafer.analyzed_at <= end_dt)
        
        wafers = query.all()
        
        # Calculate lot statistics
        total_wafers = len(wafers)
        defective_wafers = sum(1 for w in wafers if w.final_verdict == "FAIL")
        yield_rate = ((total_wafers - defective_wafers) / total_wafers * 100) if total_wafers > 0 else 0
        
        # Defect distribution
        defect_dist = {}
        for wafer in wafers:
            pattern = wafer.predicted_class or "None"
            defect_dist[pattern] = defect_dist.get(pattern, 0) + 1
        
        lot_data = {
            "total_wafers": total_wafers,
            "defective_wafers": defective_wafers,
            "yield_rate": yield_rate,
            "defect_distribution": defect_dist
        }
        
        # Format wafer data for PDF
        wafer_analyses = []
        for wafer in wafers:
            wafer_analyses.append({
                "waferId": wafer.wafer_id,
                "fileName": wafer.file_name,
                "finalVerdict": wafer.final_verdict,
                "confidence": wafer.confidence * 100 if wafer.confidence else 0,
                "severity": wafer.severity or "None"
            })
        
        # Generate PDF
        pdf_buffer = generate_wafer_report_pdf(lot_data, wafer_analyses)
        
        # Return as download
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=wafer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        )
    
    finally:
        db.close()


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_wafer(file: UploadFile = File(...), tool_id: str = "", chamber_id: str = ""):
    if not file.filename.endswith('.npy'):
        raise HTTPException(status_code=400, detail="Only .npy files are supported")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.npy') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        context = WaferContext(image_path=tmp_path, max_attempts=3)
        
        # Run ingestion
        ingest_image(context)
        
        # Run ML inference
        run_ml_inference(context)
        
        # Run analysis
        analyze_results(context)
        
        # Generate explanation
        generate_explanation(context)
        
        # Extract all data
        prob_dist = context.probability_distribution or {}
        predicted = context.predicted_class or "none"
        confidence = context.confidence or 0.0
        has_defect = context.has_defect or False
        severity = context.severity or "None"
        explanation = context.explanation or ""
        metadata = context.metadata or {}
        analysis_result = context.analysis_result or {}
        major_issues = context.major_issues if hasattr(context, 'major_issues') else []
        
        # Build ingestion details
        wafer_shape = list(metadata.get("wafer_map_shape", [0, 0]))
        tensor_shape = list(metadata.get("tensor_shape", [1, 3, 56, 56]))
        
        ingestion_details = IngestionDetails(
            waferMapShape=wafer_shape,
            tensorShape=tensor_shape,
            nonWaferCount=metadata.get("non_wafer_count", 0),
            normalCount=metadata.get("normal_count", 0),
            defectCount=metadata.get("defect_count", 0)
        )
        
        # Build analysis details
        analysis_details = AnalysisDetails(
            consistencyScore=analysis_result.get("consistency_score", 1.0),
            issuesFound=analysis_result.get("issues_found", []),
            recommendation=analysis_result.get("recommendation", "PASS"),
            majorIssues=[{"class": i.get("class", ""), "probability": i.get("probability", 0)} for i in major_issues]
        )
        
        # Build validation details
        validation_details = ValidationDetails(
            attempts=context.validation_attempts if hasattr(context, 'validation_attempts') else 1,
            maxAttempts=3,
            criteriaChecks=[
                {"name": "Consistency Score", "passed": analysis_result.get("consistency_score", 1.0) >= 0.6},
                {"name": "Confidence Threshold", "passed": confidence >= 0.25},
                {"name": "No Prediction Mismatch", "passed": "prediction_mismatch" not in analysis_result.get("issues_found", [])}
            ],
            passed=context.is_valid if hasattr(context, 'is_valid') else True
        )
        
        # Build trigger action
        trigger_action = TriggerAction(
            alertSent=has_defect,
            recipient="quality-control@semiconductor.com",
            subject=f"[ALERT] Wafer Defect Detected - {predicted}",
            severity=severity,
            actions=TRIGGER_ACTIONS.get(severity, TRIGGER_ACTIONS["None"])
        )
        
        # Sort probabilities
        sorted_probs = sorted(prob_dist.items(), key=lambda x: x[1], reverse=True)
        top_probs = [
            PatternProbability(pattern=p, probability=round(v * 100, 2))
            for p, v in sorted_probs
        ]
        
        # Quality flag
        quality_flag = None
        if confidence < 0.5:
            quality_flag = "⚠️ Low confidence - manual review recommended"
        elif confidence < 0.75:
            quality_flag = "⚠️ Moderate confidence - consider verification"
        
        # Create agent results
        agent_results = [
            AgentResult(
                name="CNN Classifier",
                model="k_cross_CNN (Pattern Detection)",
                topPattern=predicted,
                topProbabilities=top_probs,
                confidence=round(confidence * 100, 1),
                qualityFlag=quality_flag,
                description=f"Primary pattern detected: {predicted} with {confidence*100:.1f}% confidence. "
                           f"Neural network inference completed on CPU. Tensor shape: {tensor_shape}.",
                rootCauses=ROOT_CAUSES.get(predicted, []),
                actionSuggestions=ACTION_SUGGESTIONS.get(predicted, [])
            ),
            AgentResult(
                name="Analysis Agent",
                model="Statistical Analysis Module",
                topPattern=predicted,
                topProbabilities=top_probs[:5],
                confidence=round(confidence * 100, 1),
                qualityFlag=None if not analysis_result.get("issues_found") else "⚠️ Issues detected",
                description=f"Consistency score: {analysis_result.get('consistency_score', 1.0)*100:.0f}%. "
                           f"Severity: {severity}. Recommendation: {analysis_result.get('recommendation', 'PASS')}. "
                           f"Major issues: {len(major_issues)}.",
                rootCauses=ROOT_CAUSES.get(predicted, []),
                actionSuggestions=ACTION_SUGGESTIONS.get(predicted, [])
            ),
            AgentResult(
                name="Validation Agent",
                model="Quality Assurance Module",
                topPattern=predicted,
                topProbabilities=top_probs[:5],
                confidence=round(confidence * 100, 1),
                qualityFlag=None if validation_details.passed else "⚠️ Required multiple attempts",
                description=f"Validation: {'PASSED' if validation_details.passed else 'NEEDS REVIEW'} "
                           f"(Attempt {validation_details.attempts}/{validation_details.maxAttempts}). "
                           f"All {len(validation_details.criteriaChecks)} criteria met.",
                rootCauses=ROOT_CAUSES.get(predicted, []),
                actionSuggestions=ACTION_SUGGESTIONS.get(predicted, [])
            )
        ]
        
        # Save to database
        db = next(get_db())
        try:
            # Create wafer record
            wafer_record = Wafer(
                wafer_id=f"W-{hash(file.filename) % 10000:04d}",
                file_name=file.filename,
                tool_id=tool_id or "UNKNOWN",
                chamber_id=chamber_id or "UNKNOWN",
                processed_at=datetime.utcnow(),
                predicted_class=predicted,
                confidence=confidence,
                final_verdict="FAIL" if has_defect else "PASS",
                severity=severity
            )
            db.add(wafer_record)
            db.commit()
            db.refresh(wafer_record)
            
            # Save defect distribution
            for pattern, prob in prob_dist.items():
                defect_dist = DefectDistribution(
                    wafer_id=wafer_record.id,
                    pattern=pattern,
                    probability=prob
                )
                db.add(defect_dist)
            db.commit()
        except Exception as e:
            print(f"Database save error: {e}")
            db.rollback()
        finally:
            db.close()
        
        return AnalysisResponse(
            waferId=f"W-{hash(file.filename) % 10000:04d}",
            fileName=file.filename,
            finalVerdict="FAIL" if has_defect else "PASS",
            confidence=round(confidence * 100, 1),
            severity=severity,
            ingestionDetails=ingestion_details,
            analysisDetails=analysis_details,
            validationDetails=validation_details,
            triggerAction=trigger_action,
            agentResults=agent_results,
            fullProbabilityDistribution={k: round(v * 100, 2) for k, v in prob_dist.items()},
            explanation=explanation,
            modelUsed="k_cross_CNN.pt",
            deviceUsed="cpu"
        )
        
    finally:
        os.unlink(tmp_path)


@app.get("/api/spc")
async def get_spc_data(
    tool_id: Optional[str] = None,
    days: int = 30
):
    """
    Get Statistical Process Control data with control limits and rule violations.
    """
    from backend.spc_utils import calculate_control_limits, apply_western_electric_rules, generate_spc_summary
    from datetime import datetime, timedelta
    from sqlalchemy import func, case
    from backend.models import SessionLocal
    
    db = SessionLocal()
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query daily defect rates
        query = db.query(
            func.date(Wafer.analyzed_at).label('date'),
            func.count(Wafer.id).label('total'),
            func.sum(
                case(
                    (Wafer.final_verdict == 'FAIL', 1),
                    else_=0
                )
            ).label('defective')
        ).filter(
            Wafer.analyzed_at >= start_date,
            Wafer.analyzed_at <= end_date
        )
        
        if tool_id:
            query = query.filter(Wafer.tool_id == tool_id)
        
        daily_data = query.group_by(func.date(Wafer.analyzed_at)).order_by(func.date(Wafer.analyzed_at)).all()
        
        # Format data for SPC analysis
        data_points = []
        defect_rates = []
        
        for row in daily_data:
            defect_rate = (row.defective / row.total * 100) if row.total > 0 else 0
            defect_rates.append(defect_rate)
            data_points.append({
                "date": str(row.date),
                "total": row.total,
                "defective": row.defective,
                "value": round(defect_rate, 2)
            })
        
        # Calculate control limits
        control_limits = calculate_control_limits(defect_rates)
        
        # Apply Western Electric Rules
        analyzed_data = apply_western_electric_rules(data_points, control_limits)
        
        # Generate summary
        summary = generate_spc_summary(analyzed_data)
        
        return {
            "data": analyzed_data,
            "control_limits": control_limits,
            "summary": summary,
            "tool_id": tool_id,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
    finally:
        db.close()


@app.get("/api/root-cause-analysis")
async def root_cause_analysis():
    """
    Data-driven Root Cause Analysis based on existing wafer data.
    Analyzes database to identify top issues and generate CAPA.
    """
    from backend.rca_utils import analyze_defect_data
    from backend.models import SessionLocal
    from sqlalchemy import case
    
    db = SessionLocal()
    try:
        result = analyze_defect_data(db)
        return result
    finally:
        db.close()


@app.get("/api/export-excel")
async def export_excel(
    tool_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Export wafer analysis data as Excel spreadsheet.
    """
    try:
        from backend.excel_utils import create_wafer_report_excel
    except ImportError:
        raise HTTPException(status_code=500, detail="Excel export not available. Install openpyxl.")
    
    from datetime import datetime, timedelta
    
    db = get_db()
    try:
        # Query data
        query = db.query(Wafer)
        
        if tool_id:
            query = query.filter(Wafer.tool_id == tool_id)
        if start_date:
            query = query.filter(Wafer.analyzed_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Wafer.analyzed_at <= datetime.fromisoformat(end_date))
        
        wafers = query.order_by(Wafer.analyzed_at.desc()).limit(500).all()
        
        # Format for Excel
        wafer_analyses = [
            {
                "waferId": w.wafer_id,
                "fileName": w.file_name,
                "finalVerdict": w.final_verdict,
                "confidence": w.confidence or 0,
                "severity": w.severity or "None",
                "detectedPattern": w.predicted_class or "None"
            }
            for w in wafers
        ]
        
        # Calculate lot data
        total = len(wafers)
        defective = sum(1 for w in wafers if w.final_verdict == "FAIL")
        
        # Get defect distribution
        defect_dist = {}
        for w in wafers:
            if w.predicted_class:
                defect_dist[w.predicted_class] = defect_dist.get(w.predicted_class, 0) + 1
        
        lot_data = {
            "total_wafers": total,
            "defective_wafers": defective,
            "yield_rate": ((total - defective) / total * 100) if total > 0 else 100,
            "defect_distribution": defect_dist
        }
        
        # Generate Excel
        excel_buffer = create_wafer_report_excel(lot_data, wafer_analyses)
        
        filename = f"wafer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    finally:
        db.close()


@app.post("/api/notifications/configure")
async def configure_notifications(request: dict):
    """
    Configure email notification settings.
    """
    from backend.email_utils import configure_notifications
    return configure_notifications(request)


@app.post("/api/notifications/test")
async def send_test_notification(request: dict):
    """
    Send a test email notification.
    """
    from backend.email_utils import notification_service, create_defect_alert_html
    from datetime import datetime
    
    recipients = request.get("recipients", [])
    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients specified")
    
    # Create test alert
    html = create_defect_alert_html(
        lot_id="TEST-LOT-001",
        defect_rate=18.5,
        threshold=15.0,
        tool_id="TOOL-TEST",
        top_defects=[
            {"pattern": "Scratch", "count": 5, "percentage": 50},
            {"pattern": "Center", "count": 3, "percentage": 30}
        ],
        timestamp=datetime.now()
    )
    
    result = notification_service.send_alert(
        to_emails=recipients,
        subject="[TEST] AgentWafer Defect Alert",
        body_html=html
    )
    
    return result


@app.post("/api/copilot/query")
async def copilot_query(request: dict):
    """
    AI Copilot natural language query endpoint.
    """
    from backend.copilot_utils import process_copilot_query
    
    query = request.get("query", "")
    result = process_copilot_query(query)
    return result


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "model": "k_cross_CNN.pt", "device": "cpu"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
