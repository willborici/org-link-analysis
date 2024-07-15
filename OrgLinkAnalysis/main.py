import graph_viz as draw_graph
from node import Node
from link import Link
import networkx as graph

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
mixed_graph.add_node(node5.label, entity=node5)  # orphan node

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
mixed_graph.add_edge(node5.label, node1.label, directed=link2.directed, weight=link2.weight,
                     relationship=link2.label)
mixed_graph.add_edge(node5.label, node4.label, directed=link2.directed, weight=link2.weight,
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

# Visualize the graph statically:
draw_graph.build_static_network(graph, mixed_graph)

# Visualize the graph dynamically:
draw_graph.build_dynamic_network(graph, mixed_graph)
