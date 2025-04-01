import tensorflow as tf
import matplotlib.pyplot as plt
import osmnx as ox
import os

from osm_env import OSMEnv
from agent import MAPPOAgent

def load_models(location, num_agents, state_size, action_size, node_to_index):
    """Loads the actor and critic models."""
    models_dir = f"trained_models/{location.replace(' ', '_')}_{num_agents}_agents"
    agent = MAPPOAgent(state_size, action_size, num_agents, node_to_index)
    for i in range(num_agents):
        agent.actor[i] = tf.keras.models.load_model(os.path.join(models_dir, f"actor_{i}.h5"))
    agent.critic = tf.keras.models.load_model(os.path.join(models_dir, "critic.h5"), custom_objects={'mse': tf.keras.losses.MeanSquaredError()}) #add custom objects
    print(f"Models loaded from {models_dir}")
    return agent


def test_and_plot_trajectories(location, num_agents, num_evaluation_episodes=5):
    """Tests the loaded models and plots the agent trajectories."""
    env = OSMEnv() #create the enviornment.
    agent = load_models(location, num_agents, 2, 8, env.node_to_index) #load the models
    all_trails = {agent_name: [] for agent_name in env.agents} #create dictionary to hold all trails.

    for episode in range(num_evaluation_episodes):
        obs, _ = env.reset()
        done = {agent_name: False for agent_name in env.agents}
        while not all(done.values()):
            actions = {}
            for i, agent_name in enumerate(env.agents):
                action, _ = agent.act(obs[agent_name], i)
                actions[agent_name] = action
            next_obs, rewards, done, _ = env.step(actions)
            obs = next_obs
            for agent_name in env.agents:
                all_trails[agent_name].append(env.pos[agent_name])

    # Plot the trajectories
    fig, ax = ox.plot_graph(env.G, node_color="gray", edge_color="lightblue", show=False, close=False)
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    for i, agent_name in enumerate(env.agents):
        trail_x, trail_y = zip(*[(env.G.nodes[pos]['x'], env.G.nodes[pos]['y']) for pos in all_trails[agent_name]])
        ax.plot(trail_x, trail_y, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=5)
    plt.title(f"Trajectories for {location}, {num_agents} agents")
    plt.show()
    plt.close(fig)

# Example usage
# location = "Neve Tzedek, Tel Aviv, Israel"
# num_agents = 3
# test_and_plot_trajectories(location, num_agents)