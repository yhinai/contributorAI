"""Main setup script for Weaviate organization analysis system."""

import logging
import argparse
import sys
import os
from datetime import datetime

# Import our custom modules
from enhanced_weaviate_schema import EnhancedWeaviateSchema
from utils.weaviate_client import WeaviateClient
# from friendli_ai_profiler import FriendliAIProfiler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Setup environment and check prerequisites."""
    logger.info("Setting up environment...")
    
    # Check if required environment variables are set
    required_vars = ["OPENAI_API_KEY", "FRIENDLI_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.info("You can set them in your environment or provide them when running the chatbot")
    
    # Check if JSON file exists
    json_file = "/Users/alhinai/Downloads/Detailed weaviate org"
    if not os.path.exists(json_file):
        logger.error(f"JSON file not found: {json_file}")
        logger.info("Please ensure the 'Detailed weaviate org' file is in the Downloads folder")
        return False
    
    logger.info("Environment setup complete")
    return True


def initialize_weaviate_schema(client):
    """Initialize enhanced Weaviate schema."""
    logger.info("Initializing enhanced Weaviate schema...")
    
    try:
        enhanced_schema = EnhancedWeaviateSchema(client)
        enhanced_schema.create_enhanced_schema()
        logger.info("Schema initialization complete")
        return enhanced_schema
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")
        raise


def ingest_data(enhanced_schema):
    """Ingest Weaviate organization data."""
    logger.info("Starting data ingestion...")
    
    try:
        json_file = "/Users/alhinai/Downloads/Detailed weaviate org"
        enhanced_schema.ingest_weaviate_org_data(json_file)
        logger.info("Data ingestion complete")
    except Exception as e:
        logger.error(f"Failed to ingest data: {e}")
        raise


def generate_ai_profiles(client, friendli_token):
    """Generate AI profiles for top contributors."""
    logger.info("Generating AI profiles for top contributors...")
    
    try:
        # profiler = FriendliAIProfiler(friendli_token, client)
        # profiles = profiler.process_top_contributors(limit=10)
        # profiler.save_profiles_to_weaviate(profiles)
        
        # Export profiles to JSON for backup
        # import json
        # with open(f"contributor_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        #     json.dump(profiles, f, indent=2)
        
        logger.info("AI profile generation skipped (FriendliAI not available)")
        return []
    except Exception as e:
        logger.error(f"Failed to generate AI profiles: {e}")
        raise


def verify_data_ingestion(client):
    """Verify that data was ingested correctly."""
    logger.info("Verifying data ingestion...")
    
    try:
        # Check each collection
        collections = ["Contributor", "Skills", "Repository", "Contribution"]
        stats = {}
        
        for collection in collections:
            data = client.query_data(collection, limit=1000)
            stats[collection] = len(data)
            logger.info(f"{collection}: {len(data)} records")
        
        logger.info("Data verification complete")
        return stats
    except Exception as e:
        logger.error(f"Failed to verify data: {e}")
        raise


def main():
    """Main function to setup the complete system."""
    parser = argparse.ArgumentParser(description="Setup Weaviate organization analysis system")
    parser.add_argument("--skip-schema", action="store_true", help="Skip schema creation")
    parser.add_argument("--skip-ingestion", action="store_true", help="Skip data ingestion")
    parser.add_argument("--skip-profiles", action="store_true", help="Skip AI profile generation")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing data")
    parser.add_argument("--friendli-token", help="FriendliAI token for profile generation")
    
    args = parser.parse_args()
    
    try:
        # Setup environment
        if not setup_environment():
            sys.exit(1)
        
        # Initialize Weaviate client
        logger.info("Initializing Weaviate client...")
        client = WeaviateClient()
        
        # Verify data if requested
        if args.verify_only:
            verify_data_ingestion(client)
            return
        
        # Initialize schema
        if not args.skip_schema:
            enhanced_schema = initialize_weaviate_schema(client)
        else:
            enhanced_schema = EnhancedWeaviateSchema(client)
        
        # Ingest data
        if not args.skip_ingestion:
            ingest_data(enhanced_schema)
        
        # Verify ingestion
        stats = verify_data_ingestion(client)
        
        # Generate AI profiles
        if not args.skip_profiles:
            friendli_token = args.friendli_token or os.getenv("FRIENDLI_TOKEN")
            if friendli_token:
                generate_ai_profiles(client, friendli_token)
            else:
                logger.warning("No FriendliAI token provided, skipping profile generation")
                logger.info("Use --friendli-token argument or set FRIENDLI_TOKEN environment variable")
        
        # Print summary
        logger.info("=== SETUP COMPLETE ===")
        logger.info("Data ingestion statistics:")
        for collection, count in stats.items():
            logger.info(f"  {collection}: {count} records")
        
        logger.info("\\nNext steps:")
        logger.info("1. Set environment variables: OPENAI_API_KEY, FRIENDLI_TOKEN")
        logger.info("2. Run the chatbot: streamlit run streamlit_chatbot.py")
        logger.info("3. Or test the analysis bot: python llamaindex_weaviate_integration.py")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()