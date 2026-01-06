"""Add /api/history endpoint to server.py"""

endpoint_code = '''

@app.get("/api/history")
async def get_history(
    limit: int = 50,
    tool_id: Optional[str] = None,
    chamber_id: Optional[str] = None
):
    """
    Get analysis history with optional filtering.
    """
    db = next(get_db())
    try:
        query = db.query(Wafer).order_by(Wafer.processed_at.desc())
        
        if tool_id:
            query = query.filter(Wafer.tool_id == tool_id)
        if chamber_id:
            query = query.filter(Wafer.chamber_id == chamber_id)
        
        wafers = query.limit(limit).all()
        
        return {
            "total": len(wafers),
            "records": [
                {
                    "id": w.id,
                    "waferId": w.wafer_id,
                    "fileName": w.file_name,
                    "toolId": w.tool_id,
                    "chamberId": w.chamber_id,
                    "processedAt": w.processed_at.isoformat() if w.processed_at else None,
                    "predictedClass": w.predicted_class,
                    "confidence": w.confidence,
                    "finalVerdict": w.final_verdict,
                    "severity": w.severity
                }
                for w in wafers
            ]
        }
    except Exception as e:
        print(f"❌ History query error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
'''

print("Add this code to server.py after line 860 (before @app.get('/api/spc')):")
print(endpoint_code)
