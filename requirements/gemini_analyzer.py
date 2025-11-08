"""
Gemini AI Analyzer Module
Handles sentiment analysis and behavioral report generation using Gemini 2.0 API
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiAnalyzer:
    """Analyzes child behavior data using Gemini AI for sentiment and reporting."""
    
    def __init__(self):
        """Initialize Gemini API with credentials from environment."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self.model = genai.GenerativeModel(self.model_name)
    
    def calculate_sentiment_score(self, keywords: List[Dict]) -> float:
        """
        Calculate sentiment score from keywords using Gemini AI.
        Returns: float between -1 (risky) and +1 (healthy)
        """
        if not keywords:
            return 0.0
        
        keyword_list = [k.get('keyword', '') for k in keywords[:50]]  # Limit to 50 for API
        
        prompt = f"""
Analyze these search keywords from a child's browsing history and provide a sentiment score.
Score Range: -1.0 (very risky/concerning) to +1.0 (very healthy/positive)

Keywords: {', '.join(keyword_list)}

Return ONLY a JSON object with this exact structure:
{{
  "sentimentScore": 0.0,
  "reasoning": "Brief explanation of the score"
}}

Consider:
- Educational content = positive
- Age-appropriate entertainment = neutral to positive
- Violence, adult content, harmful behavior = negative
- Balanced curiosity = positive
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            score = float(result.get('sentimentScore', 0.0))
            return max(-1.0, min(1.0, score))  # Clamp between -1 and 1
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 0.0
    
    def categorize_keywords(self, keywords: List[Dict]) -> Dict[str, List[str]]:
        """
        Categorize keywords into positive, risky, and neutral using Gemini.
        """
        if not keywords:
            return {"positive": [], "risky": [], "neutral": []}
        
        keyword_list = [k.get('keyword', '') for k in keywords[:50]]
        
        prompt = f"""
Categorize these keywords from a child's search history into three categories:
- positive: Educational, creative, age-appropriate, constructive
- risky: Potentially harmful, inappropriate, concerning
- neutral: General entertainment, normal curiosity

Keywords: {', '.join(keyword_list)}

Return ONLY a JSON object:
{{
  "positive": ["keyword1", "keyword2"],
  "risky": ["keyword3"],
  "neutral": ["keyword4", "keyword5"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            print(f"Keyword categorization error: {e}")
            return {"positive": [], "risky": [], "neutral": keyword_list}
    
    def generate_behavioral_report(self, intelligence_data: Dict) -> Dict[str, Any]:
        """
        Generate comprehensive behavioral report using Gemini AI.
        Returns structured report data for PDF generation.
        """
        behavioral = intelligence_data.get('behavioralData', {})
        
        # Prepare summary for Gemini
        summary = {
            "totalApps": len(behavioral.get('mostUsedApps', [])),
            "totalKeywords": len(behavioral.get('searchedKeywords', [])),
            "blockedAttempts": len(behavioral.get('blockedNSFWAttempts', [])),
            "topApps": [app['appName'] for app in behavioral.get('mostUsedApps', [])[:5]],
            "recentKeywords": [kw['keyword'] for kw in behavioral.get('searchedKeywords', [])[:10]],
            "screenTimeWeekly": behavioral.get('screenTimeData', {}).get('weeklyAverage', 0),
            "emotionalTone": behavioral.get('emotionalTone', {}).get('overallSentiment', 0)
        }
        
        prompt = f"""
You are a child psychologist and digital wellness expert creating a professional parental control report.

CHILD'S DIGITAL ACTIVITY DATA:
{json.dumps(summary, indent=2)}

Generate a comprehensive, privacy-safe report suitable for parents and school counselors.

Return ONLY a JSON object with this structure:
{{
  "executiveSummary": "2-3 sentence overview of the child's digital behavior",
  "keyFindings": [
    "Finding 1: Clear, specific observation",
    "Finding 2: Another important pattern",
    "Finding 3: Behavioral trend"
  ],
  "emotionalTrends": {{
    "interpretation": "Detailed analysis of emotional patterns",
    "trendDirection": "improving|stable|concerning"
  }},
  "positiveHabits": [
    "Specific positive behavior 1",
    "Specific positive behavior 2"
  ],
  "possibleConcerns": [
    "Concern 1 with context",
    "Concern 2 with context"
  ],
  "guidanceForParents": "Warm, actionable guidance paragraph for parents with 3-4 specific suggestions",
  "screenTimePolicy": {{
    "recommendedDailyLimit": 120,
    "weekendLimit": 180,
    "suggestedBedtime": "21:30",
    "reasoning": "Why these limits are suggested"
  }},
  "conversationStarters": [
    "Gentle question or topic to discuss with child",
    "Another positive conversation starter"
  ]
}}

IMPORTANT:
- Use professional, neutral tone
- No raw conversations or identifiable data
- Focus on patterns, not individual incidents
- Be constructive and supportive
- Emphasize collaboration over surveillance
"""
        
        try:
            response = self.model.generate_content(prompt)
            report = json.loads(response.text.strip())
            
            # Add metadata
            report['generatedAt'] = datetime.now().isoformat()
            report['reportId'] = f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            report['emotionalTrends']['sentimentScore'] = summary['emotionalTone']
            
            return report
        except Exception as e:
            print(f"Report generation error: {e}")
            return self._generate_fallback_report(summary)
    
    def _generate_fallback_report(self, summary: Dict) -> Dict:
        """Generate a basic report if Gemini API fails."""
        return {
            "generatedAt": datetime.now().isoformat(),
            "reportId": f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "executiveSummary": f"Digital activity report based on {summary['totalKeywords']} searches and {summary['totalApps']} applications used.",
            "keyFindings": [
                f"Most used applications: {', '.join(summary['topApps'][:3])}",
                f"Average weekly screen time: {summary['screenTimeWeekly']} minutes",
                f"Blocked attempts: {summary['blockedAttempts']}"
            ],
            "emotionalTrends": {
                "sentimentScore": summary['emotionalTone'],
                "interpretation": "Monitoring data collected successfully.",
                "trendDirection": "stable"
            },
            "positiveHabits": ["Regular usage patterns", "Respecting time limits"],
            "possibleConcerns": ["Continue monitoring for changes"],
            "guidanceForParents": "Continue open communication with your child about their digital activities. Review usage patterns regularly and adjust limits as needed.",
            "screenTimePolicy": {
                "recommendedDailyLimit": 120,
                "weekendLimit": 180,
                "suggestedBedtime": "21:30",
                "reasoning": "Standard recommendations for healthy digital habits"
            },
            "conversationStarters": [
                "What did you learn online this week?",
                "Is there anything interesting you'd like to share?"
            ]
        }
    
    def analyze_app_usage(self, apps: List[Dict]) -> Dict:
        """Analyze app usage patterns and provide insights."""
        if not apps:
            return {"category": "No data", "recommendation": "Begin monitoring"}
        
        app_names = [app['appName'] for app in apps[:10]]
        
        prompt = f"""
Analyze these app usage patterns for a child:
{', '.join(app_names)}

Return ONLY a JSON object:
{{
  "category": "educational|entertainment|social|mixed",
  "recommendation": "Brief advice for parents",
  "concerns": ["any concerns or empty array"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"App analysis error: {e}")
            return {
                "category": "mixed",
                "recommendation": "Continue monitoring app usage patterns.",
                "concerns": []
            }
