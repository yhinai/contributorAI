"""Enhanced Streamlit app using mock data from weaviate_org_data file."""

import streamlit as st
import json
import logging
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import numpy as np
from collections import defaultdict, Counter
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMockApp:
    """Enhanced mock app with detailed analysis capabilities."""
    
    def __init__(self):
        """Initialize the app."""
        self.data = None
        self.contributors = {}
        self.skills_analysis = {}
        self.repositories = {}
        self.contributions = []
        self.analytics = {}
        self._load_data()
        self._process_data()
    
    def _load_data(self):
        """Load data from the weaviate_org_data file."""
        try:
            data_file = "/Users/alhinai/Desktop/github/weaviate_org_data"
            with open(data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            logger.info(f"Loaded data for {self.data['analysis_metadata']['total_contributors']} contributors")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            st.error(f"Failed to load data: {e}")
    
    def _process_data(self):
        """Process the loaded data for analysis."""
        if not self.data:
            return
        
        # Process contributors
        for username, contributor_data in self.data['contributors'].items():
            # Process basic profile
            profile = contributor_data['profile']
            
            # Calculate total contributions
            total_contributions = sum(
                contrib.get('contributions', 0) 
                for contrib in contributor_data.get('contributions', [])
            )
            
            # Process skills
            skills = contributor_data.get('skills', {})
            
            # Store processed contributor data
            self.contributors[username] = {
                'username': username,
                'profile': profile,
                'total_contributions': total_contributions,
                'total_repositories': len(contributor_data.get('contributions', [])),
                'skills': skills,
                'contributions': contributor_data.get('contributions', []),
                'summary': contributor_data.get('summary', ''),
                'tech_stack': contributor_data.get('tech_stack', []),
                'expertise_level': contributor_data.get('expertise_level', 'intermediate')
            }
            
            # Process skills for analysis
            if skills:
                self.skills_analysis[username] = skills
            
            # Process repositories
            for contrib in contributor_data.get('contributions', []):
                repo_name = contrib['repo_full_name']
                if repo_name not in self.repositories:
                    self.repositories[repo_name] = {
                        'name': contrib['repo_name'],
                        'full_name': contrib['repo_full_name'],
                        'primary_language': contrib['primary_language'],
                        'languages': contrib.get('languages', {}),
                        'topics': contrib.get('topics', []),
                        'description': contrib.get('repo_description', ''),
                        'size': contrib.get('repo_size', 0),
                        'stars': contrib.get('stars', 0),
                        'forks': contrib.get('forks', 0),
                        'contributors': []
                    }
                
                # Add contributor to repository
                self.repositories[repo_name]['contributors'].append({
                    'username': username,
                    'contributions': contrib['contributions'],
                    'primary_language': contrib['primary_language']
                })
                
                # Store individual contribution
                self.contributions.append({
                    'username': username,
                    'repo_name': repo_name,
                    'contributions': contrib['contributions'],
                    'primary_language': contrib['primary_language'],
                    'languages': contrib.get('languages', {})
                })
        
        # Generate analytics
        self._generate_analytics()
    
    def _generate_analytics(self):
        """Generate comprehensive analytics."""
        # Top contributors
        top_contributors = sorted(
            self.contributors.values(),
            key=lambda x: x['total_contributions'],
            reverse=True
        )[:20]
        
        # Language analysis
        language_stats = defaultdict(lambda: {'total_score': 0, 'contributors': 0, 'avg_score': 0})
        domain_stats = defaultdict(lambda: {'total_score': 0, 'contributors': 0, 'avg_score': 0})
        
        for username, skills in self.skills_analysis.items():
            # Programming languages
            lang_scores = skills.get('programming_languages', {})
            for lang, score in lang_scores.items():
                if score > 0:
                    language_stats[lang]['total_score'] += score
                    language_stats[lang]['contributors'] += 1
            
            # Domain expertise
            domain_scores = skills.get('domains', {})
            for domain, score in domain_scores.items():
                if score > 0:
                    domain_stats[domain]['total_score'] += score
                    domain_stats[domain]['contributors'] += 1
        
        # Calculate averages
        for lang_data in language_stats.values():
            lang_data['avg_score'] = lang_data['total_score'] / lang_data['contributors']
        
        for domain_data in domain_stats.values():
            domain_data['avg_score'] = domain_data['total_score'] / domain_data['contributors']
        
        # Repository analysis
        repo_stats = []
        for repo_name, repo_data in self.repositories.items():
            total_contributions = sum(c['contributions'] for c in repo_data['contributors'])
            repo_stats.append({
                'name': repo_data['name'],
                'full_name': repo_name,
                'contributors': len(repo_data['contributors']),
                'total_contributions': total_contributions,
                'primary_language': repo_data['primary_language'],
                'stars': repo_data['stars'],
                'forks': repo_data['forks'],
                'size': repo_data['size']
            })
        
        repo_stats.sort(key=lambda x: x['total_contributions'], reverse=True)
        
        # Technology trends
        tech_usage = defaultdict(int)
        for contrib in self.contributions:
            for lang, lines in contrib['languages'].items():
                tech_usage[lang] += lines
        
        # Expertise levels
        expertise_distribution = defaultdict(int)
        for contributor in self.contributors.values():
            level = contributor['expertise_level']
            expertise_distribution[level] += 1
        
        # Store analytics
        self.analytics = {
            'top_contributors': top_contributors,
            'language_stats': dict(language_stats),
            'domain_stats': dict(domain_stats),
            'repo_stats': repo_stats,
            'tech_usage': dict(tech_usage),
            'expertise_distribution': dict(expertise_distribution),
            'total_contributors': len(self.contributors),
            'total_repositories': len(self.repositories),
            'total_contributions': sum(c['total_contributions'] for c in self.contributors.values())
        }
    
    def run(self):
        """Run the Streamlit app."""
        st.set_page_config(
            page_title="Weaviate Organization Analysis",
            page_icon="🚀",
            layout="wide"
        )
        
        st.title("🚀 Weaviate Organization Deep Analysis")
        st.write("### Comprehensive analysis of 912 contributors from Weaviate organization")
        
        if not self.data:
            st.error("Failed to load data. Please check the data file.")
            return
        
        # Display metadata
        metadata = self.data['analysis_metadata']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Contributors", metadata['total_contributors'])
        with col2:
            st.metric("Total Repositories", metadata['total_repositories'])
        with col3:
            st.metric("Analysis Type", metadata['analysis_type'])
        with col4:
            st.metric("Analysis Date", metadata['analysis_date'][:10])
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Search & Explore", 
            "📊 Analytics Dashboard", 
            "🧠 Skills Analysis", 
            "📈 Repository Insights",
            "👥 Contributor Profiles"
        ])
        
        with tab1:
            self._create_search_tab()
        
        with tab2:
            self._create_analytics_tab()
        
        with tab3:
            self._create_skills_tab()
        
        with tab4:
            self._create_repository_tab()
        
        with tab5:
            self._create_profiles_tab()
    
    def _create_search_tab(self):
        """Create search and exploration tab."""
        st.header("🔍 Search & Explore")
        
        # Search functionality
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            search_query = st.text_input("Search contributors, technologies, or repositories:")
        
        with search_col2:
            search_type = st.selectbox("Search by:", ["Contributors", "Technologies", "Repositories"])
        
        if search_query:
            self._perform_search(search_query, search_type)
        
        # Quick filters
        st.subheader("Quick Filters")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            if st.button("🐍 Python Experts"):
                self._filter_by_skill("Python", "programming_languages")
        
        with filter_col2:
            if st.button("☕ JavaScript Developers"):
                self._filter_by_skill("JavaScript", "programming_languages")
        
        with filter_col3:
            if st.button("🤖 ML Specialists"):
                self._filter_by_skill("machine-learning", "domains")
        
        # Advanced filters
        st.subheader("Advanced Filters")
        
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        
        with adv_col1:
            min_contributions = st.slider("Minimum Contributions", 0, 1000, 10)
        
        with adv_col2:
            expertise_level = st.selectbox("Expertise Level", ["All", "beginner", "intermediate", "advanced", "expert"])
        
        with adv_col3:
            min_repos = st.slider("Minimum Repositories", 0, 50, 1)
        
        # Apply filters
        filtered_contributors = self._apply_filters(min_contributions, expertise_level, min_repos)
        
        if filtered_contributors:
            st.write(f"**Found {len(filtered_contributors)} contributors matching your criteria:**")
            
            for contributor in filtered_contributors[:10]:  # Show top 10
                with st.expander(f"#{contributor['rank']} {contributor['username']} ({contributor['total_contributions']} contributions)"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if contributor['profile'].get('avatar_url'):
                            st.image(contributor['profile']['avatar_url'], width=100)
                    
                    with col2:
                        st.write(f"**Name:** {contributor['profile'].get('name', 'N/A')}")
                        st.write(f"**Location:** {contributor['profile'].get('location', 'N/A')}")
                        st.write(f"**Company:** {contributor['profile'].get('company', 'N/A')}")
                        st.write(f"**Repositories:** {contributor['total_repositories']}")
                        st.write(f"**Expertise:** {contributor['expertise_level']}")
                        
                        # Show top skills
                        skills = contributor.get('skills', {})
                        if skills:
                            st.write("**Top Skills:**")
                            lang_skills = skills.get('programming_languages', {})
                            top_langs = sorted(lang_skills.items(), key=lambda x: x[1], reverse=True)[:3]
                            for lang, score in top_langs:
                                st.write(f"  • {lang}: {score:.2f}")
    
    def _create_analytics_tab(self):
        """Create analytics dashboard tab."""
        st.header("📊 Analytics Dashboard")
        
        # Key metrics
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric("Total Contributors", self.analytics['total_contributors'])
        with metrics_col2:
            st.metric("Total Contributions", f"{self.analytics['total_contributions']:,}")
        with metrics_col3:
            st.metric("Total Repositories", self.analytics['total_repositories'])
        with metrics_col4:
            avg_contrib = self.analytics['total_contributions'] / self.analytics['total_contributors']
            st.metric("Avg Contributions/User", f"{avg_contrib:.0f}")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Top contributors
            top_contribs = self.analytics['top_contributors'][:10]
            df_top = pd.DataFrame([{
                'Username': c['username'],
                'Contributions': c['total_contributions'],
                'Repositories': c['total_repositories']
            } for c in top_contribs])
            
            fig_top = px.bar(
                df_top,
                x='Username',
                y='Contributions',
                title='Top 10 Contributors',
                hover_data=['Repositories']
            )
            fig_top.update_xaxes(tickangle=45)
            st.plotly_chart(fig_top, use_container_width=True)
        
        with chart_col2:
            # Programming language distribution
            lang_data = []
            for lang, stats in self.analytics['language_stats'].items():
                if stats['contributors'] > 5:  # Only show languages with 5+ contributors
                    lang_data.append({
                        'Language': lang,
                        'Contributors': stats['contributors'],
                        'Avg Score': stats['avg_score']
                    })
            
            df_lang = pd.DataFrame(lang_data)
            if not df_lang.empty:
                fig_lang = px.scatter(
                    df_lang,
                    x='Contributors',
                    y='Avg Score',
                    size='Contributors',
                    hover_name='Language',
                    title='Programming Language Analysis'
                )
                st.plotly_chart(fig_lang, use_container_width=True)
        
        # Domain expertise analysis
        st.subheader("Domain Expertise Analysis")
        
        domain_data = []
        for domain, stats in self.analytics['domain_stats'].items():
            if stats['contributors'] > 3:
                domain_data.append({
                    'Domain': domain.replace('-', ' ').title(),
                    'Contributors': stats['contributors'],
                    'Avg Score': stats['avg_score'],
                    'Total Score': stats['total_score']
                })
        
        df_domain = pd.DataFrame(domain_data)
        if not df_domain.empty:
            fig_domain = px.bar(
                df_domain,
                x='Domain',
                y='Contributors',
                title='Contributors by Domain Expertise',
                hover_data=['Avg Score']
            )
            fig_domain.update_xaxes(tickangle=45)
            st.plotly_chart(fig_domain, use_container_width=True)
        
        # Repository analysis
        st.subheader("Repository Analysis")
        
        repo_data = self.analytics['repo_stats'][:15]
        df_repo = pd.DataFrame(repo_data)
        
        fig_repo = px.scatter(
            df_repo,
            x='contributors',
            y='total_contributions',
            size='stars',
            hover_name='name',
            color='primary_language',
            title='Repository Analysis (size = stars)'
        )
        st.plotly_chart(fig_repo, use_container_width=True)
        
        # Technology usage heatmap
        st.subheader("Technology Usage (Lines of Code)")
        
        tech_data = sorted(self.analytics['tech_usage'].items(), key=lambda x: x[1], reverse=True)[:20]
        df_tech = pd.DataFrame(tech_data, columns=['Technology', 'Lines of Code'])
        
        fig_tech = px.bar(
            df_tech,
            x='Technology',
            y='Lines of Code',
            title='Top 20 Technologies by Usage'
        )
        fig_tech.update_xaxes(tickangle=45)
        st.plotly_chart(fig_tech, use_container_width=True)
    
    def _create_skills_tab(self):
        """Create skills analysis tab."""
        st.header("🧠 Skills Analysis")
        
        # Skills overview
        st.subheader("Skills Overview")
        
        # Programming languages skill distribution
        lang_skills = defaultdict(list)
        for username, skills in self.skills_analysis.items():
            lang_scores = skills.get('programming_languages', {})
            for lang, score in lang_scores.items():
                if score > 0:
                    lang_skills[lang].append(score)
        
        # Create skills distribution chart
        skill_dist_data = []
        for lang, scores in lang_skills.items():
            if len(scores) > 10:  # Only show languages with 10+ users
                skill_dist_data.append({
                    'Language': lang,
                    'Users': len(scores),
                    'Avg Score': np.mean(scores),
                    'Max Score': max(scores),
                    'Min Score': min(scores)
                })
        
        df_skill_dist = pd.DataFrame(skill_dist_data)
        if not df_skill_dist.empty:
            fig_skill_dist = px.bar(
                df_skill_dist,
                x='Language',
                y='Avg Score',
                title='Average Programming Language Skills',
                hover_data=['Users', 'Max Score', 'Min Score']
            )
            fig_skill_dist.update_xaxes(tickangle=45)
            st.plotly_chart(fig_skill_dist, use_container_width=True)
        
        # Skill correlation analysis
        st.subheader("Skill Correlation Analysis")
        
        # Find users with multiple skills
        multi_skill_users = []
        for username, skills in self.skills_analysis.items():
            lang_scores = skills.get('programming_languages', {})
            domain_scores = skills.get('domains', {})
            
            user_skills = {
                'username': username,
                'python': lang_scores.get('Python', 0),
                'javascript': lang_scores.get('JavaScript', 0),
                'go': lang_scores.get('Go', 0),
                'typescript': lang_scores.get('TypeScript', 0),
                'web_dev': domain_scores.get('web-development', 0),
                'ml': domain_scores.get('machine-learning', 0),
                'data_science': domain_scores.get('data-science', 0),
                'devops': domain_scores.get('devops', 0)
            }
            
            # Only include users with at least 2 skills > 0.3
            skill_count = sum(1 for v in user_skills.values() if isinstance(v, (int, float)) and v > 0.3)
            if skill_count >= 2:
                multi_skill_users.append(user_skills)
        
        if multi_skill_users:
            df_multi = pd.DataFrame(multi_skill_users)
            numeric_cols = ['python', 'javascript', 'go', 'typescript', 'web_dev', 'ml', 'data_science', 'devops']
            correlation_matrix = df_multi[numeric_cols].corr()
            
            fig_corr = px.imshow(
                correlation_matrix,
                title='Skill Correlation Matrix',
                aspect='auto',
                color_continuous_scale='RdBu'
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        
        # Top performers by skill
        st.subheader("Top Performers by Skill")
        
        skill_select = st.selectbox(
            "Select a skill to see top performers:",
            ["Python", "JavaScript", "Go", "TypeScript", "web-development", "machine-learning", "data-science", "devops"]
        )
        
        if skill_select:
            top_performers = self._get_top_performers(skill_select)
            
            if top_performers:
                st.write(f"**Top 10 performers in {skill_select}:**")
                
                for i, (username, score) in enumerate(top_performers[:10]):
                    contributor = self.contributors[username]
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        st.write(f"**#{i+1}**")
                        if contributor['profile'].get('avatar_url'):
                            st.image(contributor['profile']['avatar_url'], width=50)
                    
                    with col2:
                        st.write(f"**{username}**")
                        st.write(f"Score: {score:.2f}")
                        st.write(f"Contributions: {contributor['total_contributions']}")
                        if contributor['profile'].get('company'):
                            st.write(f"Company: {contributor['profile']['company']}")
                    
                    with col3:
                        st.write(f"**Repos: {contributor['total_repositories']}**")
                        st.write(f"Level: {contributor['expertise_level']}")
    
    def _create_repository_tab(self):
        """Create repository insights tab."""
        st.header("📈 Repository Insights")
        
        # Repository stats
        repo_stats = self.analytics['repo_stats']
        
        # Top repositories
        st.subheader("Top Repositories by Activity")
        
        top_repos = repo_stats[:10]
        df_top_repos = pd.DataFrame(top_repos)
        
        fig_top_repos = px.bar(
            df_top_repos,
            x='name',
            y='total_contributions',
            title='Top 10 Repositories by Contributions',
            hover_data=['contributors', 'stars', 'primary_language']
        )
        fig_top_repos.update_xaxes(tickangle=45)
        st.plotly_chart(fig_top_repos, use_container_width=True)
        
        # Language distribution across repositories
        st.subheader("Language Distribution Across Repositories")
        
        lang_repo_count = defaultdict(int)
        for repo in repo_stats:
            lang_repo_count[repo['primary_language']] += 1
        
        df_lang_repos = pd.DataFrame(
            list(lang_repo_count.items()),
            columns=['Language', 'Repository Count']
        )
        
        fig_lang_repos = px.pie(
            df_lang_repos,
            values='Repository Count',
            names='Language',
            title='Primary Language Distribution Across Repositories'
        )
        st.plotly_chart(fig_lang_repos, use_container_width=True)
        
        # Repository details
        st.subheader("Repository Details")
        
        selected_repo = st.selectbox(
            "Select a repository for detailed analysis:",
            [repo['name'] for repo in repo_stats[:20]]
        )
        
        if selected_repo:
            repo_data = None
            repo_full_name = None
            
            for repo in repo_stats:
                if repo['name'] == selected_repo:
                    repo_data = repo
                    repo_full_name = repo['full_name']
                    break
            
            if repo_data and repo_full_name in self.repositories:
                repo_details = self.repositories[repo_full_name]
                
                # Repository metrics
                repo_col1, repo_col2, repo_col3, repo_col4 = st.columns(4)
                
                with repo_col1:
                    st.metric("Contributors", repo_data['contributors'])
                with repo_col2:
                    st.metric("Total Contributions", repo_data['total_contributions'])
                with repo_col3:
                    st.metric("Stars", repo_data['stars'])
                with repo_col4:
                    st.metric("Forks", repo_data['forks'])
                
                # Repository information
                st.write(f"**Primary Language:** {repo_data['primary_language']}")
                st.write(f"**Description:** {repo_details['description'] or 'No description'}")
                st.write(f"**Topics:** {', '.join(repo_details['topics']) if repo_details['topics'] else 'None'}")
                
                # Top contributors to this repository
                st.subheader(f"Top Contributors to {selected_repo}")
                
                repo_contributors = sorted(
                    repo_details['contributors'],
                    key=lambda x: x['contributions'],
                    reverse=True
                )[:10]
                
                for i, contrib in enumerate(repo_contributors):
                    contributor = self.contributors[contrib['username']]
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        st.write(f"**#{i+1}**")
                        if contributor['profile'].get('avatar_url'):
                            st.image(contributor['profile']['avatar_url'], width=50)
                    
                    with col2:
                        st.write(f"**{contrib['username']}**")
                        st.write(f"Contributions: {contrib['contributions']}")
                        if contributor['profile'].get('company'):
                            st.write(f"Company: {contributor['profile']['company']}")
                    
                    with col3:
                        st.write(f"**Total Repos: {contributor['total_repositories']}**")
                        st.write(f"Total Contributions: {contributor['total_contributions']}")
                
                # Language breakdown for this repository
                if repo_details['languages']:
                    st.subheader("Language Breakdown")
                    
                    lang_breakdown = repo_details['languages']
                    df_lang_breakdown = pd.DataFrame(
                        list(lang_breakdown.items()),
                        columns=['Language', 'Lines of Code']
                    )
                    
                    fig_lang_breakdown = px.pie(
                        df_lang_breakdown,
                        values='Lines of Code',
                        names='Language',
                        title=f'Language Distribution in {selected_repo}'
                    )
                    st.plotly_chart(fig_lang_breakdown, use_container_width=True)
    
    def _create_profiles_tab(self):
        """Create contributor profiles tab."""
        st.header("👥 Contributor Profiles")
        
        # Search and filter
        profile_search = st.text_input("Search contributors by username:")
        
        # Sort options
        sort_option = st.selectbox(
            "Sort by:",
            ["Total Contributions", "Total Repositories", "Followers", "Public Repos"]
        )
        
        # Get sorted contributors
        sort_key_map = {
            "Total Contributions": lambda x: x['total_contributions'],
            "Total Repositories": lambda x: x['total_repositories'],
            "Followers": lambda x: x['profile'].get('followers', 0),
            "Public Repos": lambda x: x['profile'].get('public_repos', 0)
        }
        
        sorted_contributors = sorted(
            self.contributors.values(),
            key=sort_key_map[sort_option],
            reverse=True
        )
        
        # Filter by search
        if profile_search:
            sorted_contributors = [
                c for c in sorted_contributors 
                if profile_search.lower() in c['username'].lower()
            ]
        
        # Display contributors
        st.write(f"**Showing {len(sorted_contributors)} contributors:**")
        
        for i, contributor in enumerate(sorted_contributors[:20]):  # Show top 20
            with st.expander(f"#{i+1} {contributor['username']} ({contributor['total_contributions']} contributions)"):
                profile_col1, profile_col2, profile_col3 = st.columns([1, 2, 1])
                
                with profile_col1:
                    if contributor['profile'].get('avatar_url'):
                        st.image(contributor['profile']['avatar_url'], width=120)
                
                with profile_col2:
                    st.write(f"**Name:** {contributor['profile'].get('name', 'N/A')}")
                    st.write(f"**Location:** {contributor['profile'].get('location', 'N/A')}")
                    st.write(f"**Company:** {contributor['profile'].get('company', 'N/A')}")
                    st.write(f"**Bio:** {contributor['profile'].get('bio', 'N/A')}")
                    
                    if contributor['profile'].get('blog'):
                        st.write(f"**Blog:** {contributor['profile']['blog']}")
                    
                    if contributor['profile'].get('twitter'):
                        st.write(f"**Twitter:** {contributor['profile']['twitter']}")
                
                with profile_col3:
                    st.write(f"**Public Repos:** {contributor['profile'].get('public_repos', 0)}")
                    st.write(f"**Followers:** {contributor['profile'].get('followers', 0)}")
                    st.write(f"**Following:** {contributor['profile'].get('following', 0)}")
                    st.write(f"**Expertise Level:** {contributor['expertise_level']}")
                    st.write(f"**Total Contributions:** {contributor['total_contributions']}")
                    st.write(f"**Total Repositories:** {contributor['total_repositories']}")
                
                # Skills section
                skills = contributor.get('skills', {})
                if skills:
                    st.subheader("Skills Analysis")
                    
                    skill_col1, skill_col2 = st.columns(2)
                    
                    with skill_col1:
                        st.write("**Programming Languages:**")
                        lang_skills = skills.get('programming_languages', {})
                        for lang, score in sorted(lang_skills.items(), key=lambda x: x[1], reverse=True)[:5]:
                            if score > 0:
                                st.write(f"• {lang}: {score:.2f}")
                    
                    with skill_col2:
                        st.write("**Domain Expertise:**")
                        domain_skills = skills.get('domains', {})
                        for domain, score in sorted(domain_skills.items(), key=lambda x: x[1], reverse=True)[:5]:
                            if score > 0:
                                st.write(f"• {domain.replace('-', ' ').title()}: {score:.2f}")
                
                # Contributions section
                st.subheader("Top Repository Contributions")
                
                top_contribs = sorted(
                    contributor['contributions'],
                    key=lambda x: x['contributions'],
                    reverse=True
                )[:5]
                
                for contrib in top_contribs:
                    st.write(f"• **{contrib['repo_name']}**: {contrib['contributions']} contributions ({contrib['primary_language']})")
    
    def _perform_search(self, query: str, search_type: str):
        """Perform search based on query and type."""
        query_lower = query.lower()
        results = []
        
        if search_type == "Contributors":
            results = [
                c for c in self.contributors.values()
                if query_lower in c['username'].lower() or
                query_lower in c['profile'].get('name', '').lower() or
                query_lower in c['profile'].get('bio', '').lower()
            ]
            
        elif search_type == "Technologies":
            for username, skills in self.skills_analysis.items():
                # Search in programming languages
                lang_skills = skills.get('programming_languages', {})
                for lang, score in lang_skills.items():
                    if query_lower in lang.lower() and score > 0:
                        results.append({
                            'username': username,
                            'match_type': 'Programming Language',
                            'match_value': lang,
                            'score': score,
                            'contributor': self.contributors[username]
                        })
                
                # Search in technologies
                technologies = skills.get('technologies', [])
                for tech in technologies:
                    if query_lower in tech.lower():
                        results.append({
                            'username': username,
                            'match_type': 'Technology',
                            'match_value': tech,
                            'score': 1.0,
                            'contributor': self.contributors[username]
                        })
        
        elif search_type == "Repositories":
            for repo_name, repo_data in self.repositories.items():
                if (query_lower in repo_data['name'].lower() or
                    query_lower in repo_data.get('description', '').lower() or
                    query_lower in repo_data['primary_language'].lower()):
                    results.append(repo_data)
        
        # Display results
        if results:
            st.subheader(f"Search Results for '{query}' ({len(results)} found)")
            
            if search_type == "Contributors":
                for result in results[:10]:
                    st.write(f"**{result['username']}** - {result['total_contributions']} contributions")
                    if result['profile'].get('bio'):
                        st.write(f"  Bio: {result['profile']['bio']}")
                    
            elif search_type == "Technologies":
                for result in results[:10]:
                    st.write(f"**{result['username']}** - {result['match_type']}: {result['match_value']} (Score: {result['score']:.2f})")
                    
            elif search_type == "Repositories":
                for result in results[:10]:
                    st.write(f"**{result['name']}** - {result['primary_language']}")
                    st.write(f"  Contributors: {len(result['contributors'])}, Stars: {result['stars']}")
                    if result.get('description'):
                        st.write(f"  Description: {result['description']}")
        else:
            st.warning(f"No results found for '{query}'")
    
    def _filter_by_skill(self, skill_name: str, skill_type: str):
        """Filter contributors by specific skill."""
        results = []
        
        for username, skills in self.skills_analysis.items():
            skill_data = skills.get(skill_type, {})
            
            for skill, score in skill_data.items():
                if skill_name.lower() in skill.lower() and score > 0.5:
                    results.append({
                        'username': username,
                        'skill': skill,
                        'score': score,
                        'contributor': self.contributors[username]
                    })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        if results:
            st.subheader(f"Top {skill_name} Experts ({len(results)} found)")
            
            for result in results[:10]:
                contributor = result['contributor']
                st.write(f"**{result['username']}** - {result['skill']} Score: {result['score']:.2f}")
                st.write(f"  Contributions: {contributor['total_contributions']}, Repos: {contributor['total_repositories']}")
                if contributor['profile'].get('company'):
                    st.write(f"  Company: {contributor['profile']['company']}")
        else:
            st.warning(f"No {skill_name} experts found")
    
    def _apply_filters(self, min_contributions: int, expertise_level: str, min_repos: int):
        """Apply filters to contributors."""
        filtered = []
        
        for contributor in self.contributors.values():
            # Apply filters
            if contributor['total_contributions'] < min_contributions:
                continue
            
            if expertise_level != "All" and contributor['expertise_level'] != expertise_level:
                continue
            
            if contributor['total_repositories'] < min_repos:
                continue
            
            filtered.append(contributor)
        
        # Sort by contributions and add rank
        filtered.sort(key=lambda x: x['total_contributions'], reverse=True)
        
        for i, contributor in enumerate(filtered):
            contributor['rank'] = i + 1
        
        return filtered
    
    def _get_top_performers(self, skill: str):
        """Get top performers for a specific skill."""
        performers = []
        
        for username, skills in self.skills_analysis.items():
            score = 0
            
            # Check programming languages
            lang_skills = skills.get('programming_languages', {})
            if skill in lang_skills:
                score = lang_skills[skill]
            
            # Check domain skills
            domain_skills = skills.get('domains', {})
            if skill in domain_skills:
                score = domain_skills[skill]
            
            if score > 0:
                performers.append((username, score))
        
        # Sort by score
        performers.sort(key=lambda x: x[1], reverse=True)
        
        return performers


def main():
    """Main function to run the app."""
    try:
        app = EnhancedMockApp()
        app.run()
    except Exception as e:
        st.error(f"Failed to start app: {e}")
        logger.error(f"App failed: {e}")


if __name__ == "__main__":
    main()