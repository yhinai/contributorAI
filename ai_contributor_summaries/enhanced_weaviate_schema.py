"""Enhanced Weaviate schema and data ingestion for detailed contributor analysis."""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.weaviate_client import WeaviateClient

logger = logging.getLogger(__name__)


class EnhancedWeaviateSchema:
    """Enhanced Weaviate schema for detailed contributor analysis."""
    
    def __init__(self, client: WeaviateClient):
        """Initialize with Weaviate client."""
        self.client = client
    
    def create_enhanced_schema(self):
        """Create enhanced schema for detailed contributor analysis."""
        try:
            # Clear existing schema
            try:
                self.client.client.schema.delete_all()
                logger.info("Cleared existing schema")
            except:
                pass
            
            # Enhanced Contributor schema with detailed skills
            contributor_schema = {
                "class": "Contributor",
                "description": "GitHub contributors with comprehensive analysis",
                "properties": [
                    {"name": "username", "dataType": ["string"], "description": "GitHub username"},
                    {"name": "name", "dataType": ["string"], "description": "Full name"},
                    {"name": "email", "dataType": ["string"], "description": "Email address"},
                    {"name": "bio", "dataType": ["text"], "description": "User bio"},
                    {"name": "location", "dataType": ["string"], "description": "Location"},
                    {"name": "company", "dataType": ["string"], "description": "Company"},
                    {"name": "blog", "dataType": ["string"], "description": "Blog URL"},
                    {"name": "twitter", "dataType": ["string"], "description": "Twitter handle"},
                    {"name": "public_repos", "dataType": ["int"], "description": "Number of public repositories"},
                    {"name": "followers", "dataType": ["int"], "description": "Number of followers"},
                    {"name": "following", "dataType": ["int"], "description": "Number of following"},
                    {"name": "created_at", "dataType": ["date"], "description": "Account creation date"},
                    {"name": "avatar_url", "dataType": ["string"], "description": "Avatar URL"},
                    {"name": "total_contributions", "dataType": ["int"], "description": "Total contributions"},
                    {"name": "total_repositories", "dataType": ["int"], "description": "Total repositories contributed to"},
                    {"name": "ai_summary", "dataType": ["text"], "description": "AI-generated profile summary"},
                    {"name": "skill_recommendations", "dataType": ["string[]"], "description": "Skill improvement recommendations"},
                    {"name": "tech_stack", "dataType": ["string[]"], "description": "Technology stack"},
                    {"name": "expertise_level", "dataType": ["string"], "description": "Overall expertise level"},
                    {"name": "contribution_pattern", "dataType": ["string"], "description": "Contribution pattern description"},
                ]
            }
            
            # Skills schema for detailed programming skills
            skills_schema = {
                "class": "Skills",
                "description": "Detailed programming skills and competencies",
                "properties": [
                    {"name": "contributor_username", "dataType": ["string"], "description": "Contributor username"},
                    {"name": "python_score", "dataType": ["number"], "description": "Python proficiency score"},
                    {"name": "javascript_score", "dataType": ["number"], "description": "JavaScript proficiency score"},
                    {"name": "go_score", "dataType": ["number"], "description": "Go proficiency score"},
                    {"name": "typescript_score", "dataType": ["number"], "description": "TypeScript proficiency score"},
                    {"name": "dockerfile_score", "dataType": ["number"], "description": "Docker proficiency score"},
                    {"name": "shell_score", "dataType": ["number"], "description": "Shell scripting proficiency score"},
                    {"name": "html_score", "dataType": ["number"], "description": "HTML proficiency score"},
                    {"name": "css_score", "dataType": ["number"], "description": "CSS proficiency score"},
                    {"name": "scala_score", "dataType": ["number"], "description": "Scala proficiency score"},
                    {"name": "c_score", "dataType": ["number"], "description": "C programming proficiency score"},
                    {"name": "ruby_score", "dataType": ["number"], "description": "Ruby proficiency score"},
                    {"name": "web_development", "dataType": ["number"], "description": "Web development domain score"},
                    {"name": "machine_learning", "dataType": ["number"], "description": "Machine learning domain score"},
                    {"name": "data_science", "dataType": ["number"], "description": "Data science domain score"},
                    {"name": "devops", "dataType": ["number"], "description": "DevOps domain score"},
                    {"name": "cloud_computing", "dataType": ["number"], "description": "Cloud computing domain score"},
                    {"name": "database", "dataType": ["number"], "description": "Database domain score"},
                    {"name": "system_programming", "dataType": ["number"], "description": "System programming domain score"},
                    {"name": "frontend", "dataType": ["number"], "description": "Frontend domain score"},
                    {"name": "backend", "dataType": ["number"], "description": "Backend domain score"},
                    {"name": "testing", "dataType": ["number"], "description": "Testing domain score"},
                    {"name": "technologies", "dataType": ["string[]"], "description": "List of technologies"},
                    {"name": "frameworks", "dataType": ["string[]"], "description": "List of frameworks"},
                    {"name": "tools", "dataType": ["string[]"], "description": "List of tools"},
                ]
            }
            
            # Repository schema for detailed repository information
            repository_schema = {
                "class": "Repository",
                "description": "Repository details and metadata",
                "properties": [
                    {"name": "repo_name", "dataType": ["string"], "description": "Repository name"},
                    {"name": "repo_full_name", "dataType": ["string"], "description": "Full repository name"},
                    {"name": "primary_language", "dataType": ["string"], "description": "Primary programming language"},
                    {"name": "repo_description", "dataType": ["text"], "description": "Repository description"},
                    {"name": "repo_size", "dataType": ["int"], "description": "Repository size"},
                    {"name": "stars", "dataType": ["int"], "description": "Number of stars"},
                    {"name": "forks", "dataType": ["int"], "description": "Number of forks"},
                    {"name": "topics", "dataType": ["string[]"], "description": "Repository topics"},
                    {"name": "languages", "dataType": ["string[]"], "description": "Programming languages used"},
                    {"name": "created_at", "dataType": ["date"], "description": "Repository creation date"},
                    {"name": "updated_at", "dataType": ["date"], "description": "Last update date"},
                    {"name": "is_fork", "dataType": ["boolean"], "description": "Whether repository is a fork"},
                    {"name": "license", "dataType": ["string"], "description": "Repository license"},
                ]
            }
            
            # Contribution schema for detailed contribution tracking
            contribution_schema = {
                "class": "Contribution",
                "description": "Detailed contribution records",
                "properties": [
                    {"name": "contributor_username", "dataType": ["string"], "description": "Contributor username"},
                    {"name": "repository_full_name", "dataType": ["string"], "description": "Repository full name"},
                    {"name": "contribution_count", "dataType": ["int"], "description": "Number of contributions"},
                    {"name": "primary_language", "dataType": ["string"], "description": "Primary language used"},
                    {"name": "contribution_type", "dataType": ["string"], "description": "Type of contribution"},
                    {"name": "impact_score", "dataType": ["number"], "description": "Impact score of contributions"},
                    {"name": "first_contribution", "dataType": ["date"], "description": "First contribution date"},
                    {"name": "last_contribution", "dataType": ["date"], "description": "Last contribution date"},
                    {"name": "languages_used", "dataType": ["string[]"], "description": "Languages used in contributions"},
                    {"name": "files_changed", "dataType": ["string[]"], "description": "Files changed"},
                    {"name": "commit_messages", "dataType": ["text"], "description": "Sample commit messages"},
                ]
            }
            
            # Create schemas
            schemas = [contributor_schema, skills_schema, repository_schema, contribution_schema]
            
            for schema in schemas:
                try:
                    self.client.client.schema.create_class(schema)
                    logger.info(f"Created schema for {schema['class']}")
                except Exception as e:
                    logger.warning(f"Schema for {schema['class']} might already exist: {e}")
            
            logger.info("Enhanced schemas created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create enhanced schemas: {e}")
            raise
    
    def ingest_weaviate_org_data(self, json_file_path: str):
        """Ingest the detailed Weaviate organization data."""
        try:
            logger.info(f"Starting ingestion of {json_file_path}")
            
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded data for {data['analysis_metadata']['total_contributors']} contributors")
            
            # Process contributors
            for username, contributor_data in data['contributors'].items():
                # Insert contributor profile
                contributor_obj = {
                    "username": username,
                    "name": str(contributor_data['profile'].get('name', '') or ''),
                    "email": str(contributor_data['profile'].get('email', '') or ''),
                    "bio": str(contributor_data['profile'].get('bio', '') or ''),
                    "location": str(contributor_data['profile'].get('location', '') or ''),
                    "company": str(contributor_data['profile'].get('company', '') or ''),
                    "blog": str(contributor_data['profile'].get('blog', '') or ''),
                    "twitter": str(contributor_data['profile'].get('twitter', '') or ''),
                    "public_repos": int(contributor_data['profile'].get('public_repos', 0) or 0),
                    "followers": int(contributor_data['profile'].get('followers', 0) or 0),
                    "following": int(contributor_data['profile'].get('following', 0) or 0),
                    "created_at": str(contributor_data['profile'].get('created_at', '') or ''),
                    "avatar_url": str(contributor_data['profile'].get('avatar_url', '') or ''),
                    "total_contributions": int(contributor_data.get('total_contributions', 0) or 0),
                    "total_repositories": len(contributor_data.get('contributions', [])),
                    "ai_summary": str(contributor_data.get('summary', '') or ''),
                    "skill_recommendations": data.get('skill_recommendations', {}).get(username, []) or [],
                    "tech_stack": contributor_data.get('tech_stack', []) or [],
                    "expertise_level": str(contributor_data.get('expertise_level', 'intermediate') or 'intermediate'),
                    "contribution_pattern": str(contributor_data.get('contribution_pattern', '') or ''),
                }
                
                self.client.insert_data("Contributor", contributor_obj)
                
                # Insert skills data if available
                if 'skills' in contributor_data:
                    skills_data = contributor_data['skills']
                    skills_obj = {
                        "contributor_username": username,
                        "technologies": skills_data.get('technologies', []),
                        "frameworks": list(skills_data.get('frameworks', {}).keys()),
                        "tools": skills_data.get('tools', []),
                    }
                    
                    # Add programming language scores
                    lang_scores = skills_data.get('programming_languages', {})
                    for lang, score in lang_scores.items():
                        lang_key = f"{lang.lower().replace(' ', '_').replace('#', 'sharp')}_score"
                        if lang_key in ["python_score", "javascript_score", "go_score", "typescript_score", 
                                       "dockerfile_score", "shell_score", "html_score", "css_score", 
                                       "scala_score", "c_score", "ruby_score"]:
                            skills_obj[lang_key] = float(score)
                    
                    # Add domain scores
                    domain_scores = skills_data.get('domains', {})
                    for domain, score in domain_scores.items():
                        domain_key = domain.replace('-', '_')
                        if domain_key in ["web_development", "machine_learning", "data_science", 
                                         "devops", "cloud_computing", "database", "system_programming", 
                                         "frontend", "backend", "testing"]:
                            skills_obj[domain_key] = float(score)
                    
                    self.client.insert_data("Skills", skills_obj)
                
                # Insert contributions
                for contribution in contributor_data.get('contributions', []):
                    # Insert repository if not exists
                    repo_obj = {
                        "repo_name": str(contribution['repo_name']),
                        "repo_full_name": str(contribution['repo_full_name']),
                        "primary_language": str(contribution['primary_language'] or ''),
                        "repo_description": str(contribution.get('repo_description', '') or ''),
                        "repo_size": int(contribution.get('repo_size', 0) or 0),
                        "stars": int(contribution.get('stars', 0) or 0),
                        "forks": int(contribution.get('forks', 0) or 0),
                        "topics": contribution.get('topics', []) or [],
                        "languages": list(contribution.get('languages', {}).keys()) or [],
                        "is_fork": bool(contribution.get('is_fork', False)),
                        "license": str(contribution.get('license', '') or ''),
                    }
                    
                    self.client.insert_data("Repository", repo_obj)
                    
                    # Insert contribution record
                    contribution_obj = {
                        "contributor_username": username,
                        "repository_full_name": str(contribution['repo_full_name']),
                        "contribution_count": int(contribution['contributions']),
                        "primary_language": str(contribution['primary_language'] or ''),
                        "contribution_type": "commits",
                        "impact_score": float(contribution.get('impact_score', 0.5) or 0.5),
                        "languages_used": list(contribution.get('languages', {}).keys()) or [],
                        "files_changed": [],
                        "commit_messages": "",
                    }
                    
                    self.client.insert_data("Contribution", contribution_obj)
                
                logger.info(f"Processed contributor: {username}")
            
            logger.info("Data ingestion completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to ingest data: {e}")
            raise


def main():
    """Main function to create schema and ingest data."""
    try:
        # Initialize enhanced schema
        client = WeaviateClient()
        enhanced_schema = EnhancedWeaviateSchema(client)
        
        # Create enhanced schema
        enhanced_schema.create_enhanced_schema()
        
        # Ingest data
        json_file_path = "/Users/alhinai/Downloads/Detailed weaviate org"
        enhanced_schema.ingest_weaviate_org_data(json_file_path)
        
        logger.info("Enhanced Weaviate setup completed successfully")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()