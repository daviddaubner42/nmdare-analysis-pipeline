import numpy as np
import networkx as nx
import pickle
import os

def bin_graph_from_fc(fc, labels, goal_density):

    np.fill_diagonal(fc, 0)
    G = nx.from_numpy_array(abs(fc))
    
    edges_with_weights = [(u, v, d['weight']) for u, v, d in G.edges(data=True)]
    edges_sorted = sorted(edges_with_weights, key=lambda x: x[2], reverse=True)
    num_edges_to_keep = int(len(edges_sorted) * goal_density)
    edges_to_keep = set((u, v) for u, v, w in edges_sorted[:num_edges_to_keep])
    for u, v in G.edges():
        if (u, v) not in edges_to_keep and (v, u) not in edges_to_keep:
            G.remove_edge(u, v)
    
    for edge, attrs in G.edges.items():
        attrs.pop('weight', None)
    
    relabelling = {}
    for i, n in enumerate(labels):
        relabelling[i] = n
    G = nx.relabel_nodes(G, relabelling)

    return G