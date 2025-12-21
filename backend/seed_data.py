"""
Seed database with dummy wafer analysis data for testing analytics dashboard.
This creates realistic historical data spanning 30 days.
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import get_db, Wafer, DefectDistribution

# Configuration
NUM_DAYS = 30
WAFERS_PER_DAY_RANGE = (10, 25)
TOOLS = ["TOOL-1", "TOOL-2", "TOOL-3", "TOOL-4", "TOOL-5", "UNKNOWN"]
CHAMBERS = ["CH-A", "CH-B", "CH-C", "CH-D"]
DEFECT_PATTERNS = ["Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc", "Random", "Scratch", "Near-full", "None"]
SEVERITIES = ["High", "Medium", "Low", "None"]

def generate_dummy_data():
    """Generate and insert dummy wafer data into database."""
    db = next(get_db())
    
    try:
        # Generate data for past 30 days
        end_date = datetime.utcnow()
        
        wafer_count = 0
        
        for day_offset in range(NUM_DAYS):
            current_date = end_date - timedelta(days=day_offset)
            wafers_today = random.randint(*WAFERS_PER_DAY_RANGE)
            
            # Introduce yield degradation trend for TOOL-3
            tool3_defect_rate = 0.1 + (day_offset * 0.02)  # Gets worse over time
            
            for i in range(wafers_today):
                tool = random.choice(TOOLS)
                
                # Simulate tool-specific defect rates
                if tool == "TOOL-3":
                    # TOOL-3 is problematic and getting worse
                    has_defect = random.random() < tool3_defect_rate
                elif tool == "TOOL-1":
                    # TOOL-1 is very reliable
                    has_defect = random.random() < 0.05
                elif tool == "UNKNOWN":
                    # Unknown tools have moderate defect rate
                    has_defect = random.random() < 0.15
                else:
                    # Other tools normal
                    has_defect = random.random() < 0.20
                
                # Select defect pattern
                if has_defect:
                    # Different tools have different typical defects
                    if tool == "TOOL-3":
                        predicted_class = random.choice(["Loc", "Edge-Ring", "Random"])
                    elif tool == "TOOL-2":
                        predicted_class = random.choice(["Scratch", "Edge-Loc"])
                    else:
                        predicted_class = random.choice(DEFECT_PATTERNS[:-1])  # Exclude "None"
                    
                    severity = random.choice(["High", "Medium", "Low"])
                    confidence = random.uniform(0.6, 0.95)
                else:
                    predicted_class = "None"
                    severity = "None"
                    confidence = random.uniform(0.85, 0.99)
                
                # Create wafer record
                wafer = Wafer(
                    wafer_id=f"W-DUMMY-{day_offset:02d}-{i:03d}",
                    file_name=f"dummy_wafer_{day_offset}_{i}.npy",
                    tool_id=tool,
                    chamber_id=random.choice(CHAMBERS),
                    processed_at=current_date - timedelta(hours=random.randint(0, 23)),
                    analyzed_at=current_date,
                    predicted_class=predicted_class,
                    confidence=confidence,
                    final_verdict="FAIL" if has_defect else "PASS",
                    severity=severity
                )
                db.add(wafer)
                db.flush()  # Get the wafer ID
                
                # Create defect distribution (probabilities for all patterns)
                remaining_prob = 1.0 - confidence
                for pattern in DEFECT_PATTERNS:
                    if pattern == predicted_class:
                        prob = confidence
                    else:
                        # Distribute remaining probability
                        prob = random.uniform(0, remaining_prob / (len(DEFECT_PATTERNS) - 1))
                    
                    defect_dist = DefectDistribution(
                        wafer_id=wafer.id,
                        pattern=pattern,
                        probability=prob
                    )
                    db.add(defect_dist)
                
                wafer_count += 1
        
        db.commit()
        print(f"✅ Successfully created {wafer_count} dummy wafer records!")
        print(f"📊 Data spans {NUM_DAYS} days with varied tools and defect patterns")
        print(f"🔧 TOOL-3 shows degrading performance trend")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding database with dummy data...")
    generate_dummy_data()
    print("✅ Database seeding complete!")
