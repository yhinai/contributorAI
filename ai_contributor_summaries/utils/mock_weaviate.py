"""Mock Weaviate client for testing without Docker."""

import json
import os
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class MockWeaviateClient:
    """Mock Weaviate client for testing without Docker."""
    
    def __init__(self):
        """Initialize mock client."""
        self.data_dir = "mock_data"
        self.collections = {}
        self.setup_storage()
    
    def setup_storage(self):
        """Setup local storage directory."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def connect(self):
        """Mock connection."""
        logger.info("Connected to Mock Weaviate (local storage)")
    
    def create_schema(self):
        """Create mock schemas."""
        schemas = ["Issue", "Commit", "RepositoryWork", "Contributor"]
        
        for schema in schemas:
            self.collections[schema] = []
            # Create empty JSON file for each collection
            filepath = os.path.join(self.data_dir, f"{schema}.json")
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump([], f)
                logger.info(f"Created mock schema for {schema}")
        
        logger.info("All mock schemas created successfully")
    
    def insert_data(self, collection_name: str, data: Dict[str, Any]) -> str:
        """Insert data into mock collection."""
        try:
            # Load existing data
            filepath = os.path.join(self.data_dir, f"{collection_name}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []
            
            # Add UUID
            import uuid
            mock_uuid = str(uuid.uuid4())
            data['uuid'] = mock_uuid
            
            # Add to collection
            existing_data.append(data)
            
            # Save back
            with open(filepath, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            logger.debug(f"Inserted data into {collection_name}: {mock_uuid}")
            return mock_uuid
            
        except Exception as e:
            logger.error(f"Failed to insert data into {collection_name}: {e}")
            raise
    
    def query_data(self, collection_name: str, where_filter: Optional[Dict] = None, 
                   limit: int = 100) -> List[Dict]:
        """Query data from mock collection."""
        try:
            filepath = os.path.join(self.data_dir, f"{collection_name}.json")
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Simple filtering (basic implementation)
            if where_filter:
                # Very basic filter implementation
                filtered_data = []
                for item in data:
                    if self._matches_filter(item, where_filter):
                        filtered_data.append(item)
                data = filtered_data
            
            return data[:limit]
            
        except Exception as e:
            logger.error(f"Failed to query data from {collection_name}: {e}")
            return []
    
    def update_data(self, collection_name: str, uuid: str, data: Dict[str, Any]):
        """Update data in mock collection."""
        try:
            filepath = os.path.join(self.data_dir, f"{collection_name}.json")
            if not os.path.exists(filepath):
                return
            
            with open(filepath, 'r') as f:
                existing_data = json.load(f)
            
            # Find and update item
            for i, item in enumerate(existing_data):
                if item.get('uuid') == uuid:
                    existing_data[i].update(data)
                    break
            
            # Save back
            with open(filepath, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            logger.debug(f"Updated data in {collection_name}: {uuid}")
            
        except Exception as e:
            logger.error(f"Failed to update data in {collection_name}: {e}")
            raise
    
    def delete_data(self, collection_name: str, uuid: str):
        """Delete data from mock collection."""
        try:
            filepath = os.path.join(self.data_dir, f"{collection_name}.json")
            if not os.path.exists(filepath):
                return
            
            with open(filepath, 'r') as f:
                existing_data = json.load(f)
            
            # Remove item
            existing_data = [item for item in existing_data if item.get('uuid') != uuid]
            
            # Save back
            with open(filepath, 'w') as f:
                json.dump(existing_data, f, indent=2, default=str)
            
            logger.debug(f"Deleted data from {collection_name}: {uuid}")
            
        except Exception as e:
            logger.error(f"Failed to delete data from {collection_name}: {e}")
            raise
    
    def search_similar(self, collection_name: str, query: str, limit: int = 10) -> List[Dict]:
        """Mock semantic search."""
        try:
            # Simple text search in mock implementation
            filepath = os.path.join(self.data_dir, f"{collection_name}.json")
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Simple text matching
            results = []
            query_lower = query.lower()
            
            for item in data:
                # Search in text fields
                text_fields = ['title', 'body', 'message', 'summary', 'username']
                for field in text_fields:
                    if field in item and item[field]:
                        if query_lower in str(item[field]).lower():
                            item['certainty'] = 0.8  # Mock certainty
                            results.append(item)
                            break
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search similar items in {collection_name}: {e}")
            return []
    
    def _matches_filter(self, item: Dict, filter_dict: Dict) -> bool:
        """Simple filter matching."""
        try:
            path = filter_dict.get('path', [])
            operator = filter_dict.get('operator', 'Equal')
            value = filter_dict.get('valueText') or filter_dict.get('valueString') or filter_dict.get('valueInt')
            
            if not path:
                return True
            
            field = path[0] if isinstance(path, list) else path
            item_value = item.get(field)
            
            if operator == 'Equal':
                return item_value == value
            elif operator == 'NotEqual':
                return item_value != value
            elif operator == 'Like':
                return value.lower() in str(item_value).lower()
            
            return True
            
        except Exception:
            return True
    
    def close(self):
        """Close mock client."""
        logger.info("Mock Weaviate client closed")


# Create mock client
mock_weaviate_client = MockWeaviateClient()