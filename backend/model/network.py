"""Network generation utilities."""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Any
from ..schemas import NetworkType, NetworkNode, NetworkEdge


def generate_network(network_type: NetworkType, n: int, k: int, beta: float = 0.1, seed: int = 42) -> nx.Graph:
    """Generate network based on type and parameters."""
    np.random.seed(seed)
    
    if network_type == NetworkType.ERDOS_RENYI:
        p = k / (n - 1)  # Calculate probability for desired average degree
        return nx.erdos_renyi_graph(n, p, seed=seed)
    
    elif network_type == NetworkType.WATTS_STROGATZ:
        return nx.watts_strogatz_graph(n, k, beta, seed=seed)
    
    elif network_type == NetworkType.BARABASI_ALBERT:
        m = k // 2  # Number of edges to attach from new node
        return nx.barabasi_albert_graph(n, m, seed=seed)
    
    else:
        raise ValueError(f"Unknown network type: {network_type}")


def network_to_preview(graph: nx.Graph, max_nodes: int = 1000) -> Tuple[List[NetworkNode], List[NetworkEdge]]:
    """Convert NetworkX graph to preview format with sampling if needed."""
    
    # Sample nodes if graph is too large
    if len(graph.nodes) > max_nodes:
        sampled_nodes = np.random.choice(list(graph.nodes), max_nodes, replace=False)
        subgraph = graph.subgraph(sampled_nodes)
    else:
        subgraph = graph
    
    # Create nodes
    nodes = []
    for node_id in subgraph.nodes():
        nodes.append(NetworkNode(
            id=int(node_id),
            label=str(node_id),
            color="#97c2fc",
            size=10
        ))
    
    # Create edges
    edges = []
    for edge in subgraph.edges():
        edges.append(NetworkEdge(
            **{"from": int(edge[0])},  # Use ** to handle 'from' keyword
            to=int(edge[1]),
            width=1.0
        ))
    
    return nodes, edges


def calculate_network_metrics(graph: nx.Graph) -> Dict[str, Any]:
    """Calculate basic network metrics."""
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(), 
        "avg_degree": sum(dict(graph.degree()).values()) / graph.number_of_nodes(),
        "clustering": nx.average_clustering(graph),
        "diameter": nx.diameter(graph) if nx.is_connected(graph) else None,
        "avg_path_length": nx.average_shortest_path_length(graph) if nx.is_connected(graph) else None
    }