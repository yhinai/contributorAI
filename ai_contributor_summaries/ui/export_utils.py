"""Data export utilities for generating reports."""

import pandas as pd
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import base64
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import streamlit as st


class DataExporter:
    """Export data in various formats."""
    
    def __init__(self):
        """Initialize the exporter."""
        self.styles = getSampleStyleSheet()
    
    def export_contributors_csv(self, contributors: List[Dict]) -> str:
        """Export contributors to CSV format."""
        if not contributors:
            return ""
        
        # Flatten complex fields
        export_data = []
        for contributor in contributors:
            export_row = {
                'username': contributor.get('username', ''),
                'github_id': contributor.get('github_id', ''),
                'total_commits': contributor.get('total_commits', 0),
                'total_issues': contributor.get('total_issues', 0),
                'repositories_count': contributor.get('repositories_count', 0),
                'activity_level': contributor.get('activity_level', ''),
                'contribution_style': contributor.get('contribution_style', ''),
                'skills': '; '.join(contributor.get('skills', [])),
                'expertise_areas': '; '.join(contributor.get('expertise_areas', [])),
                'primary_languages': '; '.join(contributor.get('primary_languages', [])),
                'summary': contributor.get('summary', '')
            }
            export_data.append(export_row)
        
        df = pd.DataFrame(export_data)
        return df.to_csv(index=False)
    
    def export_repositories_csv(self, repositories: List[Dict]) -> str:
        """Export repositories to CSV format."""
        if not repositories:
            return ""
        
        # Flatten complex fields
        export_data = []
        for repo in repositories:
            export_row = {
                'repository_name': repo.get('repository_name', ''),
                'repository_id': repo.get('repository_id', ''),
                'contributor_id': repo.get('contributor_id', ''),
                'commit_count': repo.get('commit_count', 0),
                'issue_count': repo.get('issue_count', 0),
                'contribution_type': repo.get('contribution_type', ''),
                'technologies': '; '.join(repo.get('technologies', [])),
                'files_touched': '; '.join(repo.get('files_touched', [])),
                'first_contribution': repo.get('first_contribution', ''),
                'last_contribution': repo.get('last_contribution', ''),
                'summary': repo.get('summary', '')
            }
            export_data.append(export_row)
        
        df = pd.DataFrame(export_data)
        return df.to_csv(index=False)
    
    def export_contributors_json(self, contributors: List[Dict]) -> str:
        """Export contributors to JSON format."""
        return json.dumps(contributors, indent=2, default=str)
    
    def export_repositories_json(self, repositories: List[Dict]) -> str:
        """Export repositories to JSON format."""
        return json.dumps(repositories, indent=2, default=str)
    
    def generate_contributor_report_pdf(self, contributors: List[Dict], 
                                      analytics_data: Optional[Dict] = None) -> bytes:
        """Generate a PDF report for contributors."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("AI Contributor Summaries Report", title_style))
        story.append(Spacer(1, 12))
        
        # Report metadata
        report_info = f"""
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Total Contributors:</b> {len(contributors)}<br/>
        <b>Report Type:</b> Contributor Analysis
        """
        story.append(Paragraph(report_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Analytics summary if provided
        if analytics_data:
            story.append(Paragraph("Executive Summary", self.styles['Heading2']))
            
            overview = analytics_data.get('overview', {})
            if overview:
                summary_text = f"""
                <b>Total Commits:</b> {overview.get('total_commits', 0):,}<br/>
                <b>Total Issues:</b> {overview.get('total_issues', 0):,}<br/>
                <b>Average Repositories per Contributor:</b> {overview.get('avg_repos_per_contributor', 0):.1f}<br/>
                <b>Average Commits per Contributor:</b> {overview.get('commits_per_contributor', 0):.1f}
                """
                story.append(Paragraph(summary_text, self.styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Top contributors table
        story.append(Paragraph("Top Contributors", self.styles['Heading2']))
        
        # Create table data
        table_data = [['Username', 'Commits', 'Issues', 'Repos', 'Activity', 'Top Skills']]
        
        # Sort contributors by commits and take top 20
        sorted_contributors = sorted(contributors, key=lambda x: x.get('total_commits', 0), reverse=True)[:20]
        
        for contributor in sorted_contributors:
            top_skills = contributor.get('skills', [])[:3]  # Top 3 skills
            table_data.append([
                contributor.get('username', 'Unknown'),
                str(contributor.get('total_commits', 0)),
                str(contributor.get('total_issues', 0)),
                str(contributor.get('repositories_count', 0)),
                contributor.get('activity_level', 'Unknown'),
                ', '.join(top_skills)
            ])
        
        # Create and style table
        table = Table(table_data, colWidths=[1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
        story.append(PageBreak())
        
        # Detailed contributor profiles
        story.append(Paragraph("Detailed Contributor Profiles", self.styles['Heading2']))
        
        for i, contributor in enumerate(sorted_contributors[:10]):  # Top 10 detailed profiles
            if i > 0:
                story.append(Spacer(1, 20))
            
            # Contributor header
            contributor_title = f"{contributor.get('username', 'Unknown')} - {contributor.get('activity_level', 'Unknown')} Activity"
            story.append(Paragraph(contributor_title, self.styles['Heading3']))
            
            # Contributor details
            details = f"""
            <b>Total Contributions:</b> {contributor.get('total_commits', 0)} commits, {contributor.get('total_issues', 0)} issues<br/>
            <b>Repositories:</b> {contributor.get('repositories_count', 0)}<br/>
            <b>Contribution Style:</b> {contributor.get('contribution_style', 'Unknown')}<br/>
            <b>Primary Languages:</b> {', '.join(contributor.get('primary_languages', [])[:5])}<br/>
            <b>Skills:</b> {', '.join(contributor.get('skills', [])[:10])}<br/>
            <b>Expertise Areas:</b> {', '.join(contributor.get('expertise_areas', [])[:5])}
            """
            story.append(Paragraph(details, self.styles['Normal']))
            
            # AI Summary
            summary = contributor.get('summary', '')
            if summary:
                story.append(Paragraph("<b>AI-Generated Summary:</b>", self.styles['Normal']))
                story.append(Paragraph(summary, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def generate_analytics_report_pdf(self, analytics_data: Dict[str, Any]) -> bytes:
        """Generate a PDF report for analytics insights."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1
        )
        story.append(Paragraph("AI Contributor Analytics Report", title_style))
        story.append(Spacer(1, 12))
        
        # Report metadata
        report_info = f"""
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report Type:</b> Analytics Insights
        """
        story.append(Paragraph(report_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Overview section
        overview = analytics_data.get('overview', {})
        if overview:
            story.append(Paragraph("Overview", self.styles['Heading2']))
            
            overview_text = f"""
            <b>Total Contributors:</b> {overview.get('total_contributors', 0)}<br/>
            <b>Total Commits:</b> {overview.get('total_commits', 0):,}<br/>
            <b>Total Issues:</b> {overview.get('total_issues', 0):,}<br/>
            <b>Average Repositories per Contributor:</b> {overview.get('avg_repos_per_contributor', 0):.1f}<br/>
            <b>Average Commits per Contributor:</b> {overview.get('commits_per_contributor', 0):.1f}<br/>
            <b>Average Issues per Contributor:</b> {overview.get('issues_per_contributor', 0):.1f}
            """
            story.append(Paragraph(overview_text, self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Skills analysis
        skill_analysis = analytics_data.get('skill_analysis', {})
        if skill_analysis:
            story.append(Paragraph("Skills Analysis", self.styles['Heading2']))
            
            skills_text = f"""
            <b>Total Unique Skills:</b> {skill_analysis.get('total_unique_skills', 0)}<br/>
            <b>Average Skills per Contributor:</b> {skill_analysis.get('avg_skills_per_contributor', 0):.1f}<br/>
            <b>Skill Diversity Index:</b> {skill_analysis.get('skill_diversity_index', 0):.3f}
            """
            story.append(Paragraph(skills_text, self.styles['Normal']))
            
            # Top skills table
            top_skills = skill_analysis.get('top_skills', [])
            if top_skills:
                story.append(Paragraph("Top Skills", self.styles['Heading3']))
                
                skills_table_data = [['Skill', 'Count']]
                for skill, count in top_skills[:15]:
                    skills_table_data.append([skill, str(count)])
                
                skills_table = Table(skills_table_data, colWidths=[4*inch, 1*inch])
                skills_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                story.append(skills_table)
                story.append(Spacer(1, 20))
        
        # Recommendations
        recommendations = analytics_data.get('recommendations', {})
        if recommendations:
            story.append(Paragraph("Recommendations", self.styles['Heading2']))
            
            for category, rec_list in recommendations.items():
                if rec_list:
                    category_title = category.replace('_', ' ').title()
                    story.append(Paragraph(category_title, self.styles['Heading3']))
                    
                    for rec in rec_list:
                        story.append(Paragraph(f"• {rec}", self.styles['Normal']))
                    
                    story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def create_download_link(self, data: str, filename: str, file_type: str) -> str:
        """Create a download link for data."""
        b64 = base64.b64encode(data.encode()).decode()
        return f'<a href="data:{file_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    
    def create_pdf_download_link(self, pdf_data: bytes, filename: str) -> str:
        """Create a download link for PDF data."""
        b64 = base64.b64encode(pdf_data).decode()
        return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'


# Global exporter instance
data_exporter = DataExporter()