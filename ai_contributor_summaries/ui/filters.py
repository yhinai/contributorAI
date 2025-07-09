"""Advanced filtering and search capabilities for the UI."""

import streamlit as st
import pandas as pd
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta


class AdvancedFilters:
    """Advanced filtering system for contributors and repositories."""
    
    def __init__(self):
        """Initialize the filter system."""
        self.active_filters = {}
    
    def render_contributor_filters(self, contributors: List[Dict]) -> Dict[str, Any]:
        """Render advanced contributor filters."""
        st.sidebar.header("🔍 Advanced Filters")
        
        filters = {}
        
        # Text search
        filters['search_text'] = st.sidebar.text_input(
            "Search contributors", 
            placeholder="Username, skills, or summary...",
            help="Search in username, skills, expertise areas, and summary"
        )
        
        # Activity level filter
        activity_levels = ['high', 'medium', 'low', 'active', 'inactive']
        filters['activity_levels'] = st.sidebar.multiselect(
            "Activity Level",
            activity_levels,
            help="Filter by contributor activity level"
        )
        
        # Commits range
        if contributors:
            commit_values = [c.get('total_commits', 0) for c in contributors]
            min_commits, max_commits = min(commit_values), max(commit_values)
            
            filters['commit_range'] = st.sidebar.slider(
                "Commit Range",
                min_value=min_commits,
                max_value=max_commits,
                value=(min_commits, max_commits),
                help="Filter by number of commits"
            )
        
        # Repository count range
        if contributors:
            repo_values = [c.get('repositories_count', 0) for c in contributors]
            min_repos, max_repos = min(repo_values), max(repo_values)
            
            filters['repo_range'] = st.sidebar.slider(
                "Repository Count",
                min_value=min_repos,
                max_value=max_repos,
                value=(min_repos, max_repos),
                help="Filter by number of repositories contributed to"
            )
        
        # Skills filter
        all_skills = set()
        for contributor in contributors:
            skills = contributor.get('skills', [])
            if isinstance(skills, list):
                all_skills.update(skills)
        
        if all_skills:
            filters['required_skills'] = st.sidebar.multiselect(
                "Required Skills",
                sorted(all_skills),
                help="Contributors must have ALL selected skills"
            )
            
            filters['any_skills'] = st.sidebar.multiselect(
                "Any Skills",
                sorted(all_skills),
                help="Contributors must have ANY of the selected skills"
            )
        
        # Programming languages
        all_languages = set()
        for contributor in contributors:
            languages = contributor.get('primary_languages', [])
            if isinstance(languages, list):
                all_languages.update(languages)
        
        if all_languages:
            filters['languages'] = st.sidebar.multiselect(
                "Programming Languages",
                sorted(all_languages),
                help="Filter by primary programming languages"
            )
        
        # Expertise areas
        all_expertise = set()
        for contributor in contributors:
            expertise = contributor.get('expertise_areas', [])
            if isinstance(expertise, list):
                all_expertise.update(expertise)
        
        if all_expertise:
            filters['expertise_areas'] = st.sidebar.multiselect(
                "Expertise Areas",
                sorted(all_expertise),
                help="Filter by areas of expertise"
            )
        
        # Contribution style
        contribution_styles = ['collaborative', 'independent', 'research-focused', 'detail-oriented']
        filters['contribution_styles'] = st.sidebar.multiselect(
            "Contribution Style",
            contribution_styles,
            help="Filter by contribution style"
        )
        
        # Sort options
        sort_options = [
            "Username (A-Z)",
            "Username (Z-A)",
            "Total Commits (High-Low)",
            "Total Commits (Low-High)",
            "Repository Count (High-Low)",
            "Repository Count (Low-High)",
            "Activity Level"
        ]
        filters['sort_by'] = st.sidebar.selectbox(
            "Sort By",
            sort_options,
            help="Sort contributors by selected criteria"
        )
        
        return filters
    
    def render_repository_filters(self, repositories: List[Dict]) -> Dict[str, Any]:
        """Render advanced repository filters."""
        st.sidebar.header("🔍 Repository Filters")
        
        filters = {}
        
        # Text search
        filters['search_text'] = st.sidebar.text_input(
            "Search repositories",
            placeholder="Repository name, technology, or summary...",
            help="Search in repository name, technologies, and summary"
        )
        
        # Contributor count range
        if repositories:
            contributor_counts = []
            for repo in repositories:
                # Count unique contributors for this repository
                repo_id = repo.get('repository_id', '')
                count = len(set(r.get('contributor_id', '') for r in repositories if r.get('repository_id') == repo_id))
                contributor_counts.append(count)
            
            min_contributors, max_contributors = min(contributor_counts), max(contributor_counts)
            
            filters['contributor_range'] = st.sidebar.slider(
                "Contributor Count",
                min_value=min_contributors,
                max_value=max_contributors,
                value=(min_contributors, max_contributors),
                help="Filter by number of contributors"
            )
        
        # Commit count range
        if repositories:
            commit_counts = [r.get('commit_count', 0) for r in repositories]
            min_commits, max_commits = min(commit_counts), max(commit_counts)
            
            filters['commit_range'] = st.sidebar.slider(
                "Commit Count",
                min_value=min_commits,
                max_value=max_commits,
                value=(min_commits, max_commits),
                help="Filter by total number of commits"
            )
        
        # Technologies filter
        all_technologies = set()
        for repo in repositories:
            technologies = repo.get('technologies', [])
            if isinstance(technologies, list):
                all_technologies.update(technologies)
        
        if all_technologies:
            filters['technologies'] = st.sidebar.multiselect(
                "Technologies",
                sorted(all_technologies),
                help="Filter by technologies used"
            )
        
        # Contribution type
        contribution_types = ['feature_development', 'bug_fixes', 'performance_optimization', 'security_enhancement']
        filters['contribution_types'] = st.sidebar.multiselect(
            "Contribution Type",
            contribution_types,
            help="Filter by type of contribution"
        )
        
        # Sort options
        sort_options = [
            "Repository Name (A-Z)",
            "Repository Name (Z-A)",
            "Commit Count (High-Low)",
            "Commit Count (Low-High)",
            "Contributor Count (High-Low)",
            "Contributor Count (Low-High)",
            "Recent Activity"
        ]
        filters['sort_by'] = st.sidebar.selectbox(
            "Sort By",
            sort_options,
            help="Sort repositories by selected criteria"
        )
        
        return filters
    
    def apply_contributor_filters(self, contributors: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply filters to contributor list."""
        if not contributors:
            return []
        
        filtered_contributors = contributors.copy()
        
        # Text search
        if filters.get('search_text'):
            search_text = filters['search_text'].lower()
            filtered_contributors = [
                c for c in filtered_contributors
                if self._text_search_match(c, search_text)
            ]
        
        # Activity level filter
        if filters.get('activity_levels'):
            filtered_contributors = [
                c for c in filtered_contributors
                if c.get('activity_level', '').lower() in [level.lower() for level in filters['activity_levels']]
            ]
        
        # Commit range
        if filters.get('commit_range'):
            min_commits, max_commits = filters['commit_range']
            filtered_contributors = [
                c for c in filtered_contributors
                if min_commits <= c.get('total_commits', 0) <= max_commits
            ]
        
        # Repository range
        if filters.get('repo_range'):
            min_repos, max_repos = filters['repo_range']
            filtered_contributors = [
                c for c in filtered_contributors
                if min_repos <= c.get('repositories_count', 0) <= max_repos
            ]
        
        # Required skills (must have ALL)
        if filters.get('required_skills'):
            filtered_contributors = [
                c for c in filtered_contributors
                if all(skill in c.get('skills', []) for skill in filters['required_skills'])
            ]
        
        # Any skills (must have ANY)
        if filters.get('any_skills'):
            filtered_contributors = [
                c for c in filtered_contributors
                if any(skill in c.get('skills', []) for skill in filters['any_skills'])
            ]
        
        # Programming languages
        if filters.get('languages'):
            filtered_contributors = [
                c for c in filtered_contributors
                if any(lang in c.get('primary_languages', []) for lang in filters['languages'])
            ]
        
        # Expertise areas
        if filters.get('expertise_areas'):
            filtered_contributors = [
                c for c in filtered_contributors
                if any(expertise in c.get('expertise_areas', []) for expertise in filters['expertise_areas'])
            ]
        
        # Contribution styles
        if filters.get('contribution_styles'):
            filtered_contributors = [
                c for c in filtered_contributors
                if c.get('contribution_style', '').lower() in [style.lower() for style in filters['contribution_styles']]
            ]
        
        # Sort contributors
        if filters.get('sort_by'):
            filtered_contributors = self._sort_contributors(filtered_contributors, filters['sort_by'])
        
        return filtered_contributors
    
    def apply_repository_filters(self, repositories: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply filters to repository list."""
        if not repositories:
            return []
        
        filtered_repositories = repositories.copy()
        
        # Text search
        if filters.get('search_text'):
            search_text = filters['search_text'].lower()
            filtered_repositories = [
                r for r in filtered_repositories
                if self._repo_text_search_match(r, search_text)
            ]
        
        # Commit range
        if filters.get('commit_range'):
            min_commits, max_commits = filters['commit_range']
            filtered_repositories = [
                r for r in filtered_repositories
                if min_commits <= r.get('commit_count', 0) <= max_commits
            ]
        
        # Technologies
        if filters.get('technologies'):
            filtered_repositories = [
                r for r in filtered_repositories
                if any(tech in r.get('technologies', []) for tech in filters['technologies'])
            ]
        
        # Contribution types
        if filters.get('contribution_types'):
            filtered_repositories = [
                r for r in filtered_repositories
                if r.get('contribution_type', '').lower() in [ct.lower() for ct in filters['contribution_types']]
            ]
        
        # Sort repositories
        if filters.get('sort_by'):
            filtered_repositories = self._sort_repositories(filtered_repositories, filters['sort_by'])
        
        return filtered_repositories
    
    def _text_search_match(self, contributor: Dict, search_text: str) -> bool:
        """Check if contributor matches text search."""
        searchable_fields = [
            contributor.get('username', ''),
            contributor.get('summary', ''),
            ' '.join(contributor.get('skills', [])),
            ' '.join(contributor.get('expertise_areas', [])),
            ' '.join(contributor.get('primary_languages', []))
        ]
        
        combined_text = ' '.join(searchable_fields).lower()
        
        # Support multiple search terms
        search_terms = search_text.split()
        return all(term in combined_text for term in search_terms)
    
    def _repo_text_search_match(self, repository: Dict, search_text: str) -> bool:
        """Check if repository matches text search."""
        searchable_fields = [
            repository.get('repository_name', ''),
            repository.get('repository_id', ''),
            repository.get('summary', ''),
            ' '.join(repository.get('technologies', []))
        ]
        
        combined_text = ' '.join(searchable_fields).lower()
        
        # Support multiple search terms
        search_terms = search_text.split()
        return all(term in combined_text for term in search_terms)
    
    def _sort_contributors(self, contributors: List[Dict], sort_by: str) -> List[Dict]:
        """Sort contributors based on selected criteria."""
        if sort_by == "Username (A-Z)":
            return sorted(contributors, key=lambda x: x.get('username', '').lower())
        elif sort_by == "Username (Z-A)":
            return sorted(contributors, key=lambda x: x.get('username', '').lower(), reverse=True)
        elif sort_by == "Total Commits (High-Low)":
            return sorted(contributors, key=lambda x: x.get('total_commits', 0), reverse=True)
        elif sort_by == "Total Commits (Low-High)":
            return sorted(contributors, key=lambda x: x.get('total_commits', 0))
        elif sort_by == "Repository Count (High-Low)":
            return sorted(contributors, key=lambda x: x.get('repositories_count', 0), reverse=True)
        elif sort_by == "Repository Count (Low-High)":
            return sorted(contributors, key=lambda x: x.get('repositories_count', 0))
        elif sort_by == "Activity Level":
            activity_order = {'high': 3, 'medium': 2, 'low': 1, 'active': 3, 'inactive': 0}
            return sorted(contributors, key=lambda x: activity_order.get(x.get('activity_level', '').lower(), 0), reverse=True)
        
        return contributors
    
    def _sort_repositories(self, repositories: List[Dict], sort_by: str) -> List[Dict]:
        """Sort repositories based on selected criteria."""
        if sort_by == "Repository Name (A-Z)":
            return sorted(repositories, key=lambda x: x.get('repository_name', '').lower())
        elif sort_by == "Repository Name (Z-A)":
            return sorted(repositories, key=lambda x: x.get('repository_name', '').lower(), reverse=True)
        elif sort_by == "Commit Count (High-Low)":
            return sorted(repositories, key=lambda x: x.get('commit_count', 0), reverse=True)
        elif sort_by == "Commit Count (Low-High)":
            return sorted(repositories, key=lambda x: x.get('commit_count', 0))
        elif sort_by == "Recent Activity":
            return sorted(repositories, key=lambda x: x.get('last_contribution', ''), reverse=True)
        
        return repositories
    
    def get_filter_summary(self, filters: Dict[str, Any]) -> str:
        """Generate a summary of active filters."""
        active_filters = []
        
        if filters.get('search_text'):
            active_filters.append(f"Text: '{filters['search_text']}'")
        
        if filters.get('activity_levels'):
            active_filters.append(f"Activity: {', '.join(filters['activity_levels'])}")
        
        if filters.get('required_skills'):
            active_filters.append(f"Required Skills: {', '.join(filters['required_skills'])}")
        
        if filters.get('any_skills'):
            active_filters.append(f"Any Skills: {', '.join(filters['any_skills'])}")
        
        if filters.get('languages'):
            active_filters.append(f"Languages: {', '.join(filters['languages'])}")
        
        if filters.get('expertise_areas'):
            active_filters.append(f"Expertise: {', '.join(filters['expertise_areas'])}")
        
        if filters.get('technologies'):
            active_filters.append(f"Technologies: {', '.join(filters['technologies'])}")
        
        if not active_filters:
            return "No filters active"
        
        return f"Active filters: {' | '.join(active_filters)}"


# Global filter instance
advanced_filters = AdvancedFilters()