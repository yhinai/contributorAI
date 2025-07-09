"""Test script for the enhanced Weaviate organization analysis system."""

import logging
import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.weaviate_client import WeaviateClient
from enhanced_weaviate_schema import EnhancedWeaviateSchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_weaviate_connection():
    """Test Weaviate connection."""
    logger.info("Testing Weaviate connection...")
    
    try:
        client = WeaviateClient()
        schema = client.client.schema.get()
        logger.info("✅ Weaviate connection successful")
        return client
    except Exception as e:
        logger.error(f"❌ Weaviate connection failed: {e}")
        return None


def test_schema_creation(client):
    """Test schema creation."""
    logger.info("Testing schema creation...")
    
    try:
        enhanced_schema = EnhancedWeaviateSchema(client)
        enhanced_schema.create_enhanced_schema()
        logger.info("✅ Schema creation successful")
        return enhanced_schema
    except Exception as e:
        logger.error(f"❌ Schema creation failed: {e}")
        return None


def test_data_ingestion(enhanced_schema):
    """Test data ingestion."""
    logger.info("Testing data ingestion...")
    
    try:
        json_file = "/Users/alhinai/Downloads/Detailed weaviate org"
        
        if not os.path.exists(json_file):
            logger.error(f"❌ JSON file not found: {json_file}")
            return False
        
        enhanced_schema.ingest_weaviate_org_data(json_file)
        logger.info("✅ Data ingestion successful")
        return True
    except Exception as e:
        logger.error(f"❌ Data ingestion failed: {e}")
        return False


def test_data_queries(client):
    """Test data queries."""
    logger.info("Testing data queries...")
    
    try:
        # Test each collection
        collections = ["Contributor", "Skills", "Repository", "Contribution"]
        results = {}
        
        for collection in collections:
            data = client.query_data(collection, limit=5)
            results[collection] = len(data)
            logger.info(f"  {collection}: {len(data)} records")
            
            # Show sample data
            if data:
                sample = data[0]
                logger.info(f"  Sample {collection}: {list(sample.keys())}")
        
        logger.info("✅ Data queries successful")
        return results
    except Exception as e:
        logger.error(f"❌ Data queries failed: {e}")
        return {}


def test_vector_search(client):
    """Test vector search functionality."""
    logger.info("Testing vector search...")
    
    try:
        # Test semantic search
        results = client.search_similar("Contributor", "Python developer", limit=5)
        logger.info(f"  Found {len(results)} similar contributors for 'Python developer'")
        
        for result in results[:3]:
            username = result.get("username", "unknown")
            certainty = result.get("certainty", 0)
            logger.info(f"    {username} (certainty: {certainty:.2f})")
        
        logger.info("✅ Vector search successful")
        return True
    except Exception as e:
        logger.error(f"❌ Vector search failed: {e}")
        return False


def main():
    """Main test function."""
    logger.info("🚀 Starting system tests...")
    
    # Test 1: Weaviate connection
    client = test_weaviate_connection()
    if not client:
        logger.error("Cannot continue without Weaviate connection")
        sys.exit(1)
    
    # Test 2: Schema creation
    enhanced_schema = test_schema_creation(client)
    if not enhanced_schema:
        logger.error("Cannot continue without schema")
        sys.exit(1)
    
    # Test 3: Data ingestion
    if not test_data_ingestion(enhanced_schema):
        logger.error("Data ingestion failed")
        sys.exit(1)
    
    # Test 4: Data queries
    results = test_data_queries(client)
    if not results:
        logger.error("Data queries failed")
        sys.exit(1)
    
    # Test 5: Vector search
    if not test_vector_search(client):
        logger.error("Vector search failed")
        sys.exit(1)
    
    # Summary
    logger.info("🎉 All tests passed successfully!")
    logger.info("📊 Data ingestion summary:")
    for collection, count in results.items():
        logger.info(f"  {collection}: {count} records")
    
    logger.info("\\n🔧 Next steps:")
    logger.info("1. Install additional dependencies: pip install -r requirements_enhanced.txt")
    logger.info("2. Set environment variables: OPENAI_API_KEY, FRIENDLI_TOKEN")
    logger.info("3. Run the chatbot: streamlit run streamlit_chatbot.py")
    logger.info("4. Or test individual components:")
    logger.info("   - python llamaindex_weaviate_integration.py")
    logger.info("   - python friendli_ai_profiler.py")


if __name__ == "__main__":
    main()