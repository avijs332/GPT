import random
import osmnx as ox
from OSMEnv import OSMEnv
import matplotlib.pyplot as plt

def plot_graph_with_colored_nodes_subset(G, node_subset_ids,
                                         node_marker_color='red',
                                         node_label_color='black',
                                         node_label_fontsize=10,
                                         label_bbox_facecolor='white',
                                         label_bbox_alpha=0.9,
                                         node_label_fontweight='bold',
                                         label_offset_y=8,
                                         title=""
                                        ):

    fig, ax = ox.plot_graph(G, node_color="gray", edge_color="lightblue", show=False, close=False)

    subset_x = []
    subset_y = []
    for node_id in node_subset_ids:
        if node_id in G.nodes:
            data = G.nodes[node_id]
            x_coord = data.get('x', data.get('lon'))
            y_coord = data.get('y', data.get('lat'))
            if x_coord is not None and y_coord is not None:
                subset_x.append(x_coord)
                subset_y.append(y_coord)

                ax.annotate(str(node_id), (x_coord, y_coord),
                            textcoords="offset points", xytext=(0, label_offset_y),
                            ha='center', fontsize=node_label_fontsize,
                            color=node_label_color,
                            fontweight=node_label_fontweight,
                            zorder=4,
                            bbox=dict(facecolor=label_bbox_facecolor,
                                      alpha=label_bbox_alpha,
                                      edgecolor='none',
                                      boxstyle="round,pad=0.2")
                           )

    ax.scatter(subset_x, subset_y, color=node_marker_color, s=100, zorder=3)
    ax.set_title(title)
    plt.show()

num_agents = 10
location = "Old City, Beersheba, Israel"
central_stations= [367010181, 10285992984, 318177548, 566747901, 566749403, 2320421889, 566948027, 1880782316, 319076297, 5067373990,]
interest_points = {
                    566751227: {'type': 'mall', 'grade': 1},
                    1240318661: {'type': 'school', 'grade': 0.6},
                    1295251398: {'type': 'park', 'grade': 0.8},
                    5265723735: {'type': 'restaurant', 'grade': 0.7},
                    11230870752: {'type': 'hospital', 'grade': 0.9},
                    318178073: {'type': 'cafe', 'grade': 0.5},
                    734894851: {'type': 'mall', 'grade': 1},
                    566751244: {'type': 'school', 'grade': 0.6},
                    1731446290: {'type': 'park', 'grade': 0.8},
                    1295251423: {'type': 'restaurant', 'grade': 0.7},
}

env = OSMEnv(location=location, central_stations=[], interest_points=[], num_agents=num_agents)

# --- Plotting Random Nodes ---
points_per_plot = 20 # Number of random nodes to plot in each sample
num_random_plots = 1 # How many different sets of random nodes to show

all_graph_nodes = list(env.G.nodes())
num_total_nodes = len(all_graph_nodes)

if num_total_nodes == 0:
    print("The graph has no nodes to plot. Cannot select random nodes.")
else:
    print(f"\nPlotting {num_random_plots} random sets of {points_per_plot} nodes from the graph.")
    for i in range(num_random_plots):
        # Ensure we don't try to select more nodes than available
        num_nodes_to_sample = min(points_per_plot, num_total_nodes)

        # Randomly select 'num_nodes_to_sample' unique nodes from ALL nodes in the graph
        random_points = random.sample(all_graph_nodes, num_nodes_to_sample)
        central= [3684782944, 3761306917, 3715859182, 306543884, 3761279370, 306543861]
        poi = [286303784,281397946,309076045,281391220, 3758979801,286303775,306583303,281391326,305928367]
        plot_graph_with_colored_nodes_subset(
            env.G,
            central, # Pass the randomly selected subset
            node_marker_color='orange', # Use a distinct color for random nodes
            node_label_color='darkblue',
            node_label_fontsize=9,
            label_bbox_facecolor='yellow',
            label_bbox_alpha=0.7,
            title=f"Random Graph Nodes (Sample {i+1}): {len(central)} Points"
        )
        plot_graph_with_colored_nodes_subset(
            env.G,
            poi, # Pass the randomly selected subset
            node_marker_color='pink', # Use a distinct color for random nodes
            node_label_color='darkblue',
            node_label_fontsize=9,
            label_bbox_facecolor='pink',
            label_bbox_alpha=0.7,
            title=f"Random Graph Nodes (Sample {i+1}): {len(poi)} Points"
        )
    print("Finished plotting random nodes.")