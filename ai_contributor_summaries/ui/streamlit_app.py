"""Streamlit UI for AI Contributor Summaries."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import asyncio
import os
from utils.weaviate_client import weaviate_client
from graph.organization_graph import OrganizationGraph
from ui.analytics_page import render_analytics_page

# Page configuration
st.set_page_config(
    page_title="AI Contributor Summaries",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .contributor-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .repo-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .skill-tag {
        background: #e1f5fe;
        color: #0277bd;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .summary-box {
        background: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.repositories = []
    st.session_state.contributors = []
    st.session_state.repo_works = []

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["🏠 Dashboard", "📁 Repository Explorer", "👤 Contributor Explorer", "🌐 Graph View", "📊 Advanced Analytics"]
)

# Data loading function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from Weaviate or mock."""
    try:
        # Check if using mock mode
        if os.getenv('USE_MOCK_WEAVIATE') == 'true':
            from utils.mock_weaviate import mock_weaviate_client
            client = mock_weaviate_client
        else:
            from utils.weaviate_client import weaviate_client
            if weaviate_client is None:
                raise Exception("Weaviate not available")
            client = weaviate_client
        
        repositories = client.query_data("RepositoryWork", limit=1000)
        contributors = client.query_data("Contributor", limit=1000)
        repo_works = client.query_data("RepositoryWork", limit=1000)
        
        return repositories, contributors, repo_works
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.info("💡 Make sure to run the initialization first: `python run_app.py init --mock`")
        return [], [], []

# Load data
if not st.session_state.data_loaded:
    with st.spinner("Loading data..."):
        repositories, contributors, repo_works = load_data()
        st.session_state.repositories = repositories
        st.session_state.contributors = contributors
        st.session_state.repo_works = repo_works
        st.session_state.data_loaded = True

# Dashboard Page
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">🧠 AI Contributor Summaries</div>', unsafe_allow_html=True)
    
    # Metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_repos = len(set(rw.get('repository_id', '') for rw in st.session_state.repo_works))
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_repos}</h3>
            <p>Repositories</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_contributors = len(st.session_state.contributors)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_contributors}</h3>
            <p>Contributors</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_commits = sum(c.get('total_commits', 0) for c in st.session_state.contributors)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_commits:,}</h3>
            <p>Total Commits</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_issues = sum(c.get('total_issues', 0) for c in st.session_state.contributors)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_issues:,}</h3>
            <p>Total Issues</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity and top contributors
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top Contributors by Commits")
        top_contributors = sorted(
            st.session_state.contributors,
            key=lambda x: x.get('total_commits', 0),
            reverse=True
        )[:10]
        
        for i, contributor in enumerate(top_contributors, 1):
            st.markdown(f"""
            <div class="contributor-card">
                <strong>{i}. {contributor.get('username', 'Unknown')}</strong><br>
                <small>{contributor.get('total_commits', 0)} commits • {contributor.get('total_issues', 0)} issues</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📊 Repository Activity")
        repo_activity = {}
        for rw in st.session_state.repo_works:
            repo_name = rw.get('repository_name', 'Unknown')
            repo_activity[repo_name] = repo_activity.get(repo_name, 0) + rw.get('commit_count', 0)
        
        if repo_activity:
            df = pd.DataFrame(list(repo_activity.items()), columns=['Repository', 'Commits'])
            df = df.sort_values('Commits', ascending=False).head(10)
            
            fig = px.bar(df, x='Commits', y='Repository', orientation='h',
                        title="Top Repositories by Commit Count")
            st.plotly_chart(fig, use_container_width=True)

# Repository Explorer Page
elif page == "📁 Repository Explorer":
    st.markdown('<div class="main-header">📁 Repository Explorer</div>', unsafe_allow_html=True)
    
    # Search and filter
    search_term = st.text_input("🔍 Search repositories...", placeholder="Enter repository name or technology")
    
    # Group repository work by repository
    repos_data = {}
    for rw in st.session_state.repo_works:
        repo_id = rw.get('repository_id', 'Unknown')
        if repo_id not in repos_data:
            repos_data[repo_id] = {
                'name': rw.get('repository_name', repo_id.split('/')[-1]),
                'contributors': set(),
                'total_commits': 0,
                'total_issues': 0,
                'technologies': set(),
                'summaries': []
            }
        
        repos_data[repo_id]['contributors'].add(rw.get('contributor_id', 'Unknown'))
        repos_data[repo_id]['total_commits'] += rw.get('commit_count', 0)
        repos_data[repo_id]['total_issues'] += rw.get('issue_count', 0)
        repos_data[repo_id]['technologies'].update(rw.get('technologies', []))
        if rw.get('summary'):
            repos_data[repo_id]['summaries'].append(rw.get('summary'))
    
    # Filter repositories based on search
    filtered_repos = repos_data
    if search_term:
        filtered_repos = {
            k: v for k, v in repos_data.items()
            if search_term.lower() in k.lower() or
               search_term.lower() in v['name'].lower() or
               any(search_term.lower() in tech.lower() for tech in v['technologies'])
        }
    
    # Display repositories in a grid
    cols = st.columns(2)
    for i, (repo_id, repo_data) in enumerate(filtered_repos.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="repo-card">
                <h3>{repo_data['name']}</h3>
                <p><strong>Repository:</strong> {repo_id}</p>
                <p><strong>Contributors:</strong> {len(repo_data['contributors'])}</p>
                <p><strong>Commits:</strong> {repo_data['total_commits']}</p>
                <p><strong>Issues:</strong> {repo_data['total_issues']}</p>
                <p><strong>Technologies:</strong></p>
                <div>
                    {''.join(f'<span class="skill-tag">{tech}</span>' for tech in list(repo_data['technologies'])[:10])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show summary if available
            if repo_data['summaries']:
                with st.expander(f"📝 View Summary for {repo_data['name']}"):
                    for summary in repo_data['summaries'][:3]:  # Show first 3 summaries
                        st.markdown(f"""
                        <div class="summary-box">
                            {summary}
                        </div>
                        """, unsafe_allow_html=True)

# Contributor Explorer Page
elif page == "👤 Contributor Explorer":
    st.markdown('<div class="main-header">👤 Contributor Explorer</div>', unsafe_allow_html=True)
    
    # Search and filter
    search_term = st.text_input("🔍 Search contributors...", placeholder="Enter username or skill")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        min_commits = st.slider("Minimum commits", 0, 1000, 0)
    with col2:
        min_repos = st.slider("Minimum repositories", 0, 50, 0)
    
    # Filter contributors
    filtered_contributors = [
        c for c in st.session_state.contributors
        if (not search_term or 
            search_term.lower() in c.get('username', '').lower() or
            any(search_term.lower() in skill.lower() for skill in c.get('skills', []))) and
           c.get('total_commits', 0) >= min_commits and
           c.get('repositories_count', 0) >= min_repos
    ]
    
    # Sort options
    sort_by = st.selectbox("Sort by:", ["Total Commits", "Total Issues", "Repository Count", "Username"])
    
    if sort_by == "Total Commits":
        filtered_contributors.sort(key=lambda x: x.get('total_commits', 0), reverse=True)
    elif sort_by == "Total Issues":
        filtered_contributors.sort(key=lambda x: x.get('total_issues', 0), reverse=True)
    elif sort_by == "Repository Count":
        filtered_contributors.sort(key=lambda x: x.get('repositories_count', 0), reverse=True)
    else:
        filtered_contributors.sort(key=lambda x: x.get('username', ''))
    
    # Display contributors
    for contributor in filtered_contributors:
        with st.expander(f"👤 {contributor.get('username', 'Unknown')} - {contributor.get('total_commits', 0)} commits"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if contributor.get('avatar_url'):
                    st.image(contributor['avatar_url'], width=100)
                
                st.markdown(f"""
                **GitHub:** {contributor.get('username', 'Unknown')}  
                **Commits:** {contributor.get('total_commits', 0)}  
                **Issues:** {contributor.get('total_issues', 0)}  
                **Repositories:** {contributor.get('repositories_count', 0)}  
                **Activity:** {contributor.get('activity_level', 'Unknown')}
                """)
            
            with col2:
                # Skills
                if contributor.get('skills'):
                    st.markdown("**Skills:**")
                    skills_html = ''.join(f'<span class="skill-tag">{skill}</span>' for skill in contributor.get('skills', [])[:20])
                    st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)
                
                # Expertise areas
                if contributor.get('expertise_areas'):
                    st.markdown("**Expertise Areas:**")
                    expertise_html = ''.join(f'<span class="skill-tag">{area}</span>' for area in contributor.get('expertise_areas', [])[:10])
                    st.markdown(f'<div>{expertise_html}</div>', unsafe_allow_html=True)
                
                # Primary languages
                if contributor.get('primary_languages'):
                    st.markdown("**Primary Languages:**")
                    languages_html = ''.join(f'<span class="skill-tag">{lang}</span>' for lang in contributor.get('primary_languages', [])[:10])
                    st.markdown(f'<div>{languages_html}</div>', unsafe_allow_html=True)
                
                # AI-generated summary
                if contributor.get('summary'):
                    st.markdown("**AI-Generated Profile:**")
                    st.markdown(f"""
                    <div class="summary-box">
                        {contributor.get('summary')}
                    </div>
                    """, unsafe_allow_html=True)

# Graph View Page
elif page == "🌐 Graph View":
    st.markdown('<div class="main-header">🌐 Organization Graph</div>', unsafe_allow_html=True)
    
    # Graph controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_commits_filter = st.slider("Min commits for contributors", 0, 100, 5)
    with col2:
        min_contributors_filter = st.slider("Min contributors for repos", 0, 20, 2)
    with col3:
        max_nodes = st.slider("Max nodes to display", 10, 200, 50)
    
    # Create and display graph
    try:
        graph = OrganizationGraph()
        
        # Filter data based on controls
        filtered_contributors = [
            c for c in st.session_state.contributors
            if c.get('total_commits', 0) >= min_commits_filter
        ][:max_nodes//2]
        
        # Get repositories with enough contributors
        repo_contributor_count = {}
        for rw in st.session_state.repo_works:
            repo_id = rw.get('repository_id', 'Unknown')
            repo_contributor_count[repo_id] = repo_contributor_count.get(repo_id, 0) + 1
        
        filtered_repo_works = [
            rw for rw in st.session_state.repo_works
            if repo_contributor_count.get(rw.get('repository_id', ''), 0) >= min_contributors_filter
        ]
        
        # Create graph
        graph_html = graph.create_interactive_graph(
            filtered_contributors,
            filtered_repo_works,
            max_nodes=max_nodes
        )
        
        if graph_html:
            st.components.v1.html(graph_html, height=600)
        else:
            st.warning("No graph data available with current filters")
            
        # Network statistics
        st.markdown("---")
        st.subheader("📊 Network Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Contributors", len(filtered_contributors))
        
        with col2:
            unique_repos = len(set(rw.get('repository_id', '') for rw in filtered_repo_works))
            st.metric("Repositories", unique_repos)
        
        with col3:
            total_connections = len(filtered_repo_works)
            st.metric("Connections", total_connections)
        
        # Top connected nodes
        st.subheader("🌟 Most Connected Nodes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top Contributors by Repository Count:**")
            top_contributors = sorted(
                filtered_contributors,
                key=lambda x: x.get('repositories_count', 0),
                reverse=True
            )[:10]
            
            for i, contributor in enumerate(top_contributors, 1):
                st.write(f"{i}. {contributor.get('username', 'Unknown')} ({contributor.get('repositories_count', 0)} repos)")
        
        with col2:
            st.write("**Most Active Repositories:**")
            repo_activity = {}
            for rw in filtered_repo_works:
                repo_name = rw.get('repository_name', 'Unknown')
                repo_activity[repo_name] = repo_activity.get(repo_name, 0) + 1
            
            for i, (repo, count) in enumerate(sorted(repo_activity.items(), key=lambda x: x[1], reverse=True)[:10], 1):
                st.write(f"{i}. {repo} ({count} contributors)")
                
    except Exception as e:
        st.error(f"Failed to create graph: {e}")
        st.info("Make sure you have run the data ingestion and summarization pipeline first.")

# Advanced Analytics Page
elif page == "📊 Advanced Analytics":
    render_analytics_page(st.session_state.contributors, st.session_state.repo_works)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🧠 AI Contributor Summaries - Powered by FriendliAI, Weaviate, and Hypermode</p>
    <p>Built with Streamlit • Data refreshed every 5 minutes</p>
</div>
""", unsafe_allow_html=True)

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.session_state.data_loaded = False
    st.rerun()