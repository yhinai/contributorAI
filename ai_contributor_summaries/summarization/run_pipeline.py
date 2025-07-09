"""Command-line interface for running the summarization pipeline."""

import asyncio
import logging
import sys
from typing import Optional
import click
from utils.weaviate_client import weaviate_client
from utils.mock_weaviate import mock_weaviate_client
from .hypermode_orchestrator import HypermodeOrchestrator
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """AI Contributor Summaries - Summarization Pipeline CLI."""
    pass


@cli.command()
@click.option('--batch-size', default=10, help='Number of items to process per batch')
def run_phase_1(batch_size: int):
    """Run Phase 1: Issue Summarization."""
    async def main():
        async with HypermodeOrchestrator() as orchestrator:
            result = await orchestrator.phase_1_summarize_issues(batch_size)
            click.echo(f"Phase 1 completed: {result}")
    
    asyncio.run(main())


@cli.command()
@click.option('--batch-size', default=10, help='Number of items to process per batch')
def run_phase_2(batch_size: int):
    """Run Phase 2: Commit Summarization."""
    async def main():
        async with HypermodeOrchestrator() as orchestrator:
            result = await orchestrator.phase_2_summarize_commits(batch_size)
            click.echo(f"Phase 2 completed: {result}")
    
    asyncio.run(main())


@cli.command()
@click.option('--batch-size', default=5, help='Number of items to process per batch')
def run_phase_3(batch_size: int):
    """Run Phase 3: Repository Work Summarization."""
    async def main():
        async with HypermodeOrchestrator() as orchestrator:
            result = await orchestrator.phase_3_summarize_repository_work(batch_size)
            click.echo(f"Phase 3 completed: {result}")
    
    asyncio.run(main())


@cli.command()
@click.option('--batch-size', default=5, help='Number of items to process per batch')
def run_phase_4(batch_size: int):
    """Run Phase 4: Contributor Profile Summarization."""
    async def main():
        async with HypermodeOrchestrator() as orchestrator:
            result = await orchestrator.phase_4_summarize_contributors(batch_size)
            click.echo(f"Phase 4 completed: {result}")
    
    asyncio.run(main())


@cli.command()
@click.option('--batch-size', default=10, help='Number of items to process per batch')
def run_full_pipeline(batch_size: int):
    """Run the complete 4-phase summarization pipeline."""
    async def main():
        try:
            # Initialize Weaviate schema
            if os.getenv('USE_MOCK_WEAVIATE') == 'true':
                mock_weaviate_client.create_schema()
            else:
                weaviate_client.create_schema()
            
            # Run full pipeline
            async with HypermodeOrchestrator() as orchestrator:
                result = await orchestrator.run_full_pipeline(batch_size)
                
                click.echo("\n=== Pipeline Results ===")
                for phase, data in result.items():
                    if isinstance(data, dict):
                        click.echo(f"{phase}: {data}")
                
                if "pipeline_summary" in result:
                    summary = result["pipeline_summary"]
                    click.echo(f"\nPipeline Duration: {summary['duration_seconds']:.2f} seconds")
                    click.echo(f"Total Processed: {summary['total_processed']}")
                    click.echo(f"Total Failed: {summary['total_failed']}")
                    
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(main())


@cli.command()
def init_schema():
    """Initialize Weaviate schema."""
    try:
        if os.getenv('USE_MOCK_WEAVIATE') == 'true':
            mock_weaviate_client.create_schema()
            click.echo("Mock Weaviate schema initialized successfully")
        else:
            weaviate_client.create_schema()
            click.echo("Weaviate schema initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Show pipeline status and statistics."""
    try:
        # Choose client based on environment
        if os.getenv('USE_MOCK_WEAVIATE') == 'true':
            client = mock_weaviate_client
        else:
            client = weaviate_client
        
        # Get counts from each collection
        issues = client.query_data("Issue", limit=1000)
        commits = client.query_data("Commit", limit=1000)
        repo_works = client.query_data("RepositoryWork", limit=1000)
        contributors = client.query_data("Contributor", limit=1000)
        
        # Count summarized items
        summarized_issues = sum(1 for item in issues if item.get("summary"))
        summarized_commits = sum(1 for item in commits if item.get("summary"))
        summarized_repo_works = sum(1 for item in repo_works if item.get("summary"))
        summarized_contributors = sum(1 for item in contributors if item.get("summary"))
        
        click.echo("=== Pipeline Status ===")
        click.echo(f"Issues: {summarized_issues}/{len(issues)} summarized")
        click.echo(f"Commits: {summarized_commits}/{len(commits)} summarized")
        click.echo(f"Repository Work: {summarized_repo_works}/{len(repo_works)} summarized")
        click.echo(f"Contributors: {summarized_contributors}/{len(contributors)} summarized")
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()