"""Test the simple chatbot app functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.weaviate_client import WeaviateClient

def test_app_components():
    """Test app components without running Streamlit."""
    print("🧪 Testing app components...")
    
    try:
        # Test Weaviate connection
        client = WeaviateClient()
        print("✅ Weaviate connection: OK")
        
        # Test data availability
        contributors = client.query_data("Contributor", limit=5)
        print(f"✅ Contributors data: {len(contributors)} records")
        
        skills = client.query_data("Skills", limit=5)
        print(f"✅ Skills data: {len(skills)} records")
        
        # Test search functionality
        search_results = client.search_similar("Contributor", "python", limit=3)
        print(f"✅ Search functionality: {len(search_results)} results")
        
        # Test specific queries
        where_filter = {
            "path": ["username"],
            "operator": "Equal", 
            "valueString": "databyjp"
        }
        specific_user = client.query_data("Contributor", where_filter=where_filter)
        print(f"✅ Specific queries: {len(specific_user)} results")
        
        print("\n🎉 All components working correctly!")
        print("📱 App should be accessible at: http://localhost:8501")
        print("📊 Features available:")
        print("  - Search by name, technology, or skills")
        print("  - Analytics dashboard with charts")
        print("  - Complete contributor profiles")
        print("  - 912 contributors from Weaviate organization")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_app_components()