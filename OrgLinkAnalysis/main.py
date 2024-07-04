from node import Node
from link import Link

import networkx as graph
import matplotlib.pyplot as plt
import numpy as np

# create new graph with mixed edge directions, but that can add multiple edges for two nodes
# use a MultiDiGraph to represent both directed and undirected edges
mixed_graph = graph.MultiDiGraph()

# create some nodes and links to add to the graph
node1 = Node(node_id=1, label="Will")
node2 = Node(node_id=2, label="Wilma")
node3 = Node(node_id=3, label="Willa")

link1 = Link(link_id=1, label="trust", weight=5)
link2 = Link(link_id=2, label="advice", directed=True, weight=3)
link3 = Link(link_id=3, label="chat", weight=0.2)

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

# Since networkx does not support mixed graphs, for each edge where directed=False,
# create two directed edges with the same label -- and add them to the mixed_graph instance.
# As a result there will always be at least two edges between two nodes (not ideal, but why not)
# logic: <create a function> for all added edges in mixed_graph,
#           if not edge(u->v).directed:
#               make edge(u->v) directed,
#               then mixed_graph.add_edge(v->u, directed=True)
for u, v, data in mixed_graph.edges(data=True):
    if not data['directed']:
        # Update existing edge u->v to directed
        mixed_graph[u][v][0]['directed'] = True
        # Add a new directed edge v->u, with the same attributes as u->v
        mixed_graph.add_edge(v, u, directed=True, weight=data['weight'], relationship=data['relationship'])

# Visualize the graph
plt.figure(figsize=(8, 6))

# Draw nodes with labels
pos = graph.spring_layout(mixed_graph)  # node positions (dict.) after layout
round_node_size = 2000  # needed for later when we draw edges that extend to the circumference
graph.draw_networkx_nodes(mixed_graph, pos,
                          node_color='orange', node_size=round_node_size,
                          node_shape='o', alpha=0.8)
graph.draw_networkx_labels(mixed_graph, pos,
                           labels={node: node1.label for node, node1 in mixed_graph.nodes(data='entity')},
                           font_size=10, font_color='black')

# Draw edges, such that any multiple edges between two nodes are discernible
for u, v, data in mixed_graph.edges(data=True):
    num_edges = mixed_graph.number_of_edges(u, v)
    if num_edges == 1:  # these are the originally input directed edges
        graph.draw_networkx_edges(mixed_graph, pos, edgelist=[(u, v)],
                                  style="solid", edge_color='gray',
                                  node_size=round_node_size,
                                  width=data['weight'])

        # Place edge label at midpoint of nodes u and v,
        # where [u][0] is the x value, [u][1] is they value
        label_x = (pos[u][0] + pos[v][0]) / 2
        label_y = (pos[u][1] + pos[v][1]) / 2
        edge_label = data['relationship']
        plt.text(label_x, label_y, edge_label, fontsize=10,
                 color='black', ha='center', va='center')
    else:  # multiple edges between u and v TODO: update to if-elif-else to include orphan nodes
        # Determine the layout between the x-axis and the line segment from u to v:
        #
        #        v
        #       /|
        #      / |
        #     /  | angle theta = arctan(vy-uy, vx-ux)
        # u -|----------------> x-axis
        #
        dx = pos[v][0] - pos[u][0]
        dy = pos[v][1] - pos[u][1]
        # Get the angle between the x-axis and uv line:
        theta = np.arctan2(dy, dx)

        edge_list = []  # capture edges with updated start & target coordinates
        for i in range(num_edges):
            # Calculate adjusted start and end positions for the edge
            # such that they begin and end at the node edges, not at node center points
            ux = pos[u][0]
            uy = pos[u][1]
            vx = pos[v][0]
            vy = pos[v][1]

            edge_list.append((u, v, {'start_pos': (ux, uy),
                                     'end_pos': (vx, vy)}))

            arc_curvature = 0.1 + (i * 0.3)
            graph.draw_networkx_edges(mixed_graph, pos, edgelist=edge_list,
                                      width=data['weight'],
                                      edge_color='gray',
                                      node_size=round_node_size,
                                      connectionstyle=f"arc3,rad={arc_curvature}",
                                      arrows=True)

            # Because multiple u-v edges will be curved using an arc curvature
            # as a function of the number of edges between u and v, the edge
            # labels should be place on the arc midpoint rather than the straight line.
            # The logic below is to find the perpendicular line between the arc apex
            # and the straight line midpoint, and the angle between the perpendicular
            # line and the x-axis at the arc midpoint in order to compute the label offset
            # from the straight line x and y coordinates to the arc midpoint coordinates:

            # Find the mid-point of the straight line u->v
            straight_mid_x = (ux + vx) / 2
            straight_mid_y = (uy + vy) / 2
            # Find the distance between the nodes u and v:
            distance_uv = np.sqrt((vx - ux) ** 2 + (vy - uy) ** 2)
            # Find the arc radius, given the curvature:
            arc_radius = 1 / arc_curvature
            # Find the height of the arc from the straight line midpoint to the apex
            arc_height = 0
            if arc_radius >= distance_uv / 2:  # if, for some reason, 2*arc_radius < distance_uv...
                arc_height = arc_radius - np.sqrt(arc_radius ** 2 - (distance_uv / 2) ** 2)

            # slope of straight line from u to v:
            straight_dx = vx - ux
            straight_dy = vy - uy
            slope_uv = straight_dy / straight_dx
            # slope of the perpendicular bisector from uv midpoint to arc's apex:
            slope_bisector = -1 / slope_uv

            # Get the angle between the x-axis and the perpendicular bisector:
            arc_theta = np.arctan(slope_bisector)

            # Arc apex positions are then shifted as a function of
            # the arc's height and arc's theta, as well as where the arc is located
            # in terms of the u and v layout: above or below the straight line (two cases)
            # and v and u are in different positions (two cases) == the other four cases
            # are redundant. This method is hit-and-miss, since networkx layout algorithms
            # may place arcs above or below despite curvature sign... TODO find a smarter solution
            apex_x = straight_mid_x
            apex_y = straight_mid_y
            if (vx > ux) and (vy > uy):
                # Case 1: vx > ux and vy > uy, arc is below the line UV,
                # subtract the arc height from y-coordinate of the straight line midpoint
                if arc_curvature < 0:
                    apex_x = straight_mid_x + arc_height * np.cos(arc_theta)
                    apex_y = straight_mid_y - arc_height * np.sin(arc_theta) - arc_height
                else:  # positive arc curvature means the arc will be drawn above the straight line
                    # Case 2: vx > ux and vy > uy, arc is above the line UV
                    apex_x = straight_mid_x - arc_height * np.cos(arc_theta)
                    apex_y = straight_mid_y + arc_height * np.sin(arc_theta) + arc_height
            elif (vx > ux) and (vy < uy):
                # Case 3: vx > ux but vy < uy, arc is below the line UV,
                # subtract the arc height from y-coordinate of the straight line midpoint
                if arc_curvature < 0:
                    apex_x = straight_mid_x - arc_height * np.cos(arc_theta)
                    apex_y = straight_mid_y - arc_height * np.sin(arc_theta) - arc_height
                else:  # positive arc curvature means the arc will be drawn above the straight line
                    # Case 4: vx > ux and vy > uy, arc is above the line UV
                    apex_x = straight_mid_x + arc_height * np.cos(arc_theta)
                    apex_y = straight_mid_y - arc_height * np.sin(arc_theta) - arc_height

            label_x = apex_x
            label_y = apex_y
            edge_label = data['relationship']

            plt.text(label_x, label_y, edge_label, fontsize=10,
                     color='black', ha='center', va='center')

plt.title("Mixed Graph Visualization with Curved Edges")
plt.axis('off')  # Turn off axis
plt.show()
