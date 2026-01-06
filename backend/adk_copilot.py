"""
AI Copilot Agent using Google ADK (Agentic Development Kit)
Provides intelligent answers about wafer data using Gemini via ADK.
"""
from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import Counter


def get_wafer_context(db_session, limit: int = 100) -> str:
    """
    Gather database context for the copilot to analyze.
    Returns formatted string with recent wafer statistics.
    """
    from backend.models import Wafer
    from sqlalchemy import desc
    
    try:
        # Get recent wafers
        recent_wafers = db_session.query(Wafer).order_by(desc(Wafer.processed_at)).limit(limit).all()
        
        if not recent_wafers:
            return "No wafer data available in database."
        
        # Calculate statistics
        total_wafers = len(recent_wafers)
        defect_counts = Counter(w.predicted_class for w in recent_wafers)
        verdict_counts = Counter(w.final_verdict for w in recent_wafers)
        tool_defects = Counter(w.tool_id for w in recent_wafers if w.final_verdict == "FAIL")
        
        # Average confidence
        avg_confidence = sum(w.confidence for w in recent_wafers if w.confidence) / total_wafers if total_wafers > 0 else 0
        
        # Time range
        oldest = recent_wafers[-1].processed_at if recent_wafers else None
        newest = recent_wafers[0].processed_at if recent_wafers else None
        
        # Build context string
        context = f"""**Current Wafer Detection System Data** (Last {total_wafers} analyses)

**Time Range:** {oldest.strftime('%Y-%m-%d %H:%M') if oldest else 'N/A'} to {newest.strftime('%Y-%m-%d %H:%M') if newest else 'N/A'}

**Overall Statistics:**
- Total Analyzed: {total_wafers} wafers
- Pass Rate: {verdict_counts.get('PASS', 0) / total_wafers * 100:.1f}% ({verdict_counts.get('PASS', 0)} wafers)
- Fail Rate: {verdict_counts.get('FAIL', 0) / total_wafers * 100:.1f}% ({verdict_counts.get('FAIL', 0)} wafers)
- Average Confidence: {avg_confidence * 100:.1f}%

**Defect Distribution:**
"""
        for defect_type, count in defect_counts.most_common(10):
            percentage = count / total_wafers * 100
            context += f"- {defect_type}: {count} wafers ({percentage:.1f}%)\n"
        
        if tool_defects:
            context += "\n**Tool-wise Failures:**\n"
            for tool_id, count in tool_defects.most_common(5):
                context += f"- {tool_id or 'Unknown'}: {count} failures\n"
        
        # Recent failures
        failed_wafers = [w for w in recent_wafers if w.final_verdict == "FAIL"][:10]
        if failed_wafers:
            context += "\n**Recent Failures (Last 10):**\n"
            for w in failed_wafers:
                context += f"- {w.wafer_id}: {w.predicted_class} ({w.confidence*100:.1f}%) - Tool: {w.tool_id or 'N/A'}\n"
        
        return context
    except Exception as e:
        return f"Error accessing database: {str(e)}"


def answer_question(context):
    """
    Function tool that prepares context for the copilot agent.
    The agent itself will generate the intelligent response.
    """
    # Get database session if passed in context
    db_session = getattr(context, 'db_session', None)
    user_query = getattr(context, 'user_query', '')
    
    if not user_query:
        context.copilot_response = {
            "response": "Please ask a question about your wafer data.",
            "suggestions": [
                "What's the current yield rate?",
                "Which tool has the most defects?",
                "Show recent defect trends"
            ]
        }
        return context
    
    # Gather database context
    if db_session:
        db_context = get_wafer_context(db_session, limit=100)
    else:
        db_context = "No database connection available."
    
    # Store context for the agent to use
    context.database_context = db_context
    context.query = user_query
    
    # The ADK agent will process this and generate a response
    # We'll extract it in the API endpoint
    
    return context


# Create the Copilot Agent using Google ADK
copilot_agent = Agent(
    name="copilot_agent",
    model="gemini-2.0-flash-exp",  # Fast, efficient model for interactive queries
    description="AI assistant that answers questions about wafer detection data using real database statistics.",
    instruction="""
    You are an AI Copilot for a semiconductor wafer defect detection system.
    
    **Your Role:**
    - Answer questions about wafer quality, defect patterns, and tool performance
    - Analyze trends and provide insights based on actual data
    - Calculate statistics from the provided database context
    - Suggest actionable recommendations
    
    **Guidelines:**
    1. **Use the data**: Always base answers on the database context provided
    2. **Be specific**: Cite actual numbers, percentages, and statistics
    3. **Format nicely**: Use markdown with headings, bullet points, tables, and emojis (📊 🔧 ⚠️ ✅ 📈)
    4. **Be concise**: Keep responses under 300 words
    5. **Be honest**: If you don't have the data to answer, say so clearly
    
    **Input Format:**
    You'll receive:
    - USER QUESTION: {query}
    - DATABASE CONTEXT: {database_context}
    
    **Output Format:**
    Provide a helpful, markdown-formatted response that directly answers the question.
    Focus on being accurate and actionable.
    """,
    tools=[FunctionTool(answer_question)],
    output_key="copilot_output"
)


def process_copilot_query(query: str, db_session=None) -> Dict[str, Any]:
    """
    Main entry point for copilot queries.
    Analyzes query and returns specific, targeted answers.
    """
    if not query or not query.strip():
        return {
            "response": "Please ask a question about your wafer data.",
            "suggestions": [
                "What's the current yield rate?",
                "Which tool has the most defects?",
                "Show recent defect trends"
            ]
        }
    
    try:
        # Get database statistics
        from backend.models import Wafer
        from sqlalchemy import desc, func
        
        if not db_session:
            return {
                "response": "⚠️ Database connection unavailable. Please try again.",
                "suggestions": ["Retry query", "Check system status"]
            }
        
        # Get recent wafers
        recent_wafers = db_session.query(Wafer).order_by(desc(Wafer.processed_at)).limit(100).all()
        
        if not recent_wafers:
            return {
                "response": "📊 No wafer data found in the database yet. Start analyzing some wafers to see insights!",
                "suggestions": ["Upload a wafer", "Check system status"]
            }
        
        query_lower = query.lower()
        
        # Calculate common statistics
        total = len(recent_wafers)
        passed = sum(1 for w in recent_wafers if w.final_verdict == "PASS")
        failed = sum(1 for w in recent_wafers if w.final_verdict == "FAIL")
        yield_rate = (passed / total * 100) if total > 0 else 0
        
        defect_counts = Counter(w.predicted_class for w in recent_wafers)
        tool_failures = Counter(w.tool_id for w in recent_wafers if w.final_verdict == "FAIL")
        
        # YIELD QUERIES
        if 'yield' in query_lower:
            response = f"""📊 **Yield Analysis** (Last {total} wafers)

**Current Yield Rate: {yield_rate:.1f}%**
- ✅ Passed: {passed} wafers ({passed/total*100:.1f}%)
- ❌ Failed: {failed} wafers ({failed/total*100:.1f}%)

**Breakdown by Verdict:**"""
            
            if failed > 0:
                response += f"\n\n**Top Failure Reasons:**"
                for defect, count in defect_counts.most_common(3):
                    if defect != "Normal" and defect != "none":
                        pct = count / total * 100
                        response += f"\n- {defect}: {count} wafers ({pct:.1f}%)"
                
                if tool_failures:
                    worst_tool = tool_failures.most_common(1)[0]
                    response += f"\n\n**⚠️ Tool Alert:** {worst_tool[0]} has {worst_tool[1]} failures"
            else:
                response += "\n\n✅ Excellent! All wafers passed quality checks."
            
            suggestions = [
                "Which tool is causing failures?",
                "Show defect distribution",
                "Compare with last week"
            ]
        
        # TOOL QUERIES  
        elif 'tool' in query_lower:
            if tool_failures:
                response = f"""🔧 **Tool Performance Analysis** (Last {total} wafers)

**Tools Ranked by Failures:**"""
                for tool_id, count in tool_failures.most_common(5):
                    pct = count / failed * 100 if failed > 0 else 0
                    response += f"\n- **{tool_id or 'Unknown'}**: {count} failures ({pct:.1f}% of all failures)"
                
                # Find specific tool if mentioned
                for tool_id, count in tool_failures.items():
                    if str(tool_id).lower() in query_lower:
                        tool_wafers = [w for w in recent_wafers if w.tool_id == tool_id]
                        tool_defects = Counter(w.predicted_class for w in tool_wafers if w.final_verdict == "FAIL")
                        response += f"\n\n**{tool_id} Defect Pattern:**"
                        for defect, dcount in tool_defects.most_common(3):
                            response += f"\n- {defect}: {dcount} wafers"
                        break
                
                suggestions = [
                    f"What's wrong with {tool_failures.most_common(1)[0][0]}?",
                    "Show all tool statistics",
                    "Recommend maintenance actions"
                ]
            else:
                response = f"""🔧 **Tool Performance Analysis**

✅ All tools performing well! No failures detected in the last {total} wafers."""
                suggestions = ["Show yield rate", "Defect trends", "Quality metrics"]
        
        # DEFECT QUERIES
        elif 'defect' in query_lower or 'scratch' in query_lower or 'edge' in query_lower:
            response = f"""🔍 **Defect Pattern Analysis** (Last {total} wafers)

**Defect Distribution:**"""
            for defect, count in defect_counts.most_common(10):
                pct = count / total * 100
                emoji = "❌" if defect not in ["Normal", "none"] else "✅"
                response += f"\n{emoji} **{defect}**: {count} wafers ({pct:.1f}%)"
            
            # Check for specific defect types in query
            specific_defect = None
            for defect_name in ["scratch", "edge", "center", "donut", "random"]:
                if defect_name in query_lower:
                    # Find matching defect in data
                    for defect, count in defect_counts.items():
                        if defect_name in defect.lower():
                            specific_defect = (defect, count)
                            break
                    break
            
            if specific_defect:
                defect_name, defect_count = specific_defect
                response += f"\n\n**Focus: {defect_name} Defects**"
                response += f"\n- Occurrences: {defect_count} wafers"
                response += f"\n- Percentage: {defect_count/total*100:.1f}% of total"
                
                # Find tools with this defect
                tools_with_defect = [w.tool_id for w in recent_wafers if w.predicted_class == defect_name and w.tool_id]
                if tools_with_defect:
                    tool_count = Counter(tools_with_defect)
                    response += f"\n- Most affected tool: {tool_count.most_common(1)[0][0]}"
            
            suggestions = [
                "Which tool has most defects?",
                "Show trend over time",
                "Root cause analysis"
            ]
        
        # TREND/TIME QUERIES
        elif 'trend' in query_lower or 'recent' in query_lower or 'history' in query_lower:
            # Get time range
            oldest = recent_wafers[-1].processed_at
            newest = recent_wafers[0].processed_at
            
            response = f"""📈 **Trend Analysis** (Last {total} wafers)

**Time Range:** {oldest.strftime('%Y-%m-%d %H:%M')} to {newest.strftime('%Y-%m-%d %H:%M')}

**Recent Activity:**
- Total Analyzed: {total} wafers
- Yield Rate: {yield_rate:.1f}%
- Most Common Defect: {defect_counts.most_common(1)[0][0]} ({defect_counts.most_common(1)[0][1]} wafers)

**Quality Trend:**"""
            
            # Simple trend indication
            if yield_rate >= 90:
                response += "\n✅ **Excellent** - Yield above 90%"
            elif yield_rate >= 75:
                response += "\n⚠️ **Good** - Yield 75-90%, room for improvement"
            else:
                response += "\n❌ **Concerning** - Yield below 75%, action needed"
            
            suggestions = [
                "What's causing low yield?",
                "Compare tools",
                "Show defect patterns"
            ]
        
        # GENERAL/OTHER QUERIES
        else:
            avg_confidence = sum(w.confidence for w in recent_wafers if w.confidence) / total if total > 0 else 0
            
            response = f"""🤖 **Wafer Detection System Status**

**Overview (Last {total} analyses):**
- 📊 Yield Rate: {yield_rate:.1f}%
- ✅ Passed: {passed} wafers
- ❌ Failed: {failed} wafers
- 🎯 Avg Confidence: {avg_confidence*100:.1f}%

**Top Defect Types:**"""
            for defect, count in defect_counts.most_common(3):
                response += f"\n- {defect}: {count} wafers"
            
            if tool_failures:
                response += f"\n\n**Tools Needing Attention:**"
                for tool, count in tool_failures.most_common(2):
                    response += f"\n- {tool}: {count} failures"
            
            response += "\n\n💡 Ask me specific questions about yield, tools, defects, or trends!"
            
            suggestions = [
                "What's the yield rate?",
                "Which tool has issues?",
                "Show defect patterns"
            ]
        
        return {
            "response": response,
            "suggestions": suggestions,
            "data_sources": [f"Last {total} wafer analyses"],
            "powered_by": "Wafer Analytics Engine"
        }
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Copilot error: {error_details}")
        
        return {
            "response": f"""⚠️ **Error Processing Query**

An error occurred: {str(e)}

Please try asking about:
- Yield rates
- Tool performance  
- Defect patterns""",
            "suggestions": [
                "Show system status",
                "Recent statistics",
                "Tool rankings"
            ],
            "error": str(e)
        }
