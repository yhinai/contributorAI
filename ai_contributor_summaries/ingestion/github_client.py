"""Direct GitHub API client for data ingestion."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx
from config.settings import settings
from utils.weaviate_client import weaviate_client
from utils.mock_weaviate import mock_weaviate_client
import os

logger = logging.getLogger(__name__)


class GitHubClient:
    """Direct GitHub API client for ingesting repository data."""
    
    def __init__(self):
        """Initialize GitHub client."""
        self.base_url = "https://api.github.com"
        self.token = settings.github_token
        self.session = None
        
        # Choose client based on environment
        if os.getenv('USE_MOCK_WEAVIATE') == 'true':
            self.weaviate_client = mock_weaviate_client
        else:
            self.weaviate_client = weaviate_client
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AI-Contributor-Summaries/1.0"
            },
            timeout=httpx.Timeout(30.0)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def fetch_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch basic repository information."""
        try:
            response = await self.session.get(f"/repos/{owner}/{repo}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch repository info for {owner}/{repo}: {e}")
            raise
    
    async def fetch_commits(self, owner: str, repo: str, since: Optional[datetime] = None, 
                           per_page: int = 100, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Fetch commits from repository with pagination."""
        try:
            all_commits = []
            page = 1
            
            while page <= max_pages:
                params = {
                    "per_page": per_page,
                    "page": page
                }
                
                if since:
                    params["since"] = since.isoformat()
                
                response = await self.session.get(f"/repos/{owner}/{repo}/commits", params=params)
                response.raise_for_status()
                
                commits = response.json()
                if not commits:
                    break
                
                all_commits.extend(commits)
                
                # Check if there are more pages
                if len(commits) < per_page:
                    break
                
                page += 1
                
                # Rate limiting - GitHub allows 5000 requests per hour
                await asyncio.sleep(0.1)
            
            logger.info(f"Fetched {len(all_commits)} commits for {owner}/{repo}")
            return all_commits
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch commits for {owner}/{repo}: {e}")
            raise
    
    async def fetch_commit_details(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """Fetch detailed commit information including diff."""
        try:
            response = await self.session.get(f"/repos/{owner}/{repo}/commits/{sha}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch commit details for {sha}: {e}")
            raise
    
    async def fetch_issues(self, owner: str, repo: str, state: str = "all", 
                          per_page: int = 100, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Fetch issues from repository with pagination."""
        try:
            all_issues = []
            page = 1
            
            while page <= max_pages:
                params = {
                    "state": state,
                    "per_page": per_page,
                    "page": page
                }
                
                response = await self.session.get(f"/repos/{owner}/{repo}/issues", params=params)
                response.raise_for_status()
                
                issues = response.json()
                if not issues:
                    break
                
                # Filter out pull requests (they appear in issues endpoint)
                actual_issues = [issue for issue in issues if not issue.get('pull_request')]
                all_issues.extend(actual_issues)
                
                if len(issues) < per_page:
                    break
                
                page += 1
                await asyncio.sleep(0.1)
            
            logger.info(f"Fetched {len(all_issues)} issues for {owner}/{repo}")
            return all_issues
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch issues for {owner}/{repo}: {e}")
            raise
    
    async def fetch_contributors(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch contributors from repository."""
        try:
            response = await self.session.get(
                f"/repos/{owner}/{repo}/contributors",
                params={"per_page": per_page}
            )
            response.raise_for_status()
            contributors = response.json()
            
            logger.info(f"Fetched {len(contributors)} contributors for {owner}/{repo}")
            return contributors
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch contributors for {owner}/{repo}: {e}")
            raise
    
    async def fetch_user_details(self, username: str) -> Dict[str, Any]:
        """Fetch detailed user information."""
        try:
            response = await self.session.get(f"/users/{username}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch user details for {username}: {e}")
            raise
    
    def process_commit_data(self, commit_data: Dict[str, Any], repo_id: str) -> Dict[str, Any]:
        """Process raw commit data into structured format."""
        try:
            commit_info = commit_data.get("commit", {})
            author = commit_info.get("author", {})
            committer = commit_info.get("committer", {})
            
            # Extract files changed
            files_changed = []
            if "files" in commit_data:
                files_changed = [f["filename"] for f in commit_data["files"]]
            
            # Build diff text
            diff_text = ""
            if "files" in commit_data:
                for file in commit_data["files"]:
                    if file.get("patch"):
                        diff_text += f"--- {file['filename']}\n{file['patch']}\n\n"
            
            return {
                "github_id": commit_data["sha"],
                "message": commit_info.get("message", ""),
                "diff": diff_text,
                "files_changed": files_changed,
                "summary": "",  # To be filled by summarization
                "repository_id": repo_id,
                "contributor_id": author.get("name", "unknown"),
                "created_at": datetime.fromisoformat(author.get("date", "").replace("Z", "+00:00")),
                "sha": commit_data["sha"],
                "additions": commit_data.get("stats", {}).get("additions", 0),
                "deletions": commit_data.get("stats", {}).get("deletions", 0),
                "technologies": []  # To be filled by analysis
            }
        except Exception as e:
            logger.error(f"Failed to process commit data: {e}")
            raise
    
    def process_issue_data(self, issue_data: Dict[str, Any], repo_id: str) -> Dict[str, Any]:
        """Process raw issue data into structured format."""
        try:
            return {
                "github_id": str(issue_data["id"]),
                "title": issue_data.get("title", ""),
                "body": issue_data.get("body", ""),
                "files_changed": [],  # Issues don't have direct file changes
                "summary": "",  # To be filled by summarization
                "repository_id": repo_id,
                "contributor_id": issue_data.get("user", {}).get("login", "unknown"),
                "created_at": datetime.fromisoformat(issue_data.get("created_at", "").replace("Z", "+00:00")),
                "updated_at": datetime.fromisoformat(issue_data.get("updated_at", "").replace("Z", "+00:00")),
                "state": issue_data.get("state", "unknown"),
                "labels": [label["name"] for label in issue_data.get("labels", [])]
            }
        except Exception as e:
            logger.error(f"Failed to process issue data: {e}")
            raise
    
    def process_contributor_data(self, contributor_data: Dict[str, Any], user_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process raw contributor data into structured format."""
        try:
            # Use detailed user info if available
            if user_details:
                username = user_details.get("login", contributor_data.get("login", ""))
                avatar_url = user_details.get("avatar_url", contributor_data.get("avatar_url", ""))
                github_id = str(user_details.get("id", contributor_data.get("id", 0)))
            else:
                username = contributor_data.get("login", "")
                avatar_url = contributor_data.get("avatar_url", "")
                github_id = str(contributor_data.get("id", 0))
            
            return {
                "github_id": github_id,
                "username": username,
                "avatar_url": avatar_url,
                "summary": "",  # To be filled by summarization
                "skills": [],  # To be filled by summarization
                "expertise_areas": [],  # To be filled by summarization
                "total_commits": contributor_data.get("contributions", 0),
                "total_issues": 0,  # To be calculated
                "repositories_count": 0,  # To be calculated
                "primary_languages": [],  # To be filled by analysis
                "contribution_style": "",  # To be filled by summarization
                "activity_level": ""  # To be filled by analysis
            }
        except Exception as e:
            logger.error(f"Failed to process contributor data: {e}")
            raise
    
    async def ingest_repository(self, owner: str, repo: str, max_commits: int = 500, max_issues: int = 500) -> Dict[str, int]:
        """Ingest complete repository data."""
        logger.info(f"Starting GitHub ingestion for {owner}/{repo}")
        
        try:
            repo_id = f"{owner}/{repo}"
            
            # Fetch repository info
            repo_info = await self.fetch_repository_info(owner, repo)
            logger.info(f"Repository: {repo_info.get('full_name')} - {repo_info.get('description', 'No description')}")
            
            # Fetch commits with details
            commits = await self.fetch_commits(owner, repo, max_pages=max_commits // 100)
            commit_count = 0
            
            # Process commits in batches to avoid overwhelming the API
            for i, commit in enumerate(commits):
                try:
                    # Get detailed commit info
                    commit_detail = await self.fetch_commit_details(owner, repo, commit["sha"])
                    processed_commit = self.process_commit_data(commit_detail, repo_id)
                    
                    # Store in Weaviate
                    self.weaviate_client.insert_data("Commit", processed_commit)
                    commit_count += 1
                    
                    # Rate limiting
                    if (i + 1) % 10 == 0:
                        await asyncio.sleep(1)
                        logger.info(f"Processed {i + 1}/{len(commits)} commits")
                        
                except Exception as e:
                    logger.error(f"Failed to process commit {commit['sha']}: {e}")
                    continue
            
            # Fetch and process issues
            issues = await self.fetch_issues(owner, repo, max_pages=max_issues // 100)
            issue_count = 0
            
            for issue in issues:
                try:
                    processed_issue = self.process_issue_data(issue, repo_id)
                    self.weaviate_client.insert_data("Issue", processed_issue)
                    issue_count += 1
                except Exception as e:
                    logger.error(f"Failed to process issue {issue['id']}: {e}")
                    continue
            
            # Fetch and process contributors
            contributors = await self.fetch_contributors(owner, repo)
            contributor_count = 0
            
            for contributor in contributors:
                try:
                    # Get detailed user info
                    user_details = await self.fetch_user_details(contributor["login"])
                    processed_contributor = self.process_contributor_data(contributor, user_details)
                    
                    # Check if contributor already exists
                    existing = self.weaviate_client.query_data(
                        "Contributor", 
                        where_filter={"path": ["github_id"], "operator": "Equal", "valueText": processed_contributor["github_id"]}
                    )
                    
                    if not existing:
                        self.weaviate_client.insert_data("Contributor", processed_contributor)
                        contributor_count += 1
                    
                    # Rate limiting
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"Failed to process contributor {contributor['login']}: {e}")
                    continue
            
            logger.info(f"GitHub ingestion completed for {owner}/{repo}: {commit_count} commits, {issue_count} issues, {contributor_count} contributors")
            
            return {
                "commits": commit_count,
                "issues": issue_count,
                "contributors": contributor_count
            }
            
        except Exception as e:
            logger.error(f"Failed to ingest repository {owner}/{repo}: {e}")
            raise


async def main():
    """Main function for testing ingestion."""
    async with GitHubClient() as github_client:
        # Initialize Weaviate schema
        if os.getenv('USE_MOCK_WEAVIATE') == 'true':
            mock_weaviate_client.create_schema()
        else:
            weaviate_client.create_schema()
        
        # Example repository ingestion
        result = await github_client.ingest_repository("microsoft", "vscode", max_commits=50, max_issues=50)
        print(f"Ingestion result: {result}")


if __name__ == "__main__":
    asyncio.run(main())