"""Advanced analytics engine for contributor insights."""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import logging

logger = logging.getLogger(__name__)


class InsightsEngine:
    """Generate advanced insights from contributor data."""
    
    def __init__(self, contributors: List[Dict], repo_works: List[Dict]):
        """Initialize with contributor and repository work data."""
        self.contributors = contributors
        self.repo_works = repo_works
        self.contributor_df = pd.DataFrame(contributors) if contributors else pd.DataFrame()
        self.repo_work_df = pd.DataFrame(repo_works) if repo_works else pd.DataFrame()
    
    def generate_comprehensive_insights(self) -> Dict[str, Any]:
        """Generate comprehensive insights across all dimensions."""
        insights = {
            'overview': self.get_overview_metrics(),
            'skill_analysis': self.analyze_skill_distribution(),
            'repository_insights': self.analyze_repository_patterns(),
            'contributor_segments': self.segment_contributors(),
            'collaboration_patterns': self.analyze_collaboration_patterns(),
            'technology_trends': self.analyze_technology_trends(),
            'productivity_metrics': self.calculate_productivity_metrics(),
            'recommendations': self.generate_recommendations()
        }
        return insights
    
    def get_overview_metrics(self) -> Dict[str, Any]:
        """Get high-level overview metrics."""
        if self.contributor_df.empty:
            return {}
        
        total_commits = self.contributor_df['total_commits'].sum()
        total_issues = self.contributor_df['total_issues'].sum()
        avg_repos_per_contributor = self.contributor_df['repositories_count'].mean()
        
        # Activity level distribution
        activity_dist = self.contributor_df['activity_level'].value_counts().to_dict()
        
        # Top programming languages
        all_languages = []
        for langs in self.contributor_df['primary_languages'].dropna():
            if isinstance(langs, list):
                all_languages.extend(langs)
        
        top_languages = Counter(all_languages).most_common(10)
        
        return {
            'total_contributors': len(self.contributor_df),
            'total_commits': int(total_commits),
            'total_issues': int(total_issues),
            'avg_repos_per_contributor': round(avg_repos_per_contributor, 2),
            'activity_distribution': activity_dist,
            'top_languages': top_languages,
            'commits_per_contributor': round(total_commits / len(self.contributor_df), 2),
            'issues_per_contributor': round(total_issues / len(self.contributor_df), 2)
        }
    
    def analyze_skill_distribution(self) -> Dict[str, Any]:
        """Analyze skill distribution across contributors."""
        if self.contributor_df.empty:
            return {}
        
        # Extract all skills
        all_skills = []
        skill_by_contributor = {}
        
        for _, contributor in self.contributor_df.iterrows():
            username = contributor['username']
            skills = contributor.get('skills', [])
            if isinstance(skills, list):
                all_skills.extend(skills)
                skill_by_contributor[username] = len(skills)
        
        # Skill frequency analysis
        skill_counts = Counter(all_skills)
        top_skills = skill_counts.most_common(15)
        
        # Skill diversity metrics
        avg_skills_per_contributor = np.mean(list(skill_by_contributor.values()))
        skill_diversity_index = len(skill_counts) / len(all_skills) if all_skills else 0
        
        # Rare skills (appeared in less than 20% of contributors)
        rare_threshold = len(self.contributor_df) * 0.2
        rare_skills = [skill for skill, count in skill_counts.items() if count < rare_threshold]
        
        return {
            'total_unique_skills': len(skill_counts),
            'top_skills': top_skills,
            'avg_skills_per_contributor': round(avg_skills_per_contributor, 2),
            'skill_diversity_index': round(skill_diversity_index, 3),
            'rare_skills': rare_skills[:10],  # Top 10 rare skills
            'skill_distribution': dict(skill_counts)
        }
    
    def analyze_repository_patterns(self) -> Dict[str, Any]:
        """Analyze repository contribution patterns."""
        if self.repo_work_df.empty:
            return {}
        
        # Repository activity analysis
        repo_activity = self.repo_work_df.groupby('repository_name').agg({
            'commit_count': 'sum',
            'issue_count': 'sum',
            'contributor_id': 'count'
        }).rename(columns={'contributor_id': 'contributor_count'})
        
        # Most active repositories
        most_active_repos = repo_activity.sort_values('commit_count', ascending=False).head(10)
        
        # Repository diversity
        avg_contributors_per_repo = repo_activity['contributor_count'].mean()
        
        # Technology analysis by repository
        repo_tech_analysis = defaultdict(set)
        for _, work in self.repo_work_df.iterrows():
            repo_name = work['repository_name']
            technologies = work.get('technologies', [])
            if isinstance(technologies, list):
                repo_tech_analysis[repo_name].update(technologies)
        
        # Most diverse repositories (by technology count)
        repo_diversity = {repo: len(techs) for repo, techs in repo_tech_analysis.items()}
        most_diverse_repos = sorted(repo_diversity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_repositories': len(repo_activity),
            'most_active_repositories': most_active_repos.to_dict('index'),
            'avg_contributors_per_repo': round(avg_contributors_per_repo, 2),
            'most_diverse_repositories': most_diverse_repos,
            'repository_activity_distribution': repo_activity.describe().to_dict()
        }
    
    def segment_contributors(self) -> Dict[str, Any]:
        """Segment contributors based on activity and expertise."""
        if self.contributor_df.empty:
            return {}
        
        # Create segments based on commits and repository count
        segments = {}
        
        for _, contributor in self.contributor_df.iterrows():
            commits = contributor.get('total_commits', 0)
            repos = contributor.get('repositories_count', 0)
            username = contributor['username']
            
            # Define segments
            if commits >= 100 and repos >= 3:
                segment = 'power_user'
            elif commits >= 50 and repos >= 2:
                segment = 'active_contributor'
            elif commits >= 20 or repos >= 1:
                segment = 'regular_contributor'
            else:
                segment = 'occasional_contributor'
            
            if segment not in segments:
                segments[segment] = []
            segments[segment].append(username)
        
        # Segment statistics
        segment_stats = {
            segment: {
                'count': len(contributors),
                'percentage': round(len(contributors) / len(self.contributor_df) * 100, 2)
            }
            for segment, contributors in segments.items()
        }
        
        return {
            'segments': segments,
            'segment_statistics': segment_stats,
            'segmentation_criteria': {
                'power_user': '100+ commits, 3+ repos',
                'active_contributor': '50+ commits, 2+ repos',
                'regular_contributor': '20+ commits or 1+ repos',
                'occasional_contributor': 'Less than 20 commits'
            }
        }
    
    def analyze_collaboration_patterns(self) -> Dict[str, Any]:
        """Analyze collaboration patterns between contributors."""
        if self.repo_work_df.empty:
            return {}
        
        # Find contributors who worked on the same repositories
        collaboration_matrix = defaultdict(set)
        repo_contributors = defaultdict(set)
        
        for _, work in self.repo_work_df.iterrows():
            repo_name = work['repository_name']
            contributor = work['contributor_id']
            repo_contributors[repo_name].add(contributor)
        
        # Calculate collaboration score
        collaborations = defaultdict(int)
        for repo, contributors in repo_contributors.items():
            contributor_list = list(contributors)
            for i in range(len(contributor_list)):
                for j in range(i + 1, len(contributor_list)):
                    pair = tuple(sorted([contributor_list[i], contributor_list[j]]))
                    collaborations[pair] += 1
        
        # Most frequent collaborations
        top_collaborations = sorted(collaborations.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Repository with most collaboration
        repo_collaboration_scores = {
            repo: len(contributors) * (len(contributors) - 1) // 2
            for repo, contributors in repo_contributors.items()
        }
        most_collaborative_repos = sorted(repo_collaboration_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_collaborations': len(collaborations),
            'top_collaborations': top_collaborations,
            'most_collaborative_repositories': most_collaborative_repos,
            'avg_collaborators_per_repo': round(np.mean([len(c) for c in repo_contributors.values()]), 2)
        }
    
    def analyze_technology_trends(self) -> Dict[str, Any]:
        """Analyze technology usage trends."""
        if self.repo_work_df.empty:
            return {}
        
        # Extract all technologies
        all_technologies = []
        tech_by_repo = defaultdict(set)
        
        for _, work in self.repo_work_df.iterrows():
            repo_name = work['repository_name']
            technologies = work.get('technologies', [])
            if isinstance(technologies, list):
                all_technologies.extend(technologies)
                tech_by_repo[repo_name].update(technologies)
        
        # Technology popularity
        tech_counts = Counter(all_technologies)
        popular_technologies = tech_counts.most_common(15)
        
        # Technology diversity by repository
        tech_diversity = {repo: len(techs) for repo, techs in tech_by_repo.items()}
        avg_tech_per_repo = np.mean(list(tech_diversity.values())) if tech_diversity else 0
        
        # Emerging technologies (less common but present)
        total_repos = len(tech_by_repo)
        emerging_threshold = max(1, total_repos * 0.1)  # Present in less than 10% of repos
        emerging_techs = [tech for tech, count in tech_counts.items() if count <= emerging_threshold]
        
        return {
            'total_technologies': len(tech_counts),
            'popular_technologies': popular_technologies,
            'emerging_technologies': emerging_techs[:10],
            'avg_technologies_per_repo': round(avg_tech_per_repo, 2),
            'technology_adoption_rate': dict(tech_counts)
        }
    
    def calculate_productivity_metrics(self) -> Dict[str, Any]:
        """Calculate productivity metrics for contributors."""
        if self.contributor_df.empty or self.repo_work_df.empty:
            return {}
        
        # Commits per repository
        contributor_productivity = []
        
        for _, contributor in self.contributor_df.iterrows():
            username = contributor['username']
            total_commits = contributor.get('total_commits', 0)
            total_repos = contributor.get('repositories_count', 0)
            
            if total_repos > 0:
                commits_per_repo = total_commits / total_repos
                contributor_productivity.append({
                    'username': username,
                    'commits_per_repo': commits_per_repo,
                    'total_commits': total_commits,
                    'total_repos': total_repos
                })
        
        # Sort by productivity
        contributor_productivity.sort(key=lambda x: x['commits_per_repo'], reverse=True)
        
        # Calculate percentiles
        productivity_values = [cp['commits_per_repo'] for cp in contributor_productivity]
        
        return {
            'top_productive_contributors': contributor_productivity[:10],
            'avg_commits_per_repo': round(np.mean(productivity_values), 2),
            'productivity_percentiles': {
                '90th': round(np.percentile(productivity_values, 90), 2),
                '75th': round(np.percentile(productivity_values, 75), 2),
                '50th': round(np.percentile(productivity_values, 50), 2),
                '25th': round(np.percentile(productivity_values, 25), 2)
            }
        }
    
    def generate_recommendations(self) -> Dict[str, List[str]]:
        """Generate actionable recommendations."""
        recommendations = {
            'team_composition': [],
            'skill_development': [],
            'process_improvement': [],
            'technology_adoption': []
        }
        
        if self.contributor_df.empty:
            return recommendations
        
        # Team composition recommendations
        skill_analysis = self.analyze_skill_distribution()
        if skill_analysis:
            top_skills = [skill for skill, _ in skill_analysis.get('top_skills', [])]
            rare_skills = skill_analysis.get('rare_skills', [])
            
            recommendations['team_composition'].extend([
                f"Consider hiring developers with {', '.join(top_skills[:3])} skills for high-demand areas",
                f"Recruit specialists in {', '.join(rare_skills[:3])} for niche expertise",
                "Focus on full-stack developers to improve team versatility"
            ])
        
        # Skill development recommendations
        tech_trends = self.analyze_technology_trends()
        if tech_trends:
            emerging_techs = tech_trends.get('emerging_technologies', [])
            recommendations['skill_development'].extend([
                f"Provide training in {', '.join(emerging_techs[:3])} for future readiness",
                "Encourage cross-training between frontend and backend technologies",
                "Implement mentorship programs for knowledge transfer"
            ])
        
        # Process improvement recommendations
        collab_patterns = self.analyze_collaboration_patterns()
        if collab_patterns:
            recommendations['process_improvement'].extend([
                "Implement code review processes to increase collaboration",
                "Create cross-functional teams for better knowledge sharing",
                "Establish regular tech talks and knowledge sharing sessions"
            ])
        
        # Technology adoption recommendations
        if tech_trends:
            popular_techs = [tech for tech, _ in tech_trends.get('popular_technologies', [])]
            recommendations['technology_adoption'].extend([
                f"Standardize on {', '.join(popular_techs[:3])} for consistency",
                "Evaluate modern alternatives to legacy technologies",
                "Implement technology decision frameworks for consistency"
            ])
        
        return recommendations
    
    def generate_contributor_report(self, username: str) -> Dict[str, Any]:
        """Generate detailed report for a specific contributor."""
        contributor = self.contributor_df[self.contributor_df['username'] == username]
        if contributor.empty:
            return {}
        
        contributor_data = contributor.iloc[0].to_dict()
        
        # Get repository work for this contributor
        contributor_work = self.repo_work_df[self.repo_work_df['contributor_id'] == username]
        
        # Calculate metrics
        total_commits = contributor_data.get('total_commits', 0)
        total_issues = contributor_data.get('total_issues', 0)
        total_repos = contributor_data.get('repositories_count', 0)
        
        # Repository breakdown
        repo_breakdown = []
        for _, work in contributor_work.iterrows():
            repo_breakdown.append({
                'repository': work['repository_name'],
                'commits': work.get('commit_count', 0),
                'issues': work.get('issue_count', 0),
                'technologies': work.get('technologies', []),
                'contribution_type': work.get('contribution_type', 'unknown')
            })
        
        # Skill assessment
        skills = contributor_data.get('skills', [])
        expertise_areas = contributor_data.get('expertise_areas', [])
        
        return {
            'basic_info': {
                'username': username,
                'activity_level': contributor_data.get('activity_level', 'unknown'),
                'contribution_style': contributor_data.get('contribution_style', 'unknown')
            },
            'metrics': {
                'total_commits': total_commits,
                'total_issues': total_issues,
                'total_repositories': total_repos,
                'commits_per_repo': round(total_commits / total_repos, 2) if total_repos > 0 else 0
            },
            'skills': {
                'technical_skills': skills,
                'expertise_areas': expertise_areas,
                'primary_languages': contributor_data.get('primary_languages', [])
            },
            'repository_breakdown': repo_breakdown,
            'ai_summary': contributor_data.get('summary', '')
        }