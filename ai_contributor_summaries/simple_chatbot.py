"""Simple Streamlit chatbot interface for contributor analysis."""

import streamlit as st
import logging
import json
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import os

# Import our custom modules
from utils.weaviate_client import WeaviateClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleContributorChatbot:
    """Simple Streamlit chatbot for contributor analysis."""
    
    def __init__(self):
        """Initialize chatbot components."""
        self.weaviate_client = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize Weaviate client."""
        try:
            self.weaviate_client = WeaviateClient()
            logger.info("Weaviate client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate client: {e}")
            st.error(f"Failed to initialize Weaviate client: {e}")
    
    def run(self):
        """Run the Streamlit chatbot interface."""
        st.set_page_config(
            page_title="Weaviate Contributor Analysis",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 Weaviate Contributor Analysis")
        st.write("### Explore 912 contributors from Weaviate organization")
        
        if not self.weaviate_client:
            st.error("Weaviate client not initialized. Please check your setup.")
            return
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["🔍 Search", "📊 Analytics", "👥 Contributors"])
        
        with tab1:
            self._create_search_interface()
        
        with tab2:
            self._create_analytics_dashboard()
        
        with tab3:
            self._create_contributors_list()
    
    def _create_search_interface(self):
        """Create search interface."""
        st.header("🔍 Search Contributors")
        
        # Search options
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("Search contributors by name, technology, or skills:")
        
        with col2:
            search_type = st.selectbox("Search by:", ["Name", "Technology", "Skills"])
        
        if search_query:
            self._perform_search(search_query, search_type)
        
        # Quick search buttons
        st.subheader("Quick Searches")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Top Contributors"):
                self._show_top_contributors()
        
        with col2:
            if st.button("Python Developers"):
                self._search_by_technology("python")
        
        with col3:
            if st.button("JavaScript Developers"):
                self._search_by_technology("javascript")
        
        with col4:
            if st.button("Go Developers"):
                self._search_by_technology("go")
    
    def _create_analytics_dashboard(self):
        """Create analytics dashboard."""
        st.header("📊 Analytics Dashboard")
        
        try:
            # Get data for analytics
            contributors = self.weaviate_client.query_data("Contributor", limit=100)
            skills = self.weaviate_client.query_data("Skills", limit=100)
            
            if not contributors:
                st.warning("No contributor data found. Please run the data ingestion first.")
                return
            
            # Create metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Contributors", len(contributors))
            
            with col2:
                total_contributions = sum(c.get("total_contributions", 0) for c in contributors)
                st.metric("Total Contributions", total_contributions)
            
            with col3:
                avg_repos = sum(c.get("total_repositories", 0) for c in contributors) / len(contributors)
                st.metric("Avg Repositories", f"{avg_repos:.1f}")
            
            with col4:
                total_followers = sum(c.get("followers", 0) for c in contributors)
                st.metric("Total Followers", total_followers)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Top contributors chart
                df_contributors = pd.DataFrame(contributors)
                df_contributors = df_contributors.sort_values("total_contributions", ascending=False).head(10)
                
                fig = px.bar(
                    df_contributors,
                    x="username",
                    y="total_contributions",
                    title="Top 10 Contributors by Contributions",
                    labels={"total_contributions": "Total Contributions", "username": "Username"}
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Programming language distribution
                if skills:
                    lang_scores = {}
                    for skill in skills:
                        for lang in ["python", "javascript", "go", "typescript", "java"]:
                            score = skill.get(f"{lang}_score", 0)
                            if score > 0:
                                lang_scores[lang] = lang_scores.get(lang, 0) + score
                    
                    if lang_scores:
                        df_langs = pd.DataFrame(list(lang_scores.items()), columns=["Language", "Total Score"])
                        fig = px.pie(
                            df_langs,
                            values="Total Score",
                            names="Language",
                            title="Programming Language Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Activity level distribution
            activity_levels = {}
            for contributor in contributors:
                total_contrib = contributor.get("total_contributions", 0)
                if total_contrib > 100:
                    level = "Very Active"
                elif total_contrib > 50:
                    level = "Active"
                elif total_contrib > 20:
                    level = "Moderate"
                else:
                    level = "Occasional"
                activity_levels[level] = activity_levels.get(level, 0) + 1
            
            df_activity = pd.DataFrame(list(activity_levels.items()), columns=["Level", "Count"])
            fig = px.bar(
                df_activity,
                x="Level",
                y="Count",
                title="Activity Level Distribution",
                color="Level"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating analytics dashboard: {e}")
    
    def _create_contributors_list(self):
        """Create contributors list."""
        st.header("👥 Contributors")
        
        try:
            contributors = self.weaviate_client.query_data("Contributor", limit=50)
            
            if not contributors:
                st.warning("No contributors found.")
                return
            
            # Sort by total contributions
            contributors = sorted(contributors, key=lambda x: x.get("total_contributions", 0), reverse=True)
            
            # Display contributors
            for i, contributor in enumerate(contributors):
                with st.expander(f"#{i+1} {contributor.get('username', 'Unknown')} ({contributor.get('total_contributions', 0)} contributions)"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if contributor.get("avatar_url"):
                            st.image(contributor["avatar_url"], width=100)
                    
                    with col2:
                        st.write(f"**Name:** {contributor.get('name', 'N/A')}")
                        st.write(f"**Location:** {contributor.get('location', 'N/A')}")
                        st.write(f"**Company:** {contributor.get('company', 'N/A')}")
                        st.write(f"**Bio:** {contributor.get('bio', 'N/A')}")
                        st.write(f"**Public Repos:** {contributor.get('public_repos', 0)}")
                        st.write(f"**Followers:** {contributor.get('followers', 0)}")
                        st.write(f"**Following:** {contributor.get('following', 0)}")
                        st.write(f"**Total Contributions:** {contributor.get('total_contributions', 0)}")
                        
                        if contributor.get("blog"):
                            st.write(f"**Blog:** {contributor['blog']}")
                        
                        # Show skills if available
                        skills = self._get_contributor_skills(contributor.get("username", ""))
                        if skills:
                            st.write("**Skills:**")
                            for lang in ["python", "javascript", "go", "typescript", "java"]:
                                score = skills.get(f"{lang}_score", 0)
                                if score > 0:
                                    st.write(f"  - {lang.title()}: {score:.2f}")
            
        except Exception as e:
            st.error(f"Error loading contributors: {e}")
    
    def _perform_search(self, query: str, search_type: str):
        """Perform search based on query and type."""
        try:
            if search_type == "Name":
                # Search by username
                results = self.weaviate_client.search_similar("Contributor", query, limit=10)
            elif search_type == "Technology":
                # Search by technology
                results = self.weaviate_client.search_similar("Skills", query, limit=10)
            else:  # Skills
                results = self.weaviate_client.search_similar("Skills", query, limit=10)
            
            if results:
                st.subheader(f"Search Results for '{query}'")
                
                for result in results:
                    certainty = result.get("certainty", 0)
                    if search_type == "Name":
                        username = result.get("username", "Unknown")
                        st.write(f"**{username}** (Match: {certainty:.2f})")
                        st.write(f"  - Contributions: {result.get('total_contributions', 0)}")
                        st.write(f"  - Repositories: {result.get('total_repositories', 0)}")
                    else:
                        username = result.get("contributor_username", "Unknown")
                        st.write(f"**{username}** (Match: {certainty:.2f})")
                        
                        # Show relevant skills
                        for lang in ["python", "javascript", "go", "typescript", "java"]:
                            score = result.get(f"{lang}_score", 0)
                            if score > 0:
                                st.write(f"  - {lang.title()}: {score:.2f}")
            else:
                st.warning(f"No results found for '{query}'")
                
        except Exception as e:
            st.error(f"Search error: {e}")
    
    def _show_top_contributors(self):
        """Show top contributors."""
        try:
            contributors = self.weaviate_client.query_data("Contributor", limit=20)
            contributors = sorted(contributors, key=lambda x: x.get("total_contributions", 0), reverse=True)
            
            st.subheader("Top 10 Contributors")
            
            for i, contributor in enumerate(contributors[:10]):
                st.write(f"{i+1}. **{contributor.get('username', 'Unknown')}** - {contributor.get('total_contributions', 0)} contributions")
                
        except Exception as e:
            st.error(f"Error loading top contributors: {e}")
    
    def _search_by_technology(self, technology: str):
        """Search contributors by technology."""
        try:
            results = self.weaviate_client.search_similar("Skills", technology, limit=10)
            
            if results:
                st.subheader(f"Top {technology.title()} Developers")
                
                for result in results:
                    username = result.get("contributor_username", "Unknown")
                    score = result.get(f"{technology}_score", 0)
                    certainty = result.get("certainty", 0)
                    
                    st.write(f"**{username}** - {technology.title()} Score: {score:.2f} (Match: {certainty:.2f})")
            else:
                st.warning(f"No {technology} developers found")
                
        except Exception as e:
            st.error(f"Error searching {technology} developers: {e}")
    
    def _get_contributor_skills(self, username: str):
        """Get skills for a contributor."""
        try:
            where_filter = {
                "path": ["contributor_username"],
                "operator": "Equal",
                "valueString": username
            }
            
            skills = self.weaviate_client.query_data("Skills", where_filter=where_filter, limit=1)
            return skills[0] if skills else None
            
        except Exception as e:
            logger.error(f"Error getting skills for {username}: {e}")
            return None


def main():
    """Main function to run the Streamlit app."""
    try:
        chatbot = SimpleContributorChatbot()
        chatbot.run()
    except Exception as e:
        st.error(f"Failed to start chatbot: {e}")


if __name__ == "__main__":
    main()