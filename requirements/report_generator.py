"""
PDF Report Generator Module
Creates professional, legal-style parental control reports with diagrams
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics import renderPDF
from dotenv import load_dotenv

load_dotenv()

class ReportGenerator:
    """Generates professional PDF reports from intelligence data."""
    
    def __init__(self, output_dir: str = None):
        """Initialize report generator with output directory."""
        self.output_dir = Path(output_dir or os.getenv('REPORTS_DIR', 'generated_reports'))
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        self.company_name = os.getenv('REPORT_COMPANY_NAME', 'LimitX Parental Control')
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for professional formatting."""
        # Title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        # Section header with bold font
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#1e293b'),
                spaceAfter=14,
                spaceBefore=22,
                fontName='Helvetica-Bold',
                borderPadding=(0, 0, 6, 0),
                borderColor=colors.HexColor('#3b82f6'),
                borderWidth=0,
                leftIndent=0
            ))
        
        # Body text
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                leading=14,
                alignment=TA_JUSTIFY,
                spaceAfter=6,
                spaceBefore=0
            ))
        
        # Executive summary style
        if 'ExecutiveSummary' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ExecutiveSummary',
                parent=self.styles['Normal'],
                fontSize=12,
                leading=16,
                alignment=TA_JUSTIFY,
                textColor=colors.HexColor('#2d3748'),
                spaceAfter=8,
                spaceBefore=0,
                leftIndent=20,
                rightIndent=20,
                borderPadding=10,
                backColor=colors.HexColor('#edf2f7')
            ))
    
    def generate_report(self, intelligence_data: Dict, report_type: str = 'full') -> str:
        """
        Generate PDF report from intelligence data.
        
        Args:
            intelligence_data: Complete intelligence JSON data
            report_type: 'full' or 'redacted' (removes sensitive details)
        
        Returns:
            Path to generated PDF file
        """
        report_data = intelligence_data.get('syntheticReport', {})
        if not report_data:
            raise ValueError("No synthetic report data found in intelligence data")
        
        # Generate filename
        report_id = report_data.get('reportId', f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        filename = f"{report_id}_{report_type}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document with increased margins
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=90,
            leftMargin=90,
            topMargin=90,
            bottomMargin=90
        )
        
        # Build story (content)
        story = []
        
        # Add content
        story.extend(self._build_cover_page(intelligence_data, report_data))
        story.append(PageBreak())
        story.extend(self._build_executive_summary(report_data))
        story.extend(self._build_key_findings(report_data))
        story.extend(self._build_emotional_trends(report_data))
        story.extend(self._build_positive_habits(report_data))
        story.extend(self._build_concerns(report_data, report_type))
        story.extend(self._build_guidance(report_data))
        story.extend(self._build_policy_recommendations(report_data))
        story.extend(self._build_conversation_starters(report_data))
        story.append(PageBreak())
        story.extend(self._build_footer_page(intelligence_data))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Report generated: {filepath}")
        return str(filepath)
    
    def _build_cover_page(self, intelligence_data: Dict, report_data: Dict) -> List:
        """Build cover page with logo."""
        elements = []
        
        # Add logo at top left if available (try .jpg first, then .png)
        logo_path = Path(__file__).parent / 'logo.jpg'
        if not logo_path.exists():
            logo_path = Path(__file__).parent / 'logo.png'
            
        if logo_path.exists():
            try:
                logo = Image(str(logo_path), width=1*inch, height=1*inch)
                logo_table = Table([[logo]], colWidths=[7.5*inch])
                logo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(logo_table)
                elements.append(Spacer(1, 0.3*inch))
            except:
                pass  # Skip if logo can't be loaded
        
        # Title
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph(
            f"<b>{self.company_name}</b>",
            self.styles['CustomTitle']
        ))
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(
            "<b>DIGITAL WELLNESS REPORT</b>",
            self.styles['CustomTitle']
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Report info table
        profile = intelligence_data.get('childProfile', {})
        report_info = [
            ['Report ID:', report_data.get('reportId', 'N/A')],
            ['Generated:', datetime.fromisoformat(report_data.get('generatedAt', datetime.now().isoformat())).strftime('%B %d, %Y at %I:%M %p')],
            ['Child Profile:', profile.get('childId', 'Anonymous')],
            ['Reporting Period:', f"{profile.get('profileCreated', 'N/A')} to {profile.get('lastUpdated', 'Present')}"],
        ]
        
        t = Table(report_info, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c5282')),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 1*inch))
        
        # Confidentiality notice
        elements.append(Paragraph(
            "<b>CONFIDENTIAL DOCUMENT</b>",
            ParagraphStyle(
                name='Confidential',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#c53030'),
                alignment=TA_CENTER
            )
        ))
        
        elements.append(Paragraph(
            "This report contains privacy-protected information about your child's digital activity. "
            "No raw conversations or identifiable personal data are included. "
            "This document is intended for parental guidance and may be shared with school counselors or educational professionals.",
            ParagraphStyle(
                name='ConfidentialText',
                parent=self.styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#4a5568'),
                leading=12
            )
        ))
        
        return elements
    
    def _build_executive_summary(self, report_data: Dict) -> List:
        """Build executive summary section with extended description."""
        elements = []
        
        elements.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", self.styles['SectionHeader']))
        
        # Add introductory context
        intro = ("This comprehensive report provides an in-depth analysis of your child's digital behavior patterns, "
                "online activities, and emotional wellbeing indicators derived from their device usage. "
                "Our AI-powered intelligence system has analyzed application interactions, search behaviors, "
                "screen time patterns, and content engagement to identify trends, risks, and opportunities "
                "for positive digital citizenship development.")
        
        elements.append(Paragraph(intro, self.styles['BodyText']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Main summary from AI
        summary = report_data.get('executiveSummary', 'No summary available.')
        elements.append(Paragraph(summary, self.styles['ExecutiveSummary']))
        
        # Add methodology note
        methodology = ("<b>Methodology:</b> This report utilizes advanced behavioral analytics, "
                      "natural language processing for sentiment analysis, and pattern recognition algorithms "
                      "to provide actionable insights while maintaining strict privacy standards. "
                      "No personal conversations or identifiable content are stored or analyzed.")
        
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph(methodology, ParagraphStyle(
            name='Methodology',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#4a5568'),
            leftIndent=15,
            rightIndent=15,
            backColor=colors.HexColor('#f7fafc'),
            borderPadding=8
        )))
        
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_key_findings(self, report_data: Dict) -> List:
        """Build key findings section with detailed explanations."""
        elements = []
        
        elements.append(Paragraph("<b>KEY FINDINGS & OBSERVATIONS</b>", self.styles['SectionHeader']))
        
        # Add context paragraph
        context = ("The following key findings represent significant patterns, behaviors, or concerns "
                  "identified through our multi-dimensional analysis. Each finding is supported by "
                  "behavioral data, usage statistics, and content analysis. These observations are "
                  "intended to facilitate informed conversations and appropriate interventions.")
        
        elements.append(Paragraph(context, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        findings = report_data.get('keyFindings', [])
        
        if findings:
            for i, finding in enumerate(findings, 1):
                # Create finding with emphasis
                finding_text = f"<b>Finding #{i}:</b> {finding}"
                elements.append(Paragraph(finding_text, ParagraphStyle(
                    name=f'Finding{i}',
                    parent=self.styles['BodyText'],
                    fontSize=11,
                    leading=15,
                    leftIndent=10,
                    spaceAfter=10,
                    spaceBefore=5,
                    borderWidth=0,
                    borderPadding=5,
                    borderColor=colors.HexColor('#e2e8f0'),
                    backColor=colors.HexColor('#f8fafc')
                )))
        else:
            elements.append(Paragraph(
                "No significant findings to report at this time. This indicates healthy, balanced digital behavior "
                "with no red flags or concerning patterns detected during the analysis period.",
                self.styles['BodyText']
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_emotional_trends(self, report_data: Dict) -> List:
        """Build emotional trends section with wellness diagram."""
        elements = []
        
        elements.append(Paragraph("<b>EMOTIONAL & BEHAVIORAL TRENDS</b>", self.styles['SectionHeader']))
        
        trends = report_data.get('emotionalTrends', {})
        wellness_score = trends.get('wellnessScore', 50)  # 0-100 scale
        
        # Wellness score visualization with color coding
        sentiment_text = "Moderate"
        sentiment_color = colors.HexColor('#f59e0b')
        
        if wellness_score >= 80:
            sentiment_text = "Excellent & Healthy"
            sentiment_color = colors.HexColor('#10b981')
        elif wellness_score >= 60:
            sentiment_text = "Good & Positive"
            sentiment_color = colors.HexColor('#3b82f6')
        elif wellness_score >= 40:
            sentiment_text = "Moderate - Needs Guidance"
            sentiment_color = colors.HexColor('#f59e0b')
        elif wellness_score >= 20:
            sentiment_text = "Concerning - Action Needed"
            sentiment_color = colors.HexColor('#f97316')
        else:
            sentiment_text = "Critical - Immediate Attention"
            sentiment_color = colors.HexColor('#ef4444')
        
        # Create wellness score diagram
        d = Drawing(400, 80)
        
        # Background bar
        d.add(Rect(50, 30, 300, 30, fillColor=colors.HexColor('#1e293b'), strokeColor=None))
        
        # Wellness bar (colored based on score)
        bar_width = (wellness_score / 100) * 300
        d.add(Rect(50, 30, bar_width, 30, fillColor=sentiment_color, strokeColor=None))
        
        # Score text
        d.add(String(200, 45, f"Wellness Score: {wellness_score}/100", fontSize=14, fillColor=colors.white, textAnchor='middle'))
        d.add(String(200, 10, sentiment_text, fontSize=11, fillColor=sentiment_color, textAnchor='middle', fontName='Helvetica-Bold'))
        
        elements.append(d)
        elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Paragraph(
            f"<b>Concern Level:</b> {trends.get('concernLevel', 'moderate').capitalize()}",
            self.styles['BodyText']
        ))
        elements.append(Paragraph(
            f"<b>Trend Direction:</b> {trends.get('trendDirection', 'stable').capitalize()}",
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 0.08*inch))
        elements.append(Paragraph(
            trends.get('interpretation', 'Analysis in progress.'),
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 0.15*inch))
        return elements
    
    def _build_positive_habits(self, report_data: Dict) -> List:
        """Build positive habits section."""
        elements = []
        
        elements.append(Paragraph("<b>POSITIVE DIGITAL HABITS</b>", self.styles['SectionHeader']))
        
        habits = report_data.get('positiveHabits', [])
        for habit in habits:
            elements.append(Paragraph(
                f"✓ {habit}",
                ParagraphStyle(
                    name='PositiveHabit',
                    parent=self.styles['BodyText'],
                    textColor=colors.HexColor('#10b981'),
                    spaceAfter=4
                )
            ))
        
        if not habits:
            elements.append(Paragraph("No specific positive habits identified yet.", self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.15*inch))
        return elements
    
    def _build_concerns(self, report_data: Dict, report_type: str) -> List:
        """Build possible concerns section with detailed context."""
        elements = []
        
        elements.append(Paragraph("<b>AREAS FOR ATTENTION & CONCERN</b>", self.styles['SectionHeader']))
        
        # Add explanatory context
        context = ("The following areas have been flagged for parental attention based on behavioral patterns, "
                  "content exposure risks, or usage anomalies detected during the analysis period. "
                  "These concerns are categorized by severity and supported by evidence from activity logs, "
                  "application usage data, and content analysis. Early intervention in these areas can help "
                  "prevent escalation and promote healthier digital habits.")
        
        elements.append(Paragraph(context, self.styles['BodyText']))
        elements.append(Spacer(1, 0.15*inch))
        
        concerns = report_data.get('possibleConcerns', [])
        
        if report_type == 'redacted':
            elements.append(Paragraph(
                "Specific details have been redacted for privacy. Please refer to the full report for detailed information.",
                ParagraphStyle(
                    name='Redacted',
                    parent=self.styles['BodyText'],
                    textColor=colors.HexColor('#718096'),
                    fontName='Helvetica-Oblique'
                )
            ))
        else:
            if concerns:
                for i, concern in enumerate(concerns, 1):
                    concern_text = f"<b>⚠️ Concern #{i}:</b> {concern}"
                    elements.append(Paragraph(concern_text, ParagraphStyle(
                        name=f'Concern{i}',
                        parent=self.styles['BodyText'],
                        textColor=colors.HexColor('#d69e2e'),
                        leftIndent=10,
                        spaceAfter=8,
                        borderWidth=1,
                        borderColor=colors.HexColor('#fbd38d'),
                        borderPadding=6,
                        backColor=colors.HexColor('#fffaf0')
                    )))
        
        if not concerns:
            elements.append(Paragraph(
                "✅ No significant concerns identified at this time. Current digital behavior patterns "
                "indicate healthy, balanced usage with appropriate content engagement and time management.",
                self.styles['BodyText']
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_guidance(self, report_data: Dict) -> List:
        """Build guidance for parents section with detailed recommendations."""
        elements = []
        
        elements.append(Paragraph("<b>PRACTICAL GUIDANCE FOR PARENTS</b>", self.styles['SectionHeader']))
        
        # Add introductory guidance
        intro = ("Effective digital parenting requires a balanced approach that combines monitoring, education, "
                "and open communication. The following evidence-based guidance is tailored to your child's "
                "specific behavioral patterns and developmental needs. These recommendations are designed to "
                "foster digital literacy, emotional intelligence, and responsible online citizenship while "
                "maintaining a supportive, trust-based parent-child relationship.")
        
        elements.append(Paragraph(intro, self.styles['BodyText']))
        elements.append(Spacer(1, 0.15*inch))
        
        # AI-generated guidance
        guidance = report_data.get('guidanceForParents', 'Continue open communication with your child about their online activities and experiences.')
        elements.append(Paragraph(guidance, ParagraphStyle(
            name='GuidanceHighlight',
            parent=self.styles['BodyText'],
            leftIndent=15,
            rightIndent=15,
            borderWidth=2,
            borderColor=colors.HexColor('#4299e1'),
            borderPadding=10,
            backColor=colors.HexColor('#ebf8ff'),
            spaceAfter=12
        )))
        
        # Add general best practices
        best_practices = ("<b>Universal Best Practices:</b><br/>"
                         "• Schedule regular family discussions about online safety and digital wellbeing<br/>"
                         "• Model healthy digital behavior through your own device usage<br/>"
                         "• Create device-free zones and times (e.g., during meals, before bedtime)<br/>"
                         "• Encourage offline hobbies, physical activities, and face-to-face social interactions<br/>"
                         "• Teach critical thinking skills for evaluating online content and identifying misinformation")
        
        elements.append(Paragraph(best_practices, ParagraphStyle(
            name='BestPractices',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=14,
            leftIndent=10,
            spaceAfter=8
        )))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_policy_recommendations(self, report_data: Dict) -> List:
        """Build screen time policy recommendations."""
        elements = []
        
        elements.append(Paragraph("<b>RECOMMENDED SCREEN TIME POLICY</b>", self.styles['SectionHeader']))
        
        policy = report_data.get('screenTimePolicy', {})
        
        policy_table = [
            ['Policy Item', 'Recommendation'],
            ['Daily Screen Time Limit', f"{policy.get('recommendedDailyLimit', 120)} minutes"],
            ['Weekend Limit', f"{policy.get('weekendLimit', 180)} minutes"],
            ['Suggested Bedtime', policy.get('suggestedBedtime', '21:30')],
        ]
        
        t = Table(policy_table, colWidths=[2.5*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4299e1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#edf2f7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(
            f"<b>Reasoning:</b> {policy.get('reasoning', 'Based on behavioral analysis and age-appropriate guidelines.')}",
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_conversation_starters(self, report_data: Dict) -> List:
        """Build conversation starters section."""
        elements = []
        
        elements.append(Paragraph("<b>CONVERSATION STARTERS</b>", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "Use these topics to engage positively with your child about their digital life:",
            self.styles['BodyText']
        ))
        
        starters = report_data.get('conversationStarters', [])
        for starter in starters:
            elements.append(Paragraph(
                f"💬 {starter}",
                ParagraphStyle(
                    name='ConversationStarter',
                    parent=self.styles['BodyText'],
                    leftIndent=15,
                    textColor=colors.HexColor('#4299e1'),
                    spaceAfter=8
                )
            ))
        
        if not starters:
            elements.append(Paragraph(
                "💬 What did you find most interesting online this week?",
                self.styles['BodyText']
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_footer_page(self, intelligence_data: Dict) -> List:
        """Build footer/closing page."""
        elements = []
        
        elements.append(Paragraph("<b>REPORT INFORMATION</b>", self.styles['SectionHeader']))
        
        elements.append(Paragraph(
            "<b>Methodology:</b> This report is generated using advanced AI analysis (Gemini 2.0) "
            "combined with behavioral data collected through LimitX Parental Control system. "
            "All data is encrypted and stored securely. No personal conversations or identifiable "
            "information are included in this report.",
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph(
            "<b>Privacy Commitment:</b> We prioritize your child's privacy. This system monitors "
            "patterns and trends rather than individual activities. The goal is to support healthy "
            "digital habits through understanding and guidance, not surveillance.",
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        metadata = intelligence_data.get('metadata', {})
        elements.append(Paragraph(
            f"<b>Report Version:</b> {metadata.get('version', '1.0.0')}<br/>"
            f"<b>Data Integrity:</b> {'Verified' if metadata.get('integrityVerified') else 'Pending'}<br/>"
            f"<b>Last Sync:</b> {metadata.get('lastSync', 'N/A')}",
            ParagraphStyle(
                name='FooterInfo',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#718096')
            )
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        elements.append(Paragraph(
            f"© {datetime.now().year} {self.company_name}. All rights reserved.",
            ParagraphStyle(
                name='Copyright',
                parent=self.styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#a0aec0')
            )
        ))
        
        return elements
