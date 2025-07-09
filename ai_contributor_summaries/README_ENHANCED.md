# Enhanced Weaviate Organization Analysis System

## Overview

This enhanced system provides comprehensive analysis of Weaviate organization contributors using advanced AI technologies. It integrates detailed GitHub organization data with Weaviate vector database, LlamaIndex for intelligent querying, and FriendliAI for generating detailed contributor profiles.

## Key Features

### 🔍 Comprehensive Data Analysis
- **912 Contributors**: Detailed analysis of Weaviate organization contributors
- **Skills Assessment**: Programming languages, frameworks, and domain expertise
- **Contribution Patterns**: Repository contributions, activity levels, and impact analysis
- **Technology Stack**: Technologies, frameworks, and tools used by each contributor

### 🤖 AI-Powered Chatbot
- **LlamaIndex Integration**: Semantic search and intelligent querying
- **Multi-Collection Queries**: Search across contributors, skills, repositories, and contributions
- **Conversational Interface**: Natural language queries about contributor data
- **Real-time Analytics**: Interactive dashboards and visualizations

### 📊 Advanced Analytics
- **Contributor Profiling**: AI-generated comprehensive profiles
- **Skill Mapping**: Detailed programming language and domain expertise scoring
- **Activity Analysis**: Contribution patterns and activity levels
- **Technology Trends**: Popular technologies and frameworks across the organization

### 🎯 FriendliAI Profile Generation
- **Professional Summaries**: AI-generated professional profiles
- **Technical Expertise**: Detailed analysis of technical skills and competencies
- **Career Trajectory**: Career progression and development recommendations
- **Collaboration Style**: Analysis of contribution patterns and team dynamics

## System Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│  Detailed Weaviate  │───▶│   Enhanced Weaviate │───▶│   LlamaIndex Query  │
│  Org JSON Data      │    │   Schema & Storage  │    │   Engine            │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                       │                          │
                                       ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│  FriendliAI Profile │◀───│   Streamlit Chatbot │◀───│   Semantic Search & │
│  Generator          │    │   Interface         │    │   Vector Operations │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Data Schema

### Enhanced Weaviate Collections

1. **Contributor** - Complete GitHub profiles with metadata
2. **Skills** - Detailed programming language and domain expertise scores
3. **Repository** - Repository information and characteristics
4. **Contribution** - Individual contribution records and patterns
5. **ContributorProfile** - AI-generated comprehensive profiles

### Sample Data Structure

```json
{
  "contributors": {
    "username": {
      "profile": { /* GitHub profile data */ },
      "skills": {
        "programming_languages": { "Python": 0.85, "JavaScript": 0.72 },
        "domains": { "machine_learning": 0.8, "web_development": 0.6 },
        "technologies": ["Docker", "Kubernetes", "React"],
        "frameworks": ["FastAPI", "Django", "Flask"]
      },
      "contributions": [ /* Repository contributions */ ],
      "skill_recommendations": [ /* AI-generated recommendations */ ]
    }
  }
}
```

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements_enhanced.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export FRIENDLI_TOKEN="your-friendli-token"

# Start Weaviate (if not already running)
docker-compose up -d weaviate
```

### 2. Test System

```bash
# Test the complete system
python test_system.py
```

### 3. Setup Data

```bash
# Complete setup (schema + data ingestion + AI profiles)
python weaviate_org_setup.py

# Or setup step by step
python weaviate_org_setup.py --skip-profiles  # Skip AI profile generation
python weaviate_org_setup.py --verify-only    # Only verify existing data
```

### 4. Run Chatbot

```bash
# Start the Streamlit chatbot
streamlit run streamlit_chatbot.py
```

## Usage Examples

### Chatbot Queries

```
🔍 Sample Queries:
- "Who are the top 10 Python developers in the organization?"
- "Which contributors have strong machine learning skills?"
- "What are the most active repositories?"
- "Show me contributors with DevOps expertise"
- "Analyze the skill distribution across the organization"
```

### Direct API Usage

```python
from utils.weaviate_client import WeaviateClient
from llamaindex_weaviate_integration import ContributorAnalysisBot

# Initialize
client = WeaviateClient()
bot = ContributorAnalysisBot(client, openai_key, friendli_token)

# Query contributors
response = bot.query_contributors("Find Python experts")

# Get top contributors
top_contributors = bot.get_top_contributors(10)

# Search by technology
python_devs = bot.search_by_technology("Python")
```

### Profile Generation

```python
from friendli_ai_profiler import FriendliAIProfiler

# Initialize profiler
profiler = FriendliAIProfiler(friendli_token, weaviate_client)

# Generate profiles for top contributors
profiles = profiler.process_top_contributors(limit=10)

# Save to Weaviate
profiler.save_profiles_to_weaviate(profiles)
```

## API Reference

### WeaviateClient
- `query_data(collection, filter, limit)` - Query collection data
- `search_similar(collection, query, limit)` - Vector similarity search
- `insert_data(collection, data)` - Insert new data

### ContributorAnalysisBot
- `query_contributors(query)` - Query contributor information
- `query_skills(query)` - Query skills data
- `comprehensive_query(query)` - Search across all collections
- `get_top_contributors(limit)` - Get top contributors by contribution count

### FriendliAIProfiler
- `generate_contributor_profile(contributor, skills, contributions)` - Generate AI profile
- `process_top_contributors(limit)` - Process multiple contributors
- `save_profiles_to_weaviate(profiles)` - Save profiles to database

## Features in Detail

### 1. Skill Analysis
- **Programming Languages**: Python, JavaScript, Go, TypeScript, Java, C, Ruby, Shell
- **Domain Expertise**: Web Dev, ML, Data Science, DevOps, Cloud, Database, Frontend, Backend
- **Technology Stack**: Frameworks, tools, and technologies used
- **Proficiency Scoring**: Numerical scores for each skill area

### 2. Contribution Analysis
- **Repository Contributions**: Commit counts per repository
- **Language Usage**: Primary languages used in contributions
- **Impact Assessment**: Contribution impact scoring
- **Activity Patterns**: Contribution frequency and consistency

### 3. AI Profile Generation
- **Professional Summary**: 2-3 paragraph professional overview
- **Technical Expertise**: Detailed technical skills analysis
- **Contribution Patterns**: Analysis of contribution style and preferences
- **Career Trajectory**: Career progression and development recommendations
- **Collaboration Style**: Team dynamics and collaboration patterns

### 4. Interactive Chatbot
- **Natural Language Queries**: Ask questions in plain English
- **Multi-Modal Responses**: Text, charts, and visualizations
- **Real-time Analytics**: Live dashboard with contributor statistics
- **Export Capabilities**: Export data and profiles

## Troubleshooting

### Common Issues

1. **Weaviate Connection Failed**
   ```bash
   # Check if Weaviate is running
   docker ps | grep weaviate
   
   # Start Weaviate
   docker-compose up -d weaviate
   ```

2. **Missing API Keys**
   ```bash
   # Set environment variables
   export OPENAI_API_KEY="your-key"
   export FRIENDLI_TOKEN="your-token"
   ```

3. **Data Ingestion Issues**
   ```bash
   # Verify JSON file exists
   ls -la "/Users/alhinai/Downloads/Detailed weaviate org"
   
   # Run with verbose logging
   python weaviate_org_setup.py --skip-profiles
   ```

### Performance Tips

1. **Large Dataset Handling**
   - Use pagination for large queries
   - Implement data chunking for ingestion
   - Consider async processing for profile generation

2. **Query Optimization**
   - Use specific filters to reduce search space
   - Implement caching for frequent queries
   - Optimize vector search parameters

## Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements_enhanced.txt

# Run tests
python test_system.py

# Format code
black .
isort .
flake8 .
```

### Adding New Features

1. **New Query Types**: Extend `ContributorAnalysisBot` class
2. **Additional Visualizations**: Add charts to `streamlit_chatbot.py`
3. **Enhanced Profiles**: Modify `FriendliAIProfiler` prompts
4. **New Data Sources**: Extend `EnhancedWeaviateSchema`

## License

This project is part of the AI Contributor Summaries system and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test system output
3. Verify API key configuration
4. Check Weaviate connection and data ingestion logs

## Future Enhancements

- **Real-time Data Updates**: Live GitHub API integration
- **Advanced Analytics**: Machine learning insights
- **Multi-Organization Support**: Support for multiple GitHub organizations
- **Enhanced Visualizations**: 3D network graphs and advanced charts
- **API Integration**: RESTful API for external integrations
- **Mobile Interface**: Mobile-optimized chatbot interface