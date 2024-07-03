import numpy as np

from node import Node
from link import Link

import networkx as graph
import matplotlib.pyplot as plt

# create new graph with mixed edge directions, but that can add multiple edges for two nodes
mixed_graph = graph.MultiGraph()

# create some nodes and links to add to the graph
node1 = Node(node_id=1, label="Will")
node2 = Node(node_id=2, label="Wilma")
node3 = Node(node_id=3, label="Willa")

link1 = Link(link_id=1, label="trust", weight=5)
link2 = Link(link_id=2, label="advice", directed=True, weight=3)
link3 = Link(link_id=3, label="chat", weight=1)

# add some nodes of Node class to the graph:
mixed_graph.add_node(node1.entity_id, entity=node1)
mixed_graph.add_node(node2.entity_id, entity=node2)
mixed_graph.add_node(node3.entity_id, entity=node3)

# add some links between nodes, with a label:
mixed_graph.add_edge(node1.entity_id, node2.entity_id, directed=link3.directed, weight=link3.weight,
                     relationship=link3.label)
mixed_graph.add_edge(node1.entity_id, node2.entity_id, directed=link1.directed, weight=link1.weight,
                     relationship=link1.label)
mixed_graph.add_edge(node3.entity_id, node1.entity_id, directed=link2.directed, weight=link2.weight,
                     relationship=link2.label)
mixed_graph.add_edge(node3.entity_id, node2.entity_id, directed=link2.directed, weight=link2.weight,
                     relationship=link2.label)
mixed_graph.add_edge(node3.entity_id, node1.entity_id, directed=link1.directed, weight=link1.weight,
                     relationship=link1.label)

# Visualize the graph
plt.figure(figsize=(8, 6))

# Draw nodes with labels
pos = graph.spring_layout(mixed_graph)
graph.draw_networkx_nodes(mixed_graph, pos, node_color='skyblue', node_size=2000, node_shape='o', alpha=0.9)
graph.draw_networkx_labels(mixed_graph, pos,
                           labels={node: node1.label for node, node1 in mixed_graph.nodes(data='entity')}, font_size=10,
                           font_color='black')

# # Draw undirected edges, such that any multiple edges don't overlap:
for u, v, key, d in mixed_graph.edges(data=True, keys=True):
    num_edges = mixed_graph.number_of_edges(u, v)
    edge_label = d['relationship']
    if not d.get('directed'):
        if num_edges == 1:
            graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(u, v, key)],
                                      style="solid",
                                      edge_color='gray', width=d['weight'])
            # Single edge, place label at midpoint
            label_x = (pos[u][0] + pos[v][0]) / 2
            label_y = (pos[u][1] + pos[v][1]) / 2
            plt.text(label_x, label_y, edge_label, fontsize=10, fontweight='bold', color='black', ha='center',
                     va='center')
        else:
            # Multiple edges between u and v, draw with offset
            offset = 0.1  # Offset for edge position

            # Determine angle between nodes u and v
            dx, dy = pos[v][0] - pos[u][0], pos[v][1] - pos[u][1]
            angle = np.arctan2(dy, dx)

            # Distribute edges around the angle
            distances = np.linspace(-0.2, 0.2, num_edges)
            for i, distance in enumerate(distances):
                sx = pos[u][0] + distance * np.sin(angle + np.pi / 2)
                sy = pos[u][1] - distance * np.cos(angle + np.pi / 2)
                tx = pos[v][0] + distance * np.sin(angle + np.pi / 2)
                ty = pos[v][1] - distance * np.cos(angle + np.pi / 2)

                graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(u, v)], width=d['weight'],
                                          edge_color='gray',
                                          connectionstyle=f"arc3,rad={0.1 + (i * 0.5)}")
                # Place edge label
                label_x = (sx + tx) / 2
                label_y = (sy + ty) / 2
                plt.text(label_x, label_y, edge_label, fontsize=10, fontweight='bold', color='black',
                         ha='center',
                         va='center')

# Draw directed edges, such that multiple edges don't overlap:
for u, v, key, d in mixed_graph.edges(data=True, keys=True):
    num_edges = mixed_graph.number_of_edges(u, v)
    edge_label = d['relationship']
    if d.get('directed'):
        if num_edges == 1:
            graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(u, v, key)],
                                      style='solid',
                                      edge_color='gray', width=d['weight'], arrows=True)
            # Single edge, place label at midpoint
            label_x = (pos[u][0] + pos[v][0]) / 2
            label_y = (pos[u][1] + pos[v][1]) / 2
            plt.text(label_x, label_y, edge_label, fontsize=10, fontweight='bold', color='black', ha='center',
                     va='center')
        else:
            # Multiple edges between u and v, draw wth offset
            offset = 0.1  # Offset for edge position
            # Determine angle between nodes u and v
            dx, dy = pos[v][0] - pos[u][0], pos[v][1] - pos[u][1]
            angle = np.arctan2(dy, dx)

            # Distribute edges around the angle
            distances = np.linspace(-0.2, 0.2, num_edges)
            for i, distance in enumerate(distances):
                sx = pos[u][0] + distance * np.sin(angle + np.pi / 2)
                sy = pos[u][1] - distance * np.cos(angle + np.pi / 2)
                tx = pos[v][0] + distance * np.sin(angle + np.pi / 2)
                ty = pos[v][1] - distance * np.cos(angle + np.pi / 2)

                graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(u, v)], width=d['weight'],
                                          edge_color='gray',
                                          connectionstyle=f"arc3,rad={0.1 + (i * 0.5)}", arrows=True)
                # Place edge label
                label_x = (sx + tx) / 2
                label_y = (sy + ty) / 2
                plt.text(label_x, label_y, edge_label, fontsize=10, fontweight='bold', color='black',
                         ha='center', va='center')

plt.title("Mixed Graph Visualization with Curved Edges")
plt.axis('off')  # Turn off axis
plt.show()
