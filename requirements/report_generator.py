"""
PDF Report Generator Module
Creates professional, legal-style parental control reports
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
        
        # Section header
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c5282'),
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold',
                borderPadding=(0, 0, 5, 0),
                borderColor=colors.HexColor('#4299e1'),
                borderWidth=0,
                leftIndent=0
            ))
        
        # Body text
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                spaceAfter=10
            ))
        
        # Executive summary style
        if 'ExecutiveSummary' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ExecutiveSummary',
                parent=self.styles['Normal'],
                fontSize=12,
                leading=18,
                alignment=TA_JUSTIFY,
                textColor=colors.HexColor('#2d3748'),
                spaceAfter=15,
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
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
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
        """Build cover page."""
        elements = []
        
        # Title
        elements.append(Spacer(1, 1.5*inch))
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
        """Build executive summary section."""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        elements.append(Paragraph(
            report_data.get('executiveSummary', 'No summary available.'),
            self.styles['ExecutiveSummary']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_key_findings(self, report_data: Dict) -> List:
        """Build key findings section."""
        elements = []
        
        elements.append(Paragraph("KEY FINDINGS", self.styles['SectionHeader']))
        
        findings = report_data.get('keyFindings', [])
        for i, finding in enumerate(findings, 1):
            elements.append(Paragraph(
                f"<b>{i}.</b> {finding}",
                self.styles['BodyText']
            ))
        
        if not findings:
            elements.append(Paragraph("No significant findings to report.", self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_emotional_trends(self, report_data: Dict) -> List:
        """Build emotional trends section."""
        elements = []
        
        elements.append(Paragraph("EMOTIONAL & BEHAVIORAL TRENDS", self.styles['SectionHeader']))
        
        trends = report_data.get('emotionalTrends', {})
        sentiment_score = trends.get('sentimentScore', 0)
        
        # Sentiment score visualization
        sentiment_text = "Neutral"
        sentiment_color = colors.HexColor('#718096')
        
        if sentiment_score > 0.3:
            sentiment_text = "Positive & Healthy"
            sentiment_color = colors.HexColor('#38a169')
        elif sentiment_score < -0.3:
            sentiment_text = "Concerning"
            sentiment_color = colors.HexColor('#e53e3e')
        
        elements.append(Paragraph(
            f"<b>Sentiment Score:</b> {sentiment_score:.2f} ({sentiment_text})",
            ParagraphStyle(
                name='SentimentScore',
                parent=self.styles['BodyText'],
                textColor=sentiment_color,
                fontSize=12
            )
        ))
        
        elements.append(Paragraph(
            f"<b>Trend Direction:</b> {trends.get('trendDirection', 'stable').capitalize()}",
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(
            trends.get('interpretation', 'Analysis in progress.'),
            self.styles['BodyText']
        ))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_positive_habits(self, report_data: Dict) -> List:
        """Build positive habits section."""
        elements = []
        
        elements.append(Paragraph("POSITIVE DIGITAL HABITS", self.styles['SectionHeader']))
        
        habits = report_data.get('positiveHabits', [])
        for habit in habits:
            elements.append(Paragraph(
                f"✓ {habit}",
                ParagraphStyle(
                    name='PositiveHabit',
                    parent=self.styles['BodyText'],
                    textColor=colors.HexColor('#38a169'),
                    leftIndent=15
                )
            ))
        
        if not habits:
            elements.append(Paragraph("Continue monitoring to identify positive patterns.", self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_concerns(self, report_data: Dict, report_type: str) -> List:
        """Build possible concerns section."""
        elements = []
        
        elements.append(Paragraph("AREAS FOR ATTENTION", self.styles['SectionHeader']))
        
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
            for concern in concerns:
                elements.append(Paragraph(
                    f"• {concern}",
                    ParagraphStyle(
                        name='Concern',
                        parent=self.styles['BodyText'],
                        textColor=colors.HexColor('#d69e2e'),
                        leftIndent=15
                    )
                ))
        
        if not concerns:
            elements.append(Paragraph("No significant concerns identified at this time.", self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_guidance(self, report_data: Dict) -> List:
        """Build guidance for parents section."""
        elements = []
        
        elements.append(Paragraph("GUIDANCE FOR PARENTS", self.styles['SectionHeader']))
        elements.append(Paragraph(
            report_data.get('guidanceForParents', 'Continue open communication with your child.'),
            self.styles['BodyText']
        ))
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _build_policy_recommendations(self, report_data: Dict) -> List:
        """Build screen time policy recommendations."""
        elements = []
        
        elements.append(Paragraph("RECOMMENDED SCREEN TIME POLICY", self.styles['SectionHeader']))
        
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
        
        elements.append(Paragraph("CONVERSATION STARTERS", self.styles['SectionHeader']))
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
        
        elements.append(Paragraph("REPORT INFORMATION", self.styles['SectionHeader']))
        
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
