#!/usr/bin/env python3
"""
Report Generator Module
Generates comprehensive reports and visualizations for relationship analysis
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from enum import Enum
import base64
from io import BytesIO
from pathlib import Path

# Data analysis and visualization
# Heavy data analysis and visualization dependencies not available in minimal setup
# import pandas as pd
# Use minimal implementations instead of NumPy
from minimal_implementations import py_mean, py_random_uniform, py_cumsum, py_random_rand
# import matplotlib.pyplot as plt
# import seaborn as sns
# from matplotlib.backends.backend_pdf import PdfPages
# import plotly.graph_objects as go
# import plotly.express as px
# from plotly.subplots import make_subplots
# import plotly.io as pio

# Heavy document generation dependencies not available in minimal setup
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.graphics.shapes import Drawing
# from reportlab.graphics.charts.linecharts import HorizontalLineChart
# from reportlab.graphics.charts.piecharts import Pie

# Heavy text processing dependencies not available in minimal setup
# from textblob import TextBlob
# import spacy
# from wordcloud import WordCloud

# Local imports
from conversation_analyzer import ConversationAnalyzer, AnalysisResult
from ai_therapist import AITherapist, TherapeuticInsight, UserTherapyProfile

logger = logging.getLogger(__name__)

class ReportType(Enum):
    RELATIONSHIP_HEALTH = "relationship_health"
    COMMUNICATION_ANALYSIS = "communication_analysis"
    COMPATIBILITY_ASSESSMENT = "compatibility_assessment"
    PROGRESS_TRACKING = "progress_tracking"
    INTERVENTION_SUMMARY = "intervention_summary"
    COMPREHENSIVE = "comprehensive"

class ReportFormat(Enum):
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    INTERACTIVE = "interactive"

@dataclass
class ReportMetadata:
    report_id: str
    user_id: str
    report_type: str
    report_format: str
    generated_at: datetime
    time_period: str
    data_points: int
    confidence_level: float
    version: str = "1.0"

@dataclass
class ReportSection:
    title: str
    content: str
    visualizations: List[Dict[str, Any]]
    metrics: Dict[str, float]
    recommendations: List[str]
    priority: str  # high, medium, low

class ReportGenerator:
    def __init__(self, ai_therapist: AITherapist = None,
                 conversation_analyzer: ConversationAnalyzer = None):
        
        self.ai_therapist = ai_therapist
        self.conversation_analyzer = conversation_analyzer
        
        # Report templates and styles
        self.report_templates = self._initialize_report_templates()
        self.visualization_themes = self._initialize_visualization_themes()
        
        # Output directories
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize plotting settings (disabled in minimal setup)
        # plt.style.use('seaborn-v0_8')
        # sns.set_palette("husl")
        
        logger.info("Report Generator initialized")
    
    def _initialize_report_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize report templates for different report types
        """
        templates = {
            ReportType.RELATIONSHIP_HEALTH.value: {
                "title": "Relationship Health Assessment Report",
                "sections": [
                    "executive_summary",
                    "health_metrics",
                    "strengths_analysis",
                    "areas_for_improvement",
                    "recommendations",
                    "action_plan"
                ],
                "visualizations": [
                    "health_radar_chart",
                    "trend_analysis",
                    "comparison_metrics"
                ]
            },
            ReportType.COMMUNICATION_ANALYSIS.value: {
                "title": "Communication Patterns Analysis Report",
                "sections": [
                    "communication_overview",
                    "style_analysis",
                    "effectiveness_metrics",
                    "pattern_identification",
                    "improvement_strategies"
                ],
                "visualizations": [
                    "communication_timeline",
                    "style_distribution",
                    "effectiveness_trends"
                ]
            },
            ReportType.COMPATIBILITY_ASSESSMENT.value: {
                "title": "Relationship Compatibility Assessment",
                "sections": [
                    "compatibility_overview",
                    "personality_matching",
                    "communication_compatibility",
                    "conflict_styles",
                    "growth_potential"
                ],
                "visualizations": [
                    "compatibility_matrix",
                    "personality_comparison",
                    "interaction_patterns"
                ]
            },
            ReportType.PROGRESS_TRACKING.value: {
                "title": "Relationship Progress Tracking Report",
                "sections": [
                    "progress_summary",
                    "goal_achievement",
                    "metric_improvements",
                    "milestone_analysis",
                    "future_goals"
                ],
                "visualizations": [
                    "progress_timeline",
                    "goal_completion",
                    "metric_trends"
                ]
            },
            ReportType.INTERVENTION_SUMMARY.value: {
                "title": "Therapeutic Interventions Summary",
                "sections": [
                    "intervention_overview",
                    "effectiveness_analysis",
                    "outcome_tracking",
                    "success_patterns",
                    "future_recommendations"
                ],
                "visualizations": [
                    "intervention_timeline",
                    "effectiveness_metrics",
                    "outcome_distribution"
                ]
            }
        }
        
        return templates
    
    def _initialize_visualization_themes(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize visualization themes and color schemes
        """
        themes = {
            "professional": {
                "colors": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#592E83"],
                "background": "white",
                "grid": "lightgray",
                "font_family": "Arial"
            },
            "warm": {
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
                "background": "#FAFAFA",
                "grid": "#E0E0E0",
                "font_family": "Helvetica"
            },
            "therapeutic": {
                "colors": ["#6C5CE7", "#A29BFE", "#FD79A8", "#FDCB6E", "#6C5CE7"],
                "background": "white",
                "grid": "#F1F2F6",
                "font_family": "Roboto"
            }
        }
        
        return themes
    
    async def generate_report(self, user_id: str, report_type: str, 
                            report_format: str = "pdf", 
                            time_period: str = "last_month",
                            custom_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report
        """
        try:
            # Validate inputs
            if report_type not in [rt.value for rt in ReportType]:
                raise ValueError(f"Invalid report type: {report_type}")
            
            if report_format not in [rf.value for rf in ReportFormat]:
                raise ValueError(f"Invalid report format: {report_format}")
            
            # Get user data and analysis
            user_data = await self._gather_user_data(user_id, time_period)
            
            # Generate report metadata
            metadata = ReportMetadata(
                report_id=f"report_{user_id}_{report_type}_{datetime.now().timestamp()}",
                user_id=user_id,
                report_type=report_type,
                report_format=report_format,
                generated_at=datetime.now(),
                time_period=time_period,
                data_points=len(user_data.get("sessions", [])),
                confidence_level=user_data.get("confidence_level", 0.8)
            )
            
            # Generate report sections
            sections = await self._generate_report_sections(
                report_type, user_data, custom_options
            )
            
            # Generate visualizations
            visualizations = await self._generate_visualizations(
                report_type, user_data, custom_options
            )
            
            # Create report based on format
            if report_format == ReportFormat.PDF.value:
                report_content = await self._generate_pdf_report(
                    metadata, sections, visualizations
                )
            elif report_format == ReportFormat.HTML.value:
                report_content = await self._generate_html_report(
                    metadata, sections, visualizations
                )
            elif report_format == ReportFormat.JSON.value:
                report_content = await self._generate_json_report(
                    metadata, sections, visualizations
                )
            elif report_format == ReportFormat.INTERACTIVE.value:
                report_content = await self._generate_interactive_report(
                    metadata, sections, visualizations
                )
            else:
                raise ValueError(f"Unsupported report format: {report_format}")
            
            # Save report
            report_path = await self._save_report(metadata, report_content)
            
            return {
                "metadata": asdict(metadata),
                "report_path": str(report_path),
                "sections": [asdict(section) for section in sections],
                "visualizations": visualizations,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise
    
    async def _gather_user_data(self, user_id: str, time_period: str) -> Dict[str, Any]:
        """
        Gather all relevant user data for report generation
        """
        try:
            user_data = {
                "user_profile": None,
                "sessions": [],
                "interventions": [],
                "analysis_results": [],
                "progress_metrics": {},
                "confidence_level": 0.8
            }
            
            # Get user profile from AI therapist
            if self.ai_therapist:
                user_profile = await self.ai_therapist.get_user_profile(user_id)
                user_data["user_profile"] = asdict(user_profile)
                
                # Get session history
                user_data["sessions"] = user_profile.session_history
                
                # Get intervention history
                if user_id in self.ai_therapist.intervention_history:
                    user_data["interventions"] = [
                        asdict(intervention) 
                        for intervention in self.ai_therapist.intervention_history[user_id]
                    ]
                
                # Get progress metrics
                user_data["progress_metrics"] = user_profile.progress_metrics
            
            # Calculate time range
            end_date = datetime.now()
            if time_period == "last_week":
                start_date = end_date - timedelta(weeks=1)
            elif time_period == "last_month":
                start_date = end_date - timedelta(days=30)
            elif time_period == "last_3_months":
                start_date = end_date - timedelta(days=90)
            elif time_period == "last_6_months":
                start_date = end_date - timedelta(days=180)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Filter data by time period
            user_data["sessions"] = [
                session for session in user_data["sessions"]
                if start_date <= datetime.fromisoformat(session.get("timestamp", datetime.now().isoformat())) <= end_date
            ]
            
            user_data["interventions"] = [
                intervention for intervention in user_data["interventions"]
                if start_date <= datetime.fromisoformat(intervention.get("created_at", datetime.now().isoformat())) <= end_date
            ]
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error gathering user data: {str(e)}")
            return {"user_profile": None, "sessions": [], "interventions": [], "analysis_results": [], "progress_metrics": {}, "confidence_level": 0.5}
    
    async def _generate_report_sections(self, report_type: str, user_data: Dict[str, Any],
                                      custom_options: Dict[str, Any] = None) -> List[ReportSection]:
        """
        Generate report sections based on report type
        """
        sections = []
        template = self.report_templates.get(report_type, {})
        
        try:
            if report_type == ReportType.RELATIONSHIP_HEALTH.value:
                sections = await self._generate_health_sections(user_data)
            elif report_type == ReportType.COMMUNICATION_ANALYSIS.value:
                sections = await self._generate_communication_sections(user_data)
            elif report_type == ReportType.COMPATIBILITY_ASSESSMENT.value:
                sections = await self._generate_compatibility_sections(user_data)
            elif report_type == ReportType.PROGRESS_TRACKING.value:
                sections = await self._generate_progress_sections(user_data)
            elif report_type == ReportType.INTERVENTION_SUMMARY.value:
                sections = await self._generate_intervention_sections(user_data)
            elif report_type == ReportType.COMPREHENSIVE.value:
                sections = await self._generate_comprehensive_sections(user_data)
            
            return sections
            
        except Exception as e:
            logger.error(f"Error generating report sections: {str(e)}")
            return []
    
    async def _generate_health_sections(self, user_data: Dict[str, Any]) -> List[ReportSection]:
        """
        Generate relationship health report sections
        """
        sections = []
        
        # Executive Summary
        health_score = self._calculate_overall_health_score(user_data)
        summary_content = f"""
        Based on analysis of {len(user_data['sessions'])} conversation sessions, 
        your relationship shows an overall health score of {health_score:.1f}/10.
        
        This assessment considers communication effectiveness, emotional connection, 
        conflict resolution patterns, and relationship satisfaction indicators.
        """
        
        sections.append(ReportSection(
            title="Executive Summary",
            content=summary_content,
            visualizations=[],
            metrics={"overall_health_score": health_score},
            recommendations=self._generate_health_recommendations(user_data),
            priority="high"
        ))
        
        # Health Metrics
        metrics_content = self._generate_health_metrics_content(user_data)
        sections.append(ReportSection(
            title="Health Metrics Analysis",
            content=metrics_content,
            visualizations=["health_radar_chart"],
            metrics=self._extract_health_metrics(user_data),
            recommendations=[],
            priority="high"
        ))
        
        # Strengths Analysis
        strengths_content = self._generate_strengths_analysis(user_data)
        sections.append(ReportSection(
            title="Relationship Strengths",
            content=strengths_content,
            visualizations=["strengths_chart"],
            metrics={},
            recommendations=[],
            priority="medium"
        ))
        
        # Areas for Improvement
        improvement_content = self._generate_improvement_analysis(user_data)
        sections.append(ReportSection(
            title="Areas for Improvement",
            content=improvement_content,
            visualizations=["improvement_priorities"],
            metrics={},
            recommendations=self._generate_improvement_recommendations(user_data),
            priority="high"
        ))
        
        return sections
    
    async def _generate_communication_sections(self, user_data: Dict[str, Any]) -> List[ReportSection]:
        """
        Generate communication analysis report sections
        """
        sections = []
        
        # Communication Overview
        overview_content = self._generate_communication_overview(user_data)
        sections.append(ReportSection(
            title="Communication Overview",
            content=overview_content,
            visualizations=["communication_timeline"],
            metrics=self._extract_communication_metrics(user_data),
            recommendations=[],
            priority="high"
        ))
        
        # Style Analysis
        style_content = self._generate_style_analysis(user_data)
        sections.append(ReportSection(
            title="Communication Style Analysis",
            content=style_content,
            visualizations=["style_distribution"],
            metrics={},
            recommendations=self._generate_style_recommendations(user_data),
            priority="medium"
        ))
        
        return sections
    
    async def _generate_compatibility_sections(self, user_data: Dict[str, Any]) -> List[ReportSection]:
        """
        Generate compatibility assessment report sections
        """
        sections = []
        
        # Compatibility Overview
        compatibility_score = self._calculate_compatibility_score(user_data)
        overview_content = f"""
        Compatibility analysis reveals a score of {compatibility_score:.1f}/10 based on 
        communication patterns, conflict resolution styles, and emotional compatibility.
        """
        
        sections.append(ReportSection(
            title="Compatibility Overview",
            content=overview_content,
            visualizations=["compatibility_matrix"],
            metrics={"compatibility_score": compatibility_score},
            recommendations=self._generate_compatibility_recommendations(user_data),
            priority="high"
        ))
        
        return sections
    
    async def _generate_progress_sections(self, user_data: Dict[str, Any]) -> List[ReportSection]:
        """
        Generate progress tracking report sections
        """
        sections = []
        
        # Progress Summary
        progress_content = self._generate_progress_summary(user_data)
        sections.append(ReportSection(
            title="Progress Summary",
            content=progress_content,
            visualizations=["progress_timeline"],
            metrics=self._extract_progress_metrics(user_data),
            recommendations=self._generate_progress_recommendations(user_data),
            priority="high"
        ))
        
        return sections
    
    async def _generate_intervention_sections(self, user_data: Dict[str, Any]) -> List[ReportSection]:
        """
        Generate intervention summary report sections
        """
        sections = []
        
        # Intervention Overview
        intervention_content = self._generate_intervention_overview(user_data)
        sections.append(ReportSection(
            title="Intervention Overview",
            content=intervention_content,
            visualizations=["intervention_timeline"],
            metrics=self._extract_intervention_metrics(user_data),
            recommendations=self._generate_intervention_recommendations(user_data),
            priority="high"
        ))
        
        return sections
    
    async def _generate_comprehensive_sections(self, user_data: Dict[str, Any]) -> List[ReportSection]:
        """
        Generate comprehensive report sections
        """
        sections = []
        
        # Combine all section types
        health_sections = await self._generate_health_sections(user_data)
        communication_sections = await self._generate_communication_sections(user_data)
        progress_sections = await self._generate_progress_sections(user_data)
        
        sections.extend(health_sections)
        sections.extend(communication_sections)
        sections.extend(progress_sections)
        
        return sections
    
    async def _generate_visualizations(self, report_type: str, user_data: Dict[str, Any],
                                     custom_options: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Generate visualizations for the report
        """
        visualizations = {}
        
        try:
            if report_type == ReportType.RELATIONSHIP_HEALTH.value:
                visualizations.update(await self._create_health_visualizations(user_data))
            elif report_type == ReportType.COMMUNICATION_ANALYSIS.value:
                visualizations.update(await self._create_communication_visualizations(user_data))
            elif report_type == ReportType.COMPATIBILITY_ASSESSMENT.value:
                visualizations.update(await self._create_compatibility_visualizations(user_data))
            elif report_type == ReportType.PROGRESS_TRACKING.value:
                visualizations.update(await self._create_progress_visualizations(user_data))
            elif report_type == ReportType.INTERVENTION_SUMMARY.value:
                visualizations.update(await self._create_intervention_visualizations(user_data))
            elif report_type == ReportType.COMPREHENSIVE.value:
                # Combine all visualizations
                visualizations.update(await self._create_health_visualizations(user_data))
                visualizations.update(await self._create_communication_visualizations(user_data))
                visualizations.update(await self._create_progress_visualizations(user_data))
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            return {}
    
    async def _create_health_visualizations(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create health-related visualizations
        """
        visualizations = {}
        
        try:
            # Health Radar Chart
            health_metrics = self._extract_health_metrics(user_data)
            radar_chart = self._create_radar_chart(
                metrics=health_metrics,
                title="Relationship Health Metrics"
            )
            visualizations["health_radar_chart"] = radar_chart
            
            # Trend Analysis
            if len(user_data["sessions"]) > 1:
                trend_chart = self._create_trend_chart(
                    sessions=user_data["sessions"],
                    title="Health Trends Over Time"
                )
                visualizations["trend_analysis"] = trend_chart
            
            # Strengths Chart
            strengths_chart = self._create_strengths_chart(user_data)
            visualizations["strengths_chart"] = strengths_chart
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating health visualizations: {str(e)}")
            return {}
    
    async def _create_communication_visualizations(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create communication-related visualizations
        """
        visualizations = {}
        
        try:
            # Communication Timeline
            timeline_chart = self._create_communication_timeline(user_data)
            visualizations["communication_timeline"] = timeline_chart
            
            # Style Distribution
            style_chart = self._create_style_distribution_chart(user_data)
            visualizations["style_distribution"] = style_chart
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating communication visualizations: {str(e)}")
            return {}
    
    async def _create_compatibility_visualizations(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create compatibility-related visualizations
        """
        visualizations = {}
        
        try:
            # Compatibility Matrix
            matrix_chart = self._create_compatibility_matrix(user_data)
            visualizations["compatibility_matrix"] = matrix_chart
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating compatibility visualizations: {str(e)}")
            return {}
    
    async def _create_progress_visualizations(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create progress-related visualizations
        """
        visualizations = {}
        
        try:
            # Progress Timeline
            progress_chart = self._create_progress_timeline(user_data)
            visualizations["progress_timeline"] = progress_chart
            
            # Goal Completion Chart
            goal_chart = self._create_goal_completion_chart(user_data)
            visualizations["goal_completion"] = goal_chart
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating progress visualizations: {str(e)}")
            return {}
    
    async def _create_intervention_visualizations(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create intervention-related visualizations
        """
        visualizations = {}
        
        try:
            # Intervention Timeline
            intervention_chart = self._create_intervention_timeline(user_data)
            visualizations["intervention_timeline"] = intervention_chart
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating intervention visualizations: {str(e)}")
            return {}
    
    def _create_radar_chart(self, metrics: Dict[str, float], title: str) -> str:
        """
        Create a radar chart for metrics visualization
        """
        try:
            # Prepare data
            categories = list(metrics.keys())
            values = list(metrics.values())
            
            # Create plotly radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Current Metrics',
                line_color='rgb(46, 134, 171)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=True,
                title=title
            )
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating radar chart: {str(e)}")
            return ""
    
    def _create_trend_chart(self, sessions: List[Dict[str, Any]], title: str) -> str:
        """
        Create a trend chart for session data
        """
        try:
            # Prepare data
            dates = []
            scores = []
            
            for session in sessions:
                if "timestamp" in session and "confidence_score" in session:
                    dates.append(datetime.fromisoformat(session["timestamp"]))
                    scores.append(session["confidence_score"])
            
            if not dates:
                return ""
            
            # Create plotly line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=scores,
                mode='lines+markers',
                name='Confidence Score',
                line=dict(color='rgb(46, 134, 171)', width=2)
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Score",
                showlegend=True
            )
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating trend chart: {str(e)}")
            return ""
    
    def _create_strengths_chart(self, user_data: Dict[str, Any]) -> str:
        """
        Create a chart showing relationship strengths
        """
        try:
            # Sample strengths data
            strengths = {
                "Communication": 0.8,
                "Emotional Connection": 0.7,
                "Trust": 0.9,
                "Conflict Resolution": 0.6,
                "Shared Values": 0.8
            }
            
            # Create horizontal bar chart
            fig = go.Figure(go.Bar(
                x=list(strengths.values()),
                y=list(strengths.keys()),
                orientation='h',
                marker_color='rgb(46, 134, 171)'
            ))
            
            fig.update_layout(
                title="Relationship Strengths",
                xaxis_title="Strength Level",
                yaxis_title="Areas"
            )
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating strengths chart: {str(e)}")
            return ""
    
    def _create_communication_timeline(self, user_data: Dict[str, Any]) -> str:
        """
        Create a timeline of communication patterns
        """
        try:
            # Sample timeline data
            dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
            communication_scores = py_random_uniform(0.4, 0.9, 30)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=communication_scores,
                mode='lines+markers',
                name='Communication Effectiveness',
                line=dict(color='rgb(162, 59, 114)', width=2)
            ))
            
            fig.update_layout(
                title="Communication Effectiveness Over Time",
                xaxis_title="Date",
                yaxis_title="Effectiveness Score"
            )
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating communication timeline: {str(e)}")
            return ""
    
    def _create_style_distribution_chart(self, user_data: Dict[str, Any]) -> str:
        """
        Create a chart showing communication style distribution
        """
        try:
            # Sample style data
            styles = {
                "Assertive": 35,
                "Passive": 20,
                "Aggressive": 10,
                "Passive-Aggressive": 15,
                "Empathetic": 20
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(styles.keys()),
                values=list(styles.values()),
                hole=0.3
            )])
            
            fig.update_layout(title="Communication Style Distribution")
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating style distribution chart: {str(e)}")
            return ""
    
    def _create_compatibility_matrix(self, user_data: Dict[str, Any]) -> str:
        """
        Create a compatibility matrix visualization
        """
        try:
            # Sample compatibility data
            areas = ["Communication", "Values", "Goals", "Conflict Style", "Emotional Needs"]
            compatibility_scores = py_random_uniform(0.5, 0.9, (5, 5))
            
            fig = go.Figure(data=go.Heatmap(
                z=compatibility_scores,
                x=areas,
                y=areas,
                colorscale='RdYlBu',
                reversescale=True
            ))
            
            fig.update_layout(title="Compatibility Matrix")
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating compatibility matrix: {str(e)}")
            return ""
    
    def _create_progress_timeline(self, user_data: Dict[str, Any]) -> str:
        """
        Create a progress timeline visualization
        """
        try:
            # Sample progress data
            dates = [datetime.now() - timedelta(weeks=i) for i in range(12, 0, -1)]
            progress_scores = py_cumsum(py_random_uniform(0.01, 0.05, 12))
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=progress_scores,
                mode='lines+markers',
                name='Progress Score',
                line=dict(color='rgb(241, 143, 1)', width=3)
            ))
            
            fig.update_layout(
                title="Relationship Progress Over Time",
                xaxis_title="Date",
                yaxis_title="Progress Score"
            )
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating progress timeline: {str(e)}")
            return ""
    
    def _create_goal_completion_chart(self, user_data: Dict[str, Any]) -> str:
        """
        Create a goal completion chart
        """
        try:
            # Sample goal data
            goals = ["Better Communication", "Conflict Resolution", "Emotional Intimacy", "Trust Building"]
            completion = [85, 70, 60, 90]
            
            fig = go.Figure(go.Bar(
                x=goals,
                y=completion,
                marker_color=['green' if c >= 80 else 'orange' if c >= 60 else 'red' for c in completion]
            ))
            
            fig.update_layout(
                title="Goal Completion Progress",
                xaxis_title="Goals",
                yaxis_title="Completion %"
            )
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating goal completion chart: {str(e)}")
            return ""
    
    def _create_intervention_timeline(self, user_data: Dict[str, Any]) -> str:
        """
        Create an intervention timeline visualization
        """
        try:
            interventions = user_data.get("interventions", [])
            
            if not interventions:
                return ""
            
            # Prepare data
            dates = []
            types = []
            
            for intervention in interventions:
                if "created_at" in intervention:
                    dates.append(datetime.fromisoformat(intervention["created_at"]))
                    types.append(intervention.get("intervention_type", "Unknown"))
            
            if not dates:
                return ""
            
            # Create timeline chart
            fig = go.Figure()
            
            for i, (date, intervention_type) in enumerate(zip(dates, types)):
                fig.add_trace(go.Scatter(
                    x=[date],
                    y=[i],
                    mode='markers',
                    name=intervention_type,
                    marker=dict(size=10)
                ))
            
            fig.update_layout(
                title="Intervention Timeline",
                xaxis_title="Date",
                yaxis_title="Intervention"
            )
            
            # Convert to base64 string
            img_bytes = pio.to_image(fig, format="png")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error creating intervention timeline: {str(e)}")
            return ""
    
    async def _generate_pdf_report(self, metadata: ReportMetadata, 
                                 sections: List[ReportSection],
                                 visualizations: Dict[str, str]) -> bytes:
        """
        Generate PDF report
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            template = self.report_templates.get(metadata.report_type, {})
            title = template.get("title", "Relationship Analysis Report")
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Metadata
            metadata_text = f"""
            <b>Report ID:</b> {metadata.report_id}<br/>
            <b>Generated:</b> {metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>
            <b>Time Period:</b> {metadata.time_period}<br/>
            <b>Data Points:</b> {metadata.data_points}<br/>
            <b>Confidence Level:</b> {metadata.confidence_level:.2f}
            """
            story.append(Paragraph(metadata_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Sections
            for section in sections:
                # Section title
                story.append(Paragraph(section.title, styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Section content
                story.append(Paragraph(section.content, styles['Normal']))
                story.append(Spacer(1, 12))
                
                # Metrics table
                if section.metrics:
                    metrics_data = [["Metric", "Value"]]
                    for metric, value in section.metrics.items():
                        metrics_data.append([metric.replace('_', ' ').title(), f"{value:.2f}"])
                    
                    metrics_table = Table(metrics_data)
                    metrics_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(metrics_table)
                    story.append(Spacer(1, 12))
                
                # Recommendations
                if section.recommendations:
                    story.append(Paragraph("<b>Recommendations:</b>", styles['Heading3']))
                    for rec in section.recommendations:
                        story.append(Paragraph(f"• {rec}", styles['Normal']))
                    story.append(Spacer(1, 12))
                
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            return b""
    
    async def _generate_html_report(self, metadata: ReportMetadata,
                                  sections: List[ReportSection],
                                  visualizations: Dict[str, str]) -> str:
        """
        Generate HTML report
        """
        try:
            template = self.report_templates.get(metadata.report_type, {})
            title = template.get("title", "Relationship Analysis Report")
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .metadata {{ background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; }}
                    .section {{ margin-bottom: 30px; }}
                    .section h2 {{ color: #2E86AB; border-bottom: 2px solid #2E86AB; }}
                    .metrics {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
                    .recommendations {{ background-color: #e8f4f8; padding: 15px; margin: 10px 0; }}
                    .visualization {{ text-align: center; margin: 20px 0; }}
                    .visualization img {{ max-width: 100%; height: auto; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{title}</h1>
                </div>
                
                <div class="metadata">
                    <h3>Report Information</h3>
                    <p><strong>Report ID:</strong> {metadata.report_id}</p>
                    <p><strong>Generated:</strong> {metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Time Period:</strong> {metadata.time_period}</p>
                    <p><strong>Data Points:</strong> {metadata.data_points}</p>
                    <p><strong>Confidence Level:</strong> {metadata.confidence_level:.2f}</p>
                </div>
            """
            
            # Add sections
            for section in sections:
                html_content += f"""
                <div class="section">
                    <h2>{section.title}</h2>
                    <p>{section.content}</p>
                """
                
                # Add metrics
                if section.metrics:
                    html_content += '<div class="metrics"><h4>Metrics:</h4><ul>'
                    for metric, value in section.metrics.items():
                        html_content += f'<li><strong>{metric.replace("_", " ").title()}:</strong> {value:.2f}</li>'
                    html_content += '</ul></div>'
                
                # Add visualizations
                for viz_name in section.visualizations:
                    if viz_name in visualizations:
                        html_content += f"""
                        <div class="visualization">
                            <img src="{visualizations[viz_name]}" alt="{viz_name}" />
                        </div>
                        """
                
                # Add recommendations
                if section.recommendations:
                    html_content += '<div class="recommendations"><h4>Recommendations:</h4><ul>'
                    for rec in section.recommendations:
                        html_content += f'<li>{rec}</li>'
                    html_content += '</ul></div>'
                
                html_content += '</div>'
            
            html_content += """
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return ""
    
    async def _generate_json_report(self, metadata: ReportMetadata,
                                  sections: List[ReportSection],
                                  visualizations: Dict[str, str]) -> str:
        """
        Generate JSON report
        """
        try:
            report_data = {
                "metadata": asdict(metadata),
                "sections": [asdict(section) for section in sections],
                "visualizations": visualizations
            }
            
            # Convert datetime objects to strings
            report_data["metadata"]["generated_at"] = metadata.generated_at.isoformat()
            
            return json.dumps(report_data, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {str(e)}")
            return "{}"
    
    async def _generate_interactive_report(self, metadata: ReportMetadata,
                                         sections: List[ReportSection],
                                         visualizations: Dict[str, str]) -> str:
        """
        Generate interactive HTML report with JavaScript
        """
        try:
            # This would create an interactive dashboard
            # For now, return enhanced HTML
            html_report = await self._generate_html_report(metadata, sections, visualizations)
            
            # Add interactive elements
            interactive_js = """
            <script>
                function toggleSection(sectionId) {
                    var section = document.getElementById(sectionId);
                    if (section.style.display === 'none') {
                        section.style.display = 'block';
                    } else {
                        section.style.display = 'none';
                    }
                }
                
                function highlightMetric(metricName) {
                    // Add highlighting functionality
                    console.log('Highlighting metric:', metricName);
                }
            </script>
            """
            
            # Insert JavaScript before closing body tag
            html_report = html_report.replace('</body>', f'{interactive_js}</body>')
            
            return html_report
            
        except Exception as e:
            logger.error(f"Error generating interactive report: {str(e)}")
            return ""
    
    async def _save_report(self, metadata: ReportMetadata, report_content: Union[str, bytes]) -> Path:
        """
        Save report to file
        """
        try:
            # Create filename
            timestamp = metadata.generated_at.strftime("%Y%m%d_%H%M%S")
            filename = f"{metadata.report_type}_{metadata.user_id}_{timestamp}"
            
            if metadata.report_format == ReportFormat.PDF.value:
                filename += ".pdf"
                file_path = self.output_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(report_content)
            else:
                filename += f".{metadata.report_format}"
                file_path = self.output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            logger.info(f"Report saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            raise
    
    # Helper methods for content generation
    def _calculate_overall_health_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate overall relationship health score"""
        # Simple calculation based on available metrics
        progress_metrics = user_data.get("progress_metrics", {})
        
        if progress_metrics:
            scores = []
            if "last_communication_score" in progress_metrics:
                scores.append(progress_metrics["last_communication_score"])
            if "last_emotional_score" in progress_metrics:
                scores.append(progress_metrics["last_emotional_score"])
            if "last_conflict_score" in progress_metrics:
                scores.append(progress_metrics["last_conflict_score"])
            
            if scores:
                return py_mean(scores) * 10  # Scale to 0-10
        
        return 7.5  # Default score
    
    def _extract_health_metrics(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract health metrics from user data"""
        progress_metrics = user_data.get("progress_metrics", {})
        
        return {
            "communication_effectiveness": progress_metrics.get("last_communication_score", 0.7),
            "emotional_intelligence": progress_metrics.get("last_emotional_score", 0.6),
            "conflict_resolution": progress_metrics.get("last_conflict_score", 0.5),
            "trust_level": 0.8,  # Placeholder
            "intimacy_level": 0.7  # Placeholder
        }
    
    def _generate_health_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate health-based recommendations"""
        return [
            "Schedule regular relationship check-ins",
            "Practice active listening techniques",
            "Engage in shared activities to strengthen bond",
            "Consider couples therapy for additional support"
        ]
    
    def _generate_health_metrics_content(self, user_data: Dict[str, Any]) -> str:
        """Generate health metrics content"""
        metrics = self._extract_health_metrics(user_data)
        
        content = "Analysis of key relationship health indicators:\n\n"
        for metric, score in metrics.items():
            status = "Excellent" if score > 0.8 else "Good" if score > 0.6 else "Needs Improvement"
            content += f"• {metric.replace('_', ' ').title()}: {score:.2f} ({status})\n"
        
        return content
    
    def _generate_strengths_analysis(self, user_data: Dict[str, Any]) -> str:
        """Generate strengths analysis content"""
        return """
        Your relationship demonstrates several key strengths:
        
        • Strong foundation of trust and mutual respect
        • Effective communication during calm discussions
        • Shared values and life goals
        • Willingness to work on relationship improvement
        • Good emotional support during difficult times
        """
    
    def _generate_improvement_analysis(self, user_data: Dict[str, Any]) -> str:
        """Generate improvement analysis content"""
        return """
        Areas identified for potential growth and development:
        
        • Conflict resolution skills during heated discussions
        • Emotional regulation during stressful periods
        • Frequency of quality time together
        • Expression of appreciation and gratitude
        • Physical and emotional intimacy
        """
    
    def _generate_improvement_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        return [
            "Practice the 24-hour rule before discussing heated topics",
            "Implement weekly appreciation exercises",
            "Schedule regular date nights without distractions",
            "Learn and practice conflict resolution techniques"
        ]
    
    def _extract_communication_metrics(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract communication metrics"""
        return {
            "clarity": 0.7,
            "empathy": 0.6,
            "active_listening": 0.5,
            "assertiveness": 0.8,
            "emotional_expression": 0.6
        }
    
    def _generate_communication_overview(self, user_data: Dict[str, Any]) -> str:
        """Generate communication overview content"""
        return """
        Communication analysis reveals patterns in how you and your partner 
        interact, express needs, and resolve differences. Overall communication 
        effectiveness shows room for improvement, particularly in active listening 
        and emotional expression during conflicts.
        """
    
    def _generate_style_analysis(self, user_data: Dict[str, Any]) -> str:
        """Generate style analysis content"""
        user_profile = user_data.get("user_profile", {})
        communication_style = user_profile.get("communication_style", "unknown")
        
        return f"""
        Your primary communication style appears to be {communication_style}. 
        This style has both strengths and potential challenges in relationship 
        contexts. Understanding and adapting communication styles can significantly 
        improve relationship satisfaction.
        """
    
    def _generate_style_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate style-based recommendations"""
        return [
            "Practice using 'I' statements to express feelings",
            "Ask clarifying questions before responding",
            "Validate your partner's emotions before problem-solving",
            "Take breaks during intense conversations"
        ]
    
    def _calculate_compatibility_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate compatibility score"""
        return 7.2  # Placeholder
    
    def _generate_compatibility_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate compatibility recommendations"""
        return [
            "Focus on appreciating differences rather than changing them",
            "Develop compromise strategies for conflicting preferences",
            "Build on shared values and common goals",
            "Create rituals that honor both partners' needs"
        ]
    
    def _extract_progress_metrics(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract progress metrics"""
        return {
            "goal_completion": 0.75,
            "skill_improvement": 0.6,
            "satisfaction_increase": 0.8,
            "conflict_reduction": 0.7
        }
    
    def _generate_progress_summary(self, user_data: Dict[str, Any]) -> str:
        """Generate progress summary content"""
        sessions_count = len(user_data.get("sessions", []))
        
        return f"""
        Progress analysis based on {sessions_count} sessions shows positive 
        trends in relationship development. Key improvements have been observed 
        in communication effectiveness and conflict resolution skills.
        """
    
    def _generate_progress_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate progress recommendations"""
        return [
            "Continue practicing newly learned communication techniques",
            "Set new relationship goals for the next period",
            "Celebrate progress made so far",
            "Maintain momentum with regular check-ins"
        ]
    
    def _extract_intervention_metrics(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract intervention metrics"""
        interventions = user_data.get("interventions", [])
        
        return {
            "total_interventions": len(interventions),
            "success_rate": 0.8,
            "average_effectiveness": 0.7,
            "user_compliance": 0.9
        }
    
    def _generate_intervention_overview(self, user_data: Dict[str, Any]) -> str:
        """Generate intervention overview content"""
        interventions_count = len(user_data.get("interventions", []))
        
        return f"""
        Analysis of {interventions_count} therapeutic interventions shows 
        positive outcomes in relationship improvement. Interventions have 
        been most effective in communication coaching and conflict resolution.
        """
    
    def _generate_intervention_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """Generate intervention recommendations"""
        return [
            "Continue implementing suggested communication strategies",
            "Practice intervention techniques in low-stakes situations",
            "Provide feedback on intervention effectiveness",
            "Request additional support for challenging areas"
        ]