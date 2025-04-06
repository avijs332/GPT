from pettingzoo import ParallelEnv
import osmnx as ox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Parameters
# location = "Neve Tzedek, Tel Aviv, Israel"
# num_agents = 3
# max_steps_per_episode = 100
# num_episodes = 50
# video_filename = "osm_env_training.mp4"

# central_stations= [33617427]#, 412530001, 6427502028, 3985298559, 6154187420]
# interest_points = {
#             357491441: {'type': 'mall', 'grade': 10},
#             1628415520: {'type': 'school', 'grade': 6},
#             2268450648: {'type': 'park', 'grade': 8},
#             4833025980: {'type': 'restaurant', 'grade': 7},
#             7968522921: {'type': 'hospital', 'grade': 9},
#             57046703: {'type': 'cafe', 'grade': 5}
#           }

max_steps_per_episode = 100
num_episodes = 50
video_filename = "osm_env_training.mp4"

def get_closest_node(G, points):
    result = {}

    for point in points:
        if point.osm_id in G.nodes:
            # Node exists, keep it
            result[point.osm_id] = { 'type': 'shit', 'grade': 10 }
        else:
            # Node not in graph, but we have coordinates
            nearest = ox.distance.nearest_nodes(G, X=point.lon, Y=point.lat)
            result[nearest] = { 'type': 'shit', 'grade': 10 }  # replace with nearest
    
    return result
class OSMEnv(ParallelEnv):

    def __init__(self, location, central_stations, interest_points, num_agents, run_type, initial_central_station=None):
        self.G = ox.graph_from_place(location, network_type="drive")
        self.nodes = list(self.G.nodes)
        self.node_to_index = {node: idx for idx, node in enumerate(self.nodes)}
        self.agents = [f"agent_{i}" for i in range(num_agents)]
        self.pos = {}
        self.trails = {}
        self.visited_edges = {}
        self.edge_lengths = {tuple(sorted([u, v])): self.G[u][v][0]['length'] for u, v in self.G.edges()}
        self.total_rewards = []
        self.episode_lengths = []
        self.frames = []  # Store frames for video
        self.edge_times = {}
        self.total_edge_length = sum(self.edge_lengths.values())
        self.central_stations= list(get_closest_node(self.G, central_stations).keys())
        if run_type == "train":
            self.initial_central_station=initial_central_station
        else:
          self.initial_central_station=[random.choice(self.central_stations)]
        if self.central_stations is None:
            self.central_stations = random.sample(self.nodes, 4)  # Select 4 random nodes
        self.central_stations_set = set(self.central_stations)
        self.visited_stations = {agent: set() for agent in self.agents}
        for u, v, data in self.G.edges(data=True):
            length = data.get('length', 100)  # Default length
            speed = data.get('maxspeed', 30)  # Default speed (km/h)
            if isinstance(speed, str): # if the speed is a string, then split the string and take the first number.
                speed = int(speed.split(' ')[0])
            self.edge_times[tuple(sorted([u, v]))] = length / (speed / 3.6) # calculate the time in seconds.
        self.interest_points = get_closest_node(self.G, interest_points)
        self.visited_interest_points = {agent: set() for agent in self.agents}  # Track visited interest points
      
    def reset(self, seed=None, options=None):
      self.pos = {agent: random.choice(self.initial_central_station) for agent in self.agents} # start at a central point.
      self.trails = {agent: [self.pos[agent]] for agent in self.agents}
      self.visited_edges = {agent: set() for agent in self.agents}
      self.visited_stations = {agent: set() for agent in self.agents}
      self.visited_interest_points = {agent: set() for agent in self.agents}
      self.total_rewards.append(0)
      self.episode_lengths.append(0)
      self.frames = []  # Reset frames for new episode
      observations = self._get_observations()
      return observations, {}

    def get_valid_actions(self, agent_name):
        current_node = self.pos[self.agents[agent_name]]  # Get current node of agent
        neighbors = list(self.G.neighbors(current_node))  # Get valid next nodes
        valid_actions = [self.node_to_index[n] for n in neighbors]  # Convert to indices

        return valid_actions

    def _get_observations(self):
        observations = {}
        num_nodes = self.G.number_of_nodes()
        num_edges = self.G.number_of_edges()

        for agent in self.agents:
            current_node = self.pos[agent]
            visited_edges = self.visited_edges[agent]

            # 1. Normalize current node index
            current_node_feature = self.node_to_index[current_node] / num_nodes

            # 2. Number of visited edges (normalized)
            visited_edges_feature = len(visited_edges) / num_edges if num_edges > 0 else 0.0

            # 3. Neighbor indices (average of normalized neighbor indices)
            neighbors = list(self.G.neighbors(current_node))
            if neighbors:
                neighbor_features = np.mean([
                    self.node_to_index[n] / num_nodes for n in neighbors
                ])
            else:
                neighbor_features = 0.0

            # 4. Shortest path distances to central stations (average, normalized)
            central_dists = []
            for station in self.central_stations:
                try:
                    dist = nx.shortest_path_length(self.G, current_node, station, weight='weight')
                except nx.NetworkXNoPath:
                    dist = num_nodes
                central_dists.append(dist / num_nodes)
            central_station_feature = np.mean(central_dists) if central_dists else 0.0

            # 5. Shortest path distances to interest points (average, normalized)
            poi_dists = []
            for poi in self.interest_points:
                try:
                    dist = nx.shortest_path_length(self.G, current_node, poi, weight='weight')
                except nx.NetworkXNoPath:
                    dist = num_nodes
                poi_dists.append(dist / num_nodes)
            poi_feature = np.mean(poi_dists) if poi_dists else 0.0

            # Final state vector
            state = np.array([
                current_node_feature,
                visited_edges_feature,
                neighbor_features,
                central_station_feature,
                poi_feature
            ], dtype=np.float32)

            observations[agent] = state

        return observations

    def reward_fn(self, current_node, next_node, agent, rewards):
        edge = tuple(sorted([current_node, next_node]))

        edge_length = self.edge_lengths.get(edge, 1)
        edge_time = self.edge_times.get(edge, 1)
        total_edges = len(self.G.edges)

        # === Normalize and scale each component ===

        # Edge reward (max 50m)
        edge_reward = min(edge_length, 50) / 50.0  # Range: 0 to 1
        rewards[agent] += edge_reward

        # Travel time penalty (max 20s)
        travel_time_penalty = min(0.1 * edge_time, 20) / 20.0  # Range: 0 to 1
        rewards[agent] -= travel_time_penalty

        # Distance-based reward
        total_distance = sum(self.edge_lengths.get(tuple(sorted([self.trails[agent][i], self.trails[agent][i+1]])), 0)
                            for i in range(len(self.trails[agent]) - 1))
        max_reasonable_distance = 1000  # meters
        distance_reward = min(total_distance, max_reasonable_distance) / max_reasonable_distance
        rewards[agent] += distance_reward

        # Cycle penalty (bounded to -1)
        if self.is_stuck_in_cycle(agent, current_node):
            cycle_penalty = max(-5 * self.count_cycle_repeats(agent), -50)
            rewards[agent] += cycle_penalty / 50.0  # Normalized to [-1, 0]

        # Dead-end penalty
        if self.is_dead_end(next_node):
            rewards[agent] -= 1.0  # Hard normalized penalty
            next_node = self.find_alternate_path(agent, current_node)

        # Road coverage reward
        coverage_reward = (len(self.visited_edges[agent]) / total_edges) * 0.5  # not * 1.0
        rewards[agent] += coverage_reward  # already normalized

        # Central station bonus
        if self.pos[agent] in self.central_stations_set:
            if self.pos[agent] not in self.visited_stations[agent]:
                self.visited_stations[agent].add(self.pos[agent])
                station_reward = (5 * len(self.visited_stations[agent])) / (5 * len(self.central_stations))
                rewards[agent] += station_reward

        # Interest Point Reward (grade 1-10 scaled to 0-1)
        if self.pos[agent] in self.interest_points:
          interest_point = self.interest_points[self.pos[agent]]
          grade = interest_point['grade']

          # Count how many agents have already visited this POI
          num_agents_visited = sum(
              1 for a in self.agents
              if self.pos[agent] in self.visited_interest_points[a]
          )

          # Scale down reward as more agents visit it
          base_reward = grade * 5
          scaled_reward = base_reward / (1 + num_agents_visited)  # e.g. /2 if one other agent already visited

          # Apply diminishing returns per agent (optional)
          if self.pos[agent] not in self.visited_interest_points[agent]:
              self.visited_interest_points[agent].add(self.pos[agent])
              rarity_factor = 1.0
          else:
              rarity_factor = max(1, 10 - len(self.visited_interest_points[agent]))

          normalized_reward = (scaled_reward * rarity_factor) / 50.0
          rewards[agent] += normalized_reward

        # === Final reward clip ===
        rewards[agent] = max(-1.0, min(1.0, rewards[agent]))
        return rewards

    def is_dead_end(self, node):
      """Returns True if the node is a dead-end (only one outgoing edge)."""
      neighbors = list(self.G.neighbors(node))
      return len(neighbors) == 1  # True if only one connection

    def find_alternate_path(self, agent, node):
      """Finds the last non-dead-end node to escape a dead-end."""
      for prev_node in reversed(self.trails[agent]):
          if not self.is_dead_end(prev_node):  # Find last valid node
              return prev_node
      return node  # If no way back, stay in place (rare case)

    def is_stuck_in_cycle(self, agent, current_node):
      """Detects if the agent is cycling through the same set of nodes."""
      trail = self.trails[agent]

      # If the last occurrence of the node is close in history, it's a cycle
      last_index = next((i for i, node in enumerate(reversed(trail)) if node == current_node), None)

      if last_index is not None and last_index < len(trail) // 2:
          return True  # The agent is repeating a recent cycle

      return False  # No detected cycle


    def count_cycle_repeats(self, agent):
        """Counts how many times the agent has been stuck in a cycle recently."""
        trail = self.trails[agent]
        cycle_counts = 0

        # Iterate over the trail to find repeated nodes (cycle occurrences)
        for i in range(len(trail) - 1):
            for j in range(i + 1, len(trail)):
                if trail[i] == trail[j]:  # If same node is found again, it's a cycle
                    cycle_counts += 1

        return cycle_counts


    def step(self, actions, dones):
      rewards = {agent: 0 for agent in self.agents}
      infos = {agent: {} for agent in self.agents}

      for i, agent in enumerate(self.agents):
          if dones[agent]:
              continue

          current_node = self.pos[agent]
          neighbors = list(self.G.neighbors(current_node))

          if not neighbors:
              dones[agent] = True
              continue

          valid_actions = [self.node_to_index[n] for n in neighbors]
          action_index = actions[agent]

          # Safety check
          if action_index < 0 or action_index >= len(valid_actions):
              print(f"[Warning] Agent {agent} selected invalid action index: {action_index}")
              dones[agent] = True
              continue

          selected_node_index = valid_actions[action_index]
          next_node = self.nodes[selected_node_index]  # Convert index back to node ID

          # Apply reward logic
          self.reward_fn(current_node, next_node, agent, rewards)

          # Update agent state
          self.pos[agent] = next_node
          self.trails[agent].append(next_node)
          self.total_rewards[-1] += rewards[agent]
          self.episode_lengths[-1] += 1

          # Optional: Mark edge as visited
          edge = tuple(sorted([current_node, next_node]))
          self.visited_edges[agent].add(edge)

          # End if arrived back at a different central station
          if next_node in self.central_stations_set and next_node != self.trails[agent][0]:
              dones[agent] = True

          # End if max steps reached
          if len(self.trails[agent]) >= max_steps_per_episode:
              dones[agent] = True

      # Global edge coverage reward (optional extra boost)
      all_edges = set().union(*[self.visited_edges[agent] for agent in self.agents])
      for agent in self.agents:
          rewards[agent] += 0.5 * (len(all_edges) - len(self.visited_edges[agent]))

      return self._get_observations(), rewards, dones, infos


    def render(self, mode="human"):
        fig, ax = ox.plot_graph(self.G, node_color="gray", edge_color="lightblue", show=False, close=False)
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        for i, agent in enumerate(self.agents):
            trail_x, trail_y = zip(*[(self.G.nodes[pos]['x'], self.G.nodes[pos]['y']) for pos in self.trails[agent]])
            ax.plot(trail_x, trail_y, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=5)
        if mode == "human":
            plt.draw()
            plt.pause(0.01)
        # Save frame for video
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        self.frames.append(frame)
        plt.close(fig)
        return frame

    def save_video(self, filename):
        if not self.frames:
            print("No frames to save!")
            return
        fig, ax = plt.subplots()
        def update(frame):
            ax.clear()
            ox.plot_graph(self.G, ax=ax, node_color="gray", edge_color="lightblue", show=False, close=False)
            colors = ['red', 'blue', 'green', 'purple', 'orange']
            for i, agent in enumerate(self.agents):
                trail_x, trail_y = zip(*[(self.G.nodes[pos]['x'], self.G.nodes[pos]['y']) for pos in self.trails[agent][:frame+1]])
                ax.plot(trail_x, trail_y, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=5)
            return ax,
        ani = FuncAnimation(fig, update, frames=len(self.frames), interval=100, blit=False)
        ani.save(filename, writer='ffmpeg', fps=10)
        plt.close(fig)
        print(f"Video saved as {filename}")