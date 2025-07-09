"""ACI.dev integration for GitHub data ingestion."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx
from config.settings import settings
from utils.weaviate_client import weaviate_client

logger = logging.getLogger(__name__)


class ACIIngester:
    """ACI.dev client for ingesting GitHub data."""
    
    def __init__(self):
        """Initialize ACI.dev client."""
        self.base_url = settings.aci_dev_base_url
        self.api_key = settings.aci_dev_api_key
        self.github_token = settings.github_token
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(30.0)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
    
    async def fetch_repository_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository data from GitHub via ACI.dev."""
        try:
            response = await self.session.get(
                f"/github/repositories/{owner}/{repo}",
                headers={"X-GitHub-Token": self.github_token}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch repository data for {owner}/{repo}: {e}")
            raise
    
    async def fetch_commits(self, owner: str, repo: str, since: Optional[datetime] = None, 
                           per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch commits from repository."""
        try:
            params = {"per_page": per_page}
            if since:
                params["since"] = since.isoformat()
            
            response = await self.session.get(
                f"/github/repositories/{owner}/{repo}/commits",
                params=params,
                headers={"X-GitHub-Token": self.github_token}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch commits for {owner}/{repo}: {e}")
            raise
    
    async def fetch_issues(self, owner: str, repo: str, state: str = "all", 
                          per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch issues from repository."""
        try:
            params = {"state": state, "per_page": per_page}
            
            response = await self.session.get(
                f"/github/repositories/{owner}/{repo}/issues",
                params=params,
                headers={"X-GitHub-Token": self.github_token}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch issues for {owner}/{repo}: {e}")
            raise
    
    async def fetch_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch contributors from repository."""
        try:
            response = await self.session.get(
                f"/github/repositories/{owner}/{repo}/contributors",
                headers={"X-GitHub-Token": self.github_token}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch contributors for {owner}/{repo}: {e}")
            raise
    
    async def fetch_commit_diff(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """Fetch commit diff details."""
        try:
            response = await self.session.get(
                f"/github/repositories/{owner}/{repo}/commits/{sha}",
                headers={"X-GitHub-Token": self.github_token}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch commit diff for {sha}: {e}")
            raise
    
    def process_commit_data(self, commit_data: Dict[str, Any], repo_id: str) -> Dict[str, Any]:
        """Process raw commit data into structured format."""
        try:
            author = commit_data.get("author", {})
            commit_info = commit_data.get("commit", {})
            
            return {
                "github_id": commit_data["sha"],
                "message": commit_info.get("message", ""),
                "diff": commit_data.get("patch", ""),
                "files_changed": [f["filename"] for f in commit_data.get("files", [])],
                "summary": "",  # To be filled by summarization
                "repository_id": repo_id,
                "contributor_id": author.get("login", "unknown"),
                "created_at": datetime.fromisoformat(commit_info.get("author", {}).get("date", "").replace("Z", "+00:00")),
                "sha": commit_data["sha"],
                "additions": commit_data.get("stats", {}).get("additions", 0),
                "deletions": commit_data.get("stats", {}).get("deletions", 0),
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
                "labels": [label["name"] for label in issue_data.get("labels", [])],
            }
        except Exception as e:
            logger.error(f"Failed to process issue data: {e}")
            raise
    
    def process_contributor_data(self, contributor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw contributor data into structured format."""
        try:
            return {
                "github_id": str(contributor_data["id"]),
                "username": contributor_data.get("login", ""),
                "avatar_url": contributor_data.get("avatar_url", ""),
                "summary": "",  # To be filled by summarization
                "skills": [],  # To be filled by summarization
                "expertise_areas": [],  # To be filled by summarization
                "total_commits": contributor_data.get("contributions", 0),
                "total_issues": 0,  # To be calculated
                "repositories_count": 0,  # To be calculated
                "primary_languages": [],  # To be filled by analysis
                "contribution_style": "",  # To be filled by summarization
                "activity_level": "",  # To be filled by analysis
            }
        except Exception as e:
            logger.error(f"Failed to process contributor data: {e}")
            raise
    
    async def ingest_repository(self, owner: str, repo: str) -> Dict[str, int]:
        """Ingest complete repository data."""
        logger.info(f"Starting ingestion for {owner}/{repo}")
        
        try:
            # Fetch repository metadata
            repo_data = await self.fetch_repository_data(owner, repo)
            repo_id = f"{owner}/{repo}"
            
            # Fetch and process commits
            commits = await self.fetch_commits(owner, repo)
            commit_count = 0
            
            for commit in commits:
                # Fetch detailed commit data with diff
                commit_detail = await self.fetch_commit_diff(owner, repo, commit["sha"])
                processed_commit = self.process_commit_data(commit_detail, repo_id)
                
                # Store in Weaviate
                weaviate_client.insert_data("Commit", processed_commit)
                commit_count += 1
            
            # Fetch and process issues
            issues = await self.fetch_issues(owner, repo)
            issue_count = 0
            
            for issue in issues:
                processed_issue = self.process_issue_data(issue, repo_id)
                
                # Store in Weaviate
                weaviate_client.insert_data("Issue", processed_issue)
                issue_count += 1
            
            # Fetch and process contributors
            contributors = await self.fetch_contributors(owner, repo)
            contributor_count = 0
            
            for contributor in contributors:
                processed_contributor = self.process_contributor_data(contributor)
                
                # Check if contributor already exists
                existing = weaviate_client.query_data(
                    "Contributor", 
                    where_filter={"path": ["github_id"], "operator": "Equal", "valueText": processed_contributor["github_id"]}
                )
                
                if not existing:
                    weaviate_client.insert_data("Contributor", processed_contributor)
                    contributor_count += 1
            
            logger.info(f"Ingestion completed for {owner}/{repo}: {commit_count} commits, {issue_count} issues, {contributor_count} contributors")
            
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
    async with ACIIngester() as ingester:
        # Initialize Weaviate schema
        weaviate_client.create_schema()
        
        # Example repository ingestion
        result = await ingester.ingest_repository("microsoft", "vscode")
        print(f"Ingestion result: {result}")


if __name__ == "__main__":
    asyncio.run(main())