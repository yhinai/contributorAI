"""Tests for insights engine."""

import pytest
from analytics.insights_engine import InsightsEngine


class TestInsightsEngine:
    """Test suite for insights engine."""
    
    @pytest.fixture
    def sample_contributors(self):
        """Sample contributor data for testing."""
        return [
            {
                "username": "alice",
                "total_commits": 100,
                "total_issues": 20,
                "repositories_count": 5,
                "skills": ["Python", "React", "Docker"],
                "expertise_areas": ["Backend", "DevOps"],
                "primary_languages": ["Python", "JavaScript"],
                "activity_level": "high",
                "contribution_style": "collaborative"
            },
            {
                "username": "bob",
                "total_commits": 50,
                "total_issues": 10,
                "repositories_count": 3,
                "skills": ["Java", "Spring", "Kubernetes"],
                "expertise_areas": ["Backend", "Microservices"],
                "primary_languages": ["Java", "Python"],
                "activity_level": "medium",
                "contribution_style": "independent"
            },
            {
                "username": "charlie",
                "total_commits": 25,
                "total_issues": 5,
                "repositories_count": 2,
                "skills": ["React", "TypeScript", "Node.js"],
                "expertise_areas": ["Frontend", "Full-stack"],
                "primary_languages": ["JavaScript", "TypeScript"],
                "activity_level": "low",
                "contribution_style": "collaborative"
            }
        ]
    
    @pytest.fixture
    def sample_repo_works(self):
        """Sample repository work data for testing."""
        return [
            {
                "contributor_id": "alice",
                "repository_id": "proj1",
                "repository_name": "project1",
                "commit_count": 60,
                "issue_count": 12,
                "technologies": ["Python", "Flask", "PostgreSQL"],
                "contribution_type": "feature_development"
            },
            {
                "contributor_id": "alice",
                "repository_id": "proj2",
                "repository_name": "project2",
                "commit_count": 40,
                "issue_count": 8,
                "technologies": ["React", "Node.js", "MongoDB"],
                "contribution_type": "full_stack"
            },
            {
                "contributor_id": "bob",
                "repository_id": "proj1",
                "repository_name": "project1",
                "commit_count": 30,
                "issue_count": 6,
                "technologies": ["Java", "Spring", "MySQL"],
                "contribution_type": "backend"
            },
            {
                "contributor_id": "charlie",
                "repository_id": "proj3",
                "repository_name": "project3",
                "commit_count": 25,
                "issue_count": 5,
                "technologies": ["React", "TypeScript", "GraphQL"],
                "contribution_type": "frontend"
            }
        ]
    
    @pytest.fixture
    def insights_engine(self, sample_contributors, sample_repo_works):
        """Create insights engine with sample data."""
        return InsightsEngine(sample_contributors, sample_repo_works)
    
    def test_get_overview_metrics(self, insights_engine):
        """Test overview metrics calculation."""
        overview = insights_engine.get_overview_metrics()
        
        assert overview["total_contributors"] == 3
        assert overview["total_commits"] == 175  # 100 + 50 + 25
        assert overview["total_issues"] == 35   # 20 + 10 + 5
        assert overview["avg_repos_per_contributor"] == 3.33  # (5 + 3 + 2) / 3
        assert "activity_distribution" in overview
        assert "top_languages" in overview
        assert overview["commits_per_contributor"] == 58.33  # 175 / 3
        assert overview["issues_per_contributor"] == 11.67   # 35 / 3
    
    def test_analyze_skill_distribution(self, insights_engine):
        """Test skill distribution analysis."""
        skill_analysis = insights_engine.analyze_skill_distribution()
        
        assert skill_analysis["total_unique_skills"] == 8  # All unique skills
        assert skill_analysis["avg_skills_per_contributor"] == 3.0  # Each has 3 skills
        assert "top_skills" in skill_analysis
        assert "skill_diversity_index" in skill_analysis
        assert "rare_skills" in skill_analysis
        
        # Check that React appears in top skills (appears in 2 contributors)
        top_skills_dict = dict(skill_analysis["top_skills"])
        assert "React" in top_skills_dict
        assert top_skills_dict["React"] == 2
    
    def test_analyze_repository_patterns(self, insights_engine):
        """Test repository pattern analysis."""
        repo_insights = insights_engine.analyze_repository_patterns()
        
        assert repo_insights["total_repositories"] == 3  # proj1, proj2, proj3
        assert "most_active_repositories" in repo_insights
        assert "avg_contributors_per_repo" in repo_insights
        assert "most_diverse_repositories" in repo_insights
        
        # Check that project1 has 2 contributors (alice and bob)
        most_active = repo_insights["most_active_repositories"]
        assert "project1" in most_active
        assert most_active["project1"]["contributor_count"] == 2
    
    def test_segment_contributors(self, insights_engine):
        """Test contributor segmentation."""
        segments = insights_engine.segment_contributors()
        
        assert "segments" in segments
        assert "segment_statistics" in segments
        assert "segmentation_criteria" in segments
        
        # Alice should be power_user (100 commits, 5 repos)
        assert "alice" in segments["segments"]["power_user"]
        
        # Bob should be active_contributor (50 commits, 3 repos)
        assert "bob" in segments["segments"]["active_contributor"]
        
        # Charlie should be regular_contributor (25 commits, 2 repos)
        assert "charlie" in segments["segments"]["regular_contributor"]
    
    def test_analyze_collaboration_patterns(self, insights_engine):
        """Test collaboration pattern analysis."""
        collab_patterns = insights_engine.analyze_collaboration_patterns()
        
        assert "total_collaborations" in collab_patterns
        assert "top_collaborations" in collab_patterns
        assert "most_collaborative_repositories" in collab_patterns
        
        # Alice and Bob both worked on project1, so they should be collaborators
        collaborations = collab_patterns["top_collaborations"]
        if collaborations:
            # Check if alice-bob collaboration exists
            collab_pairs = [pair for pair, count in collaborations]
            assert any(set(pair) == {"alice", "bob"} for pair in collab_pairs)
    
    def test_analyze_technology_trends(self, insights_engine):
        """Test technology trend analysis."""
        tech_trends = insights_engine.analyze_technology_trends()
        
        assert "total_technologies" in tech_trends
        assert "popular_technologies" in tech_trends
        assert "emerging_technologies" in tech_trends
        
        # React should be popular (appears in 2 repos)
        popular_techs = dict(tech_trends["popular_technologies"])
        assert "React" in popular_techs
        assert popular_techs["React"] == 2
    
    def test_calculate_productivity_metrics(self, insights_engine):
        """Test productivity metrics calculation."""
        productivity = insights_engine.calculate_productivity_metrics()
        
        assert "top_productive_contributors" in productivity
        assert "avg_commits_per_repo" in productivity
        assert "productivity_percentiles" in productivity
        
        # Alice should be most productive (100 commits / 5 repos = 20 commits per repo)
        top_productive = productivity["top_productive_contributors"]
        assert top_productive[0]["username"] == "alice"
        assert top_productive[0]["commits_per_repo"] == 20.0
    
    def test_generate_recommendations(self, insights_engine):
        """Test recommendations generation."""
        recommendations = insights_engine.generate_recommendations()
        
        assert "team_composition" in recommendations
        assert "skill_development" in recommendations
        assert "process_improvement" in recommendations
        assert "technology_adoption" in recommendations
        
        # Should have some recommendations
        assert len(recommendations["team_composition"]) > 0
        assert len(recommendations["skill_development"]) > 0
    
    def test_generate_contributor_report(self, insights_engine):
        """Test individual contributor report generation."""
        report = insights_engine.generate_contributor_report("alice")
        
        assert "basic_info" in report
        assert "metrics" in report
        assert "skills" in report
        assert "repository_breakdown" in report
        
        # Check basic info
        assert report["basic_info"]["username"] == "alice"
        assert report["basic_info"]["activity_level"] == "high"
        
        # Check metrics
        assert report["metrics"]["total_commits"] == 100
        assert report["metrics"]["total_issues"] == 20
        assert report["metrics"]["total_repositories"] == 5
        assert report["metrics"]["commits_per_repo"] == 20.0
        
        # Check skills
        assert "Python" in report["skills"]["technical_skills"]
        assert "Backend" in report["skills"]["expertise_areas"]
    
    def test_generate_contributor_report_nonexistent(self, insights_engine):
        """Test contributor report for non-existent user."""
        report = insights_engine.generate_contributor_report("nonexistent")
        
        assert report == {}
    
    def test_empty_data_handling(self):
        """Test handling of empty data."""
        empty_engine = InsightsEngine([], [])
        
        overview = empty_engine.get_overview_metrics()
        assert overview == {}
        
        skill_analysis = empty_engine.analyze_skill_distribution()
        assert skill_analysis == {}
        
        repo_insights = empty_engine.analyze_repository_patterns()
        assert repo_insights == {}


if __name__ == "__main__":
    pytest.main([__file__])