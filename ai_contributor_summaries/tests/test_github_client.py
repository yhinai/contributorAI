"""Tests for GitHub API client."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from ingestion.github_client import GitHubClient


class TestGitHubClient:
    """Test suite for GitHub API client."""
    
    @pytest.fixture
    def mock_weaviate_client(self):
        """Mock Weaviate client."""
        mock_client = Mock()
        mock_client.insert_data = Mock()
        mock_client.query_data = Mock(return_value=[])
        return mock_client
    
    @pytest.fixture
    def github_client(self, mock_weaviate_client):
        """Create GitHub client with mocked dependencies."""
        with patch('ingestion.github_client.mock_weaviate_client', mock_weaviate_client):
            with patch('os.getenv', return_value='true'):
                return GitHubClient()
    
    def test_process_commit_data(self, github_client):
        """Test commit data processing."""
        commit_data = {
            "sha": "abc123",
            "commit": {
                "message": "Fix bug in authentication",
                "author": {
                    "name": "John Doe",
                    "date": "2023-01-01T12:00:00Z"
                }
            },
            "files": [
                {"filename": "auth.py", "patch": "some diff"},
                {"filename": "tests/test_auth.py", "patch": "test diff"}
            ],
            "stats": {
                "additions": 10,
                "deletions": 5
            }
        }
        
        result = github_client.process_commit_data(commit_data, "owner/repo")
        
        assert result["github_id"] == "abc123"
        assert result["message"] == "Fix bug in authentication"
        assert result["contributor_id"] == "John Doe"
        assert result["repository_id"] == "owner/repo"
        assert result["files_changed"] == ["auth.py", "tests/test_auth.py"]
        assert result["additions"] == 10
        assert result["deletions"] == 5
        assert isinstance(result["created_at"], datetime)
    
    def test_process_issue_data(self, github_client):
        """Test issue data processing."""
        issue_data = {
            "id": 12345,
            "title": "Bug in login system",
            "body": "Users cannot login with valid credentials",
            "state": "open",
            "user": {"login": "jane_doe"},
            "created_at": "2023-01-01T12:00:00Z",
            "updated_at": "2023-01-02T12:00:00Z",
            "labels": [{"name": "bug"}, {"name": "priority-high"}]
        }
        
        result = github_client.process_issue_data(issue_data, "owner/repo")
        
        assert result["github_id"] == "12345"
        assert result["title"] == "Bug in login system"
        assert result["body"] == "Users cannot login with valid credentials"
        assert result["state"] == "open"
        assert result["contributor_id"] == "jane_doe"
        assert result["repository_id"] == "owner/repo"
        assert result["labels"] == ["bug", "priority-high"]
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)
    
    def test_process_contributor_data(self, github_client):
        """Test contributor data processing."""
        contributor_data = {
            "id": 67890,
            "login": "john_dev",
            "avatar_url": "https://github.com/john_dev.png",
            "contributions": 42
        }
        
        user_details = {
            "id": 67890,
            "login": "john_dev",
            "avatar_url": "https://github.com/john_dev.png",
            "name": "John Developer"
        }
        
        result = github_client.process_contributor_data(contributor_data, user_details)
        
        assert result["github_id"] == "67890"
        assert result["username"] == "john_dev"
        assert result["avatar_url"] == "https://github.com/john_dev.png"
        assert result["total_commits"] == 42
        assert result["total_issues"] == 0
        assert result["repositories_count"] == 0
        assert result["summary"] == ""
        assert result["skills"] == []
    
    @pytest.mark.asyncio
    async def test_fetch_repository_info(self, github_client):
        """Test repository info fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "full_name": "owner/repo",
            "description": "A test repository",
            "stargazers_count": 100
        }
        mock_response.raise_for_status = Mock()
        
        with patch.object(github_client, 'session') as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)
            
            result = await github_client.fetch_repository_info("owner", "repo")
            
            assert result["full_name"] == "owner/repo"
            assert result["description"] == "A test repository"
            assert result["stargazers_count"] == 100
            mock_session.get.assert_called_once_with("/repos/owner/repo")
    
    @pytest.mark.asyncio
    async def test_fetch_commits(self, github_client):
        """Test commits fetching with pagination."""
        mock_response1 = Mock()
        mock_response1.json.return_value = [
            {"sha": "abc123", "commit": {"message": "First commit"}},
            {"sha": "def456", "commit": {"message": "Second commit"}}
        ]
        mock_response1.raise_for_status = Mock()
        
        mock_response2 = Mock()
        mock_response2.json.return_value = []  # Empty response to stop pagination
        mock_response2.raise_for_status = Mock()
        
        with patch.object(github_client, 'session') as mock_session:
            mock_session.get = AsyncMock(side_effect=[mock_response1, mock_response2])
            
            result = await github_client.fetch_commits("owner", "repo", max_pages=2)
            
            assert len(result) == 2
            assert result[0]["sha"] == "abc123"
            assert result[1]["sha"] == "def456"
            assert mock_session.get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_fetch_issues(self, github_client):
        """Test issues fetching with PR filtering."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "title": "Bug report", "pull_request": None},
            {"id": 2, "title": "Feature request", "pull_request": {"url": "..."}},  # Should be filtered out
            {"id": 3, "title": "Another bug", "pull_request": None}
        ]
        mock_response.raise_for_status = Mock()
        
        with patch.object(github_client, 'session') as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)
            
            result = await github_client.fetch_issues("owner", "repo")
            
            assert len(result) == 2  # PR should be filtered out
            assert result[0]["id"] == 1
            assert result[1]["id"] == 3
    
    @pytest.mark.asyncio
    async def test_ingest_repository_error_handling(self, github_client, mock_weaviate_client):
        """Test error handling in repository ingestion."""
        with patch.object(github_client, 'fetch_repository_info') as mock_fetch_info:
            mock_fetch_info.side_effect = Exception("API Error")
            
            with pytest.raises(Exception) as exc_info:
                await github_client.ingest_repository("owner", "repo")
            
            assert "API Error" in str(exc_info.value)
    
    def test_github_client_initialization(self):
        """Test GitHub client initialization."""
        with patch('ingestion.github_client.settings') as mock_settings:
            mock_settings.github_token = "test_token"
            
            client = GitHubClient()
            
            assert client.base_url == "https://api.github.com"
            assert client.token == "test_token"


if __name__ == "__main__":
    pytest.main([__file__])