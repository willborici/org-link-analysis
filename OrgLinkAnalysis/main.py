import graph_viz as draw_graph
from node import Node
from link import Link
import networkx as graph
import pandas as pd  # to read the csv input data

# create new graph with mixed edge directions, but that can add multiple edges for two nodes
# use a MultiDiGraph to represent both directed and undirected edges
mixed_graph = graph.MultiDiGraph()

# read the source files:
# input/node.csv: the nodes
# input/link.csv: the kinds of links and related properties like weight
# input/relationship.csv: the links between any two given nodes
node_df = pd.read_csv('./input/node.csv')
link_df = pd.read_csv('./input/link.csv')
relationship_df = pd.read_csv('./input/relationship.csv')

# instantiate node and link objects from input data:
nodes = [Node(row['Label'], ID=row['ID']) for node_df_index, row in node_df.iterrows()]
links = [Link(row['Label'], directed=row['Directed'],
              weight=row['Weight'], ID=row['ID']) for link_df_index, row in link_df.iterrows()]

# add the nodes to the mixed graph:
for node in nodes:
    mixed_graph.add_node(node.label, entity=node)

# add the edges into the mixed_graph:
for relationship_index, row in relationship_df.iterrows():
    source_node = row['Source']
    target_node = row['Target']
    link_label = row['Link']

    # given the link label in relationship_df, search for the corresponding record in links[]
    # assume some default values in case:
    directed = False
    weight = 1.0
    for link in links:
        if link.label == link_label:
            # fetch the directed and weight values from link[]
            directed = link.directed
            weight = link.weight
            break

    # if this is an undirected edge, create two directed edges because nextworkx
    # does not support mixed graphs -- so normalize all edges to directed:
    if not directed:
        mixed_graph.add_edge(source_node, target_node, directed=True, weight=weight,
                             relationship=link_label)
        mixed_graph.add_edge(target_node, source_node, directed=True, weight=weight,
                             relationship=link_label)
    else:
        mixed_graph.add_edge(source_node, target_node, directed=True, weight=weight,
                             relationship=link_label)

# Visualize the graph statically:
draw_graph.build_static_network(graph, mixed_graph)

# Visualize the graph dynamically:
draw_graph.build_dynamic_network(graph, mixed_graph)
