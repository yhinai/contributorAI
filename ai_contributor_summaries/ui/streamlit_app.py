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
from config.settings import settings
from utils.weaviate_client import weaviate_client
from utils.mock_weaviate import mock_weaviate_client
from graph.organization_graph import OrganizationGraph
from ui.analytics_page import render_analytics_page

# Page configuration
st.set_page_config(
    page_title="AI Contributor Summaries",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Futuristic UI Styling
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    .stDeployButton, .stDecoration, footer {
        display: none !important;
    }
    
    /* Main container */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Headers */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 3rem;
        letter-spacing: -0.02em;
        position: relative;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
    }
    
    /* Glassmorphism cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-card p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
    }
    
    /* Enhanced contributor cards */
    .contributor-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .contributor-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        transition: width 0.3s ease;
    }
    
    .contributor-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        transition: width 0.3s ease;
    }
    
    .contributor-card:hover::before {
        width: 6px;
    }
    
    .contributor-card:hover::after {
        width: 100%;
    }
    
    .contributor-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Enhanced repository cards */
    .repo-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .repo-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(135deg, #764ba2, #667eea);
        transition: width 0.3s ease;
    }
    
    .repo-card::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(135deg, rgba(118, 75, 162, 0.1), rgba(102, 126, 234, 0.1));
        transition: width 0.3s ease;
    }
    
    .repo-card:hover::before {
        width: 6px;
    }
    
    .repo-card:hover::after {
        width: 100%;
    }
    
    .repo-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 40px rgba(118, 75, 162, 0.2);
        border-color: rgba(118, 75, 162, 0.3);
    }
    
    /* Enhanced skill tags */
    .skill-tag {
        background: rgba(102, 126, 234, 0.2);
        color: #667eea;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        margin: 0.3rem;
        display: inline-block;
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 500;
        cursor: default;
        position: relative;
        overflow: hidden;
    }
    
    .skill-tag::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .skill-tag:hover::before {
        left: 100%;
    }
    
    .skill-tag:hover {
        background: rgba(102, 126, 234, 0.3);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* Summary boxes */
    .summary-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 12px 12px 0;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Sidebar text */
    .css-1d391kg .css-1v0mbdj {
        color: #ffffff;
    }
    
    /* Enhanced buttons with subtle animation */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.5);
    }
    
    /* Enhanced select boxes */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #ffffff;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stSelectbox > div > div:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Enhanced text inputs */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #ffffff;
        padding: 0.8rem 1rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* Enhanced navigation styling */
    .css-1d391kg {
        background: rgba(10, 10, 10, 0.95);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Loading states */
    .stSpinner {
        border-color: #667eea;
    }
    
    /* Enhanced form elements */
    .stSlider > div > div > div {
        background: rgba(102, 126, 234, 0.2);
    }
    
    .stSlider > div > div > div > div {
        background: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
    }
    
    /* Enhanced tooltips */
    .stTooltip {
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    /* Enhanced metrics with subtle glow */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        transform: rotate(45deg);
        transition: all 0.3s ease;
        opacity: 0;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    /* Enhanced plotly charts */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Enhanced expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* Enhanced table styling */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    /* Responsive design with better breakpoints */
    @media (max-width: 1200px) {
        .main .block-container {
            padding: 1.5rem 1rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
    }
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            margin: 0.5rem;
            padding: 1.5rem;
        }
        
        .metric-card h3 {
            font-size: 2rem;
        }
        
        .contributor-card, .repo-card {
            padding: 1rem;
        }
        
        .main .block-container {
            padding: 1rem 0.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }
        
        .metric-card {
            margin: 0.25rem;
            padding: 1rem;
        }
        
        .metric-card h3 {
            font-size: 1.5rem;
        }
        
        .skill-tag {
            font-size: 0.7rem;
            padding: 0.3rem 0.8rem;
            margin: 0.2rem;
        }
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-top: 2px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
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
        if settings.use_mock_weaviate:
            client = mock_weaviate_client
        else:
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

# Load data with enhanced loading experience
if not st.session_state.data_loaded:
    # Enhanced loading with custom spinner
    st.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
    with st.spinner("🔄 Loading data... Please wait"):
        repositories, contributors, repo_works = load_data()
        st.session_state.repositories = repositories
        st.session_state.contributors = contributors
        st.session_state.repo_works = repo_works
        st.session_state.data_loaded = True

# Dashboard Page with enhanced animations
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">🧠 AI Contributor Summaries</div>', unsafe_allow_html=True)
    
    # Add subtle intro animation
    st.markdown("""
    <div style="
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in-out;
    ">
        Discover insights from your development team's contributions
    </div>
    
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown("""
    <div style="
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in-out;
    ">
        Explore repositories and their contribution patterns
    </div>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown("""
    <div style="
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in-out;
    ">
        Discover talented contributors and their expertise
    </div>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown("""
    <div style="
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in-out;
    ">
        Visualize the network of contributors and repositories
    </div>
    """, unsafe_allow_html=True)
    
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

# Enhanced footer with better styling
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="
    text-align: center;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 3rem;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
">
    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">🧠 AI Contributor Summaries</p>
    <p style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.5);">
        Powered by FriendliAI, Weaviate, and Hypermode • Built with Streamlit
    </p>
    <p style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.4); margin-top: 0.5rem;">
        Data refreshed every 5 minutes
    </p>
</div>
""", unsafe_allow_html=True)

# Enhanced refresh button with better placement
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        st.cache_data.clear()
        st.session_state.data_loaded = False
        st.rerun()