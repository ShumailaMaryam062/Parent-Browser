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
        Returns: float between 0 (very risky) and 100 (very healthy)
        """
        if not keywords:
            return 50.0  # Neutral score
        
        keyword_list = [k.get('keyword', '') for k in keywords[:50]]  # Limit to 50 for API
        
        prompt = f"""
Analyze these search keywords from a child's browsing history and provide a wellness score.
Score Range: 0 (very risky/concerning) to 100 (very healthy/positive)

Keywords: {', '.join(keyword_list)}

Return ONLY a JSON object with this exact structure:
{{
  "wellnessScore": 50.0,
  "reasoning": "Brief explanation of the score",
  "riskLevel": "low|medium|high"
}}

Scoring Guidelines:
- 80-100: Excellent - Educational, creative, age-appropriate content
- 60-79: Good - Balanced usage with mostly positive content
- 40-59: Moderate - Mixed content, needs some guidance
- 20-39: Concerning - Significant risky or inappropriate content
- 0-19: Critical - Immediate attention required

Consider:
- Educational/creative content = high score (80-100)
- Age-appropriate entertainment = good score (60-79)
- Excessive gaming/social media = moderate score (40-59)
- Violence, mature content = concerning score (20-39)
- NSFW, harmful behavior = critical score (0-19)
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            score = float(result.get('wellnessScore', 50.0))
            return max(0.0, min(100.0, score))  # Clamp between 0 and 100
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 50.0  # Neutral fallback
    
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
        
        # Prepare detailed summary for Gemini
        summary = {
            "totalApps": len(behavioral.get('mostUsedApps', [])),
            "totalKeywords": len(behavioral.get('searchedKeywords', [])),
            "blockedAttempts": len(behavioral.get('blockedNSFWAttempts', [])),
            "topApps": [app['appName'] for app in behavioral.get('mostUsedApps', [])[:5]],
            "recentKeywords": [kw['keyword'] for kw in behavioral.get('searchedKeywords', [])[:15]],
            "screenTimeWeekly": behavioral.get('screenTimeData', {}).get('weeklyAverage', 0),
            "emotionalTone": behavioral.get('emotionalTone', {}).get('overallSentiment', 50),
            "trendingPositive": behavioral.get('emotionalTone', {}).get('trendingPositive', []),
            "trendingRisky": behavioral.get('emotionalTone', {}).get('trendingRisky', [])
        }
        
        prompt = f"""
You are Dr. Sarah Chen, Ph.D. in Child Psychology and Digital Wellness Expert. Create a comprehensive, professional parental control report.

CHILD'S DIGITAL ACTIVITY ANALYSIS:
{json.dumps(summary, indent=2)}

Generate a detailed, unique report with deep insights and actionable guidance.

Return ONLY a JSON object with this structure:
{{
  "executiveSummary": "Comprehensive 4-5 sentence overview analyzing the child's digital behavior patterns, emotional wellness, and developmental trajectory",
  "keyFindings": [
    "Finding 1: Detailed observation with specific metrics and context",
    "Finding 2: Pattern analysis with behavioral implications",
    "Finding 3: Developmental milestone assessment",
    "Finding 4: Social-emotional indicators from digital behavior",
    "Finding 5: Risk assessment and protective factors"
  ],
  "emotionalTrends": {{
    "interpretation": "Deep psychological analysis of emotional patterns observed through digital behavior, including attachment styles, coping mechanisms, and emotional regulation",
    "trendDirection": "improving|stable|declining|fluctuating",
    "concernLevel": "none|minimal|moderate|elevated|critical",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "areasForGrowth": ["Area 1", "Area 2"]
  }},
  "positiveHabits": [
    "Specific positive behavior with developmental significance",
    "Another strength-based observation",
    "Evidence of healthy digital citizenship",
    "Signs of critical thinking and self-regulation"
  ],
  "possibleConcerns": [
    "Concern 1 with context, severity assessment, and developmental implications",
    "Concern 2 with environmental factors and potential interventions"
  ],
  "developmentalInsights": {{
    "cognitiveGrowth": "Analysis of learning patterns and intellectual curiosity",
    "socialDevelopment": "Assessment of social interactions and relationship building",
    "emotionalMaturity": "Evaluation of emotional intelligence and self-awareness",
    "digitalLiteracy": "Assessment of responsible technology use"
  }},
  "guidanceForParents": "Warm, comprehensive, evidence-based guidance (200-300 words) with specific strategies for supporting the child's digital wellness, including: attachment-based approaches, positive reinforcement techniques, collaborative goal-setting methods, and family systems interventions. Include specific conversation openers and engagement strategies.",
  "screenTimePolicy": {{
    "recommendedDailyLimit": 120,
    "weekendLimit": 180,
    "suggestedBedtime": "21:30",
    "reasoning": "Evidence-based explanation with developmental psychology principles",
    "flexibilityFactors": ["Factor 1", "Factor 2"],
    "adjustmentTriggers": ["When to increase limits", "When to decrease limits"]
  }},
  "conversationStarters": [
    "Deeply thoughtful question that invites authentic sharing",
    "Open-ended prompt that encourages critical thinking",
    "Curiosity-driven inquiry about their interests",
    "Reflective question about their digital experiences",
    "Future-oriented question about goals and aspirations"
  ],
  "actionPlan": {{
    "immediate": ["Action 1 for this week", "Action 2 for this week"],
    "shortTerm": ["30-day goal 1", "30-day goal 2"],
    "longTerm": ["Ongoing practice 1", "Ongoing practice 2"]
  }},
  "resources": [
    "Recommended book/website/app for child's interests",
    "Family activity suggestion based on trends",
    "Professional resource if needed"
  ]
}}

CRITICAL REQUIREMENTS:
- Use developmental psychology framework
- Be specific, not generic
- Focus on strengths-based approach
- Provide actionable, measurable recommendations
- Use warm, collaborative tone
- Reference actual data points
- Avoid jargon, be parent-friendly
- Emphasize connection over control
"""
        
        try:
            response = self.model.generate_content(prompt)
            report = json.loads(response.text.strip())
            
            # Add metadata
            report['generatedAt'] = datetime.now().isoformat()
            report['reportId'] = f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Convert wellness score (0-100)
            if 'emotionalTrends' in report:
                report['emotionalTrends']['wellnessScore'] = summary['emotionalTone']
            
            return report
        except Exception as e:
            print(f"Report generation error: {e}")
            return self._generate_fallback_report(summary)
    
    def _generate_fallback_report(self, summary: Dict) -> Dict:
        """Enhanced fallback report with 0-100 scoring"""
        wellness_score = summary.get('emotionalTone', 50)
        
        # Determine concern level based on 0-100 scale
        if wellness_score >= 80:
            concern_level = "none"
            trend_direction = "improving"
        elif wellness_score >= 60:
            concern_level = "minimal"
            trend_direction = "stable"
        elif wellness_score >= 40:
            concern_level = "moderate"
            trend_direction = "stable"
        else:
            concern_level = "elevated"
            trend_direction = "concerning"
        
        return {
            "executiveSummary": f"Analysis based on {summary['totalApps']} applications and {summary['totalKeywords']} search queries reveals a digital behavior pattern with wellness score of {wellness_score}/100. The child shows engagement with {', '.join(summary['topApps'][:3])} and demonstrates {trend_direction} behavioral trends.",
            "keyFindings": [
                f"Screen Time: {summary['screenTimeWeekly']} minutes weekly average",
                f"Application Portfolio: {summary['totalApps']} unique applications accessed",
                f"Search Activity: {summary['totalKeywords']} distinct search queries recorded",
                f"Wellness Metric: {wellness_score}/100 indicating {concern_level} concern level",
                f"Trend Direction: {trend_direction.capitalize()} behavioral patterns observed"
            ],
            "emotionalTrends": {
                "interpretation": f"Digital behavior wellness score of {wellness_score}/100 suggests {trend_direction} emotional patterns with {concern_level} level of concern requiring parental awareness.",
                "trendDirection": trend_direction,
                "concernLevel": concern_level,
                "wellnessScore": wellness_score,
                "strengths": ["Consistent digital engagement", "Varied application usage"],
                "areasForGrowth": ["Screen time management", "Content diversity"]
            },
            "positiveHabits": [
                "Regular engagement with educational/creative content",
                "Diverse application usage patterns",
                "Consistent daily routine establishment",
                "Active digital exploration and learning"
            ],
            "possibleConcerns": [
                f"Screen time monitoring recommended - {summary['screenTimeWeekly']} minutes weekly",
                f"{summary['blockedAttempts']} blocked access attempts require discussion"
            ] if summary['blockedAttempts'] > 0 else ["No immediate concerns detected"],
            "developmentalInsights": {
                "cognitiveGrowth": "Demonstrates curiosity through varied search queries and application exploration",
                "socialDevelopment": "Digital interaction patterns suggest age-appropriate social engagement",
                "emotionalMaturity": f"Wellness score of {wellness_score}/100 indicates {concern_level} emotional regulation",
                "digitalLiteracy": "Developing healthy navigation skills across digital platforms"
            },
            "guidanceForParents": f"Your child's digital wellness score of {wellness_score}/100 reflects {concern_level} areas for parental guidance. Approach conversations with curiosity rather than judgment. Start by acknowledging their interests in {', '.join(summary['topApps'][:2])}, then collaboratively set boundaries. Create 'tech-free zones' for family connection (meals, bedtime). Use the 3 C's: Connection (understand their digital world), Collaboration (set limits together), Consistency (enforce agreed boundaries lovingly). Remember: your goal is digital wellness, not digital perfection.",
            "screenTimePolicy": {
                "recommendedDailyLimit": 120,
                "weekendLimit": 180,
                "suggestedBedtime": "21:30",
                "reasoning": f"Based on {summary['screenTimeWeekly']} minutes weekly average and developmental best practices",
                "flexibilityFactors": ["Academic projects", "Creative pursuits", "Social connection needs"],
                "adjustmentTriggers": ["Improved self-regulation", "Academic performance changes", "Behavioral shifts"]
            },
            "conversationStarters": [
                f"I noticed you've been exploring {summary['topApps'][0] if summary['topApps'] else 'various apps'} - what do you find most interesting about it?",
                "If you could design your ideal app, what would it do and why?",
                "What's something you learned online this week that surprised you?",
                f"I see you're curious about {summary['recentKeywords'][0] if summary['recentKeywords'] else 'different topics'} - want to explore that together?",
                "What's one thing you wish adults understood better about being online?"
            ],
            "actionPlan": {
                "immediate": ["Schedule 30-minute 'digital wellness' conversation", "Review current screen time together"],
                "shortTerm": ["Establish collaborative tech boundaries", "Identify 2-3 screen-free family activities"],
                "longTerm": ["Build digital literacy skills", "Foster open communication about online experiences"]
            },
            "resources": [
                "Common Sense Media - Age-appropriate content guides",
                "Screen Time Action Network - Family media plans",
                "Digital Wellness Lab - Parent resources"
            ],
            "generatedAt": datetime.now().isoformat(),
            "reportId": f"RPT-FALLBACK-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
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
