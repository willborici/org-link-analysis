import graph_viz as draw_graph
import report as report
from node import Node
from link import Link
import networkx as graph
import pandas as pd  # to read the csv input data

# create new graph with mixed edge directions, but that can add multiple edges for two nodes
# use a MultiDiGraph to represent both directed and undirected edges
original_graph = graph.MultiDiGraph()  # store the original undirected and directed edges
mixed_graph = graph.MultiDiGraph()  # normalize all edges to directed

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

    # add edge to original_graph:
    original_graph.add_edge(source_node, target_node, directed=directed, weight=weight,
                            relationship=link_label)

    # if this is an undirected edge, create two directed edges because nextworkx
    # does not support mixed graphs -- so normalize all edges to directed into mixed_graph:
    if not directed:
        mixed_graph.add_edge(source_node, target_node, directed=True, weight=weight,
                             relationship=link_label)
        mixed_graph.add_edge(target_node, source_node, directed=True, weight=weight,
                             relationship=link_label)
    else:
        mixed_graph.add_edge(source_node, target_node, directed=True, weight=weight,
                             relationship=link_label)


# Return a sub-graph given a link
def get_subgraph_from_link(main_graph, relationship, is_directed):
    subgraph_edges = {(u, v, k) for u, v, k, data in main_graph.edges(keys=True, data=True) if
                      data.get('relationship') == relationship}

    # Create the subgraph
    subgraph = main_graph.edge_subgraph(subgraph_edges)

    # Return as Graph or DiGraph (simple undirected or directed graph)
    if is_directed:
        return graph.DiGraph(subgraph)
    else:
        return graph.Graph(subgraph)


# fetch a dictionary of sub-graphs for each link:
# key: link label, value: sub-graph
subgraphs = {}
for link in links:
    subgraphs[link.label] = get_subgraph_from_link(original_graph, link.label, link.directed)


# Given a graph, analyze by running various algorithms and get a report
def analyze_graph(networkx_graph, graph_to_analyze):
    # fetch the graph type to pass it to the report generator below
    # since some graph algorithms run on specific graph types
    graph_type = ''
    if '.Graph' in str(type(graph_to_analyze)):
        graph_type = 'simple undirected'
    elif '.DiGraph' in str(type(graph_to_analyze)):
        graph_type = 'simple directed'
    elif '.MultiGraph' in str(type(graph_to_analyze)):
        graph_type = 'multi-graph'
    elif '.MultiDiGraph' in str(type(graph_to_analyze)):
        graph_type = 'multi-digraph'

    # generate a report of the graph-algorithmic analysis
    report.generate_analysis_report(networkx_graph, graph_type, graph_to_analyze)


# analyze mixed graph:
analyze_graph(graph, mixed_graph)

# analyze all other subgraphs:
for link, subgraph in subgraphs.items():
    analyze_graph(graph, subgraphs[link])


# Visualize a graph
def visualize_graph(networkx_graph, graph_to_visualize):
    # fetch the graph type to pass it to the report generator below
    # since some graph algorithms run on specific graph types
    graph_type = ''
    if '.Graph' in str(type(graph_to_visualize)):
        graph_type = 'simple undirected'
    elif '.DiGraph' in str(type(graph_to_visualize)):
        graph_type = 'simple directed'
    elif '.MultiGraph' in str(type(graph_to_visualize)):
        graph_type = 'multi-graph'
    elif '.MultiDiGraph' in str(type(graph_to_visualize)):
        graph_type = 'multi-digraph'

    # if simple graphs:
    if graph_type in ('simple undirected', 'simple directed'):
        # matplotlib (static):
        draw_graph.build_static_network(networkx_graph, graph_to_visualize)

        # plotly (dynamic):
 #       draw_graph.build_dynamic_network(networkx_graph, graph_to_visualize)
    else:  # multigraphs
        # matplotlib (static):
        draw_graph.build_static_multi_network(graph, mixed_graph)

        # plotly (dynamic):
#        draw_graph.build_dynamic_multi_network(graph, mixed_graph)


# visualize the mixed graph:
visualize_graph(graph, mixed_graph)

# visualize all other subgraphs:
for link, subgraph in subgraphs.items():
    visualize_graph(graph, subgraphs[link])
