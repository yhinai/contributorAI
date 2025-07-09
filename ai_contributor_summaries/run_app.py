#!/usr/bin/env python3
"""
Main application runner for AI Contributor Summaries.
This script provides a unified interface to run different components of the application.
"""

import click
import subprocess
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@click.group()
def cli():
    """AI Contributor Summaries - Main Application Runner"""
    pass

@cli.command()
@click.option('--port', default=8501, help='Port to run Streamlit on')
@click.option('--host', default='localhost', help='Host to run Streamlit on')
@click.option('--mock', is_flag=True, help='Use mock Weaviate')
def ui(port, host, mock):
    """Launch the Streamlit UI."""
    click.echo(f"🚀 Starting Streamlit UI on http://{host}:{port}")
    
    # Set mock mode environment variable
    if mock:
        os.environ['USE_MOCK_WEAVIATE'] = 'true'
        click.echo("🧪 Running in mock mode (using local storage)")
    
    subprocess.run([
        sys.executable, '-m', 'streamlit', 'run', 
        'ui/streamlit_app.py',
        '--server.port', str(port),
        '--server.address', host
    ])

@cli.command()
@click.option('--repo', required=True, help='Repository in format owner/repo')
@click.option('--max-commits', default=500, help='Maximum number of commits to ingest')
@click.option('--max-issues', default=500, help='Maximum number of issues to ingest')
@click.option('--use-github', is_flag=True, help='Use direct GitHub API instead of ACI.dev')
@click.option('--mock', is_flag=True, help='Use mock Weaviate')
def ingest(repo, max_commits, max_issues, use_github, mock):
    """Ingest data for a specific repository."""
    click.echo(f"📥 Ingesting data for repository: {repo}")
    
    # Parse owner and repo
    try:
        owner, repo_name = repo.split('/')
    except ValueError:
        click.echo("❌ Repository format should be 'owner/repo'")
        return
    
    # Set mock mode if requested
    if mock:
        os.environ['USE_MOCK_WEAVIATE'] = 'true'
        click.echo("🧪 Running in mock mode")
    
    # Run ingestion
    try:
        import asyncio
        
        async def run_ingestion():
            if use_github:
                from ingestion.github_client import GitHubClient
                async with GitHubClient() as ingester:
                    result = await ingester.ingest_repository(owner, repo_name, max_commits, max_issues)
                    click.echo(f"✅ GitHub ingestion completed: {result}")
            else:
                from ingestion.aci_ingest import ACIIngester
                async with ACIIngester() as ingester:
                    result = await ingester.ingest_repository(owner, repo_name)
                    click.echo(f"✅ ACI.dev ingestion completed: {result}")
        
        asyncio.run(run_ingestion())
    except Exception as e:
        click.echo(f"❌ Ingestion failed: {e}")
        click.echo("💡 Try using --use-github flag for direct GitHub API access")
        if not mock:
            click.echo("💡 Try using --mock flag for local storage")

@cli.command()
@click.option('--batch-size', default=10, help='Batch size for processing')
@click.option('--phase', type=click.Choice(['1', '2', '3', '4', 'all']), default='all', help='Phase to run')
def summarize(batch_size, phase):
    """Run the summarization pipeline."""
    click.echo(f"🤖 Running summarization pipeline - Phase: {phase}")
    
    if phase == 'all':
        subprocess.run([
            sys.executable, '-m', 'summarization.run_pipeline',
            'run-full-pipeline',
            '--batch-size', str(batch_size)
        ])
    else:
        subprocess.run([
            sys.executable, '-m', 'summarization.run_pipeline',
            f'run-phase-{phase}',
            '--batch-size', str(batch_size)
        ])

@cli.command()
@click.option('--mock', is_flag=True, help='Use mock Weaviate (no Docker required)')
def init(mock):
    """Initialize the application (create schemas, etc.)."""
    click.echo("🔧 Initializing application...")
    
    try:
        if mock:
            from utils.mock_weaviate import mock_weaviate_client
            mock_weaviate_client.create_schema()
            click.echo("✅ Mock Weaviate schema created successfully")
            click.echo("📁 Data will be stored in: mock_data/")
            
            # Set environment variable to use mock mode
            os.environ['USE_MOCK_WEAVIATE'] = 'true'
        else:
            from utils.weaviate_client import weaviate_client
            if weaviate_client is None:
                raise Exception("Weaviate client not available. Start Weaviate or use --mock flag")
            weaviate_client.create_schema()
            click.echo("✅ Weaviate schema created successfully")
    except Exception as e:
        click.echo(f"❌ Initialization failed: {e}")
        if not mock:
            click.echo("💡 Try running with --mock flag to use local storage instead")
            click.echo("   Example: python run_app.py init --mock")

@cli.command()
@click.option('--mock', is_flag=True, help='Use mock Weaviate')
def status(mock):
    """Show application status."""
    click.echo("📊 Application Status:")
    
    # Check if using mock mode
    if mock or os.getenv('USE_MOCK_WEAVIATE') == 'true':
        try:
            from utils.mock_weaviate import mock_weaviate_client
            click.echo("✅ Mock Weaviate: Connected")
            client = mock_weaviate_client
        except Exception as e:
            click.echo(f"❌ Mock Weaviate: {e}")
            return
    else:
        # Check Weaviate connection
        try:
            from utils.weaviate_client import weaviate_client
            if weaviate_client is None:
                raise Exception("Weaviate client not available")
            issues = weaviate_client.query_data("Issue", limit=1)
            click.echo("✅ Weaviate: Connected")
            client = weaviate_client
        except Exception as e:
            click.echo(f"❌ Weaviate: {e}")
            click.echo("💡 Try using --mock flag or start Weaviate first")
            return
    
    # Check data counts
    try:
        issues = client.query_data("Issue", limit=1000)
        commits = client.query_data("Commit", limit=1000)
        repo_works = client.query_data("RepositoryWork", limit=1000)
        contributors = client.query_data("Contributor", limit=1000)
        
        click.echo(f"📊 Data Counts:")
        click.echo(f"   Issues: {len(issues)}")
        click.echo(f"   Commits: {len(commits)}")
        click.echo(f"   Repository Work: {len(repo_works)}")
        click.echo(f"   Contributors: {len(contributors)}")
        
        # Count summarized items
        summarized_issues = sum(1 for item in issues if item.get("summary"))
        summarized_commits = sum(1 for item in commits if item.get("summary"))
        summarized_repo_works = sum(1 for item in repo_works if item.get("summary"))
        summarized_contributors = sum(1 for item in contributors if item.get("summary"))
        
        click.echo(f"🤖 Summarization Progress:")
        click.echo(f"   Issues: {summarized_issues}/{len(issues)} ({summarized_issues/len(issues)*100:.1f}%)" if issues else "   Issues: 0/0")
        click.echo(f"   Commits: {summarized_commits}/{len(commits)} ({summarized_commits/len(commits)*100:.1f}%)" if commits else "   Commits: 0/0")
        click.echo(f"   Repository Work: {summarized_repo_works}/{len(repo_works)} ({summarized_repo_works/len(repo_works)*100:.1f}%)" if repo_works else "   Repository Work: 0/0")
        click.echo(f"   Contributors: {summarized_contributors}/{len(contributors)} ({summarized_contributors/len(contributors)*100:.1f}%)" if contributors else "   Contributors: 0/0")
        
    except Exception as e:
        click.echo(f"❌ Failed to get data counts: {e}")

@cli.command()
@click.option('--check-env', is_flag=True, help='Check environment variables')
def config(check_env):
    """Show configuration information."""
    click.echo("⚙️  Configuration:")
    
    if check_env:
        # Check required environment variables
        required_vars = [
            'WEAVIATE_URL',
            'FRIENDLIAI_API_KEY',
            'GITHUB_TOKEN',
            'HYPERMODE_API_KEY',
            'ACI_DEV_API_KEY'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Show first 4 and last 4 characters for security
                if len(value) > 8:
                    masked = value[:4] + '*' * (len(value) - 8) + value[-4:]
                else:
                    masked = '*' * len(value)
                click.echo(f"   ✅ {var}: {masked}")
            else:
                click.echo(f"   ❌ {var}: Not set")

@cli.command()
@click.option('--mock', is_flag=True, help='Use mock Weaviate')
def demo(mock):
    """Run a complete demo workflow."""
    click.echo("🎯 Running complete demo workflow...")
    
    # Step 1: Initialize
    click.echo("Step 1: Initializing...")
    try:
        if mock:
            from utils.mock_weaviate import mock_weaviate_client
            mock_weaviate_client.create_schema()
            client = mock_weaviate_client
            click.echo("✅ Mock schema initialized")
        else:
            from utils.weaviate_client import weaviate_client
            if weaviate_client is None:
                raise Exception("Weaviate not available")
            weaviate_client.create_schema()
            client = weaviate_client
            click.echo("✅ Schema initialized")
    except Exception as e:
        click.echo(f"❌ Initialization failed: {e}")
        return
    
    # Step 2: Create sample data for demo
    click.echo("Step 2: Creating sample data...")
    try:
        from datetime import datetime
        
        # Sample contributors
        contributors = [
            {
                "github_id": "12345",
                "username": "alice-developer",
                "avatar_url": "https://github.com/alice-developer.png",
                "summary": "Full-stack developer with expertise in React, Node.js, and Python. Focuses on building scalable web applications and has strong experience in API development and database design.",
                "skills": ["React", "Node.js", "Python", "PostgreSQL", "Docker"],
                "expertise_areas": ["Frontend Development", "Backend APIs", "Database Design"],
                "total_commits": 342,
                "total_issues": 28,
                "repositories_count": 5,
                "primary_languages": ["JavaScript", "Python", "TypeScript"],
                "contribution_style": "collaborative",
                "activity_level": "high"
            },
            {
                "github_id": "67890",
                "username": "bob-security",
                "avatar_url": "https://github.com/bob-security.png",
                "summary": "Security engineer specializing in application security, penetration testing, and DevSecOps. Experienced in implementing security measures and conducting security audits.",
                "skills": ["Security Testing", "DevSecOps", "Python", "Go", "Kubernetes"],
                "expertise_areas": ["Application Security", "DevSecOps", "Penetration Testing"],
                "total_commits": 156,
                "total_issues": 45,
                "repositories_count": 3,
                "primary_languages": ["Python", "Go", "Shell"],
                "contribution_style": "detail-oriented",
                "activity_level": "medium"
            },
            {
                "github_id": "54321",
                "username": "charlie-ai",
                "avatar_url": "https://github.com/charlie-ai.png",
                "summary": "Machine learning engineer with focus on deep learning, NLP, and computer vision. Contributes to AI/ML libraries and research projects.",
                "skills": ["TensorFlow", "PyTorch", "Python", "CUDA", "Docker"],
                "expertise_areas": ["Machine Learning", "Deep Learning", "NLP"],
                "total_commits": 89,
                "total_issues": 12,
                "repositories_count": 2,
                "primary_languages": ["Python", "Jupyter Notebook", "C++"],
                "contribution_style": "research-focused",
                "activity_level": "medium"
            }
        ]
        
        # Sample repository work
        repo_works = [
            {
                "contributor_id": "alice-developer",
                "repository_id": "microsoft/vscode",
                "repository_name": "vscode",
                "summary": "Contributed to VS Code's extension system, focusing on improving the debugging experience and adding new language support features.",
                "commit_count": 45,
                "issue_count": 8,
                "files_touched": ["src/vs/workbench/contrib/debug/", "extensions/typescript/", "src/vs/platform/"],
                "technologies": ["TypeScript", "Node.js", "Electron"],
                "contribution_type": "feature_development",
                "first_contribution": "2023-01-15",
                "last_contribution": "2024-01-10"
            },
            {
                "contributor_id": "alice-developer",
                "repository_id": "facebook/react",
                "repository_name": "react",
                "summary": "Worked on React's core reconciliation algorithm and contributed to performance improvements in the virtual DOM implementation.",
                "commit_count": 23,
                "issue_count": 5,
                "files_touched": ["packages/react-reconciler/", "packages/react-dom/", "packages/react/"],
                "technologies": ["JavaScript", "React", "Flow"],
                "contribution_type": "performance_optimization",
                "first_contribution": "2023-03-20",
                "last_contribution": "2023-11-28"
            },
            {
                "contributor_id": "bob-security",
                "repository_id": "kubernetes/kubernetes",
                "repository_name": "kubernetes",
                "summary": "Enhanced Kubernetes security features, implemented RBAC improvements, and contributed to pod security standards.",
                "commit_count": 67,
                "issue_count": 23,
                "files_touched": ["pkg/auth/", "pkg/apis/rbac/", "pkg/kubelet/"],
                "technologies": ["Go", "Kubernetes", "Docker"],
                "contribution_type": "security_enhancement",
                "first_contribution": "2023-02-10",
                "last_contribution": "2024-01-05"
            },
            {
                "contributor_id": "charlie-ai",
                "repository_id": "tensorflow/tensorflow",
                "repository_name": "tensorflow",
                "summary": "Contributed to TensorFlow's neural network operators and optimized GPU kernels for better performance on NVIDIA hardware.",
                "commit_count": 34,
                "issue_count": 7,
                "files_touched": ["tensorflow/core/kernels/", "tensorflow/python/ops/", "tensorflow/compiler/"],
                "technologies": ["Python", "C++", "CUDA"],
                "contribution_type": "performance_optimization",
                "first_contribution": "2023-04-01",
                "last_contribution": "2023-12-15"
            }
        ]
        
        # Insert sample data
        for contributor in contributors:
            client.insert_data("Contributor", contributor)
            
        for repo_work in repo_works:
            client.insert_data("RepositoryWork", repo_work)
            
        click.echo("✅ Sample data created successfully")
        
    except Exception as e:
        click.echo(f"❌ Failed to create sample data: {e}")
        return
    
    # Step 3: Launch UI
    click.echo("Step 3: Ready to launch UI...")
    click.echo("✅ Demo setup complete!")
    click.echo("🚀 Run: python run_app.py ui --mock")
    
    if mock:
        click.echo("📁 Sample data stored in: mock_data/")
    
    click.echo("🎉 Demo ready! You can now explore the UI with sample data.")

if __name__ == '__main__':
    cli()