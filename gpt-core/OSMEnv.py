from pettingzoo import ParallelEnv
import osmnx as ox
import random
from collections import deque
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import imageio.v2 as imageio
from consts import *


class OSMEnv(ParallelEnv):

    def __init__(self, location, central_stations, interest_points, num_agents):
        self.G = ox.graph_from_place(location, network_type="drive")
        self.nodes = list(self.G.nodes)
        self.node_to_index = {node: idx for idx, node in enumerate(self.nodes)}
        self.agents = [f"agent_{i}" for i in range(num_agents)]
        self.pos = {}
        self.trails = {}
        self.visited_edges = {agent: set() for agent in self.agents}
        self.edge_visit_counts = {}
        self.node_visit_counts = {agent: {} for agent in self.agents}
        self.agent_step_counts = {agent: 0 for agent in self.agents}
        self.edge_lengths = {tuple(sorted([u, v])): self.G[u][v][0]['length'] for u, v in self.G.edges()}
        self.total_rewards = []
        self.episode_lengths = []
        self.frames = []  # Store frames for video
        self.edge_times = {}
        self.total_edge_length = sum(self.edge_lengths.values())
        self.episode_count = 0
        self.agent_start_points = {}
        self.central_stations = central_stations
        if self.central_stations is None:
            self.central_stations = random.sample(self.nodes,
                                                  4)  # Select 4 random nodes if we dont get stations from the client
        self.central_stations_set = set(self.central_stations)
        self.visited_stations = {agent: set() for agent in self.agents}
        for u, v, data in self.G.edges(data=True):
            length = data.get('length', 100)
            speed = data.get('maxspeed', 50)
            if isinstance(speed, str):
                speed = int(speed.split(' ')[0])
            self.edge_times[tuple(sorted([u, v]))] = length / (speed / 3.6)  # calculate the time in seconds.
        self.interest_points = {}
        if interest_points:
            for osmid, data in interest_points.items():
                if osmid in self.G.nodes:
                    self.interest_points[osmid] = data
                else:
                    nearest = ox.distance.nearest_nodes(self.G, X=data['lon'], Y=data['lat'])
                    self.interest_points[nearest] = data
        self.visited_interest_points = {poi_node: 0 for poi_node in
                                        self.interest_points}
        self.potential_station_nodes = set(
            self.nodes) - self.central_stations_set  # Avoid placing on existing central stations
        self.placed_stations = set()
        self.station_placement_count = 0
        self.terminate_action_id = 9999  # A special high ID not used by real actions
        self.place_station_action_id = 10000
        self.global_step_count = 0
        self.min_global_steps_before_terminate = 30
        self.buffer_size = 1000
        self.min_samples = 50
        self.component_stats = {}
        self.ready_for_normalization = {}
        for agent in self.agents:
            self.component_stats[agent] = {
                'distance': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'coverage': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'cycle': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'dead_end': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'overlap': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'exploration': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'interest_point': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'crossing': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'proximity': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'multi_route': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'density_penalty': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'station_cost': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
                'total': {'values': deque(maxlen=self.buffer_size), 'mean': 0.0, 'std': 1.0},
            }
            self.ready_for_normalization[agent] = {comp: False for comp in self.component_stats[agent]}

    def reset(self, seed=None, options=None):
        self.episode_count += 1

        # Only shuffle agent start points every agent_start_refresh_rate episodes
        if self.episode_count % agent_start_refresh_rate == 1 or not self.agent_start_points:
            available_stations = self.central_stations.copy()
            random.shuffle(available_stations)
            self.agent_start_points = {}

            for agent in self.agents:
                if available_stations:
                    start_station = available_stations.pop()
                else:
                    start_station = random.choice(self.central_stations)
                self.agent_start_points[agent] = start_station

            print(f"Shuffled Agent Start Stations! Episode: {self.episode_count}")

        self.placed_stations = set()
        self.potential_station_nodes = set(self.nodes) - self.central_stations_set
        self.station_placement_count = 0

        self.pos = {agent: self.agent_start_points[agent] for agent in self.agents}
        self.trails = {agent: [self.pos[agent]] for agent in self.agents}
        self.visited_edges = {agent: set() for agent in self.agents}
        self.edge_visit_counts = {}
        self.node_visit_counts = {agent: {} for agent in self.agents}
        self.agent_step_counts = {agent: 0 for agent in self.agents}
        self.visited_interest_points = {poi_node: 0 for poi_node in
                                        self.interest_points}

        self.total_rewards.append(0)
        self.episode_lengths.append(0)

        observations = self._get_observations()
        return observations, {}

    def get_valid_actions(self, agent_index):
        current_node = self.pos[self.agents[agent_index]]
        agent_name = f"agent_{agent_index}"
        neighbors = list(self.G.neighbors(current_node))
        valid_actions = [self.node_to_index[n] for n in neighbors if
                         n not in self.trails[agent_name]]

        # Allow placing a station if not too many placed and current node is not already a station
        if (self.station_placement_count < max_number_stations and
                current_node not in self.placed_stations and
                current_node in self.potential_station_nodes):  # Only place on truly potential nodes
            valid_actions.append(self.place_station_action_id)

        if self.global_step_count < self.min_global_steps_before_terminate:
            return valid_actions

        return valid_actions + [self.terminate_action_id]  # Allow terminate after enough global steps

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

            # 6. Shortest path distances to ALL placed stations (average, normalized)
            placed_station_dists = []
            if self.placed_stations:
                for placed_station_node in self.placed_stations:
                    try:
                        dist = nx.shortest_path_length(self.G, current_node, placed_station_node, weight='weight')
                    except nx.NetworkXNoPath:
                        # If no path, treat as very far (normalized to 1.0 or num_nodes)
                        dist = num_nodes
                    placed_station_dists.append(dist / num_nodes)
                placed_station_feature = np.mean(placed_station_dists)
            else:
                placed_station_feature = 0.0


            state = np.array([
                current_node_feature,
                visited_edges_feature,
                neighbor_features,
                central_station_feature,
                poi_feature,
                placed_station_feature
            ], dtype=np.float32)

            observations[agent] = state

        return observations

    def update_component_stats(self, agent, component_name, value):
        if agent not in self.component_stats or component_name not in self.component_stats[agent]:
            return value

        stats = self.component_stats[agent][component_name]
        stats['values'].append(value)

        if len(stats['values']) >= self.min_samples:
            stats['mean'] = np.mean(stats['values'])
            stats['std'] = max(np.std(stats['values']), 1e-8)
            self.ready_for_normalization[agent][component_name] = True

        return value

    def normalize_component(self, agent, component_name, value):
        self.update_component_stats(agent, component_name, value)

        if self.ready_for_normalization[agent][component_name]:
            stats = self.component_stats[agent][component_name]
            normalized = (value - stats['mean']) / stats['std']
            return np.clip(normalized, -3.0, 3.0)
        else:
            return value

    def termination_reward(self, agent, rewards):
        if self.pos[agent] in self.central_stations_set and self.pos[agent] != self.trails[agent][0]:
            termination_reward = 1.0 * Weights["Success"]
        else:
            termination_reward = 1.0 * Weights["Fail"]

        rewards[agent] += termination_reward

        rewards[agent] = np.clip(rewards[agent], -10.0, 10.0)
        return rewards

    def coverage_reward(self, agent, from_node, to_node):
        edge = tuple(sorted([from_node, to_node]))
        num_visits = self.edge_visit_counts.get(edge, 0)
        reward = 1.0 / (1 + num_visits)

        return self.normalize_component(agent, 'coverage', reward)

    def distance_reward(self, agent, current_node, next_node):
        edge = tuple(sorted([current_node, next_node]))

        edge_length = self.edge_lengths.get(edge, 1000)  # meters
        edge_time = self.edge_times.get(edge, 300)  # seconds

        min_edge_length, max_edge_length = 1, 5000
        min_edge_time, max_edge_time = 30, 3600

        length_score = (edge_length - min_edge_length) / (max_edge_length - min_edge_length)
        time_score = (edge_time - min_edge_time) / (max_edge_time - min_edge_time)

        reward = Weights["TravelLength"] * length_score + Weights["TravelTime"] * time_score

        return self.normalize_component(agent, 'distance', reward)

    def cycle_panelty(self, agent, next_node):
        visits = self.node_visit_counts[agent].get(next_node, 0)
        max_penalty_visits = 5

        if visits == 0:
            raw_penalty = 0.0
        else:
            raw_penalty = -min(1.0, visits / max_penalty_visits)

        return self.normalize_component(agent, 'cycle', raw_penalty)

    def dead_end_panelty(self, agent, next_node):
        penalty = 1 if self.is_dead_end(next_node) else 0.0

        return self.normalize_component(agent, 'dead_end', penalty)

    def overlap_penalty(self, agent, next_edge):
        overlap_count = 0

        for other_agent, visited in self.visited_edges.items():
            if other_agent != agent and next_edge in visited:
                overlap_count += 1

        if overlap_count == 0:
            penalty = 0.0
        else:
            penalty = overlap_count * 0.5

        return self.normalize_component(agent, 'overlap', penalty)

    def interest_point_reward(self, agent):
        if self.pos[agent] not in self.interest_points:
            return self.normalize_component(agent, 'interest_point', 0.0)

        grade = self.interest_points[self.pos[agent]]['grade']
        num_agents_visited = self.visited_interest_points[self.pos[agent]]

        scaled_reward = grade / (1 + num_agents_visited)

        return self.normalize_component(agent, 'interest_point', scaled_reward)

    def path_crossing_reward(self, agent, next_node):
        crossing_count = 0

        for other_agent, visited in self.visited_stations.items():
            if other_agent != agent and next_node in visited:
                crossing_count += 1

        reward = 0 if crossing_count == 0 else 1.0 / crossing_count

        return self.normalize_component(agent, 'crossing', reward)

    def multi_bus_station_reward(self, agent, node_to_place_station):
        num_agents_passing_through = sum(
            1 for a in self.agents if node_to_place_station in self.trails[a]
        )
        raw_multi_route_reward = (num_agents_passing_through / len(self.agents)) * Weights["StationMultiRouteUse"]

        return self.normalize_component(agent, 'multi_route', raw_multi_route_reward)

    def proximity_station_reward(self, agent, node_to_place_station):
        poi_dists = []
        for poi_node in self.interest_points:
            try:
                dist = nx.shortest_path_length(self.G, node_to_place_station, poi_node, weight='length')
                poi_dists.append(dist)
            except nx.NetworkXNoPath:
                poi_dists.append(self.total_edge_length * 2)

        if poi_dists:
            avg_poi_dist = np.mean(poi_dists)
            normalized_avg_poi_dist = avg_poi_dist / (self.total_edge_length + 1e-6)
            raw_proximity_reward = (1 - normalized_avg_poi_dist) * Weights["StationProximityPOI"]
            return self.normalize_component(agent, 'proximity', raw_proximity_reward)
        else:
            return 0.0

    def density_station_reward(self, agent, node_to_place_station):
        min_dist_to_other_stations = float('inf')
        for existing_station in self.placed_stations:
            if existing_station != node_to_place_station:
                try:
                    dist = nx.shortest_path_length(self.G, node_to_place_station, existing_station, weight='length')
                    min_dist_to_other_stations = min(min_dist_to_other_stations, dist)
                except nx.NetworkXNoPath:
                    pass

        station_min_distance_threshold = 200  # meters
        if min_dist_to_other_stations < station_min_distance_threshold:
            penalty = ((min_dist_to_other_stations - station_min_distance_threshold) / station_min_distance_threshold) * \
                      Weights["StationDensityPenalty"]
        else:
            penalty = 0.0
        return self.normalize_component(agent, 'density_penalty', penalty)

    def station_placement_reward(self, agent, node_to_place_station):
        reward = 0.0
        reward += self.multi_bus_station_reward(agent, node_to_place_station)
        reward += self.proximity_station_reward(agent, node_to_place_station)
        reward += self.density_station_reward(agent, node_to_place_station)
        reward += self.normalize_component(agent, 'station_cost', Weights["StationCost"])

        return reward

    def exploration_reward(self, agent, next_node):
        reward_value = 0.0

        if next_node not in self.node_visit_counts[agent]:
            reward_value = 1.0 / (1.0 + EXPLORATION_DECAY_RATE * self.agent_step_counts[agent])

        return self.normalize_component(agent, 'exploration', reward_value)

    def reward_fn(self, current_node, next_node, agent, rewards, terminated=False, station_placed=False):
        if terminated:
            return self.termination_reward(agent, rewards)

        # Add station placement reward if this action was placing a station
        if station_placed:
            rewards[agent] = self.station_placement_reward(agent, current_node)  # current_node is the placed station
            return rewards

        reward_components = {
            'distance': self.distance_reward(agent, current_node, next_node),
            'cycle': self.cycle_panelty(agent, next_node),
            'dead_end': self.dead_end_panelty(agent, next_node),
            'interest_point': self.interest_point_reward(agent),
            'crossing': self.path_crossing_reward(agent, next_node),
            'exploration': self.exploration_reward(agent, next_node)
        }

        weighted_rewards = [
            reward_components['cycle'] * Weights["Cycle"],
            reward_components['dead_end'] * Weights["DeadEnd"],
            reward_components['distance'] * Weights["DistanceTimeAvg"],
            reward_components['interest_point'] * Weights["POI"],
            reward_components['crossing'] * Weights["Crossing"],
            reward_components['exploration'] * Weights["Exploration"],
        ]

        total_reward = sum(weighted_rewards)

        normalized_total = self.normalize_component(agent, 'total', total_reward)

        rewards[agent] = normalized_total

        return rewards

    def is_dead_end(self, node):
        neighbors = list(self.G.neighbors(node))
        return len(neighbors) == 1

    def is_stuck_in_cycle(self, agent, current_node):
        trail = self.trails[agent]

        # If the last occurrence of the node is close in history, it's a cycle
        last_index = next((i for i, node in enumerate(reversed(trail)) if node == current_node), None)

        if last_index is not None and last_index < len(trail) // 2:
            return True

        return False

    def count_cycle_repeats(self, agent):
        trail = self.trails[agent]
        cycle_counts = 0

        for i in range(len(trail) - 1):
            for j in range(i + 1, len(trail)):
                if trail[i] == trail[j]:
                    cycle_counts += 1

        return cycle_counts

    def step(self, actions, dones, valid_actions_per_agent):
        rewards = {agent: 0 for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        for i, agent in enumerate(self.agents):
            if dones[agent]:
                continue

            action_index = actions[agent]

            # Terminate action logic
            if valid_actions_per_agent[agent][action_index] == self.terminate_action_id:
                self.reward_fn(current_node=None, next_node=None, agent=agent, rewards=rewards, terminated=True)
                dones[agent] = True
                continue

            current_node = self.pos[agent]
            neighbors = list(self.G.neighbors(current_node))

            if valid_actions_per_agent[agent][action_index] == self.place_station_action_id:
                print('Placing a station')
                if current_node in self.potential_station_nodes:
                    self.placed_stations.add(current_node)
                    self.potential_station_nodes.remove(current_node)
                    self.station_placement_count += 1

                    self.reward_fn(current_node=current_node, next_node=None, agent=agent, rewards=rewards,
                                   station_placed=True)

                    self.trails[agent].append(current_node)
                    self.total_rewards[-1] += rewards[agent]
                else:
                    # Penalize if tried to place station on an invalid node (already a station, or not a potential node)
                    rewards[agent] -= 5.0 * Weights["Fail"]
                    self.total_rewards[-1] += rewards[agent]
                continue

            if not neighbors:
                dones[agent] = True
                continue

            valid_actions = valid_actions_per_agent[agent]

            if action_index < 0 or action_index >= len(valid_actions):
                print(f"[Warning] Agent {agent} selected invalid action index: {action_index} / {len(valid_actions)}")
                dones[agent] = True
                continue

            selected_node_index = valid_actions[action_index]
            next_node = self.nodes[selected_node_index]  # Convert index back to node ID

            self.reward_fn(current_node, next_node, agent, rewards)

            self.pos[agent] = next_node
            self.trails[agent].append(next_node)
            self.total_rewards[-1] += rewards[agent]
            self.episode_lengths[-1] += 1
            self.global_step_count += 1
            self.agent_step_counts[agent] += 1


            if next_node in self.interest_points:
                self.visited_interest_points[next_node] += 1

            edge = tuple(sorted([current_node, next_node]))
            self.visited_edges[agent].add(edge)
            self.edge_visit_counts[edge] = self.edge_visit_counts.get(edge, 0) + 1

            if next_node in self.node_visit_counts[agent]:
                self.node_visit_counts[agent][next_node] += 1
            else:
                self.node_visit_counts[agent][next_node] = 1

            self.visited_stations[agent].add(next_node)

            # End if arrived back at a different central station
            if next_node in self.central_stations_set and next_node != self.trails[agent][0]:
                dones[agent] = True

            # End if max steps reached
            if len(self.trails[agent]) >= max_steps_per_episode:
                dones[agent] = True


        all_edges = set().union(*[self.visited_edges[agent] for agent in self.agents])
        total_edges = len(all_edges) if len(all_edges) > 0 else 1
        for agent in self.agents:
            rewards[agent] += (len(self.visited_edges[agent]) / total_edges)

        return self._get_observations(), rewards, dones, infos

    def render(self, episode, mode="human"):
        fig, ax = ox.plot_graph(self.G, node_color="gray", edge_color="lightblue", show=False, close=False)
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'pink', 'yellow', 'black', 'brown']

        for i, agent_name in enumerate(self.agents):
            trail_x, trail_y = zip(
                *[(self.G.nodes[pos]['x'], self.G.nodes[pos]['y']) for pos in self.trails[agent_name]])
            ax.plot(trail_x, trail_y, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=5,
                    label=f'{agent_name}')

        station_x = [self.G.nodes[station]['x'] for station in self.placed_stations]
        station_y = [self.G.nodes[station]['y'] for station in self.placed_stations]
        ax.scatter(station_x, station_y, c='gold', edgecolors='black', s=120, marker='*', label='Placed Stations',
                   zorder=5)

        central_station_x = [self.G.nodes[station]['x'] for station in self.central_stations_set]
        central_station_y = [self.G.nodes[station]['y'] for station in self.central_stations_set]
        ax.scatter(central_station_x, central_station_y, c='pink', edgecolors='black', s=120, marker='*',
                   label='Central Stations', zorder=5)

        interest_pt_x = [self.G.nodes[station]['x'] for station in self.interest_points]
        interest_pt_y = [self.G.nodes[station]['y'] for station in self.interest_points]
        ax.scatter(interest_pt_x, interest_pt_y, c='green', edgecolors='black', s=120, marker='*',
                   label='Interest Points', zorder=5)

        ax.set_title(f"Episode {episode + 1}")
        ax.legend()

        plt.draw()
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()
        buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        frame = buf.reshape(h, w, 4)[..., :3].copy()
        self.frames.append(frame)
        plt.close(fig)

    def save_video(self, filename):
        if not self.frames or len(self.frames) == 0:
            print("No frames to save!")
            return

        imageio.mimsave(filename, self.frames, fps=6)
        print(f"Video saved as {filename} ({len(self.frames)} frames)")
