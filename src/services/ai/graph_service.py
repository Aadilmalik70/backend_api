"""
Graph Service - Content relationship mapping using NetworkX

Provides graph-based content analysis including:
- Content relationship mapping
- Topic clustering and connectivity analysis
- Content gap identification through graph analysis
- Authority and influence scoring
- Content recommendation based on graph traversal

Designed for understanding content ecosystems and competitive landscapes.
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
import time
import hashlib
import json

class GraphService:
    """
    NetworkX-based graph analysis service for content relationships.
    
    Features:
    - Content similarity graph construction
    - Community detection and clustering
    - Centrality analysis for content importance
    - Path analysis for content gaps
    - Recommendation systems based on graph structure
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.initialized = False
        
        # Graph storage
        self.content_graphs = {}
        
        # Configuration
        self.config = {
            'similarity_threshold': 0.3,  # Minimum similarity for edge creation
            'max_nodes': 1000,  # Maximum nodes per graph
            'centrality_algorithms': ['degree', 'betweenness', 'pagerank', 'eigenvector'],
            'community_resolution': 1.0,
            'min_community_size': 3
        }
        
        # NetworkX will be imported lazily
        self.nx = None
        self.community = None
    
    async def initialize(self):
        """Initialize NetworkX and community detection libraries."""
        if self.initialized:
            return True
        
        try:
            import networkx as nx
            self.nx = nx
            
            # Try to import community detection
            try:
                import networkx.algorithms.community as community
                self.community = community
                self.logger.info("✅ Community detection available")
            except ImportError:
                self.logger.warning("Community detection not available")
                self.community = None
            
            self.logger.info("✅ Graph Service (NetworkX) initialized")
            self.initialized = True
            return True
            
        except ImportError as e:
            self.logger.error(f"NetworkX not available: {e}")
            self.logger.info("Install with: pip install networkx")
            return False
        except Exception as e:
            self.logger.error(f"Graph service initialization failed: {e}")
            return False
    
    async def build_content_graph(self, content_data: List[str], 
                                content_metadata: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Build a graph representation of content relationships.
        
        Args:
            content_data: List of content texts
            content_metadata: Optional metadata for each content piece
            
        Returns:
            Graph analysis results including structure and metrics
        """
        if not self.initialized or not self.nx:
            return {}
        
        try:
            start_time = time.time()
            
            if len(content_data) < 2:
                self.logger.warning("Need at least 2 content pieces to build graph")
                return {}
            
            # Create graph
            G = self.nx.Graph()
            
            # Add nodes
            for i, content in enumerate(content_data):
                node_attrs = {
                    'content': content[:200],  # Store truncated content
                    'content_length': len(content),
                    'index': i
                }
                
                # Add metadata if available
                if content_metadata and i < len(content_metadata):
                    node_attrs.update(content_metadata[i])
                
                G.add_node(i, **node_attrs)
            
            # Calculate content similarities and add edges
            similarities = await self._calculate_content_similarities(content_data)
            edges_added = 0
            
            for i in range(len(content_data)):
                for j in range(i + 1, len(content_data)):
                    if i < len(similarities) and j < len(similarities[i]):
                        similarity = similarities[i][j]
                        
                        if similarity > self.config['similarity_threshold']:
                            G.add_edge(i, j, weight=similarity, similarity=similarity)
                            edges_added += 1
            
            self.logger.debug(f"Built graph with {G.number_of_nodes()} nodes and {edges_added} edges")
            
            # Perform graph analysis
            analysis_results = await self._analyze_graph_structure(G)
            
            # Store graph for future use
            graph_id = self._generate_graph_id(content_data)
            self.content_graphs[graph_id] = G
            
            analysis_results['graph_id'] = graph_id
            analysis_results['processing_time'] = time.time() - start_time
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Content graph building failed: {e}")
            return {}
    
    async def _calculate_content_similarities(self, content_data: List[str]) -> List[List[float]]:
        """Calculate pairwise similarities between content pieces."""
        try:
            # Simple text-based similarity calculation
            # In production, you might want to use embeddings from semantic_service
            
            n = len(content_data)
            similarities = [[0.0 for _ in range(n)] for _ in range(n)]
            
            # Preprocess content for similarity calculation
            processed_content = []
            for content in content_data:
                # Simple preprocessing
                words = set(content.lower().split())
                processed_content.append(words)
            
            # Calculate Jaccard similarity
            for i in range(n):
                for j in range(i + 1, n):
                    intersection = len(processed_content[i] & processed_content[j])
                    union = len(processed_content[i] | processed_content[j])
                    
                    if union > 0:
                        similarity = intersection / union
                        similarities[i][j] = similarity
                        similarities[j][i] = similarity  # Symmetric
            
            return similarities
            
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {e}")
            return []
    
    async def _analyze_graph_structure(self, G) -> Dict[str, Any]:
        """Perform comprehensive graph structure analysis."""
        try:
            analysis = {}
            
            # Basic graph metrics
            analysis['basic_metrics'] = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': self.nx.density(G),
                'is_connected': self.nx.is_connected(G),
                'number_of_components': self.nx.number_connected_components(G)
            }
            
            # Centrality analysis
            analysis['centrality'] = await self._calculate_centralities(G)
            
            # Community detection
            if self.community and G.number_of_edges() > 0:
                analysis['communities'] = await self._detect_communities(G)
            
            # Path analysis
            analysis['path_analysis'] = await self._analyze_paths(G)
            
            # Content gaps identification
            analysis['content_gaps'] = await self._identify_graph_gaps(G)
            
            # Influential content identification
            analysis['influential_content'] = await self._identify_influential_content(G)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Graph structure analysis failed: {e}")
            return {}
    
    async def _calculate_centralities(self, G) -> Dict[str, Dict[int, float]]:
        """Calculate various centrality measures for graph nodes."""
        try:
            centralities = {}
            
            if G.number_of_nodes() == 0:
                return centralities
            
            # Degree centrality
            try:
                centralities['degree'] = dict(self.nx.degree_centrality(G))
            except Exception as e:
                self.logger.warning(f"Degree centrality calculation failed: {e}")
            
            # Betweenness centrality (for connected graphs)
            if self.nx.is_connected(G):
                try:
                    centralities['betweenness'] = dict(self.nx.betweenness_centrality(G))
                except Exception as e:
                    self.logger.warning(f"Betweenness centrality calculation failed: {e}")
            
            # PageRank centrality
            try:
                centralities['pagerank'] = dict(self.nx.pagerank(G))
            except Exception as e:
                self.logger.warning(f"PageRank calculation failed: {e}")
            
            # Eigenvector centrality (if graph is connected)
            if self.nx.is_connected(G):
                try:
                    centralities['eigenvector'] = dict(self.nx.eigenvector_centrality(G))
                except Exception as e:
                    self.logger.warning(f"Eigenvector centrality calculation failed: {e}")
            
            return centralities
            
        except Exception as e:
            self.logger.error(f"Centrality calculation failed: {e}")
            return {}
    
    async def _detect_communities(self, G) -> Dict[str, Any]:
        """Detect communities/clusters in the content graph."""
        try:
            if not self.community or G.number_of_edges() == 0:
                return {}
            
            # Use different community detection algorithms
            communities_result = {}
            
            # Louvain method (if available)
            try:
                if hasattr(self.community, 'louvain_communities'):
                    communities = list(self.community.louvain_communities(G))
                elif hasattr(self.community, 'best_partition'):
                    # Alternative community detection
                    partition = self.community.best_partition(G)
                    communities = {}
                    for node, comm_id in partition.items():
                        if comm_id not in communities:
                            communities[comm_id] = []
                        communities[comm_id].append(node)
                    communities = list(communities.values())
                else:
                    # Fallback: connected components
                    communities = list(self.nx.connected_components(G))
                
                # Process communities
                community_info = []
                for i, community in enumerate(communities):
                    if len(community) >= self.config['min_community_size']:
                        # Get community characteristics
                        subgraph = G.subgraph(community)
                        
                        community_info.append({
                            'id': i,
                            'nodes': list(community),
                            'size': len(community),
                            'density': self.nx.density(subgraph),
                            'avg_clustering': self.nx.average_clustering(subgraph) if subgraph.number_of_nodes() > 2 else 0
                        })
                
                communities_result = {
                    'communities': community_info,
                    'num_communities': len(community_info),
                    'modularity': self._calculate_modularity(G, communities) if communities else 0
                }
                
            except Exception as e:
                self.logger.warning(f"Community detection failed: {e}")
                communities_result = {}
            
            return communities_result
            
        except Exception as e:
            self.logger.error(f"Community detection failed: {e}")
            return {}
    
    def _calculate_modularity(self, G, communities) -> float:
        """Calculate modularity score for community structure."""
        try:
            if hasattr(self.nx, 'algorithms') and hasattr(self.nx.algorithms, 'community'):
                return self.nx.algorithms.community.modularity(G, communities)
            else:
                # Simple modularity approximation
                return 0.5  # Placeholder
        except Exception:
            return 0.0
    
    async def _analyze_paths(self, G) -> Dict[str, Any]:
        """Analyze path structures in the graph."""
        try:
            path_analysis = {}
            
            if G.number_of_nodes() < 2:
                return path_analysis
            
            # Calculate average path length for connected components
            if self.nx.is_connected(G):
                path_analysis['average_shortest_path'] = self.nx.average_shortest_path_length(G)
                path_analysis['diameter'] = self.nx.diameter(G)
                path_analysis['radius'] = self.nx.radius(G)
            else:
                # For disconnected graphs, analyze largest component
                largest_cc = max(self.nx.connected_components(G), key=len)
                if len(largest_cc) > 1:
                    largest_subgraph = G.subgraph(largest_cc)
                    path_analysis['largest_component_avg_path'] = self.nx.average_shortest_path_length(largest_subgraph)
                    path_analysis['largest_component_diameter'] = self.nx.diameter(largest_subgraph)
            
            # Calculate clustering coefficient
            path_analysis['average_clustering'] = self.nx.average_clustering(G)
            path_analysis['transitivity'] = self.nx.transitivity(G)
            
            return path_analysis
            
        except Exception as e:
            self.logger.error(f"Path analysis failed: {e}")
            return {}
    
    async def _identify_graph_gaps(self, G) -> List[Dict[str, Any]]:
        """Identify content gaps based on graph structure."""
        try:
            gaps = []
            
            # Find nodes with low connectivity (isolated content)
            degree_centrality = self.nx.degree_centrality(G)
            
            for node, centrality in degree_centrality.items():
                if centrality < 0.1:  # Low connectivity threshold
                    node_data = G.nodes[node]
                    gaps.append({
                        'node': node,
                        'type': 'isolated_content',
                        'degree_centrality': centrality,
                        'content_preview': node_data.get('content', '')[:100]
                    })
            
            # Find potential bridge content (high betweenness, low degree)
            if self.nx.is_connected(G):
                betweenness = self.nx.betweenness_centrality(G)
                degree = dict(G.degree())
                
                for node in G.nodes():
                    if betweenness.get(node, 0) > 0.1 and degree.get(node, 0) < 3:
                        node_data = G.nodes[node]
                        gaps.append({
                            'node': node,
                            'type': 'bridge_opportunity',
                            'betweenness_centrality': betweenness.get(node, 0),
                            'degree': degree.get(node, 0),
                            'content_preview': node_data.get('content', '')[:100]
                        })
            
            return gaps[:10]  # Return top 10 gaps
            
        except Exception as e:
            self.logger.error(f"Gap identification failed: {e}")
            return []
    
    async def _identify_influential_content(self, G) -> List[Dict[str, Any]]:
        """Identify influential content based on centrality measures."""
        try:
            influential_content = []
            
            # Get centrality measures
            centralities = await self._calculate_centralities(G)
            
            # Combine different centrality measures
            combined_scores = {}
            
            for node in G.nodes():
                score = 0
                count = 0
                
                for centrality_type, centrality_values in centralities.items():
                    if node in centrality_values:
                        score += centrality_values[node]
                        count += 1
                
                if count > 0:
                    combined_scores[node] = score / count
            
            # Sort by combined score
            sorted_nodes = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Get top influential content
            for node, score in sorted_nodes[:5]:
                node_data = G.nodes[node]
                influential_content.append({
                    'node': node,
                    'influence_score': score,
                    'content_preview': node_data.get('content', '')[:100],
                    'content_length': node_data.get('content_length', 0),
                    'centrality_details': {
                        centrality_type: centrality_values.get(node, 0)
                        for centrality_type, centrality_values in centralities.items()
                    }
                })
            
            return influential_content
            
        except Exception as e:
            self.logger.error(f"Influential content identification failed: {e}")
            return []
    
    async def recommend_content_connections(self, graph_id: str, target_node: int, 
                                          num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend content that should be connected to a target piece.
        
        Args:
            graph_id: ID of the graph to analyze
            target_node: Node to find recommendations for
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of content connection recommendations
        """
        if graph_id not in self.content_graphs:
            return []
        
        try:
            G = self.content_graphs[graph_id]
            
            if target_node not in G:
                return []
            
            recommendations = []
            
            # Find nodes that are 2 hops away (friends of friends)
            two_hop_neighbors = set()
            for neighbor in G.neighbors(target_node):
                for second_neighbor in G.neighbors(neighbor):
                    if second_neighbor != target_node and second_neighbor not in G.neighbors(target_node):
                        two_hop_neighbors.add(second_neighbor)
            
            # Calculate recommendation scores
            for candidate in two_hop_neighbors:
                # Score based on common neighbors
                common_neighbors = len(set(G.neighbors(target_node)) & set(G.neighbors(candidate)))
                
                # Score based on centrality
                degree_centrality = self.nx.degree_centrality(G).get(candidate, 0)
                
                # Combined score
                recommendation_score = common_neighbors * 0.7 + degree_centrality * 0.3
                
                candidate_data = G.nodes[candidate]
                recommendations.append({
                    'node': candidate,
                    'recommendation_score': recommendation_score,
                    'common_neighbors': common_neighbors,
                    'content_preview': candidate_data.get('content', '')[:100],
                    'reason': 'Connected through mutual connections'
                })
            
            # Sort by score and return top recommendations
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            return recommendations[:num_recommendations]
            
        except Exception as e:
            self.logger.error(f"Content recommendation failed: {e}")
            return []
    
    async def analyze_content_ecosystem(self, content_data: List[str], 
                                      content_categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze the overall content ecosystem and provide strategic insights.
        
        Args:
            content_data: List of content pieces
            content_categories: Optional categories for each content piece
            
        Returns:
            Ecosystem analysis with strategic recommendations
        """
        try:
            # Build content graph
            metadata = []
            if content_categories:
                for i, category in enumerate(content_categories):
                    if i < len(content_data):
                        metadata.append({'category': category})
            
            graph_analysis = await self.build_content_graph(content_data, metadata)
            
            if not graph_analysis:
                return {}
            
            # Additional ecosystem analysis
            ecosystem_insights = {
                'content_distribution': await self._analyze_content_distribution(graph_analysis),
                'connectivity_health': await self._assess_connectivity_health(graph_analysis),
                'strategic_opportunities': await self._identify_strategic_opportunities(graph_analysis),
                'content_portfolio_balance': await self._analyze_portfolio_balance(graph_analysis, content_categories)
            }
            
            # Combine with graph analysis
            ecosystem_analysis = {
                'graph_analysis': graph_analysis,
                'ecosystem_insights': ecosystem_insights,
                'recommendations': await self._generate_ecosystem_recommendations(graph_analysis, ecosystem_insights)
            }
            
            return ecosystem_analysis
            
        except Exception as e:
            self.logger.error(f"Ecosystem analysis failed: {e}")
            return {}
    
    async def _analyze_content_distribution(self, graph_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how content is distributed across the graph."""
        try:
            basic_metrics = graph_analysis.get('basic_metrics', {})
            
            return {
                'content_connectivity': {
                    'highly_connected': len([c for c in graph_analysis.get('centrality', {}).get('degree', {}).values() if c > 0.5]),
                    'moderately_connected': len([c for c in graph_analysis.get('centrality', {}).get('degree', {}).values() if 0.2 < c <= 0.5]),
                    'poorly_connected': len([c for c in graph_analysis.get('centrality', {}).get('degree', {}).values() if c <= 0.2])
                },
                'network_density': basic_metrics.get('density', 0),
                'fragmentation_level': 1 - (1 / max(basic_metrics.get('number_of_components', 1), 1))
            }
        except Exception:
            return {}
    
    async def _assess_connectivity_health(self, graph_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the health of content connectivity."""
        try:
            basic_metrics = graph_analysis.get('basic_metrics', {})
            
            health_score = 0
            factors = []
            
            # Connectivity factor
            if basic_metrics.get('is_connected', False):
                health_score += 30
                factors.append("Content is well connected")
            else:
                factors.append("Content has disconnected clusters")
            
            # Density factor
            density = basic_metrics.get('density', 0)
            if density > 0.3:
                health_score += 25
                factors.append("Good content density")
            elif density > 0.1:
                health_score += 15
                factors.append("Moderate content density")
            else:
                factors.append("Low content density")
            
            # Community structure factor
            communities = graph_analysis.get('communities', {})
            if communities.get('num_communities', 0) > 1:
                health_score += 20
                factors.append("Clear content clusters identified")
            
            # Central content factor
            centralities = graph_analysis.get('centrality', {})
            if centralities.get('degree'):
                max_centrality = max(centralities['degree'].values())
                if max_centrality > 0.3:
                    health_score += 25
                    factors.append("Strong content hubs present")
            
            return {
                'health_score': health_score,
                'health_level': self._get_health_level(health_score),
                'contributing_factors': factors
            }
        except Exception:
            return {}
    
    async def _identify_strategic_opportunities(self, graph_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify strategic content opportunities."""
        try:
            opportunities = []
            
            # Gap-filling opportunities
            gaps = graph_analysis.get('content_gaps', [])
            if gaps:
                opportunities.append({
                    'type': 'fill_content_gaps',
                    'description': 'Create content to connect isolated pieces',
                    'priority': 'high',
                    'potential_impact': 'improved_connectivity'
                })
            
            # Hub creation opportunities
            centralities = graph_analysis.get('centrality', {})
            if centralities.get('degree'):
                max_centrality = max(centralities['degree'].values())
                if max_centrality < 0.3:
                    opportunities.append({
                        'type': 'create_hub_content',
                        'description': 'Create central content that connects multiple topics',
                        'priority': 'medium',
                        'potential_impact': 'increased_authority'
                    })
            
            # Community bridging opportunities
            communities = graph_analysis.get('communities', {})
            if communities.get('num_communities', 0) > 2:
                opportunities.append({
                    'type': 'bridge_communities',
                    'description': 'Create content that bridges different topic clusters',
                    'priority': 'medium',
                    'potential_impact': 'better_content_flow'
                })
            
            return opportunities
        except Exception:
            return []
    
    async def _analyze_portfolio_balance(self, graph_analysis: Dict[str, Any], 
                                       content_categories: Optional[List[str]]) -> Dict[str, Any]:
        """Analyze the balance of content portfolio."""
        try:
            if not content_categories:
                return {}
            
            category_counts = {}
            for category in content_categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            total_content = len(content_categories)
            category_distribution = {
                cat: count / total_content for cat, count in category_counts.items()
            }
            
            # Calculate balance score
            ideal_distribution = 1.0 / len(category_counts)
            balance_score = 1.0 - sum(abs(dist - ideal_distribution) for dist in category_distribution.values()) / 2
            
            return {
                'category_distribution': category_distribution,
                'balance_score': balance_score,
                'balance_level': self._get_balance_level(balance_score),
                'dominant_categories': [cat for cat, dist in category_distribution.items() if dist > 0.3],
                'underrepresented_categories': [cat for cat, dist in category_distribution.items() if dist < 0.1]
            }
        except Exception:
            return {}
    
    async def _generate_ecosystem_recommendations(self, graph_analysis: Dict[str, Any], 
                                                ecosystem_insights: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations for the content ecosystem."""
        try:
            recommendations = []
            
            # Connectivity recommendations
            connectivity_health = ecosystem_insights.get('connectivity_health', {})
            health_score = connectivity_health.get('health_score', 0)
            
            if health_score < 50:
                recommendations.append("Improve content connectivity by creating linking content between isolated pieces")
            
            # Balance recommendations
            portfolio_balance = ecosystem_insights.get('content_portfolio_balance', {})
            if portfolio_balance.get('balance_score', 1) < 0.7:
                recommendations.append("Rebalance content portfolio to cover underrepresented topic areas")
            
            # Strategic opportunities
            opportunities = ecosystem_insights.get('strategic_opportunities', [])
            for opportunity in opportunities[:3]:  # Top 3 opportunities
                recommendations.append(f"Consider {opportunity.get('description', 'strategic content creation')}")
            
            return recommendations[:5]  # Top 5 recommendations
        except Exception:
            return []
    
    def _generate_graph_id(self, content_data: List[str]) -> str:
        """Generate a unique ID for the content graph."""
        content_hash = hashlib.md5(''.join(content_data).encode('utf-8')).hexdigest()
        return f"graph_{content_hash[:8]}"
    
    def _get_health_level(self, score: float) -> str:
        """Convert health score to descriptive level."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _get_balance_level(self, score: float) -> str:
        """Convert balance score to descriptive level."""
        if score >= 0.8:
            return "Well Balanced"
        elif score >= 0.6:
            return "Moderately Balanced"
        else:
            return "Unbalanced"
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about stored graphs."""
        return {
            'stored_graphs': len(self.content_graphs),
            'total_nodes': sum(G.number_of_nodes() for G in self.content_graphs.values()),
            'total_edges': sum(G.number_of_edges() for G in self.content_graphs.values()),
            'config': self.config
        }
    
    def clear_graphs(self):
        """Clear stored graphs to free memory."""
        self.content_graphs.clear()
        self.logger.info("Graph service cache cleared")