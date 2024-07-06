from node import Node
from link import Link
import networkx as graph
import matplotlib.pyplot as plt

# create new graph with mixed edge directions, but that can add multiple edges for two nodes
# use a MultiDiGraph to represent both directed and undirected edges
mixed_graph = graph.MultiDiGraph()

# create some nodes and links to add to the graph
node1 = Node(label="Will")
node2 = Node(label="Wilma")
node3 = Node(label="Willa")
node4 = Node(label="Bob")
node5 = Node(label="Alice")

link1 = Link(label="trust", weight=5)
link2 = Link(label="advice", directed=True, weight=3)
link3 = Link(label="chat", weight=0.5)

# add some nodes of Node class to the graph:
mixed_graph.add_node(node1.label, entity=node1)
mixed_graph.add_node(node2.label, entity=node2)
mixed_graph.add_node(node3.label, entity=node3)
mixed_graph.add_node(node4.label, entity=node4)
# mixed_graph.add_node(node5.label, entity=node5)  # orphan node

# add some links between nodes, with a label:
mixed_graph.add_edge(node1.label, node2.label, directed=link3.directed, weight=link3.weight,
                     relationship=link3.label)
mixed_graph.add_edge(node1.label, node2.label, directed=link1.directed, weight=link1.weight,
                     relationship=link1.label)
mixed_graph.add_edge(node3.label, node1.label, directed=link2.directed, weight=link2.weight,
                     relationship=link2.label)
mixed_graph.add_edge(node3.label, node2.label, directed=link2.directed, weight=link2.weight,
                     relationship=link2.label)
mixed_graph.add_edge(node3.label, node1.label, directed=link1.directed, weight=link1.weight,
                     relationship=link1.label)
mixed_graph.add_edge(node4.label, node1.label, directed=link3.directed, weight=link3.weight,
                     relationship=link3.label)
mixed_graph.add_edge(node4.label, node3.label, directed=link2.directed, weight=link2.weight,
                     relationship=link2.label)

# Since networkx does not support mixed graphs, for each edge where directed=False,
# create two directed edges with the same label -- and add them to the mixed_graph instance.
# As a result there will always be at least two edges between two nodes (not ideal, but why not)
# logic: <create a function> for all added edges in mixed_graph,
#           if not edge(u->v).directed:
#               make edge(u->v) directed,
#               then mixed_graph.add_edge(v->u, directed=True)
# key is needed to update the graph (see if not below), otherwise unexpected networkx behavior!
for u, v, key, data in list(mixed_graph.edges(data=True, keys=True)):
    if not data['directed']:
        # Update existing edge u->v to directed
        mixed_graph[u][v][key]['directed'] = True
        # Check if v->u already exists, so it doesn't process twice
        if not mixed_graph.has_edge(v, u, key):
            # Add a new directed edge v -> u with the same attributes as u -> v
            mixed_graph.add_edge(v, u, key, directed=True, weight=data['weight'],
                                 relationship=data['relationship'])

# Visualize the graph
plt.figure(figsize=(8, 8))

# Draw nodes with node labels
pos = graph.spring_layout(mixed_graph)  # node positions (dict.) after layout
round_node_size = 1000  # needed for later when we draw edges that extend to the circumference
graph.draw_networkx_nodes(mixed_graph, pos,
                          node_color='orange', node_size=round_node_size,
                          node_shape='o', alpha=0.8)
node_labels = {node: node1.label for node, node1 in mixed_graph.nodes(data='entity')}
graph.draw_networkx_labels(mixed_graph, pos,
                           labels=node_labels,
                           font_size=10, font_color='black')

# Preprocess number of edges between each pair of nodes
num_edges_d = {}
for u, v in mixed_graph.edges():
    if (u, v) not in num_edges_d:
        num_edges_d[(u, v)] = 0
    num_edges_d[(u, v)] += 1
    if (v, u) not in num_edges_d:
        num_edges_d[(v, u)] = 0
    num_edges_d[(v, u)] += 1

# Draw edges, such that any multiple edges between two nodes are discernible
for u, v, key, data in mixed_graph.edges(data=True, keys=True):
    # Retrieve the number of edges (ignoring direction) between
    # u and v from preprocessed dictionary num_edges_d
    num_edges = num_edges_d.get((u, v), 0)  # return 0 if no edges

    if num_edges == 1:  # these are the originally input directed edges
        graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(u, v, key)],
                                  style="solid", edge_color='gray',
                                  node_size=round_node_size, width=data['weight'],
                                  connectionstyle=f"arc3,rad=0.1")
        edge_labels = {(u, v, key): data['relationship']}
        label_pos = 0.5  # one edge, keep label centered on drawn line
        graph.draw_networkx_edge_labels(mixed_graph, pos, edge_labels=edge_labels,
                                        label_pos=label_pos,
                                        font_size=10, font_color='black')
    elif num_edges > 1:  # multiple edges between u and v
        # gather into the edge_list all the edge keys from the graph:
        edge_list = [(u, v, key) for key in mixed_graph[u][v]]

        # for each edge/key tuple from the edge_list, draw the edge arc in a way
        # that tries to eliminate overlays, using variable arc_style radians
        for i, (source, target, edge_key) in enumerate(edge_list):
            arc_style = 0.1 + 0.3 * (i / num_edges)
            graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(source, target, edge_key)],
                                      style="solid", edge_color='gray',
                                      node_size=round_node_size, width=data['weight'],
                                      connectionstyle=f"arc3,rad={arc_style}")
            edge_labels = {(source, target, edge_key): mixed_graph[source][target][edge_key]['relationship']}
            # play with this to move label around to minimize overlays
            label_pos = 0.5 + 0.4 * (i / num_edges)
            graph.draw_networkx_edge_labels(mixed_graph, pos, edge_labels=edge_labels,
                                            label_pos=label_pos,
                                            font_size=10, font_color='black')
    else:  # TODO: update to include logic, if any, for orphan nodes
        pass

plt.title("Mixed Graph Visualization with Curved Edges")
plt.axis('off')  # Turn off axis
plt.show()
