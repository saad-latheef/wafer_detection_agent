"""
AI Copilot utilities for natural language queries about wafer data.
Uses pattern matching and data aggregation to answer fab-related questions.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re


# Query patterns and their handlers
QUERY_PATTERNS = {
    r"yield.*drop|drop.*yield|why.*yield": "yield_analysis",
    r"highest.*defect|defect.*rate|worst.*tool": "tool_ranking",
    r"scratch|center|donut|edge|random|loc": "defect_type_query",
    r"trend|over time|history": "trend_query",
    r"compare|versus|vs|between": "comparison_query",
    r"shift|day|night": "shift_analysis",
    r"tool.*\d+|TOOL-\d+": "specific_tool",
    r"last.*week|yesterday|today|recent": "time_based_query",
}


def analyze_query(query: str) -> Dict[str, Any]:
    """
    Analyze the natural language query and determine the intent.
    """
    query_lower = query.lower()
    
    for pattern, intent in QUERY_PATTERNS.items():
        if re.search(pattern, query_lower, re.IGNORECASE):
            return {"intent": intent, "query": query}
    
    return {"intent": "general", "query": query}


def generate_response(query: str, db_session=None) -> Dict[str, Any]:
    """
    Generate a response to a natural language query about wafer data.
    
    For hackathon demo, uses mock data. In production, would query actual database.
    """
    analysis = analyze_query(query)
    intent = analysis["intent"]
    
    # Mock responses for demo
    responses = {
        "yield_analysis": {
            "response": """📊 **Yield Drop Analysis**

Based on recent data, I identified a yield drop of approximately 5.2% on Tuesday, December 19th.

**Root Cause Analysis:**
1. **Primary Factor**: TOOL-3 showed 23% higher defect rate during night shift
2. **Defect Pattern**: 68% of failures were "Scratch" type defects
3. **Correlation**: PM was performed on TOOL-3 the previous day - possible calibration issue

**Recommended Actions:**
- Review TOOL-3 PM checklist completion
- Verify chuck vacuum levels on TOOL-3
- Run calibration wafer before next production lot""",
            "suggestions": [
                "Show TOOL-3 defect history",
                "Compare day vs night shift yields",
                "What's the current yield rate?"
            ]
        },
        "tool_ranking": {
            "response": """🔧 **Tool Defect Rate Ranking**

Here are the tools ranked by defect rate (last 30 days):

| Tool | Defect Rate | Total Wafers | Top Defect |
|------|-------------|--------------|------------|
| TOOL-3 | 18.5% | 234 | Scratch |
| TOOL-5 | 14.2% | 189 | Edge-Ring |
| TOOL-1 | 12.8% | 312 | Center |
| TOOL-2 | 8.4% | 287 | Random |
| TOOL-4 | 6.2% | 256 | None |

**Insight**: TOOL-3 has consistently higher defect rates. Consider prioritizing maintenance.""",
            "suggestions": [
                "Why is TOOL-3 defect rate high?",
                "Show TOOL-3 maintenance history",
                "Compare TOOL-3 vs TOOL-4"
            ]
        },
        "defect_type_query": {
            "response": """🔍 **Defect Pattern Analysis**

I found the following distribution for the defect type you mentioned:

**Scratch Defects (Last 7 Days):**
- Total occurrences: 47
- Affected tools: TOOL-3 (62%), TOOL-5 (23%), Others (15%)
- Peak occurrence: Night shift (65% of cases)
- Trend: ↗️ Increasing (+12% vs previous week)

**Common Root Causes for Scratch:**
1. Wafer handling during transport
2. Chuck surface degradation
3. Robot arm misalignment

Would you like me to run a root cause analysis?""",
            "suggestions": [
                "Run 5-Why analysis for scratches",
                "Show scratch trend over time",
                "Which lot has most scratches?"
            ]
        },
        "trend_query": {
            "response": """📈 **Trend Analysis**

Here's the yield trend for the past 30 days:

- **Average Yield**: 87.3%
- **Best Day**: Dec 15 (94.2%)
- **Worst Day**: Dec 19 (82.1%)
- **Trend Direction**: ↘️ Slight decline (-2.1% vs previous month)

**Key Observations:**
1. Weekend yields are consistently higher (fewer handling operations)
2. Night shift yields are 3.2% lower on average
3. TOOL-3 issues are the primary yield detractor

View the SPC charts for detailed control limit analysis.""",
            "suggestions": [
                "Show SPC control chart",
                "What's causing the decline?",
                "Compare this month vs last"
            ]
        },
        "shift_analysis": {
            "response": """🌙 **Shift Comparison Analysis**

**Day Shift (6AM - 6PM):**
- Average Yield: 89.1%
- Wafers Processed: 1,247
- Top Defect: Center (32%)

**Night Shift (6PM - 6AM):**
- Average Yield: 85.9%
- Wafers Processed: 1,089
- Top Defect: Scratch (45%)

**Key Difference**: Night shift shows 3.2% lower yield, primarily due to higher scratch defect rates. This correlates with reduced supervision and potential handling issues during shift handoffs.""",
            "suggestions": [
                "Why more scratches at night?",
                "Show operator performance",
                "Recommend actions"
            ]
        },
        "general": {
            "response": f"""🤖 I understood your question: "{query}"

I can help you with:
- **Yield Analysis**: "Why did yield drop last week?"
- **Tool Performance**: "Which tool has the highest defect rate?"
- **Defect Patterns**: "Show me scratch defects from TOOL-3"
- **Trends**: "What's the trend for edge-ring defects?"
- **Comparisons**: "Compare day vs night shift yields"

Try asking a more specific question about your fab data!""",
            "suggestions": [
                "Show tool rankings",
                "What's the current yield?",
                "Any SPC violations?"
            ]
        }
    }
    
    result = responses.get(intent, responses["general"])
    return result


def process_copilot_query(query: str) -> Dict[str, Any]:
    """
    Main entry point for processing copilot queries.
    """
    if not query or not query.strip():
        return {
            "response": "Please ask a question about your wafer data.",
            "suggestions": ["Show current yield", "Tool rankings", "Recent defects"]
        }
    
    return generate_response(query)
