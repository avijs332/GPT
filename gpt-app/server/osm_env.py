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
central_stations= [33617427, 412530001, 6427502028, 3985298559, 6154187420]


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
            if isinstance(speed, str): #if the speed is a string, then split the string and take the first number.
                speed = int(speed.split(' ')[0])
            self.edge_times[tuple(sorted([u, v]))] = length / (speed / 3.6) #calculate the time in seconds.

    def reset(self, seed=None, options=None):
      self.pos = {agent: random.choice(self.central_stations) for agent in self.agents} #start at a central point.
      self.trails = {agent: [self.pos[agent]] for agent in self.agents}
      self.visited_edges = {agent: set() for agent in self.agents}
      self.visited_stations = {agent: set() for agent in self.agents}
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

      edge_length = self.edge_lengths.get(edge)
      edge_time = self.edge_times.get(edge)

      # **Positive Reward for step Length**: Reward for traveling a longer distance
      step_length_reward = self.get_step_length_reward(edge_length)
      rewards[agent] += step_length_reward

      # **Penalty for Long Travel Times**: Lower penalty for long travel times
      travel_time_penalty = self.get_travel_time_penalty(edge_time)
      rewards[agent] -= travel_time_penalty

      # **Penalize Low Connectivity Nodes**: Discourage nodes with low connectivity
      connectivity_penalty = self.get_connectivity_penalty(next_node)
      rewards[agent] -= connectivity_penalty

      # **Cycle Detection**: Light penalty for cycles
      if self.is_stuck_in_cycle(agent, current_node, next_node):
          rewards[agent] -= 15  # Mild penalty for cycles, if needed

      # Normal visit reward or penalty for revisiting an edge
      if edge not in self.visited_edges[agent]:
          rewards[agent] += 15 / (1 + edge_length / 100)
          self.visited_edges[agent].add(edge)
      else:
          rewards[agent] -= 0.2  # Very small penalty for revisiting an edge

      #Reward for covering new roads (edges)**
      rewards[agent] += self.get_road_coverage_reward(agent)  # Reward for covering new road
      rewards[agent] += self.get_road_length_reward(agent)  # Reward for longer roads

      # Check for station visits
      if self.pos[agent] in self.central_stations_set:
        if self.pos[agent] not in self.visited_stations[agent]:
            self.visited_stations[agent].add(self.pos[agent])
            rewards[agent] += 50  # Reward for visiting a station
      # Check if all stations are visited
      all_stations_visited = all(len(self.visited_stations[agent]) == len(self.central_stations) for agent in self.agents)
      if all_stations_visited:
          for agent in self.agents:
              rewards[agent] += 200  # Large reward for visiting all stations


    def step(self, actions, dones):
        rewards = {agent: 0 for agent in self.agents}  # Start with 0 rewards to avoid overall negativity
        infos = {agent: {} for agent in self.agents}

        for agent in self.agents:
            #print(f"Agent: {agent_name}, Done: {done[agent_name]}")
            if dones[agent]:
              continue

            current_node = self.pos[agent]
            neighbors = list(self.G.neighbors(current_node))

            if neighbors:
                # print(f"neighbors for agent {agent} at node {current_node}")
                action = actions[agent]
                #print(f"Agent {agent} takes action {action}")
                # if action == -1:  # Ignore invalid actions
                #   continue
                next_node = neighbors[action]

                self.reward_fn(current_node, next_node, agent, rewards)

                # Update position and trail
                self.pos[agent] = next_node
                self.trails[agent].append(next_node)
                self.total_rewards[-1] += rewards[agent]
                self.episode_lengths[-1] += 1

            # Terminate episode if maximum length reached
            if len(self.trails[agent]) >= max_steps_per_episode:
                dones[agent] = True

        # Calculate global reward for visiting new edges (same as before)
        all_edges = set().union(*[self.visited_edges[agent] for agent in self.agents])
        for agent in self.agents:
            rewards[agent] += 0.5 * (len(all_edges) - len(self.visited_edges[agent]))

        return self._get_observations(), rewards, dones, infos

    def get_road_coverage_reward(self, agent):
        num_visited_edges = len(self.visited_edges[agent])
        total_edges = len(self.G.edges)
        if total_edges == 0:
          return 0
        return ((num_visited_edges / total_edges) * 100 )/20

    def get_road_length_reward(self, agent):
        """
        Reward the agent for longer road lengths (without penalizing travel time too much).
        A longer road indicates more exploration.
        """
        visited_length = 0
        for edge in self.visited_edges[agent]:
            visited_length += self.edge_lengths.get(edge, 0)
        if self.total_edge_length == 0:
            return 0
        return ((visited_length / self.total_edge_length) * 100)/20


    def get_step_length_reward(self, edge_length):
        # print(edge_length)
        return edge_length / 5  # Example: Reward 0.02 per unit of road length

    def get_travel_time_penalty(self, edge_time):
        """
        Penalize the agent for long travel times between stops, but reduce the penalty.
        We want to penalize inefficient paths, but not too severely.
        """
        return edge_time / 100  # Example: Penalize 0.02 per unit of edge length

    def get_connectivity_penalty(self, node):
        """
        Penalize nodes with low connectivity (fewer neighbors).
        A node with fewer neighbors is considered less efficient for bus routes.
        """
        return len(list(self.G.neighbors(node)))

    def is_stuck_in_cycle(self, agent, current_node, next_node, max_cycle_length=5):
        """
        Check if the agent is stuck in a cycle by revisiting nodes in a short window.
        We track the last few positions and check if the agent revisits a recent node.
        """
        # Track the last 'max_cycle_length' nodes in the agent's trail
        trail = self.trails[agent]
        if len(trail) > max_cycle_length:
            recent_nodes = trail[-max_cycle_length:]
        else:
            recent_nodes = trail  # If fewer than 'max_cycle_length' steps, use the whole trail

        # If the next node is in the recent history, it's a cycle
        if next_node in recent_nodes:
            return True  # The agent is stuck in a cycle

        return False  # The agent is not stuck in a cycle

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