"""FriendliAI integration for generating detailed contributor profiles."""

import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import asyncio
from llama_index.llms.friendli import FriendliLLM
from utils.weaviate_client import WeaviateClient

logger = logging.getLogger(__name__)


class FriendliAIProfiler:
    """Generate detailed contributor profiles using FriendliAI."""
    
    def __init__(self, friendli_token: str, weaviate_client: WeaviateClient):
        """Initialize FriendliAI profiler."""
        self.friendli_token = friendli_token
        self.weaviate_client = weaviate_client
        
        # Initialize FriendliAI LLM
        self.llm = FriendliLLM(
            model="meta-llama/Llama-3.1-8B-Instruct",
            token=friendli_token,
            max_tokens=2000,
            temperature=0.3  # Lower temperature for more factual profiles
        )
        
        logger.info("FriendliAI profiler initialized successfully")
    
    def generate_contributor_profile(self, contributor_data: Dict, skills_data: Dict, 
                                   contributions_data: List[Dict]) -> Dict:
        """Generate comprehensive contributor profile."""
        try:
            # Prepare context for AI
            context = self._prepare_contributor_context(contributor_data, skills_data, contributions_data)
            
            # Generate profile sections
            profile_sections = {}
            
            # Generate professional summary
            profile_sections["professional_summary"] = self._generate_professional_summary(context)
            
            # Generate technical expertise
            profile_sections["technical_expertise"] = self._generate_technical_expertise(context)
            
            # Generate contribution analysis
            profile_sections["contribution_analysis"] = self._generate_contribution_analysis(context)
            
            # Generate strengths and recommendations
            profile_sections["strengths_recommendations"] = self._generate_strengths_recommendations(context)
            
            # Generate collaboration style
            profile_sections["collaboration_style"] = self._generate_collaboration_style(context)
            
            # Generate career trajectory
            profile_sections["career_trajectory"] = self._generate_career_trajectory(context)
            
            # Compile comprehensive profile
            comprehensive_profile = {
                "username": contributor_data.get("username", ""),
                "generated_at": datetime.now().isoformat(),
                "profile_sections": profile_sections,
                "metadata": {
                    "total_contributions": contributor_data.get("total_contributions", 0),
                    "total_repositories": contributor_data.get("total_repositories", 0),
                    "primary_languages": self._extract_primary_languages(skills_data),
                    "expertise_level": self._assess_expertise_level(skills_data, contributions_data),
                    "activity_level": self._assess_activity_level(contributions_data),
                    "specialization_areas": self._identify_specialization_areas(skills_data)
                }
            }
            
            logger.info(f"Generated comprehensive profile for {contributor_data.get('username', '')}")
            return comprehensive_profile
            
        except Exception as e:
            logger.error(f"Failed to generate contributor profile: {e}")
            raise
    
    def _prepare_contributor_context(self, contributor_data: Dict, skills_data: Dict, 
                                   contributions_data: List[Dict]) -> str:
        """Prepare context string for AI processing."""
        context_parts = []
        
        # Basic profile information
        context_parts.append(f"CONTRIBUTOR PROFILE:")
        context_parts.append(f"Username: {contributor_data.get('username', '')}")
        context_parts.append(f"Name: {contributor_data.get('name', '')}")
        context_parts.append(f"Location: {contributor_data.get('location', '')}")
        context_parts.append(f"Company: {contributor_data.get('company', '')}")
        context_parts.append(f"Bio: {contributor_data.get('bio', '')}")
        context_parts.append(f"Public Repositories: {contributor_data.get('public_repos', 0)}")
        context_parts.append(f"Followers: {contributor_data.get('followers', 0)}")
        context_parts.append(f"Total Contributions: {contributor_data.get('total_contributions', 0)}")
        
        # Skills information
        if skills_data:
            context_parts.append(f"\\nSKILLS ASSESSMENT:")
            context_parts.append(f"Programming Languages:")
            for lang in ["python", "javascript", "go", "typescript", "shell", "c", "ruby"]:
                score = skills_data.get(f"{lang}_score", 0)
                if score > 0:
                    context_parts.append(f"  - {lang.title()}: {score:.2f}")
            
            context_parts.append(f"Domain Expertise:")
            for domain in ["web_development", "machine_learning", "data_science", "devops", 
                          "cloud_computing", "database", "backend", "frontend"]:
                score = skills_data.get(domain, 0)
                if score > 0:
                    context_parts.append(f"  - {domain.replace('_', ' ').title()}: {score:.2f}")
            
            context_parts.append(f"Technologies: {', '.join(skills_data.get('technologies', []))}")
            context_parts.append(f"Frameworks: {', '.join(skills_data.get('frameworks', []))}")
        
        # Contributions information
        if contributions_data:
            context_parts.append(f"\\nCONTRIBUTIONS:")
            for contrib in contributions_data[:10]:  # Limit to top 10
                context_parts.append(f"  - {contrib.get('repository_full_name', '')}: "
                                   f"{contrib.get('contribution_count', 0)} contributions "
                                   f"({contrib.get('primary_language', '')})")
        
        return "\\n".join(context_parts)
    
    def _generate_professional_summary(self, context: str) -> str:
        """Generate professional summary."""
        prompt = f"""
        Based on the following contributor data, generate a professional summary (2-3 paragraphs) 
        that highlights their key strengths, expertise, and professional identity:

        {context}

        Focus on:
        - Overall technical expertise and experience level
        - Key programming languages and technologies
        - Types of projects and contributions
        - Professional strengths and unique value

        Generate a compelling professional summary:
        """
        
        response = self.llm.complete(prompt)
        return str(response).strip()
    
    def _generate_technical_expertise(self, context: str) -> str:
        """Generate technical expertise analysis."""
        prompt = f"""
        Based on the following contributor data, analyze their technical expertise:

        {context}

        Provide a detailed analysis covering:
        - Primary programming languages and proficiency levels
        - Technical domains and specialization areas
        - Frameworks and tools expertise
        - Technology stack preferences
        - Technical breadth vs depth assessment

        Generate a comprehensive technical expertise analysis:
        """
        
        response = self.llm.complete(prompt)
        return str(response).strip()
    
    def _generate_contribution_analysis(self, context: str) -> str:
        """Generate contribution pattern analysis."""
        prompt = f"""
        Based on the following contributor data, analyze their contribution patterns:

        {context}

        Analyze:
        - Contribution frequency and consistency
        - Types of repositories they contribute to
        - Collaboration patterns
        - Impact and influence within projects
        - Preferred project types and domains

        Generate a detailed contribution analysis:
        """
        
        response = self.llm.complete(prompt)
        return str(response).strip()
    
    def _generate_strengths_recommendations(self, context: str) -> str:
        """Generate strengths and development recommendations."""
        prompt = f"""
        Based on the following contributor data, identify their key strengths and provide 
        development recommendations:

        {context}

        Provide:
        - Top 5 technical strengths
        - Top 3 professional strengths
        - 3-5 specific development recommendations
        - Suggested learning paths or skill improvements
        - Potential career advancement opportunities

        Generate strengths and recommendations:
        """
        
        response = self.llm.complete(prompt)
        return str(response).strip()
    
    def _generate_collaboration_style(self, context: str) -> str:
        """Generate collaboration style analysis."""
        prompt = f"""
        Based on the following contributor data, analyze their collaboration style:

        {context}

        Analyze:
        - Communication and collaboration patterns
        - Leadership and mentoring indicators
        - Community involvement level
        - Preferred working styles
        - Team contribution approach

        Generate a collaboration style analysis:
        """
        
        response = self.llm.complete(prompt)
        return str(response).strip()
    
    def _generate_career_trajectory(self, context: str) -> str:
        """Generate career trajectory analysis."""
        prompt = f"""
        Based on the following contributor data, analyze their career trajectory and potential:

        {context}

        Analyze:
        - Career progression indicators
        - Skill development patterns
        - Industry positioning
        - Future potential and opportunities
        - Recommended career paths

        Generate a career trajectory analysis:
        """
        
        response = self.llm.complete(prompt)
        return str(response).strip()
    
    def _extract_primary_languages(self, skills_data: Dict) -> List[str]:
        """Extract primary programming languages."""
        if not skills_data:
            return []
        
        languages = []
        for lang in ["python", "javascript", "go", "typescript", "java", "c", "ruby", "shell"]:
            score = skills_data.get(f"{lang}_score", 0)
            if score > 0.3:  # Threshold for primary language
                languages.append(lang.title())
        
        return sorted(languages, key=lambda x: skills_data.get(f"{x.lower()}_score", 0), reverse=True)
    
    def _assess_expertise_level(self, skills_data: Dict, contributions_data: List[Dict]) -> str:
        """Assess overall expertise level."""
        if not skills_data or not contributions_data:
            return "beginner"
        
        # Calculate average skill scores
        skill_scores = []
        for lang in ["python", "javascript", "go", "typescript", "java", "c", "ruby"]:
            score = skills_data.get(f"{lang}_score", 0)
            if score > 0:
                skill_scores.append(score)
        
        avg_skill_score = sum(skill_scores) / len(skill_scores) if skill_scores else 0
        total_contributions = sum(contrib.get("contribution_count", 0) for contrib in contributions_data)
        
        if avg_skill_score > 0.7 and total_contributions > 100:
            return "expert"
        elif avg_skill_score > 0.5 and total_contributions > 50:
            return "advanced"
        elif avg_skill_score > 0.3 and total_contributions > 20:
            return "intermediate"
        else:
            return "beginner"
    
    def _assess_activity_level(self, contributions_data: List[Dict]) -> str:
        """Assess activity level."""
        if not contributions_data:
            return "inactive"
        
        total_contributions = sum(contrib.get("contribution_count", 0) for contrib in contributions_data)
        repo_count = len(contributions_data)
        
        if total_contributions > 200 and repo_count > 10:
            return "very_active"
        elif total_contributions > 100 and repo_count > 5:
            return "active"
        elif total_contributions > 50 and repo_count > 3:
            return "moderately_active"
        else:
            return "occasional"
    
    def _identify_specialization_areas(self, skills_data: Dict) -> List[str]:
        """Identify areas of specialization."""
        if not skills_data:
            return []
        
        specializations = []
        domain_threshold = 0.6
        
        domain_mapping = {
            "web_development": "Web Development",
            "machine_learning": "Machine Learning",
            "data_science": "Data Science",
            "devops": "DevOps",
            "cloud_computing": "Cloud Computing",
            "database": "Database Systems",
            "backend": "Backend Development",
            "frontend": "Frontend Development",
            "system_programming": "System Programming"
        }
        
        for domain, label in domain_mapping.items():
            score = skills_data.get(domain, 0)
            if score > domain_threshold:
                specializations.append(label)
        
        return specializations
    
    def process_top_contributors(self, limit: int = 20) -> List[Dict]:
        """Process top contributors and generate profiles."""
        try:
            logger.info(f"Processing top {limit} contributors")
            
            # Get top contributors
            contributors = self.weaviate_client.query_data("Contributor", limit=limit)
            
            # Sort by total contributions
            sorted_contributors = sorted(
                contributors, 
                key=lambda x: x.get("total_contributions", 0), 
                reverse=True
            )
            
            processed_profiles = []
            
            for contributor in sorted_contributors[:limit]:
                try:
                    username = contributor.get("username", "")
                    
                    # Get skills data
                    skills_filter = {
                        "path": ["contributor_username"],
                        "operator": "Equal",
                        "valueString": username
                    }
                    skills_data = self.weaviate_client.query_data("Skills", where_filter=skills_filter)
                    skills = skills_data[0] if skills_data else {}
                    
                    # Get contributions data
                    contrib_filter = {
                        "path": ["contributor_username"],
                        "operator": "Equal",
                        "valueString": username
                    }
                    contributions_data = self.weaviate_client.query_data("Contribution", where_filter=contrib_filter)
                    
                    # Generate profile
                    profile = self.generate_contributor_profile(contributor, skills, contributions_data)
                    processed_profiles.append(profile)
                    
                    logger.info(f"Generated profile for {username}")
                    
                except Exception as e:
                    logger.error(f"Failed to process contributor {contributor.get('username', '')}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_profiles)} contributor profiles")
            return processed_profiles
            
        except Exception as e:
            logger.error(f"Failed to process top contributors: {e}")
            raise
    
    def save_profiles_to_weaviate(self, profiles: List[Dict]):
        """Save generated profiles back to Weaviate."""
        try:
            # Create ContributorProfile schema if it doesn't exist
            profile_schema = {
                "class": "ContributorProfile",
                "description": "AI-generated comprehensive contributor profiles",
                "properties": [
                    {"name": "username", "dataType": ["string"], "description": "Contributor username"},
                    {"name": "generated_at", "dataType": ["date"], "description": "Profile generation date"},
                    {"name": "professional_summary", "dataType": ["text"], "description": "Professional summary"},
                    {"name": "technical_expertise", "dataType": ["text"], "description": "Technical expertise analysis"},
                    {"name": "contribution_analysis", "dataType": ["text"], "description": "Contribution pattern analysis"},
                    {"name": "strengths_recommendations", "dataType": ["text"], "description": "Strengths and recommendations"},
                    {"name": "collaboration_style", "dataType": ["text"], "description": "Collaboration style analysis"},
                    {"name": "career_trajectory", "dataType": ["text"], "description": "Career trajectory analysis"},
                    {"name": "expertise_level", "dataType": ["string"], "description": "Overall expertise level"},
                    {"name": "activity_level", "dataType": ["string"], "description": "Activity level assessment"},
                    {"name": "primary_languages", "dataType": ["string[]"], "description": "Primary programming languages"},
                    {"name": "specialization_areas", "dataType": ["string[]"], "description": "Areas of specialization"},
                    {"name": "total_contributions", "dataType": ["int"], "description": "Total contributions"},
                    {"name": "total_repositories", "dataType": ["int"], "description": "Total repositories"},
                ]
            }
            
            try:
                self.weaviate_client.client.schema.create_class(profile_schema)
                logger.info("Created ContributorProfile schema")
            except Exception as e:
                logger.info(f"ContributorProfile schema might already exist: {e}")
            
            # Save profiles
            for profile in profiles:
                try:
                    profile_data = {
                        "username": profile["username"],
                        "generated_at": profile["generated_at"],
                        "professional_summary": profile["profile_sections"]["professional_summary"],
                        "technical_expertise": profile["profile_sections"]["technical_expertise"],
                        "contribution_analysis": profile["profile_sections"]["contribution_analysis"],
                        "strengths_recommendations": profile["profile_sections"]["strengths_recommendations"],
                        "collaboration_style": profile["profile_sections"]["collaboration_style"],
                        "career_trajectory": profile["profile_sections"]["career_trajectory"],
                        "expertise_level": profile["metadata"]["expertise_level"],
                        "activity_level": profile["metadata"]["activity_level"],
                        "primary_languages": profile["metadata"]["primary_languages"],
                        "specialization_areas": profile["metadata"]["specialization_areas"],
                        "total_contributions": profile["metadata"]["total_contributions"],
                        "total_repositories": profile["metadata"]["total_repositories"],
                    }
                    
                    self.weaviate_client.insert_data("ContributorProfile", profile_data)
                    logger.info(f"Saved profile for {profile['username']}")
                    
                except Exception as e:
                    logger.error(f"Failed to save profile for {profile['username']}: {e}")
                    continue
            
            logger.info("All profiles saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
            raise


def main():
    """Main function to generate contributor profiles."""
    try:
        # Initialize components
        weaviate_client = WeaviateClient()
        
        # Initialize profiler (you'll need to provide FriendliAI token)
        profiler = FriendliAIProfiler(
            friendli_token="your-friendli-token",
            weaviate_client=weaviate_client
        )
        
        # Process top contributors
        profiles = profiler.process_top_contributors(limit=10)
        
        # Save profiles to Weaviate
        profiler.save_profiles_to_weaviate(profiles)
        
        # Export profiles to JSON
        with open("contributor_profiles.json", "w") as f:
            json.dump(profiles, f, indent=2)
        
        logger.info("Contributor profiling completed successfully")
        
    except Exception as e:
        logger.error(f"Profiling failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()