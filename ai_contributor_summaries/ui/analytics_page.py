"""Advanced Analytics Page for Streamlit UI."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any
from analytics.insights_engine import InsightsEngine


def render_analytics_page(contributors: List[Dict], repo_works: List[Dict]):
    """Render the advanced analytics page."""
    st.markdown('<div class="main-header">📊 Advanced Analytics</div>', unsafe_allow_html=True)
    
    if not contributors or not repo_works:
        st.warning("No data available for analysis. Please run the ingestion process first.")
        return
    
    # Initialize insights engine
    insights_engine = InsightsEngine(contributors, repo_works)
    insights = insights_engine.generate_comprehensive_insights()
    
    # Sidebar for analytics options
    st.sidebar.header("📊 Analytics Options")
    analysis_type = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Overview", "Skill Analysis", "Repository Insights", "Contributor Segments", 
         "Collaboration Patterns", "Technology Trends", "Productivity Metrics", "Recommendations"]
    )
    
    # Render based on selection
    if analysis_type == "Overview":
        render_overview_analysis(insights.get('overview', {}))
    elif analysis_type == "Skill Analysis":
        render_skill_analysis(insights.get('skill_analysis', {}), contributors)
    elif analysis_type == "Repository Insights":
        render_repository_insights(insights.get('repository_insights', {}), repo_works)
    elif analysis_type == "Contributor Segments":
        render_contributor_segments(insights.get('contributor_segments', {}), contributors)
    elif analysis_type == "Collaboration Patterns":
        render_collaboration_analysis(insights.get('collaboration_patterns', {}))
    elif analysis_type == "Technology Trends":
        render_technology_trends(insights.get('technology_trends', {}))
    elif analysis_type == "Productivity Metrics":
        render_productivity_metrics(insights.get('productivity_metrics', {}))
    elif analysis_type == "Recommendations":
        render_recommendations(insights.get('recommendations', {}))


def render_overview_analysis(overview: Dict[str, Any]):
    """Render overview analytics."""
    st.header("🎯 Overview Analytics")
    
    if not overview:
        st.warning("No overview data available.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Contributors",
            overview.get('total_contributors', 0),
            help="Total number of contributors in the dataset"
        )
    
    with col2:
        st.metric(
            "Total Commits",
            f"{overview.get('total_commits', 0):,}",
            help="Total commits across all repositories"
        )
    
    with col3:
        st.metric(
            "Total Issues",
            f"{overview.get('total_issues', 0):,}",
            help="Total issues across all repositories"
        )
    
    with col4:
        st.metric(
            "Avg Repos/Contributor",
            f"{overview.get('avg_repos_per_contributor', 0):.1f}",
            help="Average number of repositories per contributor"
        )
    
    # Activity distribution
    st.subheader("📈 Activity Level Distribution")
    activity_dist = overview.get('activity_distribution', {})
    
    if activity_dist:
        fig = px.pie(
            values=list(activity_dist.values()),
            names=list(activity_dist.keys()),
            title="Contributors by Activity Level",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top programming languages
    st.subheader("💻 Top Programming Languages")
    top_languages = overview.get('top_languages', [])
    
    if top_languages:
        lang_df = pd.DataFrame(top_languages, columns=['Language', 'Count'])
        fig = px.bar(
            lang_df,
            x='Count',
            y='Language',
            orientation='h',
            title="Most Popular Programming Languages",
            color='Count',
            color_continuous_scale='viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Productivity indicators
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Commits per Contributor",
            f"{overview.get('commits_per_contributor', 0):.1f}",
            help="Average commits per contributor"
        )
    
    with col2:
        st.metric(
            "Issues per Contributor",
            f"{overview.get('issues_per_contributor', 0):.1f}",
            help="Average issues per contributor"
        )


def render_skill_analysis(skill_analysis: Dict[str, Any], contributors: List[Dict]):
    """Render skill analysis."""
    st.header("🧠 Skill Analysis")
    
    if not skill_analysis:
        st.warning("No skill analysis data available.")
        return
    
    # Skill metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Unique Skills",
            skill_analysis.get('total_unique_skills', 0),
            help="Total number of unique skills across all contributors"
        )
    
    with col2:
        st.metric(
            "Avg Skills per Contributor",
            f"{skill_analysis.get('avg_skills_per_contributor', 0):.1f}",
            help="Average number of skills per contributor"
        )
    
    with col3:
        st.metric(
            "Skill Diversity Index",
            f"{skill_analysis.get('skill_diversity_index', 0):.3f}",
            help="Measure of skill diversity (0-1, higher = more diverse)"
        )
    
    # Top skills visualization
    st.subheader("🔝 Most In-Demand Skills")
    top_skills = skill_analysis.get('top_skills', [])
    
    if top_skills:
        skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
        fig = px.bar(
            skills_df,
            x='Count',
            y='Skill',
            orientation='h',
            title="Most Common Skills",
            color='Count',
            color_continuous_scale='plasma'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Rare skills
    st.subheader("💎 Rare and Specialized Skills")
    rare_skills = skill_analysis.get('rare_skills', [])
    
    if rare_skills:
        st.write("These skills are possessed by fewer than 20% of contributors:")
        
        # Create columns for rare skills
        cols = st.columns(3)
        for i, skill in enumerate(rare_skills):
            with cols[i % 3]:
                st.markdown(f"**{skill}**")
    
    # Skill distribution heatmap
    st.subheader("📊 Skill Distribution Heatmap")
    
    # Create skill matrix
    if contributors:
        skill_matrix_data = []
        all_skills = set()
        
        for contributor in contributors:
            skills = contributor.get('skills', [])
            if isinstance(skills, list):
                all_skills.update(skills)
        
        # Limit to top 20 skills for visualization
        top_skill_names = [skill for skill, _ in top_skills[:20]]
        
        for contributor in contributors:
            username = contributor.get('username', 'Unknown')
            skills = contributor.get('skills', [])
            skill_row = []
            
            for skill in top_skill_names:
                skill_row.append(1 if skill in skills else 0)
            
            skill_matrix_data.append([username] + skill_row)
        
        if skill_matrix_data:
            skill_df = pd.DataFrame(skill_matrix_data, columns=['Contributor'] + top_skill_names)
            skill_df = skill_df.set_index('Contributor')
            
            fig = px.imshow(
                skill_df,
                aspect="auto",
                color_continuous_scale='viridis',
                title="Contributor Skill Matrix"
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)


def render_repository_insights(repo_insights: Dict[str, Any], repo_works: List[Dict]):
    """Render repository insights."""
    st.header("📁 Repository Insights")
    
    if not repo_insights:
        st.warning("No repository insights available.")
        return
    
    # Repository metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Repositories",
            repo_insights.get('total_repositories', 0),
            help="Total number of repositories analyzed"
        )
    
    with col2:
        st.metric(
            "Avg Contributors per Repo",
            f"{repo_insights.get('avg_contributors_per_repo', 0):.1f}",
            help="Average number of contributors per repository"
        )
    
    # Most active repositories
    st.subheader("🔥 Most Active Repositories")
    most_active = repo_insights.get('most_active_repositories', {})
    
    if most_active:
        active_df = pd.DataFrame.from_dict(most_active, orient='index')
        active_df = active_df.reset_index().rename(columns={'index': 'Repository'})
        
        fig = px.bar(
            active_df,
            x='commit_count',
            y='Repository',
            orientation='h',
            title="Repositories by Commit Count",
            color='commit_count',
            color_continuous_scale='reds'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Repository diversity
    st.subheader("🌈 Most Technologically Diverse Repositories")
    diverse_repos = repo_insights.get('most_diverse_repositories', [])
    
    if diverse_repos:
        diverse_df = pd.DataFrame(diverse_repos, columns=['Repository', 'Technology Count'])
        fig = px.bar(
            diverse_df,
            x='Technology Count',
            y='Repository',
            orientation='h',
            title="Repositories by Technology Diversity",
            color='Technology Count',
            color_continuous_scale='viridis'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)


def render_contributor_segments(segments: Dict[str, Any], contributors: List[Dict]):
    """Render contributor segmentation analysis."""
    st.header("👥 Contributor Segments")
    
    if not segments:
        st.warning("No segmentation data available.")
        return
    
    segment_stats = segments.get('segment_statistics', {})
    
    # Segment distribution
    st.subheader("📊 Contributor Segmentation")
    
    if segment_stats:
        # Create pie chart
        fig = px.pie(
            values=[stats['count'] for stats in segment_stats.values()],
            names=list(segment_stats.keys()),
            title="Contributor Segments Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Segment details
        st.subheader("📋 Segment Details")
        for segment, stats in segment_stats.items():
            with st.expander(f"{segment.replace('_', ' ').title()} ({stats['count']} contributors)"):
                st.write(f"**Percentage:** {stats['percentage']:.1f}%")
                
                # Show criteria
                criteria = segments.get('segmentation_criteria', {})
                if segment in criteria:
                    st.write(f"**Criteria:** {criteria[segment]}")
                
                # Show some contributors in this segment
                segment_contributors = segments.get('segments', {}).get(segment, [])
                if segment_contributors:
                    st.write(f"**Sample Contributors:** {', '.join(segment_contributors[:5])}")


def render_collaboration_analysis(collab_patterns: Dict[str, Any]):
    """Render collaboration patterns analysis."""
    st.header("🤝 Collaboration Patterns")
    
    if not collab_patterns:
        st.warning("No collaboration data available.")
        return
    
    # Collaboration metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Collaborations",
            collab_patterns.get('total_collaborations', 0),
            help="Number of contributor pairs who worked on same repositories"
        )
    
    with col2:
        st.metric(
            "Avg Collaborators per Repo",
            f"{collab_patterns.get('avg_collaborators_per_repo', 0):.1f}",
            help="Average number of collaborators per repository"
        )
    
    # Top collaborations
    st.subheader("🔗 Most Frequent Collaborations")
    top_collaborations = collab_patterns.get('top_collaborations', [])
    
    if top_collaborations:
        collab_df = pd.DataFrame([
            {'Contributor 1': pair[0], 'Contributor 2': pair[1], 'Shared Repositories': count}
            for (pair, count) in top_collaborations
        ])
        
        fig = px.bar(
            collab_df,
            x='Shared Repositories',
            y=[f"{row['Contributor 1']} ↔ {row['Contributor 2']}" for _, row in collab_df.iterrows()],
            orientation='h',
            title="Most Frequent Collaborator Pairs",
            color='Shared Repositories',
            color_continuous_scale='blues'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Most collaborative repositories
    st.subheader("🌟 Most Collaborative Repositories")
    collaborative_repos = collab_patterns.get('most_collaborative_repositories', [])
    
    if collaborative_repos:
        collab_repo_df = pd.DataFrame(collaborative_repos, columns=['Repository', 'Collaboration Score'])
        
        fig = px.bar(
            collab_repo_df,
            x='Collaboration Score',
            y='Repository',
            orientation='h',
            title="Repositories with Highest Collaboration",
            color='Collaboration Score',
            color_continuous_scale='greens'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)


def render_technology_trends(tech_trends: Dict[str, Any]):
    """Render technology trends analysis."""
    st.header("🚀 Technology Trends")
    
    if not tech_trends:
        st.warning("No technology trends data available.")
        return
    
    # Technology metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Technologies",
            tech_trends.get('total_technologies', 0),
            help="Total unique technologies across all repositories"
        )
    
    with col2:
        st.metric(
            "Avg Technologies per Repo",
            f"{tech_trends.get('avg_technologies_per_repo', 0):.1f}",
            help="Average number of technologies per repository"
        )
    
    # Popular technologies
    st.subheader("📈 Most Popular Technologies")
    popular_techs = tech_trends.get('popular_technologies', [])
    
    if popular_techs:
        tech_df = pd.DataFrame(popular_techs, columns=['Technology', 'Usage Count'])
        
        fig = px.bar(
            tech_df,
            x='Usage Count',
            y='Technology',
            orientation='h',
            title="Technology Adoption Rates",
            color='Usage Count',
            color_continuous_scale='plasma'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Emerging technologies
    st.subheader("🌱 Emerging Technologies")
    emerging_techs = tech_trends.get('emerging_technologies', [])
    
    if emerging_techs:
        st.write("These technologies are used in less than 10% of repositories but show potential:")
        
        cols = st.columns(3)
        for i, tech in enumerate(emerging_techs):
            with cols[i % 3]:
                st.markdown(f"**{tech}**")


def render_productivity_metrics(productivity: Dict[str, Any]):
    """Render productivity metrics."""
    st.header("⚡ Productivity Metrics")
    
    if not productivity:
        st.warning("No productivity data available.")
        return
    
    # Productivity overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Avg Commits per Repo",
            f"{productivity.get('avg_commits_per_repo', 0):.1f}",
            help="Average commits per repository across all contributors"
        )
    
    with col2:
        percentiles = productivity.get('productivity_percentiles', {})
        st.metric(
            "Top 25% Productivity",
            f"{percentiles.get('75th', 0):.1f}",
            help="75th percentile of commits per repository"
        )
    
    # Top productive contributors
    st.subheader("🏆 Most Productive Contributors")
    top_productive = productivity.get('top_productive_contributors', [])
    
    if top_productive:
        productive_df = pd.DataFrame(top_productive)
        
        fig = px.bar(
            productive_df,
            x='commits_per_repo',
            y='username',
            orientation='h',
            title="Contributors by Productivity (Commits per Repository)",
            color='commits_per_repo',
            color_continuous_scale='reds'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Productivity distribution
    st.subheader("📊 Productivity Distribution")
    percentiles = productivity.get('productivity_percentiles', {})
    
    if percentiles:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(percentiles.keys()),
            y=list(percentiles.values()),
            name='Productivity Percentiles',
            marker_color='lightblue'
        ))
        fig.update_layout(
            title="Productivity Distribution (Commits per Repository)",
            xaxis_title="Percentile",
            yaxis_title="Commits per Repository"
        )
        st.plotly_chart(fig, use_container_width=True)


def render_recommendations(recommendations: Dict[str, List[str]]):
    """Render recommendations."""
    st.header("💡 Recommendations")
    
    if not recommendations:
        st.warning("No recommendations available.")
        return
    
    # Team composition recommendations
    st.subheader("👥 Team Composition")
    team_recs = recommendations.get('team_composition', [])
    for rec in team_recs:
        st.write(f"• {rec}")
    
    # Skill development recommendations
    st.subheader("📚 Skill Development")
    skill_recs = recommendations.get('skill_development', [])
    for rec in skill_recs:
        st.write(f"• {rec}")
    
    # Process improvement recommendations
    st.subheader("⚙️ Process Improvement")
    process_recs = recommendations.get('process_improvement', [])
    for rec in process_recs:
        st.write(f"• {rec}")
    
    # Technology adoption recommendations
    st.subheader("🔧 Technology Adoption")
    tech_recs = recommendations.get('technology_adoption', [])
    for rec in tech_recs:
        st.write(f"• {rec}")