from pettingzoo import ParallelEnv
import osmnx as ox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
location = "Neve Tzedek, Tel Aviv, Israel"
num_agents = 3
max_steps_per_episode = 100
num_episodes = 50
video_filename = "osm_env_training.mp4"

central_stations= [33617427]#, 412530001, 6427502028, 3985298559, 6154187420]
interest_points = {
            357491441: {'type': 'mall', 'grade': 10},
            1628415520: {'type': 'school', 'grade': 6},
            2268450648: {'type': 'park', 'grade': 8},
            4833025980: {'type': 'restaurant', 'grade': 7},
            7968522921: {'type': 'hospital', 'grade': 9},
            57046703: {'type': 'cafe', 'grade': 5}
          }

class OSMEnv(ParallelEnv):

    def __init__(self):
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
        self.central_stations=central_stations
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
        self.interest_points = interest_points
        self.visited_interest_points = {agent: set() for agent in self.agents}  # Track visited interest points

    def reset(self, seed=None, options=None):
      self.pos = {agent: random.choice(self.central_stations) for agent in self.agents} # start at a central point.
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
          return {agent: np.array([self.node_to_index[self.pos[agent]], len(self.visited_edges[agent])], dtype=np.float32)
                  for agent in self.agents}

    def reward_fn(self, current_node, next_node, agent, rewards):
        edge = tuple(sorted([current_node, next_node]))

        edge_length = self.edge_lengths.get(edge, 1)
        edge_time = self.edge_times.get(edge, 1)

        # Reward for moving towards a new road (scaled)
        rewards[agent] += min(edge_length, 50)

        # Smooth penalty for travel time
        travel_time_penalty = min(20, 0.1 * edge_time)
        rewards[agent] -= travel_time_penalty

        # Reward for covering more road distance (longer routes)
        rewards[agent] += self.get_total_distance_reward(agent)

        # Prevent Dead-Ends
        if self.is_dead_end(next_node):
            rewards[agent] -= 30  # Discourage dead-ends
            next_node = self.find_alternate_path(agent, current_node)  # Find escape route

        # Cycle detection (progressive penalty)
        if self.is_stuck_in_cycle(agent, current_node):
            cycle_penalty = max(-5 * self.count_cycle_repeats(agent), -50)
            rewards[agent] += cycle_penalty

        # Reward for covering new roads
        rewards[agent] += self.get_road_coverage_reward(agent)

        # Visiting stations (scaled reward)
        if self.pos[agent] in self.central_stations_set:
            if self.pos[agent] not in self.visited_stations[agent]:
                self.visited_stations[agent].add(self.pos[agent])
                rewards[agent] += 20 + 5 * len(self.visited_stations[agent])

        # Interest Point Reward (Scaled + Diminishing Returns)
        if self.pos[agent] in self.interest_points:  # Check if the agent is at an interest point
            interest_point = self.interest_points[self.pos[agent]]

            # If the agent has already visited this interest point, apply diminishing returns
            if self.pos[agent] not in self.visited_interest_points[agent]:
                # First time visit: No diminishing return
                rarity_factor = 1
                rewards[agent] += (interest_point['grade'] * 5) * rarity_factor / 10  # Max reward
                self.visited_interest_points[agent].add(self.pos[agent])  # Mark as visited
            else:
                # Diminishing returns for subsequent visits
                # Reward decreases as the agent visits the same point multiple times
                rarity_factor = max(1, 10 - len(self.visited_interest_points[agent]))  # Reward decreases with each visit
                rewards[agent] += (interest_point['grade'] * 5) * rarity_factor / 10  # Diminishing reward


        # Reward clipping
        rewards[agent] = max(-50, min(50, rewards[agent]))

        return rewards

    def get_road_coverage_reward(self, agent):
        covered_edges = len(self.visited_edges[agent])
        total_edges = len(self.G.edges)

        # More reward for first-time coverage, less for repeated coverage
        return (covered_edges / total_edges) * 50

    def get_total_distance_reward(self, agent):
      """Rewards agents for covering longer total distances in kilometers."""
      total_distance = sum(self.edge_lengths.get(tuple(sorted([self.trails[agent][i], self.trails[agent][i+1]])), 0)
                          for i in range(len(self.trails[agent]) - 1))
      return total_distance * 0.1  # Scale the reward to balance other rewards


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