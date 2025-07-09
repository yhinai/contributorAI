"""Weaviate client utilities for AI Contributor Summaries."""

import logging
from typing import Dict, List, Optional, Any
import weaviate
from config.settings import settings

logger = logging.getLogger(__name__)


class WeaviateClient:
    """Weaviate client wrapper for managing data operations."""
    
    def __init__(self):
        """Initialize Weaviate client connection."""
        self.client = None
        self.connect()
    
    def connect(self):
        """Connect to Weaviate instance."""
        try:
            # Simple connection without authentication for local development
            self.client = weaviate.Client(
                url=settings.weaviate_url,
                timeout_config=(5, 15),
                additional_headers={
                    'X-OpenAI-Api-Key': settings.weaviate_api_key or ''
                } if settings.weaviate_api_key else {}
            )
            
            # Test connection
            schema = self.client.schema.get()
            logger.info("Connected to Weaviate successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            logger.info("Make sure Weaviate is running at: " + settings.weaviate_url)
            raise
    
    def create_schema(self):
        """Create all required schemas for the application."""
        try:
            # Clear existing schema for development
            try:
                self.client.schema.delete_all()
                logger.info("Cleared existing schema")
            except:
                pass
            
            # Create Issue schema
            issue_schema = {
                "class": "Issue",
                "description": "GitHub issues with AI-generated summaries",
                "vectorizer": "text2vec-openai",
                "properties": [
                    {"name": "github_id", "dataType": ["string"], "description": "GitHub issue ID"},
                    {"name": "title", "dataType": ["text"], "description": "Issue title"},
                    {"name": "body", "dataType": ["text"], "description": "Issue body content"},
                    {"name": "files_changed", "dataType": ["string[]"], "description": "Files mentioned in issue"},
                    {"name": "summary", "dataType": ["text"], "description": "AI-generated summary"},
                    {"name": "repository_id", "dataType": ["string"], "description": "Repository identifier"},
                    {"name": "contributor_id", "dataType": ["string"], "description": "Contributor username"},
                    {"name": "created_at", "dataType": ["date"], "description": "Issue creation date"},
                    {"name": "updated_at", "dataType": ["date"], "description": "Issue update date"},
                    {"name": "state", "dataType": ["string"], "description": "Issue state (open/closed)"},
                    {"name": "labels", "dataType": ["string[]"], "description": "Issue labels"},
                ]
            }
            
            # Create Commit schema
            commit_schema = {
                "class": "Commit",
                "description": "Git commits with AI-generated summaries",
                "vectorizer": "text2vec-openai",
                "properties": [
                    {"name": "github_id", "dataType": ["string"], "description": "Commit SHA"},
                    {"name": "message", "dataType": ["text"], "description": "Commit message"},
                    {"name": "diff", "dataType": ["text"], "description": "Commit diff/patch"},
                    {"name": "files_changed", "dataType": ["string[]"], "description": "Files changed in commit"},
                    {"name": "summary", "dataType": ["text"], "description": "AI-generated summary"},
                    {"name": "repository_id", "dataType": ["string"], "description": "Repository identifier"},
                    {"name": "contributor_id", "dataType": ["string"], "description": "Contributor username"},
                    {"name": "created_at", "dataType": ["date"], "description": "Commit date"},
                    {"name": "sha", "dataType": ["string"], "description": "Commit SHA"},
                    {"name": "additions", "dataType": ["int"], "description": "Lines added"},
                    {"name": "deletions", "dataType": ["int"], "description": "Lines deleted"},
                    {"name": "technologies", "dataType": ["string[]"], "description": "Technologies detected"},
                ]
            }
            
            # Create RepositoryWork schema
            repo_work_schema = {
                "class": "RepositoryWork",
                "description": "Contributor work within specific repositories",
                "vectorizer": "text2vec-openai",
                "properties": [
                    {"name": "contributor_id", "dataType": ["string"], "description": "Contributor username"},
                    {"name": "repository_id", "dataType": ["string"], "description": "Repository identifier"},
                    {"name": "repository_name", "dataType": ["string"], "description": "Repository name"},
                    {"name": "summary", "dataType": ["text"], "description": "AI-generated work summary"},
                    {"name": "commit_count", "dataType": ["int"], "description": "Number of commits"},
                    {"name": "issue_count", "dataType": ["int"], "description": "Number of issues"},
                    {"name": "files_touched", "dataType": ["string[]"], "description": "Files modified"},
                    {"name": "technologies", "dataType": ["string[]"], "description": "Technologies used"},
                    {"name": "contribution_type", "dataType": ["string"], "description": "Type of contribution"},
                    {"name": "first_contribution", "dataType": ["date"], "description": "First contribution date"},
                    {"name": "last_contribution", "dataType": ["date"], "description": "Last contribution date"},
                ]
            }
            
            # Create Contributor schema
            contributor_schema = {
                "class": "Contributor",
                "description": "GitHub contributors with AI-generated profiles",
                "vectorizer": "text2vec-openai",
                "properties": [
                    {"name": "github_id", "dataType": ["string"], "description": "GitHub user ID"},
                    {"name": "username", "dataType": ["string"], "description": "GitHub username"},
                    {"name": "avatar_url", "dataType": ["string"], "description": "Avatar URL"},
                    {"name": "summary", "dataType": ["text"], "description": "AI-generated profile summary"},
                    {"name": "skills", "dataType": ["string[]"], "description": "Extracted skills"},
                    {"name": "expertise_areas", "dataType": ["string[]"], "description": "Areas of expertise"},
                    {"name": "total_commits", "dataType": ["int"], "description": "Total commits across all repos"},
                    {"name": "total_issues", "dataType": ["int"], "description": "Total issues across all repos"},
                    {"name": "repositories_count", "dataType": ["int"], "description": "Number of repositories contributed to"},
                    {"name": "primary_languages", "dataType": ["string[]"], "description": "Primary programming languages"},
                    {"name": "contribution_style", "dataType": ["string"], "description": "Contribution style description"},
                    {"name": "activity_level", "dataType": ["string"], "description": "Activity level assessment"},
                ]
            }
            
            # Create schemas
            schemas = [issue_schema, commit_schema, repo_work_schema, contributor_schema]
            
            for schema in schemas:
                try:
                    self.client.schema.create_class(schema)
                    logger.info(f"Created schema for {schema['class']}")
                except Exception as e:
                    logger.warning(f"Schema for {schema['class']} might already exist: {e}")
            
            logger.info("All schemas created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create schemas: {e}")
            raise
    
    def insert_data(self, collection_name: str, data: Dict[str, Any]) -> str:
        """Insert data into specified collection."""
        try:
            # Clean data for Weaviate
            cleaned_data = self._clean_data_for_weaviate(data)
            
            result = self.client.data_object.create(
                data_object=cleaned_data,
                class_name=collection_name
            )
            
            logger.debug(f"Inserted data into {collection_name}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to insert data into {collection_name}: {e}")
            raise
    
    def query_data(self, collection_name: str, where_filter: Optional[Dict] = None, 
                   limit: int = 100) -> List[Dict]:
        """Query data from specified collection."""
        try:
            query_builder = self.client.query.get(collection_name)
            
            if where_filter:
                query_builder = query_builder.with_where(where_filter)
            
            query_builder = query_builder.with_limit(limit)
            
            # Get all properties for the class
            schema = self.client.schema.get(collection_name)
            properties = [prop['name'] for prop in schema['properties']]
            
            # Add properties to query
            for prop in properties:
                query_builder = query_builder.with_additional(['id'])
            
            result = query_builder.do()
            
            # Extract data
            objects = []
            if 'data' in result and 'Get' in result['data'] and collection_name in result['data']['Get']:
                for obj in result['data']['Get'][collection_name]:
                    # Add UUID from additional
                    if '_additional' in obj:
                        obj['uuid'] = obj['_additional'].get('id', '')
                    objects.append(obj)
            
            return objects
            
        except Exception as e:
            logger.error(f"Failed to query data from {collection_name}: {e}")
            return []
    
    def update_data(self, collection_name: str, uuid: str, data: Dict[str, Any]):
        """Update data in specified collection."""
        try:
            cleaned_data = self._clean_data_for_weaviate(data)
            
            self.client.data_object.update(
                uuid=uuid,
                class_name=collection_name,
                data_object=cleaned_data
            )
            
            logger.debug(f"Updated data in {collection_name}: {uuid}")
            
        except Exception as e:
            logger.error(f"Failed to update data in {collection_name}: {e}")
            raise
    
    def delete_data(self, collection_name: str, uuid: str):
        """Delete data from specified collection."""
        try:
            self.client.data_object.delete(
                uuid=uuid,
                class_name=collection_name
            )
            
            logger.debug(f"Deleted data from {collection_name}: {uuid}")
            
        except Exception as e:
            logger.error(f"Failed to delete data from {collection_name}: {e}")
            raise
    
    def search_similar(self, collection_name: str, query: str, limit: int = 10) -> List[Dict]:
        """Search for similar items using vector search."""
        try:
            result = (
                self.client.query
                .get(collection_name)
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .with_additional(['certainty', 'id'])
                .do()
            )
            
            objects = []
            if 'data' in result and 'Get' in result['data'] and collection_name in result['data']['Get']:
                for obj in result['data']['Get'][collection_name]:
                    if '_additional' in obj:
                        obj['uuid'] = obj['_additional'].get('id', '')
                        obj['certainty'] = obj['_additional'].get('certainty', 0)
                    objects.append(obj)
            
            return objects
            
        except Exception as e:
            logger.error(f"Failed to search similar items in {collection_name}: {e}")
            return []
    
    def _clean_data_for_weaviate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean data for Weaviate insertion."""
        cleaned = {}
        
        for key, value in data.items():
            if key == 'uuid':
                continue  # Skip UUID field
            
            if value is None:
                continue
            
            # Handle datetime objects
            if hasattr(value, 'isoformat'):
                cleaned[key] = value.isoformat()
            elif isinstance(value, list):
                # Filter out None values from lists
                cleaned[key] = [v for v in value if v is not None]
            else:
                cleaned[key] = value
        
        return cleaned
    
    def close(self):
        """Close Weaviate client connection."""
        if self.client:
            # Weaviate v3 client doesn't need explicit closing
            logger.info("Weaviate client connection closed")


# Global client instance
try:
    weaviate_client = WeaviateClient()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to initialize Weaviate client: {e}")
    logger.info("Use mock mode with --mock flag or start Weaviate first")
    weaviate_client = None