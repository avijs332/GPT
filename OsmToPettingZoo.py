import osmnx as ox
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from gymnasium import spaces
from pettingzoo import ParallelEnv

# Parameters
location = "Neve Tzedek, Tel Aviv, Israel"
num_agents = 3
display_time = 10  # Time in seconds before plot disappears

class OSMEnv(ParallelEnv):
    """PettingZoo Multi-Agent Environment using an OSM Graph."""

    metadata = {"render.modes": ["human"], "name": "osm_env", "render_mode": "human"}

    def __init__(self):
        self.G = ox.graph_from_place(location, network_type="drive")
        self.nodes = list(self.G.nodes)
        self.agents = [f"agent_{i}" for i in range(num_agents)]
        self.pos = {agent: np.random.choice(self.nodes) for agent in self.agents}
        self.trails = {agent: [self.pos[agent]] for agent in self.agents}

        # Define action and observation spaces
        self.action_spaces = {agent: spaces.Discrete(10) for agent in self.agents}
        self.observation_spaces = {agent: spaces.Discrete(len(self.nodes)) for agent in self.agents}

    def reset(self, seed=None, options=None):
        """Resets agent positions and trails."""
        self.pos = {agent: np.random.choice(self.nodes) for agent in self.agents}
        self.trails = {agent: [self.pos[agent]] for agent in self.agents}
    
        observations = self.pos  # Initial observations
        info = {}  # Empty info dictionary (can be expanded later)
    
        return observations, info

    def step(self, actions):
        """Moves agents based on their chosen actions."""
        rewards = {agent: -1 for agent in self.agents}  # Default penalty per step
        dones = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        for agent in self.agents:
            current_node = self.pos[agent]
            neighbors = list(self.G.neighbors(current_node))

            if neighbors:
                action_index = min(actions[agent], len(neighbors) - 1)
                self.pos[agent] = neighbors[action_index]
                self.trails[agent].append(self.pos[agent])
                rewards[agent] = 1  # Reward for moving

        return self.pos, rewards, dones, infos

    def render(self):
        """Plots the OSM graph with agent trails."""
        fig, ax = ox.plot_graph(self.G, node_color="gray", edge_color="lightblue", show=False, close=False)
        
        # Define colors for agents
        colors = ['red', 'blue', 'green', 'purple', 'orange']

        for i, agent in enumerate(self.agents):
            # Get the trail of positions for the agent
            trail_x, trail_y = zip(*[(self.G.nodes[pos]['x'], self.G.nodes[pos]['y']) for pos in self.trails[agent]])
            ax.plot(trail_x, trail_y, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=5, label=f"{agent} Trail")
            
            # Get the current position and previous position
            current_pos = self.pos[agent]
            current_x = self.G.nodes[current_pos]['x']
            current_y = self.G.nodes[current_pos]['y']

            # Get the previous position for direction
            prev_pos = self.trails[agent][-2] if len(self.trails[agent]) > 1 else current_pos
            prev_x = self.G.nodes[prev_pos]['x']
            prev_y = self.G.nodes[prev_pos]['y']

            # Calculate the direction of the arrow (from the previous position to the current position)
            dx = current_x - prev_x
            dy = current_y - prev_y

            # Create an arrow pointing in the direction of movement
            arrow = FancyArrowPatch(
                (current_x, current_y), 
                (current_x + dx * 0.001, current_y + dy * 0.001),  # Scale the arrow size
                mutation_scale=15,  # Adjust the size of the arrowhead
                color=colors[i % len(colors)],
                arrowstyle="->", 
                linewidth=2
            )

            ax.add_patch(arrow)


        # add a legend to differentiate agents
        ax.legend()

        plt.draw()
        plt.pause(display_time)  # Show plot for a few seconds
        plt.close(fig)

    def observe(self, agent):
        """Returns the observation for a specific agent."""
        return self.pos[agent]

    def close(self):
        """Cleanup function (not required here)."""
        pass

# Run the PettingZoo environment
env = OSMEnv()
result = env.reset()
print("Initial Observations:", result)

for _ in range(10):  # Move agents for 5 steps
    actions = {agent: np.random.randint(10) for agent in env.agents}
    obs, rewards, dones, infos = env.step(actions)
    print("Step Results:", obs, rewards)
    env.render()

