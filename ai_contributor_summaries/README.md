# 🧠 AI-Powered Contributor Summaries

A fullstack AI application that automatically generates AI-powered summaries of GitHub contributors' work using a comprehensive 4-phase summarization pipeline.

## 🚀 Features

- **📊 Smart Data Ingestion**: Automated GitHub data collection via ACI.dev
- **🤖 AI-Powered Summarization**: 4-phase pipeline using FriendliAI LLMs
- **🎯 Vector Database**: Weaviate for efficient data storage and retrieval
- **🌐 Interactive UI**: Streamlit-based web interface with multiple views
- **📈 Network Visualization**: Interactive contributor-repository graphs
- **⚡ Workflow Orchestration**: Hypermode-powered pipeline management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Data   │───▶│   ACI.dev       │───▶│   Weaviate      │
│   (Issues,      │    │   Ingestion     │    │   Vector DB     │
│   Commits, etc) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │◀───│   4-Phase       │◀───│   FriendliAI    │
│   (Dashboard,   │    │   Hypermode     │    │   LLM           │
│   Explorer,     │    │   Orchestration │    │   Summarization │
│   Graph View)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Tech Stack

- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Python with asyncio for concurrent processing
- **Vector Database**: Weaviate for embeddings and semantic search
- **Data Ingestion**: ACI.dev for GitHub API integration
- **AI/LLM**: FriendliAI for text summarization
- **Orchestration**: Hypermode for workflow management
- **Visualization**: NetworkX + PyVis for interactive graphs
- **Configuration**: Pydantic for settings management

## 📦 Installation

### Prerequisites

- Python 3.9+
- Docker (for Weaviate)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai_contributor_summaries
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 4. Required API Keys

You'll need to obtain API keys for:

- **Weaviate**: If using Weaviate Cloud
- **FriendliAI**: For LLM summarization
- **GitHub**: Personal access token for API access
- **Hypermode**: For workflow orchestration
- **ACI.dev**: For enhanced GitHub data ingestion

### 5. Start Weaviate (Local)

```bash
# Using Docker
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
  -e DEFAULT_VECTORIZER_MODULE='none' \
  -e ENABLE_MODULES='text2vec-openai,generative-openai' \
  -e CLUSTER_HOSTNAME='node1' \
  semitechnologies/weaviate:latest
```

## 🚀 Quick Start

### 1. Initialize the Database Schema

```bash
cd ai_contributor_summaries
python -m summarization.run_pipeline init-schema
```

### 2. Ingest GitHub Data

```bash
# Ingest a specific repository
python -m ingestion.aci_ingest --repo "microsoft/vscode"

# Or run the ingestion script directly
python ingestion/aci_ingest.py
```

### 3. Run the Summarization Pipeline

```bash
# Run the complete 4-phase pipeline
python -m summarization.run_pipeline run-full-pipeline

# Or run individual phases
python -m summarization.run_pipeline run-phase-1  # Issues
python -m summarization.run_pipeline run-phase-2  # Commits
python -m summarization.run_pipeline run-phase-3  # Repository Work
python -m summarization.run_pipeline run-phase-4  # Contributors
```

### 4. Launch the UI

```bash
streamlit run ui/streamlit_app.py
```

Visit `http://localhost:8501` to access the application.

## 📊 Usage Guide

### Dashboard
- **Overview metrics**: Total repositories, contributors, commits, and issues
- **Top contributors**: Ranked by commit activity
- **Repository activity**: Most active repositories

### Repository Explorer
- **Search repositories**: By name or technology
- **Repository cards**: Detailed stats and technology stacks
- **AI summaries**: Generated insights about repository contributions

### Contributor Explorer
- **Search contributors**: By username or skills
- **Filter options**: Minimum commits, repositories, etc.
- **Detailed profiles**: Skills, expertise areas, and AI-generated summaries
- **Activity visualization**: Contribution patterns and statistics

### Graph View
- **Interactive network**: Contributors connected to repositories
- **Filter controls**: Adjust minimum thresholds and node counts
- **Network statistics**: Connectivity metrics and top nodes
- **Hover details**: Rich information on nodes and connections

## 🔄 4-Phase Summarization Pipeline

### Phase 1: Issue Summarization
- **Input**: Raw GitHub issues
- **Process**: AI analysis of issue content, labels, and context
- **Output**: Structured technical summaries

### Phase 2: Commit Summarization
- **Input**: Git commits with diffs
- **Process**: Code change analysis and impact assessment
- **Output**: Implementation-focused summaries

### Phase 3: Repository Work Aggregation
- **Input**: Issue and commit summaries per contributor per repository
- **Process**: Synthesis of contribution patterns and focus areas
- **Output**: Repository-level contribution summaries

### Phase 4: Contributor Profile Generation
- **Input**: All repository work summaries for each contributor
- **Process**: Skill extraction and professional profile generation
- **Output**: Comprehensive contributor profiles with expertise areas

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEAVIATE_URL` | Weaviate instance URL | `http://localhost:8080` |
| `WEAVIATE_API_KEY` | Weaviate API key (if using cloud) | `None` |
| `FRIENDLIAI_API_KEY` | FriendliAI API key | **Required** |
| `GITHUB_TOKEN` | GitHub personal access token | **Required** |
| `HYPERMODE_API_KEY` | Hypermode API key | **Required** |
| `ACI_DEV_API_KEY` | ACI.dev API key | **Required** |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Customization

#### System Prompts
Edit prompts in `prompts/prompt_templates.py`:
- `ISSUES_SYSTEM_PROMPT`: Issue analysis prompt
- `COMMITS_SYSTEM_PROMPT`: Commit analysis prompt
- `REPO_WORK_SYSTEM_PROMPT`: Repository work synthesis prompt
- `CONTRIBUTOR_SYSTEM_PROMPT`: Contributor profile generation prompt

#### Weaviate Schemas
Modify schemas in `utils/weaviate_client.py`:
- Add new properties to existing schemas
- Create additional schemas for custom data types
- Adjust vectorizer configurations

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### Performance Tests
```bash
python -m pytest tests/performance/
```

## 📈 Monitoring

### Pipeline Status
```bash
python -m summarization.run_pipeline status
```

### Weaviate Health
```bash
curl http://localhost:8080/v1/meta
```

### Performance Metrics
- Check Hypermode dashboard for workflow performance
- Monitor FriendliAI usage in their console
- Use Weaviate's built-in monitoring tools

## 🔍 Troubleshooting

### Common Issues

#### 1. Weaviate Connection Error
```bash
# Check if Weaviate is running
docker ps | grep weaviate

# Check logs
docker logs weaviate
```

#### 2. API Rate Limits
- GitHub API: 5000 requests/hour for authenticated users
- FriendliAI: Check your plan limits
- Implement exponential backoff for rate limiting

#### 3. Memory Issues
- Reduce batch sizes in pipeline configuration
- Use pagination for large datasets
- Monitor memory usage during processing

#### 4. Slow Summarization
- Check FriendliAI model performance
- Optimize prompt lengths
- Consider parallel processing for independent tasks

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 🚀 Deployment

### Local Development
```bash
streamlit run ui/streamlit_app.py
```

### Docker Deployment
```bash
# Build image
docker build -t ai-contributor-summaries .

# Run container
docker run -p 8501:8501 ai-contributor-summaries
```

### Cloud Deployment

#### Streamlit Cloud
1. Push to GitHub repository
2. Connect to Streamlit Cloud
3. Configure secrets in Streamlit Cloud dashboard

#### Heroku
```bash
# Install Heroku CLI
heroku create ai-contributor-summaries
git push heroku main
```

#### AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Configure environment variables
- Set up load balancing and auto-scaling

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings for all functions
- Maintain test coverage >90%

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FriendliAI**: For providing LLM capabilities
- **Weaviate**: For vector database infrastructure
- **Hypermode**: For workflow orchestration
- **ACI.dev**: For enhanced GitHub data access
- **Streamlit**: For the web UI framework
- **NetworkX**: For graph algorithms
- **PyVis**: For interactive visualizations

## 📞 Support

### Documentation
- [API Reference](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)

### Community
- [GitHub Issues](https://github.com/your-org/ai-contributor-summaries/issues)
- [Discord Community](https://discord.gg/your-invite)
- [Contributing Guide](CONTRIBUTING.md)

### Commercial Support
For enterprise support and customization:
- Email: support@yourcompany.com
- Schedule a consultation: [calendly.com/your-link](https://calendly.com/your-link)

---

**Built with ❤️ by the AI Contributor Summaries Team**