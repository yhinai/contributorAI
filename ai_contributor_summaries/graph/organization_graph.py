"""Network graph visualization for contributor-repository relationships."""

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network
import tempfile
import os
from typing import List, Dict, Any, Optional
import logging
import colorsys

logger = logging.getLogger(__name__)


class OrganizationGraph:
    """Create and manage organization network graphs."""
    
    def __init__(self):
        """Initialize the graph."""
        self.G = nx.Graph()
        self.contributor_colors = {}
        self.repo_colors = {}
    
    def _generate_color_palette(self, n: int) -> List[str]:
        """Generate a diverse color palette."""
        colors = []
        for i in range(n):
            hue = i / n
            saturation = 0.7
            value = 0.8
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            hex_color = '#%02x%02x%02x' % tuple(int(c * 255) for c in rgb)
            colors.append(hex_color)
        return colors
    
    def build_graph(self, contributors: List[Dict], repo_works: List[Dict], max_nodes: int = 100):
        """Build the network graph from contributors and repository work data."""
        self.G.clear()
        
        # Add contributor nodes
        contributor_colors = self._generate_color_palette(len(contributors))
        for i, contributor in enumerate(contributors[:max_nodes//2]):
            username = contributor.get('username', 'Unknown')
            
            # Node attributes
            node_attrs = {
                'type': 'contributor',
                'label': username,
                'size': min(contributor.get('total_commits', 0) / 10, 50) + 10,
                'color': contributor_colors[i % len(contributor_colors)],
                'title': f"""
                    <b>{username}</b><br>
                    Commits: {contributor.get('total_commits', 0)}<br>
                    Issues: {contributor.get('total_issues', 0)}<br>
                    Repositories: {contributor.get('repositories_count', 0)}<br>
                    Activity: {contributor.get('activity_level', 'Unknown')}
                """,
                'total_commits': contributor.get('total_commits', 0),
                'total_issues': contributor.get('total_issues', 0),
                'repositories_count': contributor.get('repositories_count', 0),
                'skills': contributor.get('skills', []),
                'expertise_areas': contributor.get('expertise_areas', [])
            }
            
            self.G.add_node(username, **node_attrs)
        
        # Add repository nodes and edges
        repositories = {}
        for rw in repo_works:
            repo_id = rw.get('repository_id', 'Unknown')
            contributor_id = rw.get('contributor_id', 'Unknown')
            
            # Skip if contributor is not in graph
            if contributor_id not in self.G.nodes:
                continue
            
            # Add repository node if not exists
            if repo_id not in repositories:
                repositories[repo_id] = {
                    'name': rw.get('repository_name', repo_id.split('/')[-1]),
                    'contributors': set(),
                    'total_commits': 0,
                    'total_issues': 0,
                    'technologies': set()
                }
            
            # Update repository data
            repositories[repo_id]['contributors'].add(contributor_id)
            repositories[repo_id]['total_commits'] += rw.get('commit_count', 0)
            repositories[repo_id]['total_issues'] += rw.get('issue_count', 0)
            repositories[repo_id]['technologies'].update(rw.get('technologies', []))
        
        # Add repository nodes with enough contributors
        repo_colors = self._generate_color_palette(len(repositories))
        for i, (repo_id, repo_data) in enumerate(repositories.items()):
            if len(repo_data['contributors']) >= 1:  # At least 1 contributor
                repo_name = repo_data['name']
                
                repo_attrs = {
                    'type': 'repository',
                    'label': repo_name,
                    'size': min(len(repo_data['contributors']) * 5, 40) + 15,
                    'color': repo_colors[i % len(repo_colors)],
                    'shape': 'square',
                    'title': f"""
                        <b>{repo_name}</b><br>
                        Repository: {repo_id}<br>
                        Contributors: {len(repo_data['contributors'])}<br>
                        Commits: {repo_data['total_commits']}<br>
                        Issues: {repo_data['total_issues']}<br>
                        Technologies: {', '.join(list(repo_data['technologies'])[:5])}
                    """,
                    'contributors_count': len(repo_data['contributors']),
                    'total_commits': repo_data['total_commits'],
                    'total_issues': repo_data['total_issues'],
                    'technologies': list(repo_data['technologies'])
                }
                
                self.G.add_node(repo_id, **repo_attrs)
                
                # Add edges between contributors and repositories
                for contributor_id in repo_data['contributors']:
                    if contributor_id in self.G.nodes:
                        # Find the repository work for edge weight
                        edge_weight = 1
                        for rw in repo_works:
                            if (rw.get('repository_id') == repo_id and 
                                rw.get('contributor_id') == contributor_id):
                                edge_weight = max(rw.get('commit_count', 1), 1)
                                break
                        
                        self.G.add_edge(
                            contributor_id, 
                            repo_id, 
                            weight=edge_weight,
                            width=min(edge_weight / 5, 10) + 1
                        )
        
        logger.info(f"Graph built with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges")
    
    def create_interactive_graph(self, contributors: List[Dict], repo_works: List[Dict], 
                                max_nodes: int = 100) -> Optional[str]:
        """Create an interactive graph using pyvis."""
        try:
            # Build the graph
            self.build_graph(contributors, repo_works, max_nodes)
            
            if self.G.number_of_nodes() == 0:
                return None
            
            # Create pyvis network
            net = Network(
                height="600px",
                width="100%",
                bgcolor="#ffffff",
                font_color="black",
                directed=False
            )
            
            # Configure physics
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "forceAtlas2Based": {
                        "gravitationalConstant": -50,
                        "centralGravity": 0.01,
                        "springLength": 100,
                        "springConstant": 0.08,
                        "damping": 0.4,
                        "avoidOverlap": 0.5
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1,
                    "solver": "forceAtlas2Based",
                    "timestep": 0.35,
                    "stabilization": {"iterations": 150}
                },
                "interaction": {
                    "hover": true,
                    "tooltipDelay": 200
                }
            }
            """)
            
            # Add nodes to pyvis
            for node, attrs in self.G.nodes(data=True):
                net.add_node(
                    node,
                    label=attrs.get('label', node),
                    color=attrs.get('color', '#97c2fc'),
                    size=attrs.get('size', 20),
                    shape=attrs.get('shape', 'dot'),
                    title=attrs.get('title', node),
                    physics=True
                )
            
            # Add edges to pyvis
            for edge in self.G.edges(data=True):
                net.add_edge(
                    edge[0],
                    edge[1],
                    width=edge[2].get('width', 1),
                    color={'color': '#848484', 'highlight': '#848484'},
                    physics=True
                )
            
            # Generate HTML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                net.save_graph(f.name)
                with open(f.name, 'r') as html_file:
                    html_content = html_file.read()
                
                # Clean up temp file
                os.unlink(f.name)
                
                return html_content
            
        except Exception as e:
            logger.error(f"Failed to create interactive graph: {e}")
            return None
    
    def create_plotly_graph(self, contributors: List[Dict], repo_works: List[Dict], 
                           max_nodes: int = 100) -> Optional[go.Figure]:
        """Create a graph using plotly."""
        try:
            # Build the graph
            self.build_graph(contributors, repo_works, max_nodes)
            
            if self.G.number_of_nodes() == 0:
                return None
            
            # Use spring layout for positioning
            pos = nx.spring_layout(self.G, k=3, iterations=50)
            
            # Prepare edge traces
            edge_x = []
            edge_y = []
            for edge in self.G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Prepare node traces
            contributor_x = []
            contributor_y = []
            contributor_text = []
            contributor_size = []
            contributor_color = []
            
            repo_x = []
            repo_y = []
            repo_text = []
            repo_size = []
            repo_color = []
            
            for node, attrs in self.G.nodes(data=True):
                x, y = pos[node]
                if attrs.get('type') == 'contributor':
                    contributor_x.append(x)
                    contributor_y.append(y)
                    contributor_text.append(attrs.get('label', node))
                    contributor_size.append(attrs.get('size', 20))
                    contributor_color.append(attrs.get('total_commits', 0))
                else:
                    repo_x.append(x)
                    repo_y.append(y)
                    repo_text.append(attrs.get('label', node))
                    repo_size.append(attrs.get('size', 20))
                    repo_color.append(attrs.get('contributors_count', 0))
            
            # Contributor nodes
            contributor_trace = go.Scatter(
                x=contributor_x, y=contributor_y,
                mode='markers+text',
                hoverinfo='text',
                text=contributor_text,
                textposition="middle center",
                marker=dict(
                    size=contributor_size,
                    color=contributor_color,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Commits"),
                    line=dict(width=2, color='black')
                ),
                name='Contributors'
            )
            
            # Repository nodes
            repo_trace = go.Scatter(
                x=repo_x, y=repo_y,
                mode='markers+text',
                hoverinfo='text',
                text=repo_text,
                textposition="middle center",
                marker=dict(
                    size=repo_size,
                    color=repo_color,
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Contributors", x=1.1),
                    symbol='square',
                    line=dict(width=2, color='black')
                ),
                name='Repositories'
            )
            
            # Create figure
            fig = go.Figure(
                data=[edge_trace, contributor_trace, repo_trace],
                layout=go.Layout(
                    title='Contributor-Repository Network',
                    titlefont_size=16,
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[
                        dict(
                            text="Network visualization of contributors and repositories",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002,
                            xanchor="left", yanchor="bottom",
                            font=dict(color="#888", size=12)
                        )
                    ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='white'
                )
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create plotly graph: {e}")
            return None
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """Get network statistics."""
        if self.G.number_of_nodes() == 0:
            return {}
        
        try:
            stats = {
                'nodes': self.G.number_of_nodes(),
                'edges': self.G.number_of_edges(),
                'density': nx.density(self.G),
                'average_clustering': nx.average_clustering(self.G),
                'connected_components': nx.number_connected_components(self.G)
            }
            
            # Central nodes
            centrality = nx.degree_centrality(self.G)
            stats['most_central_nodes'] = sorted(
                centrality.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate network statistics: {e}")
            return {}
    
    def export_graph(self, filename: str, format: str = 'gexf'):
        """Export graph to file."""
        try:
            if format == 'gexf':
                nx.write_gexf(self.G, filename)
            elif format == 'graphml':
                nx.write_graphml(self.G, filename)
            elif format == 'gml':
                nx.write_gml(self.G, filename)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Graph exported to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            raise