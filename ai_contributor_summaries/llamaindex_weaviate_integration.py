"""LlamaIndex integration with Weaviate for contributor analysis chatbot."""

import logging
from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, ServiceContext, StorageContext
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.response.schema import Response
from llama_index.core.schema import Document
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.friendli import FriendliLLM
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from utils.weaviate_client import WeaviateClient
import weaviate

logger = logging.getLogger(__name__)


class ContributorAnalysisBot:
    """LlamaIndex-powered chatbot for contributor analysis."""
    
    def __init__(self, 
                 weaviate_client: WeaviateClient,
                 openai_api_key: str,
                 friendli_token: str):
        """Initialize the chatbot with Weaviate and LlamaIndex."""
        self.weaviate_client = weaviate_client
        self.openai_api_key = openai_api_key
        self.friendli_token = friendli_token
        
        # Initialize LlamaIndex components
        self._setup_llama_index()
        
        # Create vector store indices
        self.contributor_index = None
        self.skills_index = None
        self.repository_index = None
        self.contribution_index = None
        
        # Create query engines
        self.contributor_query_engine = None
        self.skills_query_engine = None
        self.repository_query_engine = None
        self.contribution_query_engine = None
        
        # Setup indices and query engines
        self._setup_indices()
    
    def _setup_llama_index(self):
        """Setup LlamaIndex components."""
        try:
            # Initialize embedding model
            self.embedding_model = OpenAIEmbedding(
                api_key=self.openai_api_key,
                model="text-embedding-3-small"
            )
            
            # Initialize LLM (FriendliAI)
            self.llm = FriendliLLM(
                model="meta-llama/Llama-3.1-8B-Instruct",
                token=self.friendli_token,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Create service context
            self.service_context = ServiceContext.from_defaults(
                llm=self.llm,
                embed_model=self.embedding_model,
                node_parser=SentenceSplitter(chunk_size=1000, chunk_overlap=100)
            )
            
            logger.info("LlamaIndex components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup LlamaIndex: {e}")
            raise
    
    def _setup_indices(self):
        """Setup vector store indices for each collection."""
        try:
            collections = ["Contributor", "Skills", "Repository", "Contribution"]
            
            for collection in collections:
                # Create Weaviate vector store
                vector_store = WeaviateVectorStore(
                    weaviate_client=self.weaviate_client.client,
                    index_name=collection,
                    text_key="content"
                )
                
                # Create storage context
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store
                )
                
                # Get documents from Weaviate
                documents = self._get_documents_from_collection(collection)
                
                if documents:
                    # Create index
                    index = VectorStoreIndex.from_documents(
                        documents,
                        storage_context=storage_context,
                        service_context=self.service_context
                    )
                    
                    # Create query engine with retriever
                    retriever = VectorIndexRetriever(
                        index=index,
                        similarity_top_k=10
                    )
                    
                    query_engine = RetrieverQueryEngine(
                        retriever=retriever,
                        node_postprocessors=[
                            SimilarityPostprocessor(similarity_cutoff=0.7)
                        ]
                    )
                    
                    # Store index and query engine
                    setattr(self, f"{collection.lower()}_index", index)
                    setattr(self, f"{collection.lower()}_query_engine", query_engine)
                    
                    logger.info(f"Created index for {collection} with {len(documents)} documents")
                else:
                    logger.warning(f"No documents found for {collection}")
            
            logger.info("All indices created successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup indices: {e}")
            raise
    
    def _get_documents_from_collection(self, collection: str) -> List[Document]:
        """Get documents from Weaviate collection."""
        try:
            data = self.weaviate_client.query_data(collection, limit=1000)
            documents = []
            
            for item in data:
                # Create content string from relevant fields
                content = self._create_content_from_item(item, collection)
                
                # Create metadata
                metadata = {
                    "collection": collection,
                    "uuid": item.get("uuid", ""),
                    "source": f"{collection}_{item.get('uuid', '')}"
                }
                
                # Add collection-specific metadata
                if collection == "Contributor":
                    metadata.update({
                        "username": item.get("username", ""),
                        "location": item.get("location", ""),
                        "company": item.get("company", ""),
                        "expertise_level": item.get("expertise_level", "")
                    })
                elif collection == "Skills":
                    metadata.update({
                        "contributor_username": item.get("contributor_username", ""),
                        "technologies": item.get("technologies", [])
                    })
                elif collection == "Repository":
                    metadata.update({
                        "repo_name": item.get("repo_name", ""),
                        "primary_language": item.get("primary_language", ""),
                        "stars": item.get("stars", 0)
                    })
                elif collection == "Contribution":
                    metadata.update({
                        "contributor_username": item.get("contributor_username", ""),
                        "repository_full_name": item.get("repository_full_name", ""),
                        "contribution_count": item.get("contribution_count", 0)
                    })
                
                document = Document(
                    text=content,
                    metadata=metadata
                )
                documents.append(document)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to get documents from {collection}: {e}")
            return []
    
    def _create_content_from_item(self, item: Dict, collection: str) -> str:
        """Create searchable content from item data."""
        content_parts = []
        
        if collection == "Contributor":
            content_parts.extend([
                f"Username: {item.get('username', '')}",
                f"Name: {item.get('name', '')}",
                f"Bio: {item.get('bio', '')}",
                f"Location: {item.get('location', '')}",
                f"Company: {item.get('company', '')}",
                f"Expertise Level: {item.get('expertise_level', '')}",
                f"AI Summary: {item.get('ai_summary', '')}",
                f"Tech Stack: {', '.join(item.get('tech_stack', []))}",
                f"Skill Recommendations: {', '.join(item.get('skill_recommendations', []))}",
                f"Followers: {item.get('followers', 0)}",
                f"Public Repos: {item.get('public_repos', 0)}",
                f"Total Contributions: {item.get('total_contributions', 0)}"
            ])
        elif collection == "Skills":
            content_parts.extend([
                f"Contributor: {item.get('contributor_username', '')}",
                f"Technologies: {', '.join(item.get('technologies', []))}",
                f"Frameworks: {', '.join(item.get('frameworks', []))}",
                f"Tools: {', '.join(item.get('tools', []))}",
                f"Python Score: {item.get('python_score', 0)}",
                f"JavaScript Score: {item.get('javascript_score', 0)}",
                f"Go Score: {item.get('go_score', 0)}",
                f"TypeScript Score: {item.get('typescript_score', 0)}",
                f"Web Development: {item.get('web_development', 0)}",
                f"Machine Learning: {item.get('machine_learning', 0)}",
                f"Data Science: {item.get('data_science', 0)}",
                f"DevOps: {item.get('devops', 0)}",
                f"Cloud Computing: {item.get('cloud_computing', 0)}",
                f"Database: {item.get('database', 0)}",
                f"Backend: {item.get('backend', 0)}",
                f"Frontend: {item.get('frontend', 0)}"
            ])
        elif collection == "Repository":
            content_parts.extend([
                f"Repository: {item.get('repo_name', '')}",
                f"Full Name: {item.get('repo_full_name', '')}",
                f"Description: {item.get('repo_description', '')}",
                f"Primary Language: {item.get('primary_language', '')}",
                f"Languages: {', '.join(item.get('languages', []))}",
                f"Topics: {', '.join(item.get('topics', []))}",
                f"Stars: {item.get('stars', 0)}",
                f"Forks: {item.get('forks', 0)}",
                f"Size: {item.get('repo_size', 0)}"
            ])
        elif collection == "Contribution":
            content_parts.extend([
                f"Contributor: {item.get('contributor_username', '')}",
                f"Repository: {item.get('repository_full_name', '')}",
                f"Contribution Count: {item.get('contribution_count', 0)}",
                f"Primary Language: {item.get('primary_language', '')}",
                f"Languages Used: {', '.join(item.get('languages_used', []))}",
                f"Contribution Type: {item.get('contribution_type', '')}",
                f"Impact Score: {item.get('impact_score', 0)}"
            ])
        
        return " | ".join([part for part in content_parts if part])
    
    def query_contributors(self, query: str) -> Response:
        """Query contributor information."""
        try:
            if not self.contributor_query_engine:
                raise ValueError("Contributor query engine not initialized")
            
            response = self.contributor_query_engine.query(
                f"Based on the contributor data, {query}"
            )
            return response
            
        except Exception as e:
            logger.error(f"Failed to query contributors: {e}")
            raise
    
    def query_skills(self, query: str) -> Response:
        """Query skills information."""
        try:
            if not self.skills_query_engine:
                raise ValueError("Skills query engine not initialized")
            
            response = self.skills_query_engine.query(
                f"Based on the skills data, {query}"
            )
            return response
            
        except Exception as e:
            logger.error(f"Failed to query skills: {e}")
            raise
    
    def query_repositories(self, query: str) -> Response:
        """Query repository information."""
        try:
            if not self.repository_query_engine:
                raise ValueError("Repository query engine not initialized")
            
            response = self.repository_query_engine.query(
                f"Based on the repository data, {query}"
            )
            return response
            
        except Exception as e:
            logger.error(f"Failed to query repositories: {e}")
            raise
    
    def query_contributions(self, query: str) -> Response:
        """Query contribution information."""
        try:
            if not self.contribution_query_engine:
                raise ValueError("Contribution query engine not initialized")
            
            response = self.contribution_query_engine.query(
                f"Based on the contribution data, {query}"
            )
            return response
            
        except Exception as e:
            logger.error(f"Failed to query contributions: {e}")
            raise
    
    def comprehensive_query(self, query: str) -> Dict[str, Any]:
        """Perform comprehensive query across all collections."""
        try:
            results = {}
            
            # Query each collection
            collections = ["contributors", "skills", "repositories", "contributions"]
            
            for collection in collections:
                try:
                    query_engine = getattr(self, f"{collection[:-1]}_query_engine")
                    if query_engine:
                        response = query_engine.query(query)
                        results[collection] = {
                            "response": str(response),
                            "source_nodes": [
                                {
                                    "text": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                                    "metadata": node.metadata,
                                    "score": node.score
                                }
                                for node in response.source_nodes
                            ]
                        }
                    else:
                        results[collection] = {"response": "Query engine not available", "source_nodes": []}
                except Exception as e:
                    logger.error(f"Error querying {collection}: {e}")
                    results[collection] = {"response": f"Error: {e}", "source_nodes": []}
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform comprehensive query: {e}")
            raise
    
    def get_top_contributors(self, limit: int = 10) -> List[Dict]:
        """Get top contributors by contribution count."""
        try:
            contributors = self.weaviate_client.query_data("Contributor", limit=limit)
            
            # Sort by total contributions
            sorted_contributors = sorted(
                contributors, 
                key=lambda x: x.get("total_contributions", 0), 
                reverse=True
            )
            
            return sorted_contributors[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top contributors: {e}")
            return []
    
    def get_contributor_skills(self, username: str) -> Optional[Dict]:
        """Get skills for a specific contributor."""
        try:
            where_filter = {
                "path": ["contributor_username"],
                "operator": "Equal",
                "valueString": username
            }
            
            skills = self.weaviate_client.query_data("Skills", where_filter=where_filter)
            
            if skills:
                return skills[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get skills for {username}: {e}")
            return None
    
    def search_by_technology(self, technology: str) -> List[Dict]:
        """Search contributors by technology."""
        try:
            # Search using vector similarity
            results = self.weaviate_client.search_similar("Skills", technology, limit=20)
            
            # Get contributor details
            contributors = []
            for result in results:
                contributor = self.weaviate_client.query_data(
                    "Contributor",
                    where_filter={
                        "path": ["username"],
                        "operator": "Equal",
                        "valueString": result.get("contributor_username", "")
                    }
                )
                
                if contributor:
                    contributor_data = contributor[0]
                    contributor_data["skill_match_score"] = result.get("certainty", 0)
                    contributors.append(contributor_data)
            
            return contributors
            
        except Exception as e:
            logger.error(f"Failed to search by technology {technology}: {e}")
            return []


def main():
    """Main function to test the chatbot."""
    try:
        # Initialize components
        weaviate_client = WeaviateClient()
        
        # Initialize chatbot (you'll need to provide API keys)
        chatbot = ContributorAnalysisBot(
            weaviate_client=weaviate_client,
            openai_api_key="your-openai-key",
            friendli_token="your-friendli-token"
        )
        
        # Test queries
        print("=== Testing Contributor Analysis Bot ===")
        
        # Test comprehensive query
        results = chatbot.comprehensive_query("Who are the top Python developers?")
        print(f"Comprehensive query results: {results}")
        
        # Test top contributors
        top_contributors = chatbot.get_top_contributors(5)
        print(f"Top contributors: {[c.get('username', '') for c in top_contributors]}")
        
        # Test technology search
        python_devs = chatbot.search_by_technology("Python")
        print(f"Python developers: {[c.get('username', '') for c in python_devs[:5]]}")
        
        logger.info("Chatbot testing completed successfully")
        
    except Exception as e:
        logger.error(f"Testing failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()