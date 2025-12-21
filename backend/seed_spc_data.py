"""
Seed script to populate the database with 30+ days of realistic wafer analysis data
for SPC Charts demonstration.
"""
import random
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import init_db, SessionLocal, Lot, Wafer, DefectDistribution

# Defect patterns and their base probabilities
DEFECT_PATTERNS = ["Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc", "Random", "Scratch", "Near-full", "None"]
TOOLS = ["TOOL-1", "TOOL-2", "TOOL-3", "TOOL-4", "TOOL-5"]
CHAMBERS = ["A", "B", "C"]

def seed_database():
    """Populate database with 30 days of realistic wafer data"""
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(DefectDistribution).delete()
        db.query(Wafer).delete()
        db.query(Lot).delete()
        db.commit()
        print("Cleared existing data...")
        
        # Generate 30 days of data
        start_date = datetime.now() - timedelta(days=30)
        wafer_count = 0
        lot_count = 0
        
        for day_offset in range(30):
            current_date = start_date + timedelta(days=day_offset)
            
            # Create 2-4 lots per day
            lots_per_day = random.randint(2, 4)
            
            for lot_num in range(lots_per_day):
                lot_count += 1
                lot_id = f"LOT-{current_date.strftime('%Y%m%d')}-{lot_num + 1:02d}"
                
                # Random number of wafers per lot (15-30)
                wafers_in_lot = random.randint(15, 30)
                
                # Assign primary tool for this lot
                primary_tool = random.choice(TOOLS)
                
                # Simulate varying defect rates
                # TOOL-3 has higher defect rate (for demo purposes)
                if primary_tool == "TOOL-3":
                    base_defect_rate = 0.18 + random.uniform(-0.05, 0.05)
                elif primary_tool == "TOOL-5":
                    base_defect_rate = 0.14 + random.uniform(-0.04, 0.04)
                else:
                    base_defect_rate = 0.08 + random.uniform(-0.03, 0.03)
                
                # Add some temporal variation (simulate an "incident" mid-month)
                if 12 <= day_offset <= 15:
                    base_defect_rate += 0.05  # SPC should detect this spike
                
                defective_count = 0
                
                # Create wafers for this lot
                for wafer_num in range(wafers_in_lot):
                    wafer_count += 1
                    wafer_id = f"W-{current_date.strftime('%Y%m%d')}-{lot_num + 1:02d}-{wafer_num + 1:03d}"
                    
                    # Determine if this wafer is defective
                    is_defective = random.random() < base_defect_rate
                    
                    if is_defective:
                        defective_count += 1
                        # Choose defect pattern (weighted)
                        if primary_tool == "TOOL-3":
                            # TOOL-3 tends to produce scratches
                            pattern = random.choices(
                                DEFECT_PATTERNS[:-1],  # Exclude "None"
                                weights=[0.1, 0.05, 0.1, 0.15, 0.1, 0.1, 0.35, 0.05]
                            )[0]
                        else:
                            pattern = random.choice(DEFECT_PATTERNS[:-1])
                        verdict = "FAIL"
                        confidence = random.uniform(75, 98)
                        severity = random.choice(["Low", "Medium", "High"])
                    else:
                        pattern = "None"
                        verdict = "PASS"
                        confidence = random.uniform(90, 99.5)
                        severity = "None"
                    
                    # Create wafer record (without lot_id FK for now)
                    wafer = Wafer(
                        wafer_id=wafer_id,
                        file_name=f"{wafer_id}.npy",
                        tool_id=primary_tool,
                        chamber_id=random.choice(CHAMBERS),
                        processed_at=current_date + timedelta(hours=random.randint(0, 23)),
                        analyzed_at=current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                        predicted_class=pattern,
                        confidence=round(confidence, 2),
                        final_verdict=verdict,
                        severity=severity
                    )
                    db.add(wafer)
                
                # Create lot record
                yield_rate = ((wafers_in_lot - defective_count) / wafers_in_lot) * 100
                lot = Lot(
                    lot_id=lot_id,
                    created_at=current_date,
                    total_wafers=wafers_in_lot,
                    defective_wafers=defective_count,
                    yield_rate=round(yield_rate, 2)
                )
                db.add(lot)
        
        db.commit()
        
        print(f"✅ Seeded {lot_count} lots and {wafer_count} wafers across 30 days")
        print(f"   Date range: {start_date.date()} to {datetime.now().date()}")
        
        # Print summary by tool
        print("\n📊 Summary by Tool:")
        for tool in TOOLS:
            total = db.query(Wafer).filter(Wafer.tool_id == tool).count()
            fails = db.query(Wafer).filter(Wafer.tool_id == tool, Wafer.final_verdict == "FAIL").count()
            rate = (fails / total * 100) if total > 0 else 0
            print(f"   {tool}: {total} wafers, {fails} defective ({rate:.1f}% defect rate)")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding database with SPC demo data...")
    seed_database()
    print("\n✨ Done! SPC Charts should now show real data.")
