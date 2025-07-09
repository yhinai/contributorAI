"""FriendliAI client for LLM-powered summarization."""

import logging
from typing import Dict, List, Optional, Any
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)


class FriendliAIClient:
    """FriendliAI client for generating AI summaries."""
    
    def __init__(self):
        """Initialize FriendliAI client."""
        self.base_url = settings.friendliai_base_url
        self.api_key = settings.friendliai_api_key
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(120.0)  # Longer timeout for AI processing
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def generate_completion(self, messages: List[Dict[str, str]], 
                                 model: str = "mixtral-8x7b-instruct",
                                 max_tokens: int = 1000,
                                 temperature: float = 0.1) -> str:
        """Generate completion using FriendliAI."""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = await self.session.post("/v1/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except httpx.HTTPError as e:
            logger.error(f"FriendliAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to generate completion: {e}")
            raise
    
    async def summarize_issue(self, issue_data: Dict[str, Any], system_prompt: str) -> str:
        """Summarize a GitHub issue using AI."""
        try:
            user_message = f"""
            Title: {issue_data.get('title', 'No title')}
            Body: {issue_data.get('body', 'No body')}
            Labels: {', '.join(issue_data.get('labels', []))}
            Files mentioned: {', '.join(issue_data.get('files_changed', []))}
            State: {issue_data.get('state', 'unknown')}
            Created: {issue_data.get('created_at', 'unknown')}
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message.strip()}
            ]
            
            return await self.generate_completion(messages, max_tokens=300)
            
        except Exception as e:
            logger.error(f"Failed to summarize issue {issue_data.get('github_id', 'unknown')}: {e}")
            raise
    
    async def summarize_commit(self, commit_data: Dict[str, Any], system_prompt: str) -> str:
        """Summarize a Git commit using AI."""
        try:
            # Truncate diff if too long
            diff = commit_data.get('diff', '')
            if len(diff) > 3000:
                diff = diff[:3000] + "\n... (truncated)"
            
            user_message = f"""
            Commit message: {commit_data.get('message', 'No message')}
            Diff/Patch: {diff}
            Files changed: {', '.join(commit_data.get('files_changed', []))}
            Additions: {commit_data.get('additions', 0)} lines
            Deletions: {commit_data.get('deletions', 0)} lines
            SHA: {commit_data.get('sha', 'unknown')}
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message.strip()}
            ]
            
            return await self.generate_completion(messages, max_tokens=250)
            
        except Exception as e:
            logger.error(f"Failed to summarize commit {commit_data.get('github_id', 'unknown')}: {e}")
            raise
    
    async def summarize_repository_work(self, repo_work_data: Dict[str, Any], 
                                       commit_summaries: List[str],
                                       issue_summaries: List[str],
                                       system_prompt: str) -> str:
        """Summarize a contributor's work in a repository."""
        try:
            # Combine and truncate summaries if too long
            combined_commits = "\n".join(commit_summaries[:10])  # Limit to 10 recent commits
            combined_issues = "\n".join(issue_summaries[:10])    # Limit to 10 recent issues
            
            user_message = f"""
            Repository: {repo_work_data.get('repository_name', 'Unknown')}
            Contributor: {repo_work_data.get('contributor_id', 'Unknown')}
            
            Commit summaries:
            {combined_commits}
            
            Issue summaries:
            {combined_issues}
            
            Files frequently modified: {', '.join(repo_work_data.get('files_touched', []))}
            Contribution timeframe: {repo_work_data.get('first_contribution', 'Unknown')} to {repo_work_data.get('last_contribution', 'Unknown')}
            Total commits: {repo_work_data.get('commit_count', 0)}
            Total issues: {repo_work_data.get('issue_count', 0)}
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message.strip()}
            ]
            
            return await self.generate_completion(messages, max_tokens=400)
            
        except Exception as e:
            logger.error(f"Failed to summarize repository work: {e}")
            raise
    
    async def summarize_contributor(self, contributor_data: Dict[str, Any],
                                   repository_summaries: List[str],
                                   system_prompt: str) -> str:
        """Summarize a contributor's overall profile."""
        try:
            # Combine repository summaries with truncation
            combined_repos = "\n\n".join(repository_summaries[:5])  # Limit to 5 repositories
            
            user_message = f"""
            Contributor: {contributor_data.get('username', 'Unknown')}
            
            Repository work summaries:
            {combined_repos}
            
            Total commits: {contributor_data.get('total_commits', 0)}
            Total issues: {contributor_data.get('total_issues', 0)}
            Primary languages: {', '.join(contributor_data.get('primary_languages', []))}
            Repositories contributed to: {contributor_data.get('repositories_count', 0)}
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message.strip()}
            ]
            
            return await self.generate_completion(messages, max_tokens=500)
            
        except Exception as e:
            logger.error(f"Failed to summarize contributor {contributor_data.get('username', 'unknown')}: {e}")
            raise
    
    async def extract_skills(self, work_summary: str, extraction_prompt: str) -> List[str]:
        """Extract skills from work summary."""
        try:
            user_message = f"Technical work: {work_summary}"
            
            messages = [
                {"role": "system", "content": extraction_prompt},
                {"role": "user", "content": user_message}
            ]
            
            result = await self.generate_completion(messages, max_tokens=200)
            
            # Parse JSON response and extract skills
            import json
            try:
                skills_data = json.loads(result)
                all_skills = []
                for category, skills in skills_data.items():
                    all_skills.extend(skills)
                return all_skills
            except json.JSONDecodeError:
                # Fallback: extract skills from text
                return [skill.strip() for skill in result.split(',') if skill.strip()]
                
        except Exception as e:
            logger.error(f"Failed to extract skills: {e}")
            return []
    
    async def detect_technologies(self, files_changed: List[str], 
                                 commit_message: str, 
                                 diff_snippet: str,
                                 detection_prompt: str) -> List[str]:
        """Detect technologies from code changes."""
        try:
            user_message = f"""
            Files changed: {', '.join(files_changed)}
            Commit message: {commit_message}
            Code diff: {diff_snippet[:1000]}  # Truncate for context
            """
            
            messages = [
                {"role": "system", "content": detection_prompt},
                {"role": "user", "content": user_message}
            ]
            
            result = await self.generate_completion(messages, max_tokens=150)
            
            # Parse JSON response or fallback to text parsing
            import json
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return [tech.strip() for tech in result.split(',') if tech.strip()]
                
        except Exception as e:
            logger.error(f"Failed to detect technologies: {e}")
            return []


# Global client instance
friendliai_client = FriendliAIClient()