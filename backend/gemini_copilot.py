"""
Gemini-powered AI Copilot for Wafer Detection System
Uses Google's Gemini API to provide intelligent answers about wafer data.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
from collections import Counter

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("⚠️ google-generativeai not installed. Install with: pip install google-generativeai")


class GeminiCopilot:
    """AI Copilot powered by Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client using Google ADK's API key configuration"""
        # Google ADK automatically handles API key from:
        # 1. GOOGLE_API_KEY environment variable
        # 2. ADK credentials file
        # 3. Google Cloud credentials
        # We'll use the same approach
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        if not HAS_GEMINI:
            self.model = None
            print("⚠️ google-generativeai not installed")
            return
            
        # Try to configure Gemini
        # If no API key is explicitly set, it might still work via ADK credentials
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
            # else: genai might use default credentials from ADK/Google Cloud
            
            self.model = genai.GenerativeModel(self.model_name)
            print(f"✅ Gemini copilot initialized with {self.model_name}")
        except Exception as e:
            print(f"⚠️ Gemini initialization: {e}")
            print("   Copilot will use fallback responses")
            self.model = None
    
    def get_database_context(self, db_session, limit: int = 100) -> str:
        """
        Gather context from database for Gemini to analyze.
        Returns formatted string with recent wafer data and statistics.
        """
        from backend.models import Wafer
        from sqlalchemy import func, desc
        
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
            context = f"""WAFER DETECTION SYSTEM DATA (Last {total_wafers} wafers)

TIME RANGE:
- From: {oldest.strftime('%Y-%m-%d %H:%M') if oldest else 'N/A'}
- To: {newest.strftime('%Y-%m-%d %H:%M') if newest else 'N/A'}

OVERALL STATISTICS:
- Total Wafers Analyzed: {total_wafers}
- Pass Rate: {verdict_counts.get('PASS', 0) / total_wafers * 100:.1f}% ({verdict_counts.get('PASS', 0)} wafers)
- Fail Rate: {verdict_counts.get('FAIL', 0) / total_wafers * 100:.1f}% ({verdict_counts.get('FAIL', 0)} wafers)
- Average Confidence: {avg_confidence * 100:.1f}%

DEFECT TYPE DISTRIBUTION:
"""
            for defect_type, count in defect_counts.most_common(10):
                percentage = count / total_wafers * 100
                context += f"- {defect_type}: {count} wafers ({percentage:.1f}%)\n"
            
            if tool_defects:
                context += "\nTOOL-WISE DEFECT COUNT (Failed Wafers):\n"
                for tool_id, count in tool_defects.most_common(5):
                    context += f"- {tool_id or 'Unknown'}: {count} defects\n"
            
            # Recent defects detail (last 10)
            context += "\nRECENT DEFECTS (Last 10 Failed Wafers):\n"
            failed_wafers = [w for w in recent_wafers if w.final_verdict == "FAIL"][:10]
            for w in failed_wafers:
                context += f"- {w.wafer_id}: {w.predicted_class} ({w.confidence*100:.1f}% confidence) - Tool: {w.tool_id or 'N/A'}\n"
            
            return context
            
        except Exception as e:
            print(f"Error gathering database context: {e}")
            return f"Error accessing database: {str(e)}"
    
    def create_prompt(self, user_query: str, db_context: str) -> str:
        """Create the full prompt for Gemini"""
        system_instruction = """You are an AI assistant for a semiconductor wafer defect detection system. You help fab engineers and quality control teams analyze wafer inspection data.

Your capabilities:
- Analyze defect patterns and trends
- Identify tool performance issues  
- Suggest root causes for quality problems
- Provide actionable recommendations
- Calculate statistics from provided data

Guidelines:
- Be specific and cite actual numbers from the data
- Format responses in markdown with clear headings, bullet points, and tables
- Use relevant emojis (📊 🔧 ⚠️ ✅ 📈 📉) for visual clarity
- If asked about data you don't have, say so clearly
- Provide 3 relevant follow-up questions as suggestions
- Keep responses concise but informative (max 300 words)"""

        full_prompt = f"""{system_instruction}

DATABASE CONTEXT:
{db_context}

USER QUESTION: {user_query}

Provide a helpful, accurate response based on the available data."""

        return full_prompt
    
    def query(self, user_query: str, db_session=None) -> Dict[str, Any]:
        """
        Main query method - gets context and queries Gemini.
        Returns structured response with answer and suggestions.
        """
        if not self.model or not HAS_GEMINI:
            return self._fallback_response(user_query)
        
        try:
            # Get database context
            db_context = "No database session provided." if not db_session else self.get_database_context(db_session)
            
            # Create prompt
            prompt = self.create_prompt(user_query, db_context)
            
            # Query Gemini
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return self._fallback_response(user_query)
            
            # Parse response
            answer_text = response.text.strip()
            
            # Generate follow-up suggestions using Gemini
            suggestions = self._generate_suggestions(user_query, answer_text)
            
            return {
                "response": answer_text,
                "suggestions": suggestions,
                "data_sources": [f"Last {db_context.count('wafer')} wafers from database"],
                "powered_by": f"Google {self.model_name}"
            }
            
        except Exception as e:
            print(f"Gemini query error: {e}")
            return {
                "response": f"⚠️ **Error querying AI**\n\nI encountered an error: {str(e)}\n\nPlease try rephrasing your question or check the system logs.",
                "suggestions": [
                    "Show current yield rate",
                    "Which tool has most defects?",
                    "Recent defect trends"
                ],
                "error": str(e)
            }
    
    def _generate_suggestions(self, original_query: str, answer: str) -> List[str]:
        """Generate 3 relevant follow-up questions based on the conversation"""
        try:
            suggestion_prompt = f"""Based on this Q&A, suggest 3 brief follow-up questions a fab engineer might ask.
Make them specific and actionable. Return ONLY the 3 questions, one per line, no numbering.

Original Question: {original_query}
Answer Given: {answer[:200]}..."""

            response = self.model.generate_content(suggestion_prompt)
            suggestions = [s.strip() for s in response.text.strip().split('\n') if s.strip()][:3]
            
            # Fallback if parsing fails
            if len(suggestions) < 3:
                return [
                    "Show detailed breakdown",
                    "What's the root cause?",
                    "Recommend action items"
                ]
            
            return suggestions
            
        except:
            return [
                "Show more details",
                "Analyze the trend",
                "What should we do?"
            ]
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Fallback response when Gemini is unavailable"""
        return {
            "response": f"""🤖 **AI Copilot (Limited Mode)**

I received your question: "{query}"

⚠️ Full AI features are currently unavailable (Gemini API not configured).

I can still help you navigate the system! Try:
- **Dashboard**: View recent wafer analyses
- **Analytics**: See defect distribution charts  
- **SPC Charts**: Monitor process control
- **Scan History**: Review past results

To enable full AI capabilities, configure the GEMINI_API_KEY environment variable.""",
            "suggestions": [
                "Go to Dashboard",
                "View Analytics",
                "Check SPC Charts"
            ]
        }


# Global copilot instance
_copilot_instance = None

def get_copilot() -> GeminiCopilot:
    """Get or create the global copilot instance"""
    global _copilot_instance
    if _copilot_instance is None:
        _copilot_instance = GeminiCopilot()
    return _copilot_instance


def process_copilot_query(query: str, db_session=None) -> Dict[str, Any]:
    """
    Main entry point for copilot queries.
    Used by API endpoint.
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
    
    copilot = get_copilot()
    return copilot.query(query, db_session)
