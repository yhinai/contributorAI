"""Hypermode workflow orchestrator for 4-phase summarization pipeline."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx
from config.settings import settings
from utils.weaviate_client import weaviate_client
from utils.mock_weaviate import mock_weaviate_client
import os
from .friendliai_client import FriendliAIClient
from prompts import (
    ISSUES_SYSTEM_PROMPT,
    COMMITS_SYSTEM_PROMPT,
    REPO_WORK_SYSTEM_PROMPT,
    CONTRIBUTOR_SYSTEM_PROMPT,
    SKILLS_EXTRACTION_PROMPT,
    TECHNOLOGY_DETECTION_PROMPT
)

logger = logging.getLogger(__name__)


class HypermodeOrchestrator:
    """Hypermode orchestrator for managing summarization workflows."""
    
    def __init__(self):
        """Initialize Hypermode orchestrator."""
        self.base_url = settings.hypermode_base_url
        self.api_key = settings.hypermode_api_key
        self.session = None
        self.friendliai_client = FriendliAIClient()
        
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
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(300.0)  # 5 minute timeout for workflows
        )
        await self.friendliai_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()
        await self.friendliai_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def create_workflow(self, workflow_name: str, workflow_config: Dict[str, Any]) -> str:
        """Create a new workflow in Hypermode."""
        try:
            payload = {
                "name": workflow_name,
                "config": workflow_config,
                "description": f"AI Contributor Summaries - {workflow_name}",
                "version": "1.0.0"
            }
            
            response = await self.session.post("/v1/workflows", json=payload)
            response.raise_for_status()
            
            result = response.json()
            workflow_id = result["id"]
            logger.info(f"Created workflow: {workflow_name} ({workflow_id})")
            return workflow_id
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to create workflow {workflow_name}: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with input data."""
        try:
            payload = {
                "workflow_id": workflow_id,
                "input": input_data,
                "async": False
            }
            
            response = await self.session.post("/v1/workflows/execute", json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Executed workflow {workflow_id}")
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            raise
    
    async def phase_1_summarize_issues(self, batch_size: int = 10) -> Dict[str, int]:
        """Phase 1: Summarize unsummarized issues."""
        logger.info("Starting Phase 1: Issue Summarization")
        
        # Query unsummarized issues
        issues = self.weaviate_client.query_data(
            "Issue",
            where_filter={"path": ["summary"], "operator": "Equal", "valueText": ""},
            limit=batch_size
        )
        
        processed_count = 0
        failed_count = 0
        
        for issue in issues:
            try:
                # Generate summary using FriendliAI
                summary = await self.friendliai_client.summarize_issue(
                    issue, ISSUES_SYSTEM_PROMPT
                )
                
                # Update issue with summary
                self.weaviate_client.update_data(
                    "Issue", 
                    issue["uuid"], 
                    {"summary": summary}
                )
                
                processed_count += 1
                logger.debug(f"Summarized issue {issue['github_id']}")
                
            except Exception as e:
                logger.error(f"Failed to summarize issue {issue.get('github_id', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"Phase 1 completed: {processed_count} issues summarized, {failed_count} failed")
        return {"processed": processed_count, "failed": failed_count}
    
    async def phase_2_summarize_commits(self, batch_size: int = 10) -> Dict[str, int]:
        """Phase 2: Summarize unsummarized commits."""
        logger.info("Starting Phase 2: Commit Summarization")
        
        # Query unsummarized commits
        commits = self.weaviate_client.query_data(
            "Commit",
            where_filter={"path": ["summary"], "operator": "Equal", "valueText": ""},
            limit=batch_size
        )
        
        processed_count = 0
        failed_count = 0
        
        for commit in commits:
            try:
                # Generate summary using FriendliAI
                summary = await self.friendliai_client.summarize_commit(
                    commit, COMMITS_SYSTEM_PROMPT
                )
                
                # Detect technologies from commit
                technologies = await self.friendliai_client.detect_technologies(
                    commit.get('files_changed', []),
                    commit.get('message', ''),
                    commit.get('diff', ''),
                    TECHNOLOGY_DETECTION_PROMPT
                )
                
                # Update commit with summary and technologies
                self.weaviate_client.update_data(
                    "Commit", 
                    commit["uuid"], 
                    {
                        "summary": summary,
                        "technologies": technologies
                    }
                )
                
                processed_count += 1
                logger.debug(f"Summarized commit {commit['github_id']}")
                
            except Exception as e:
                logger.error(f"Failed to summarize commit {commit.get('github_id', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"Phase 2 completed: {processed_count} commits summarized, {failed_count} failed")
        return {"processed": processed_count, "failed": failed_count}
    
    async def phase_3_summarize_repository_work(self, batch_size: int = 5) -> Dict[str, int]:
        """Phase 3: Aggregate commits and issues into repository-level summaries."""
        logger.info("Starting Phase 3: Repository Work Summarization")
        
        # Get all contributors and their repositories
        contributors = self.weaviate_client.query_data("Contributor", limit=batch_size)
        
        processed_count = 0
        failed_count = 0
        
        for contributor in contributors:
            try:
                # Get commits for this contributor
                commits = self.weaviate_client.query_data(
                    "Commit",
                    where_filter={"path": ["contributor_id"], "operator": "Equal", "valueText": contributor["username"]},
                    limit=100
                )
                
                # Get issues for this contributor
                issues = self.weaviate_client.query_data(
                    "Issue",
                    where_filter={"path": ["contributor_id"], "operator": "Equal", "valueText": contributor["username"]},
                    limit=100
                )
                
                # Group by repository
                repos_work = {}
                for commit in commits:
                    repo_id = commit.get("repository_id")
                    if repo_id not in repos_work:
                        repos_work[repo_id] = {
                            "commits": [],
                            "issues": [],
                            "files_touched": set(),
                            "first_contribution": None,
                            "last_contribution": None
                        }
                    
                    repos_work[repo_id]["commits"].append(commit)
                    repos_work[repo_id]["files_touched"].update(commit.get("files_changed", []))
                    
                    # Update contribution dates
                    commit_date = commit.get("created_at")
                    if commit_date:
                        if not repos_work[repo_id]["first_contribution"] or commit_date < repos_work[repo_id]["first_contribution"]:
                            repos_work[repo_id]["first_contribution"] = commit_date
                        if not repos_work[repo_id]["last_contribution"] or commit_date > repos_work[repo_id]["last_contribution"]:
                            repos_work[repo_id]["last_contribution"] = commit_date
                
                # Add issues to repository work
                for issue in issues:
                    repo_id = issue.get("repository_id")
                    if repo_id in repos_work:
                        repos_work[repo_id]["issues"].append(issue)
                
                # Generate repository work summaries
                for repo_id, work_data in repos_work.items():
                    try:
                        # Check if repository work already exists
                        existing_work = self.weaviate_client.query_data(
                            "RepositoryWork",
                            where_filter={
                                "operator": "And",
                                "operands": [
                                    {"path": ["contributor_id"], "operator": "Equal", "valueText": contributor["username"]},
                                    {"path": ["repository_id"], "operator": "Equal", "valueText": repo_id}
                                ]
                            }
                        )
                        
                        if existing_work:
                            continue  # Skip if already exists
                        
                        # Prepare data for summarization
                        repo_work_data = {
                            "contributor_id": contributor["username"],
                            "repository_id": repo_id,
                            "repository_name": repo_id.split("/")[-1],
                            "commit_count": len(work_data["commits"]),
                            "issue_count": len(work_data["issues"]),
                            "files_touched": list(work_data["files_touched"]),
                            "first_contribution": work_data["first_contribution"],
                            "last_contribution": work_data["last_contribution"]
                        }
                        
                        # Get commit and issue summaries
                        commit_summaries = [c.get("summary", "") for c in work_data["commits"] if c.get("summary")]
                        issue_summaries = [i.get("summary", "") for i in work_data["issues"] if i.get("summary")]
                        
                        # Generate repository work summary
                        if commit_summaries or issue_summaries:
                            summary = await self.friendliai_client.summarize_repository_work(
                                repo_work_data,
                                commit_summaries,
                                issue_summaries,
                                REPO_WORK_SYSTEM_PROMPT
                            )
                            
                            # Extract technologies from commits
                            all_technologies = set()
                            for commit in work_data["commits"]:
                                all_technologies.update(commit.get("technologies", []))
                            
                            # Store repository work summary
                            repo_work_data.update({
                                "summary": summary,
                                "technologies": list(all_technologies),
                                "contribution_type": "mixed"  # Can be enhanced with classification
                            })
                            
                            self.weaviate_client.insert_data("RepositoryWork", repo_work_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to summarize repository work for {repo_id}: {e}")
                        failed_count += 1
                
                processed_count += 1
                logger.debug(f"Processed repository work for {contributor['username']}")
                
            except Exception as e:
                logger.error(f"Failed to process contributor {contributor.get('username', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"Phase 3 completed: {processed_count} contributors processed, {failed_count} failed")
        return {"processed": processed_count, "failed": failed_count}
    
    async def phase_4_summarize_contributors(self, batch_size: int = 5) -> Dict[str, int]:
        """Phase 4: Aggregate repository work into contributor profiles."""
        logger.info("Starting Phase 4: Contributor Profile Summarization")
        
        # Get contributors without summaries
        contributors = self.weaviate_client.query_data(
            "Contributor",
            where_filter={"path": ["summary"], "operator": "Equal", "valueText": ""},
            limit=batch_size
        )
        
        processed_count = 0
        failed_count = 0
        
        for contributor in contributors:
            try:
                # Get repository work summaries for this contributor
                repo_works = self.weaviate_client.query_data(
                    "RepositoryWork",
                    where_filter={"path": ["contributor_id"], "operator": "Equal", "valueText": contributor["username"]},
                    limit=50
                )
                
                if not repo_works:
                    continue
                
                # Prepare data for contributor summarization
                repository_summaries = [rw.get("summary", "") for rw in repo_works if rw.get("summary")]
                
                # Calculate totals
                total_commits = sum(rw.get("commit_count", 0) for rw in repo_works)
                total_issues = sum(rw.get("issue_count", 0) for rw in repo_works)
                
                # Extract technologies and languages
                all_technologies = set()
                for rw in repo_works:
                    all_technologies.update(rw.get("technologies", []))
                
                # Update contributor data
                contributor_data = {
                    "username": contributor["username"],
                    "total_commits": total_commits,
                    "total_issues": total_issues,
                    "repositories_count": len(repo_works),
                    "primary_languages": list(all_technologies)[:10]  # Top 10 technologies
                }
                
                # Generate contributor profile summary
                if repository_summaries:
                    summary = await self.friendliai_client.summarize_contributor(
                        contributor_data,
                        repository_summaries,
                        CONTRIBUTOR_SYSTEM_PROMPT
                    )
                    
                    # Extract skills from summary
                    skills = await self.friendliai_client.extract_skills(
                        summary,
                        SKILLS_EXTRACTION_PROMPT
                    )
                    
                    # Update contributor with profile data
                    update_data = {
                        "summary": summary,
                        "skills": skills,
                        "expertise_areas": list(all_technologies)[:5],  # Top 5 as expertise
                        "total_commits": total_commits,
                        "total_issues": total_issues,
                        "repositories_count": len(repo_works),
                        "primary_languages": list(all_technologies)[:10],
                        "contribution_style": "collaborative",  # Can be enhanced with analysis
                        "activity_level": "active"  # Can be enhanced with analysis
                    }
                    
                    self.weaviate_client.update_data("Contributor", contributor["uuid"], update_data)
                    
                    processed_count += 1
                    logger.debug(f"Summarized contributor {contributor['username']}")
                
            except Exception as e:
                logger.error(f"Failed to summarize contributor {contributor.get('username', 'unknown')}: {e}")
                failed_count += 1
        
        logger.info(f"Phase 4 completed: {processed_count} contributors summarized, {failed_count} failed")
        return {"processed": processed_count, "failed": failed_count}
    
    async def run_full_pipeline(self, batch_size: int = 10) -> Dict[str, Any]:
        """Run the complete 4-phase summarization pipeline."""
        logger.info("Starting complete 4-phase summarization pipeline")
        
        start_time = datetime.now()
        results = {}
        
        try:
            # Phase 1: Summarize Issues
            results["phase_1"] = await self.phase_1_summarize_issues(batch_size)
            
            # Phase 2: Summarize Commits
            results["phase_2"] = await self.phase_2_summarize_commits(batch_size)
            
            # Phase 3: Summarize Repository Work
            results["phase_3"] = await self.phase_3_summarize_repository_work(batch_size // 2)
            
            # Phase 4: Summarize Contributors
            results["phase_4"] = await self.phase_4_summarize_contributors(batch_size // 2)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results["pipeline_summary"] = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "total_processed": sum(phase.get("processed", 0) for phase in results.values() if isinstance(phase, dict)),
                "total_failed": sum(phase.get("failed", 0) for phase in results.values() if isinstance(phase, dict))
            }
            
            logger.info(f"Pipeline completed in {duration:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise


# Global orchestrator instance
hypermode_orchestrator = HypermodeOrchestrator()