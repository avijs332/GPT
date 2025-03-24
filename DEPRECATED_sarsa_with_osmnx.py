import numpy as np
import random
import networkx as nx
import osmnx as osmUtils
import matplotlib.pyplot as plt

# Load graph for Tel Aviv (you can change it to another city or place if needed)
full_graph = osmUtils.graph_from_place("Neve Tzedek, Tel Aviv, Israel", network_type="drive")

edges = osmUtils.graph_to_gdfs(full_graph, nodes=False)

# Filter the edges based on 'highway=residential'
residential_edges = edges[edges['highway'] == 'residential']

uIndexes = residential_edges.index.get_level_values('u').to_list()
vIndexes = residential_edges.index.get_level_values('v').to_list()

# Extract the nodes connected by residential edges
residential_nodes = list(set(uIndexes).union(set(vIndexes)))

print(len(residential_nodes))

# Get the nodes as a GeoDataFrame
all_nodes = osmUtils.graph_to_gdfs(full_graph, edges=False)

# Filter only the residential nodes
graph = full_graph.subgraph(residential_nodes).copy()
nodes = all_nodes[all_nodes.index.isin(residential_nodes)]

# Add random 'interest' values for each node
nodes['interest'] = np.random.randint(1, 11, size=len(nodes))
nodes[''] = 0

def plot_graph(G, figure_title=None, print_shortest_path=False, src_node=None, filename=None,
               added_edges=None, node_size=150, edge_width=1, font_size=5):
    """
    Function to plot the graph and optionally highlight paths and nodes.

    Parameters:
    - G: NetworkX graph
    - figure_title: Title for the plot
    - print_shortest_path: Whether to print and highlight the shortest path
    - src_node: Node to highlight as the start node (if any)
    - filename: Optional filename to save the plot
    - added_edges: Edges to highlight (e.g., the current path in SARSA)
    - pause: Whether to pause the plot to allow visualization
    - node_size: Size of nodes (default: 300)
    - edge_width: Width of the edges (default: 2)
    - font_size: Font size for labels and edge labels (default: 12)
    """



    # Clear any previous plots
    plt.close()
    fig = plt.figure(figsize=(10, 8))  # Set figure size for better readability

    # Set the title of the plot
    if figure_title is None:
        plt.title("Graph Visualization")
    else:
        plt.title(figure_title)

    # Get the positions of the nodes (this can be customized for different layouts)
    pos = nx.kamada_kawai_layout(G)


    min_value = min(nodes['interest'])
    max_value = max(nodes['interest'])

    smoothed_values = [np.sqrt(value) for value in nodes['interest']]  # Apply square root
    normalized_values = [(value - np.sqrt(min_value)) / (np.sqrt(max_value) - np.sqrt(min_value)) for value in smoothed_values]

    cmap = plt.cm.Greys  # You can change this to any matplotlib colormap
    node_colors = [cmap(value) for value in normalized_values]

    # Draw the graph with nodes, edges, and labels
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=node_colors, edgecolors='black')
    nx.draw_networkx_edges(G, pos, width=edge_width, alpha=0.8, edge_color='black')
    nx.draw_networkx_labels(G, pos, font_size=font_size, font_color='black')

    # If we need to highlight a start node (e.g., for SARSA exploration), color it differently
    if src_node is not None:
        nx.draw_networkx_nodes(G, pos, nodelist=[src_node], node_size=node_size, node_color='green', edgecolors='black')

    legend_elements = []
    # Highlight added edges (e.g., the current path from SARSA algorithm) in red
    if added_edges is not None:
        for agent_id in range(num_agents):
            color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            legend_elements.append(Line2D([0], [0], marker='o', color=color, label=f"Agent {agent_id + 1}", lw=0,
                          markerfacecolor=color, markersize=10))

            nx.draw_networkx_edges(G, pos, edgelist=list(zip(agent_paths[agent_id][:-1], agent_paths[agent_id][1:])), width=2, edge_color=color, alpha=0.7)

    # Optionally print the shortest path from every node to the target (node 0 in this case)
    if print_shortest_path:
        target_node = 0
        for node in G.nodes():
            shortest_path = nx.dijkstra_path(G, node, target_node)
            print(f"Shortest path from node {node} to node {target_node}: {shortest_path}")
            added_edges += list(zip(shortest_path, shortest_path[1:]))

    # Draw edge labels with weights (i.e., distances)
    edge_labels = nx.get_edge_attributes(G, 'length')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=[], font_size=font_size)

    # If a filename is provided, save the figure to that file
    if filename is not None:
        plt.savefig(filename, bbox_inches='tight')

    # Show the plot and optionally pause
    ax = plt.gca()
    ax.legend(handles=legend_elements, loc='upper right')
    plt.show()

    # Convert to image (for use in video generation, for example)
    fig.canvas.draw()  # This draws the figure on the canvas

    # Get the RGBA data from the canvas as a numpy array
    img = np.array(fig.canvas.buffer_rgba())

    # Return the image
    return img

import pickle
from google.colab import drive

drive.mount('/content/drive', force_remount=True)

# Initialize Q-table or load it
try:
    with open('/content/drive/MyDrive/sarsa_model.pkl', 'rb') as f:
        print("Loaded existing model.")

        loaded_model = pickle.load(f)

        Q_table = loaded_model['Q_table']
        alpha = loaded_model['alpha']
        gamma = loaded_model['gamma']
        epsilon = loaded_model['epsilon']
        epsilon_decay = loaded_model['epsilon_decay']
        num_episodes = loaded_model['num_episodes']
        weights = loaded_model['weights']
        num_agents = loaded_model['num_agents']
        agent_Q_tables = loaded_model['agent_Q_tables']

except FileNotFoundError:
    print("No saved model found, starting fresh.")

    # Initialize Q-table: each state (node) has an entry for each possible action (neighboring node)
    Q_table = {}
    for node in nodes.index:
        Q_table[node] = {}
        for neighbor in graph.neighbors(node):
            Q_table[node][neighbor] = 0  # Initialize Q-values to 0

    # SARSA Hyperparameters
    alpha = 0.3  # Learning rate
    gamma = 0.9  # Discount factor
    epsilon = 0.6  # Exploration rate
    epsilon_decay = 0.9995
    num_episodes = 1000  # Number of episodes for training
    weights = {
                'shorter_path': 0.4,
                'unique_stations': -1.0,
                'interest_value': 0.5,
                'distance_value': 0.2
            }
    num_agents = 4  # Number of agents
    agent_Q_tables = [{node: {neighbor: 0 for neighbor in graph.neighbors(node)} for node in nodes.index} for _ in range(num_agents)]

print(alpha, gamma, epsilon, epsilon_decay, num_episodes, weights)
print(Q_table)
print(agent_Q_tables)