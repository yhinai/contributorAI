"""Streamlit chatbot interface for contributor analysis."""

import streamlit as st
import logging
import json
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import os

# Import our custom modules
from utils.weaviate_client import WeaviateClient
from llamaindex_weaviate_integration import ContributorAnalysisBot
from friendli_ai_profiler import FriendliAIProfiler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContributorChatbot:
    """Streamlit chatbot for contributor analysis."""
    
    def __init__(self):
        """Initialize chatbot components."""
        self.weaviate_client = None
        self.analysis_bot = None
        self.profiler = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize Weaviate and AI components."""
        try:
            # Initialize Weaviate client
            self.weaviate_client = WeaviateClient()
            
            # Get API keys from environment or Streamlit secrets
            openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
            friendli_token = os.getenv("FRIENDLI_TOKEN") or st.secrets.get("FRIENDLI_TOKEN", "")
            
            if openai_key and friendli_token:
                # Initialize analysis bot
                self.analysis_bot = ContributorAnalysisBot(
                    weaviate_client=self.weaviate_client,
                    openai_api_key=openai_key,
                    friendli_token=friendli_token
                )
                
                # Initialize profiler
                self.profiler = FriendliAIProfiler(
                    friendli_token=friendli_token,
                    weaviate_client=self.weaviate_client
                )
                
                logger.info("All components initialized successfully")
            else:
                st.warning("Please configure OpenAI API key and FriendliAI token in environment variables or Streamlit secrets")
                
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            st.error(f"Failed to initialize components: {e}")
    
    def run(self):
        """Run the Streamlit chatbot interface."""
        st.set_page_config(
            page_title="Weaviate Contributor Analysis Chatbot",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 Weaviate Contributor Analysis Chatbot")
        st.subtitle("AI-powered insights into Weaviate organization contributors")
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_query" not in st.session_state:
            st.session_state.current_query = ""
        
        # Sidebar for navigation and controls
        self._create_sidebar()
        
        # Main chat interface
        self._create_chat_interface()
        
        # Analytics dashboard
        self._create_analytics_dashboard()
    
    def _create_sidebar(self):
        """Create sidebar with navigation and controls."""
        with st.sidebar:
            st.header("🔧 Controls")
            
            # Query mode selection
            query_mode = st.selectbox(
                "Query Mode",
                ["Comprehensive", "Contributors", "Skills", "Repositories", "Contributions"],
                help="Select the type of data to query"
            )
            st.session_state.query_mode = query_mode
            
            # Quick query buttons
            st.subheader("Quick Queries")
            
            if st.button("Top Contributors"):
                self._handle_quick_query("Who are the top 10 contributors by total contributions?")
            
            if st.button("Python Experts"):
                self._handle_quick_query("Who are the top Python developers in the organization?")
            
            if st.button("Machine Learning Skills"):
                self._handle_quick_query("Which contributors have strong machine learning skills?")
            
            if st.button("Most Active Repos"):
                self._handle_quick_query("What are the most active repositories in terms of contributions?")
            
            if st.button("DevOps Specialists"):
                self._handle_quick_query("Who are the contributors with strong DevOps skills?")
            
            # Data statistics
            st.subheader("📊 Data Statistics")
            if self.weaviate_client:
                try:
                    contributors_count = len(self.weaviate_client.query_data("Contributor", limit=1000))
                    skills_count = len(self.weaviate_client.query_data("Skills", limit=1000))
                    repos_count = len(self.weaviate_client.query_data("Repository", limit=1000))
                    
                    st.metric("Contributors", contributors_count)
                    st.metric("Skills Records", skills_count)
                    st.metric("Repositories", repos_count)
                    
                except Exception as e:
                    st.error(f"Error loading statistics: {e}")
            
            # Profile generation
            st.subheader("🔮 AI Profile Generation")
            if st.button("Generate Top Contributor Profiles"):
                self._generate_profiles()
    
    def _create_chat_interface(self):
        """Create the main chat interface."""
        st.header("💬 Chat Interface")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and "visualizations" in message:
                    st.write(message["content"])
                    for viz in message["visualizations"]:
                        st.plotly_chart(viz, use_container_width=True)
                else:
                    st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about Weaviate contributors, skills, or repositories..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Process query and display response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = self._process_query(prompt)
                    st.write(response["content"])
                    
                    # Display visualizations if any
                    if "visualizations" in response:
                        for viz in response["visualizations"]:
                            st.plotly_chart(viz, use_container_width=True)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append(response)
    
    def _create_analytics_dashboard(self):
        """Create analytics dashboard."""
        st.header("📈 Analytics Dashboard")
        
        if not self.weaviate_client:
            st.error("Weaviate client not initialized")
            return
        
        try:
            # Get data for analytics
            contributors = self.weaviate_client.query_data("Contributor", limit=100)
            skills = self.weaviate_client.query_data("Skills", limit=100)
            contributions = self.weaviate_client.query_data("Contribution", limit=200)
            
            # Create dashboard columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Top contributors chart
                if contributors:
                    df_contributors = pd.DataFrame(contributors)
                    df_contributors = df_contributors.sort_values("total_contributions", ascending=False).head(10)
                    
                    fig = px.bar(
                        df_contributors,
                        x="username",
                        y="total_contributions",
                        title="Top 10 Contributors by Total Contributions",
                        labels={"total_contributions": "Total Contributions", "username": "Username"}
                    )
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                
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
            
            with col2:
                # Expertise level distribution
                if contributors:
                    expertise_levels = {}
                    for contributor in contributors:
                        level = contributor.get("expertise_level", "intermediate")
                        expertise_levels[level] = expertise_levels.get(level, 0) + 1
                    
                    df_expertise = pd.DataFrame(list(expertise_levels.items()), columns=["Level", "Count"])
                    fig = px.bar(
                        df_expertise,
                        x="Level",
                        y="Count",
                        title="Expertise Level Distribution",
                        color="Level"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Activity level distribution
                if contributors:
                    activity_levels = {}
                    for contributor in contributors:
                        level = contributor.get("activity_level", "moderate")
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
            
            # Repository contribution heatmap
            if contributions:
                contrib_matrix = {}
                for contrib in contributions:
                    username = contrib.get("contributor_username", "")
                    repo = contrib.get("repository_full_name", "").split("/")[-1]  # Get repo name only
                    count = contrib.get("contribution_count", 0)
                    
                    if username not in contrib_matrix:
                        contrib_matrix[username] = {}
                    contrib_matrix[username][repo] = count
                
                # Convert to DataFrame for heatmap
                df_heatmap = pd.DataFrame(contrib_matrix).fillna(0)
                
                if not df_heatmap.empty and df_heatmap.shape[0] > 0 and df_heatmap.shape[1] > 0:
                    # Limit to top repositories and contributors
                    df_heatmap = df_heatmap.head(10).iloc[:, :10]
                    
                    fig = px.imshow(
                        df_heatmap,
                        title="Contribution Heatmap (Top Contributors vs Repositories)",
                        labels=dict(x="Contributors", y="Repositories", color="Contributions"),
                        aspect="auto"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating analytics dashboard: {e}")
    
    def _process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and return response."""
        try:
            if not self.analysis_bot:
                return {
                    "role": "assistant",
                    "content": "Sorry, the analysis bot is not initialized. Please check your API keys."
                }
            
            query_mode = st.session_state.get("query_mode", "Comprehensive")
            
            if query_mode == "Comprehensive":
                results = self.analysis_bot.comprehensive_query(query)
                content = self._format_comprehensive_results(results)
                visualizations = self._create_query_visualizations(query, results)
            elif query_mode == "Contributors":
                response = self.analysis_bot.query_contributors(query)
                content = str(response)
                visualizations = []
            elif query_mode == "Skills":
                response = self.analysis_bot.query_skills(query)
                content = str(response)
                visualizations = []
            elif query_mode == "Repositories":
                response = self.analysis_bot.query_repositories(query)
                content = str(response)
                visualizations = []
            elif query_mode == "Contributions":
                response = self.analysis_bot.query_contributions(query)
                content = str(response)
                visualizations = []
            else:
                content = "Invalid query mode selected."
                visualizations = []
            
            return {
                "role": "assistant",
                "content": content,
                "visualizations": visualizations
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {e}"
            }
    
    def _format_comprehensive_results(self, results: Dict[str, Any]) -> str:
        """Format comprehensive query results."""
        formatted = ["## Comprehensive Analysis Results\\n"]
        
        for collection, data in results.items():
            formatted.append(f"### {collection.title()}\\n")
            formatted.append(f"**Response:** {data['response']}\\n")
            
            if data.get('source_nodes'):
                formatted.append("**Relevant Sources:**")
                for node in data['source_nodes'][:3]:  # Show top 3 sources
                    formatted.append(f"- {node['text'][:100]}... (Score: {node.get('score', 0):.2f})")
                formatted.append("")
        
        return "\\n".join(formatted)
    
    def _create_query_visualizations(self, query: str, results: Dict[str, Any]) -> List[go.Figure]:
        """Create visualizations based on query results."""
        visualizations = []
        
        try:
            # Check if query is about top contributors
            if "top" in query.lower() and "contributor" in query.lower():
                top_contributors = self.analysis_bot.get_top_contributors(10)
                if top_contributors:
                    df = pd.DataFrame(top_contributors)
                    fig = px.bar(
                        df,
                        x="username",
                        y="total_contributions",
                        title="Top Contributors by Total Contributions",
                        labels={"total_contributions": "Total Contributions", "username": "Username"}
                    )
                    fig.update_xaxes(tickangle=45)
                    visualizations.append(fig)
            
            # Check if query is about programming languages
            if "python" in query.lower() or "javascript" in query.lower() or "language" in query.lower():
                skills = self.weaviate_client.query_data("Skills", limit=50)
                if skills:
                    lang_data = []
                    for skill in skills:
                        username = skill.get("contributor_username", "")
                        for lang in ["python", "javascript", "go", "typescript"]:
                            score = skill.get(f"{lang}_score", 0)
                            if score > 0:
                                lang_data.append({
                                    "username": username,
                                    "language": lang,
                                    "score": score
                                })
                    
                    if lang_data:
                        df = pd.DataFrame(lang_data)
                        fig = px.scatter(
                            df,
                            x="username",
                            y="score",
                            color="language",
                            title="Programming Language Skills by Contributor",
                            labels={"score": "Skill Score", "username": "Username"}
                        )
                        fig.update_xaxes(tickangle=45)
                        visualizations.append(fig)
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
        
        return visualizations
    
    def _handle_quick_query(self, query: str):
        """Handle quick query button clicks."""
        st.session_state.current_query = query
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Process the query
        response = self._process_query(query)
        st.session_state.messages.append(response)
        
        # Force rerun to update the chat
        st.rerun()
    
    def _generate_profiles(self):
        """Generate AI profiles for top contributors."""
        if not self.profiler:
            st.error("Profiler not initialized")
            return
        
        try:
            with st.spinner("Generating AI profiles for top contributors..."):
                profiles = self.profiler.process_top_contributors(limit=5)
                
                # Save profiles
                self.profiler.save_profiles_to_weaviate(profiles)
                
                st.success(f"Generated {len(profiles)} AI profiles successfully!")
                
                # Display sample profile
                if profiles:
                    st.subheader("Sample Generated Profile")
                    sample_profile = profiles[0]
                    st.write(f"**Username:** {sample_profile['username']}")
                    st.write(f"**Professional Summary:**")
                    st.write(sample_profile['profile_sections']['professional_summary'])
                    
        except Exception as e:
            st.error(f"Error generating profiles: {e}")


def main():
    """Main function to run the Streamlit app."""
    try:
        chatbot = ContributorChatbot()
        chatbot.run()
    except Exception as e:
        st.error(f"Failed to start chatbot: {e}")


if __name__ == "__main__":
    main()