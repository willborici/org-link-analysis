# functions to visualize graphs via matplotlib (static) and plotly (dynamic)
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np


# function to return a dictionary of (u, v) node tuples and the number between them
# for multi/multidigraphs
def number_of_edges_u_v(mixed_graph):
    # Preprocess number of edges between each pair of nodes
    num_edges_d = {}
    for u, v in mixed_graph.edges():
        if (u, v) not in num_edges_d:
            num_edges_d[(u, v)] = 0
        num_edges_d[(u, v)] += 1
        if (v, u) not in num_edges_d:
            num_edges_d[(v, u)] = 0
        num_edges_d[(v, u)] += 1

    return num_edges_d


# static multi/multidigraph visualization via matplotlib:
def build_static_multi_network(graph, mixed_graph):
    plt.figure(figsize=(8, 8))

    # Draw nodes with node labels
    pos = graph.fruchterman_reingold_layout(mixed_graph)  # node positions (dict.) after layout
    round_node_size = 1000  # needed for later when we draw edges that extend to the circumference
    graph.draw_networkx_nodes(mixed_graph, pos,
                              node_color='orange', node_size=round_node_size,
                              node_shape='o', alpha=0.8)
    node_labels = {node: node1.label for node, node1 in mixed_graph.nodes(data='entity')}
    graph.draw_networkx_labels(mixed_graph, pos,
                               labels=node_labels,
                               font_size=10, font_color='black')

    # Draw edges, such that any multiple edges between two nodes are discernible
    for u, v, key, data in mixed_graph.edges(data=True, keys=True):
        # Retrieve the number of edges (ignoring direction) between
        # u and v from preprocessed dictionary num_edges_d
        num_edges = number_of_edges_u_v(mixed_graph).get((u, v), 0)  # return 0 if no edges

        if num_edges == 1:  # these are the originally input directed edges
            graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(u, v, key)],
                                      style="solid", edge_color='gray',
                                      node_size=round_node_size, width=data['weight'],
                                      connectionstyle=f"arc3,rad=0.1")
            edge_labels = {(u, v, key): data['relationship']}
            graph.draw_networkx_edge_labels(mixed_graph, pos, edge_labels=edge_labels,
                                            font_size=7, font_color='black')
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
                label_pos = 0.1 + 0.3 * (i / num_edges) + 0.5
                graph.draw_networkx_edge_labels(mixed_graph, pos, edge_labels=edge_labels,
                                                label_pos=label_pos,
                                                font_size=7, font_color='black')
        else:  # TODO: update to include logic, if any, for orphan nodes
            pass

    plt.title(f"{mixed_graph}")
    plt.axis('off')  # Turn off axis
    # plt.show()  # Comment out for large graphs
    image_file_name = str(mixed_graph).replace(' ', '-')
    plt.savefig(f'./output/{image_file_name}.png')


# Static visualization for Graph/DiGraph types:
def build_static_network(graph, simple_graph):
    plt.figure(figsize=(8, 8))

    # Draw nodes with node labels
    pos = graph.spring_layout(simple_graph)  # Use a layout algorithm suitable for the graph type
    round_node_size = 1000
    graph.draw_networkx_nodes(simple_graph, pos,
                              node_color='orange', node_size=round_node_size,
                              node_shape='o', alpha=0.8)

    # Extract node labels from the graph
    node_labels = {node: simple_graph.nodes[node].get('label', str(node)) for node in simple_graph.nodes()}
    graph.draw_networkx_labels(simple_graph, pos,
                               labels=node_labels,
                               font_size=10, font_color='black')

    # Draw edges with edge labels
    for u, v, data in simple_graph.edges(data=True):
        if simple_graph.is_directed():
            edge_label = {(u, v): data['relationship']}
        else:
            edge_label = {(min(u, v), max(u, v)): data['relationship']}  # Handle undirected graphs

        # Draw each edge separately
        graph.draw_networkx_edges(simple_graph, pos, edgelist=[(u, v)],
                                  style="solid", edge_color='gray',
                                  node_size=round_node_size,
                                  width=data.get('weight', 1.0))

        graph.draw_networkx_edge_labels(simple_graph, pos, edge_labels=edge_label,
                                        font_size=7, font_color='black',
                                        label_pos=0.5, verticalalignment='center')

    plt.title(f"{simple_graph}")
    plt.axis('off')  # Turn off axis
    # plt.show()  # comment out for larger graphs
    image_file_name = str(simple_graph).replace(' ', '-')
    plt.savefig(f'./output/{image_file_name}.png')


# dynamic multi/multidigraph visualization via plotly:
def build_dynamic_multi_network(graph, mixed_graph):
    # plotly code below -- experimental but not as nice as matplot lib for curves
    fig = go.Figure()
    pos = graph.fruchterman_reingold_layout(mixed_graph)  # try this layout
    for node in mixed_graph.nodes():
        x, y = pos[node]
        fig.add_trace(go.Scatter(x=[x],
                                 y=[y],
                                 mode='markers+text',
                                 marker=dict(size=10, color='blue'),
                                 text=node,
                                 name=node,
                                 textposition='bottom center',
                                 hoverinfo='text'))

    for u, v, key, data in mixed_graph.edges(data=True, keys=True):
        # Retrieve the number of edges (ignoring direction) between
        # u and v from preprocessed dictionary num_edges_d
        num_edges = number_of_edges_u_v(mixed_graph).get((u, v), 0)  # return 0 if no edges

        if num_edges == 1:
            # Single edge case, draw a straight line
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            fig.add_trace(go.Scatter(x=[x0, x1],
                                     y=[y0, y1],
                                     mode='lines+text',
                                     line=dict(width=data['weight'], color='gray'),
                                     text=data['relationship'],
                                     textposition='top center',
                                     hoverinfo='text'))
        else:
            # Multiple edges, draw arcs
            edge_list = [(u, v, key) for key in mixed_graph[u][v]]
            for i, (source, target, edge_key) in enumerate(edge_list):
                arc_style = 0.5 * (1 - np.cos(np.pi * (i + 1) / (num_edges + 1)))

                x0, y0 = pos[u]
                x1, y1 = pos[v]

                # Calculate control points for Bézier curve
                # TODO make this a smoother Bézier line
                cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)  # set to mid-point of (x0, y0) and (x1, y1)
                control_x = cx + arc_style * (y1 - y0)
                control_y = cy - arc_style * (x0 - x1)

                # Create Bézier curve path
                fig.add_trace(go.Scatter(x=[x0, control_x, x1],
                                         y=[y0, control_y, y1],
                                         mode='lines+text',
                                         line=dict(width=mixed_graph[source][target][edge_key]['weight'], color='gray'),
                                         text=mixed_graph[source][target][edge_key]['relationship'],
                                         textposition='top center',
                                         hoverinfo='text'))

    fig.update_layout(
        title=f'{mixed_graph}',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig.show()


# Function to build dynamic (plotly) visualizations for simple graphs
def build_dynamic_network(graph, mixed_graph):
    # Initialize the figure
    fig = go.Figure()

    # Compute layout (adjust layout method as per the graph type)
    if isinstance(mixed_graph, graph.Graph):
        pos = graph.spring_layout(mixed_graph)  # Example layout for undirected graphs
    elif isinstance(mixed_graph, graph.DiGraph):
        pos = graph.fruchterman_reingold_layout(mixed_graph)  # Example layout for directed graphs
    else:
        raise ValueError("Unsupported graph type. Supported types are Graph and DiGraph.")

    # Add nodes
    for node in mixed_graph.nodes():
        x, y = pos[node]
        fig.add_trace(go.Scatter(x=[x], y=[y],
                                 mode='markers+text',
                                 marker=dict(size=10, color='blue'),
                                 text=node,
                                 name=node,
                                 textposition='bottom center',
                                 hoverinfo='text'))

    # Add edges
    for u, v, data in mixed_graph.edges(data=True):
        num_edges = mixed_graph.number_of_edges(u, v)

        if num_edges == 1:
            # Single edge case, draw a straight line
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1],
                                     mode='lines+text',
                                     line=dict(width=data.get('weight', 1), color='gray'),
                                     text=data.get('relationship', ''),
                                     textposition='top center',
                                     hoverinfo='text'))
        else:
            # Multiple edges, draw arcs
            for i, (source, target, edge_data) in enumerate(mixed_graph.edges(u, v, data=True)):
                arc_style = 0.5 * (1 - np.cos(np.pi * (i + 1) / (num_edges + 1)))

                x0, y0 = pos[u]
                x1, y1 = pos[v]

                # Calculate control points for Bézier curve
                cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
                control_x = cx + arc_style * (y1 - y0)
                control_y = cy - arc_style * (x0 - x1)

                # Create Bézier curve path
                fig.add_trace(go.Scatter(x=[x0, control_x, x1], y=[y0, control_y, y1],
                                         mode='lines+text',
                                         line=dict(width=edge_data.get('weight', 1), color='gray'),
                                         text=edge_data.get('relationship', ''),
                                         textposition='top center',
                                         hoverinfo='text'))

    # Update layout and display the figure
    fig.update_layout(
        title=f'{mixed_graph}',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig.show()
