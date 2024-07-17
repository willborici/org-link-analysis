# output of graph algorithms into an org-mode file for report generation

REPORT_FILE = './output/report.org'


def analyze_centrality(graph, graph_type, mixed_graph):
    centrality_analysis = {}

    centrality_analysis['degree'] = graph.degree_centrality(mixed_graph)

    if graph_type in ('simple directed', 'simple undirected'):
        try:
            centrality_analysis['eigenvector'] = graph.eigenvector_centrality(mixed_graph)
        except graph.PowerIterationFailedConvergence:
            centrality_analysis['eigenvector'] = 'power iteration convergence failure for eigenvector'
    else:
        centrality_analysis['eigenvector'] = 'no eigenvector for mixed graphs'

    centrality_analysis['closeness'] = graph.closeness_centrality(mixed_graph)

    centrality_analysis['betweenness'] = graph.betweenness_centrality(mixed_graph)

    return centrality_analysis


def analyze_connectivity(graph, graph_type, mixed_graph):
    connectivity_analysis = {}

    if graph_type == 'simple undirected':
        # Find connected components
        connectivity_analysis['connected components'] = list(graph.connected_components(mixed_graph))

    elif graph_type == 'simple directed':
        # Find strongly connected components (SCC)
        connectivity_analysis['SCC'] = list(graph.strongly_connected_components(mixed_graph))

        # Find weakly connected components (WCC)
        connectivity_analysis['WCC'] = list(graph.weakly_connected_components(mixed_graph))

        # Check reachability
        connectivity_analysis['reachability'] = 'strong' if graph.is_strongly_connected(mixed_graph) else 'weak'

    elif graph_type == 'multi-graph' or graph_type == 'multi-digraph':
        # Compute edge connectivity for multi-graphs and multi-diGraphs
        connectivity_analysis['edge connectivity'] = graph.edge_connectivity(mixed_graph)

        # Find strongly connected components (SCC) for multi-diGraphs
        if graph_type == 'multi-digraph':
            connectivity_analysis['SCC'] = list(graph.strongly_connected_components(mixed_graph))

    return connectivity_analysis


def analyze_paths(graph, graph_type, mixed_graph):
    # Shortest Paths: Computes the shortest paths between nodes, which can indicate communication
    # efficiency or how quickly information can spread through the network.
    path_analysis = {}

    if graph_type in ['simple undirected', 'simple directed']:
        # Shortest paths between all pairs of nodes
        path_analysis['all_pairs_shortest_paths'] = dict(graph.all_pairs_shortest_path(mixed_graph))

        # Check if the graph is weakly connected (for directed graphs)
        if graph_type == 'simple directed':
            if not graph.is_strongly_connected(mixed_graph):
                try:
                    # Average shortest path length (only if the graph is strongly connected)
                    path_analysis['average_shortest_path_length'] = graph.average_shortest_path_length(mixed_graph)
                except graph.NetworkXError:
                    path_analysis['average_shortest_path_length'] = float('inf')  # Handle error case
        else:
            path_analysis['average_shortest_path_length'] = float('inf')  # Handle case where not strongly connected

    elif graph_type in ['multi-graph', 'multi-digraph']:
        # Multi-graphs and multi-diGraphs also support shortest paths
        path_analysis['all_pairs_shortest_paths'] = dict(graph.all_pairs_shortest_path(mixed_graph))

        # Average shortest path length (only if the graph is weakly connected or multi-graph)
        if not graph.is_weakly_connected(mixed_graph) or graph_type == 'multi-graph':
            try:
                path_analysis['average_shortest_path_length'] = graph.average_shortest_path_length(mixed_graph)
            except graph.NetworkXError:
                path_analysis['average_shortest_path_length'] = float('inf')  # Handle error case
        else:
            path_analysis['average_shortest_path_length'] = float('inf')  # Handle case where not weakly connected

    return path_analysis


def compute_clustering_coefficient_multidigraph(graph):
    clustering_coefficients = {}
    for node in graph.nodes():
        neighbors = list(graph.neighbors(node))
        if len(neighbors) < 2:
            clustering_coefficients[node] = 0.0
        else:
            num_triangles = 0
            possible_triangles = len(neighbors) * (len(neighbors) - 1)
            for neighbor1 in neighbors:
                for neighbor2 in neighbors:
                    if neighbor1 != neighbor2 and graph.has_edge(neighbor1, neighbor2):
                        num_triangles += 1
            clustering_coefficients[node] = num_triangles / possible_triangles if possible_triangles > 0 else 0.0
    return clustering_coefficients


def analyze_clustering(graph, graph_type, mixed_graph):
    # Clustering Coefficient measures the density of connections among a node's neighbors.
    # For advice, it shows how likely nodes receiving advice from the same person are to also
    # interact. For trust and chat, it reflects the formation of clusters of trust or communication.
    # Transitivity: In a directed graph context, measures the likelihood that if node A trusts or
    # chats with node B and node B trusts or chats with node C, then node A also trusts or
    # chats with node C. It reflects the formation of trust or communication triangles in your
    # network.
    clustering_analysis = {}

    if graph_type == 'simple undirected':
        # Clustering coefficient for undirected graph
        clustering_analysis['clustering_coefficient'] = graph.clustering(mixed_graph)

        # Transitivity (ratio of triangles to triplets in the graph)
        clustering_analysis['transitivity'] = graph.transitivity(mixed_graph)

    elif graph_type == 'simple directed':
        # Clustering coefficient for directed graph
        clustering_analysis['clustering_coefficient'] = graph.clustering(mixed_graph.to_undirected())

        # Transitivity for directed graphs
        clustering_analysis['transitivity'] = graph.transitivity(mixed_graph.to_undirected())

    elif graph_type == 'multi-graph':
        # Clustering coefficient for multi-graph (undirected)
        clustering_analysis['clustering_coefficient'] = graph.clustering(mixed_graph)

        # Transitivity for multi-graph (undirected)
        clustering_analysis['transitivity'] = graph.transitivity(mixed_graph.to_undirected())

    elif graph_type == 'multi-digraph':
        # Clustering coefficient for multi-diGraph (convert to undirected)
        clustering_analysis['clustering_coefficient'] = compute_clustering_coefficient_multidigraph(mixed_graph)

    return clustering_analysis


def analyze_assortativity(graph, graph_type, mixed_graph):
    # Assortativity Coefficient measures the tendency of nodes to connect to others that are
    # similar in some way (e.g., similar degree). This can show whether individuals tend to
    # connect with others who seek advice, trust each other, or chat frequently.
    assortativity_analysis = {}

    if graph_type in ['simple undirected', 'multi-graph']:
        # Assortativity coefficient
        assortativity_analysis['assortativity'] = graph.degree_assortativity_coefficient(mixed_graph)

    elif graph_type in ['simple directed', 'multi-digraph']:
        # In-degree assortativity coefficient
        assortativity_analysis['in_degree_assortativity'] = graph.degree_assortativity_coefficient(mixed_graph, x='in', y='in')
        assortativity_analysis['out_degree_assortativity'] = graph.degree_assortativity_coefficient(mixed_graph, x='out', y='out')

    return assortativity_analysis


# function to insert analysis output into the corresponding section
# of the report.org file (org-mode, because emacs rocks!) in the output directory
# NB: the section headers need to be given literally
def insert_output_to_file(report_file, section_header, output_text):
    with open(report_file, 'r') as output_file:
        lines = output_file.readlines()

    with open(report_file, 'w') as output_file:
        section_found = False
        for line in lines:
            if line.strip().startswith(section_header):
                section_found = True
                output_file.write(line)  # Write the section header
                output_file.write(output_text)  # Write the output under this section
            else:
                output_file.write(line)  # Write the line as-is

        if not section_found:
            output_file.write(f"\n* {section_header}\n")  # If section doesn't exist, create it
            output_file.write(output_text)


# main function to run and report on the various networkx graph algorithms
# TODO: remove the print debugging statements and create a Report.org file to
#       process the output into a readable report
def generate_analysis_report(graph, graph_type, graph_to_analyze):

    output_text = ''

    # print graph information:
    output_text = f"Graph properties: {graph_to_analyze}\n----------------\n"
    insert_output_to_file(REPORT_FILE,
                          'Introduction',
                          output_text)

    # Centrality Algorithms:
    centrality_report = analyze_centrality(graph, graph_type, graph_to_analyze)
    output_text = f'Centrality Report:\n {centrality_report} \n\n'
    insert_output_to_file(REPORT_FILE,
                          'Centrality Analysis',
                          output_text)

    # Connectivity Algorithms
    connectivity_report = analyze_connectivity(graph, graph_type, graph_to_analyze)
    output_text = f'Connectivity Report:\n {connectivity_report} \n\n'
    insert_output_to_file(REPORT_FILE,
                          'Connectivity Analysis',
                          output_text)

    # Path Algorithms:
    path_report = analyze_paths(graph, graph_type, graph_to_analyze)
    output_text = f'Path Analysis Report:\n {path_report} \n\n'
    insert_output_to_file(REPORT_FILE,
                          'Path Analysis',
                          output_text)

    # Clustering Algorithms:
    clustering_report = analyze_clustering(graph, graph_type, graph_to_analyze)
    output_text = f'Clustering Report:\n {clustering_report} \n\n'
    insert_output_to_file(REPORT_FILE,
                          'Clustering Analysis',
                          output_text)

    # Assortativity Algorithms:
    assortativity_report = analyze_assortativity(graph, graph_type, graph_to_analyze)
    output_text = f'Assortativity Report:\n {assortativity_report} \n\n'
    insert_output_to_file(REPORT_FILE,
                          'Assortativity Analysis',
                          output_text)
