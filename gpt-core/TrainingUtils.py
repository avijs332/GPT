import matplotlib.pyplot as plt
import osmnx as ox
from keras.models import load_model
import os

def plot_metrics(total_rewards, episode_lengths, per_agent_rewards):
    episodes = range(1, len(total_rewards) + 1)

    plt.figure(figsize=(16, 6))

    plt.subplot(1, 3, 1)
    plt.plot(episodes, total_rewards, label='Total Reward', color='black')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Total Reward Over Time')
    plt.legend()

    plt.subplot(1, 3, 2)
    for agent, rewards in per_agent_rewards.items():
        plt.plot(episodes, rewards, label=agent)
    plt.xlabel('Episode')
    plt.ylabel('Per-Agent Reward')
    plt.title('Reward Per Agent')
    plt.legend()

    # Episode length
    plt.subplot(1, 3, 3)
    plt.plot(episodes, episode_lengths, label='Episode Length', color='purple')
    plt.xlabel('Episode')
    plt.ylabel('Length')
    plt.title('Episode Length Over Time')
    plt.legend()

    plt.tight_layout()
    plt.show()

def save_models(agent, location, num_agents):
    models_dir = f"trained_models/{location.replace(' ', '_')}_{num_agents}_agents"
    os.makedirs(models_dir, exist_ok=True) #create directory if it doesnt exist.
    for i in range(agent.num_agents):
        agent.actor[i].save(os.path.join(models_dir, f"actor_{i}.keras"))
    agent.critic.save(os.path.join(models_dir, "critic.keras"))
    print(f"Models saved to {models_dir}")

def load_models(agent, location, num_agents):
    models_dir = f"trained_models/{location.replace(' ', '_')}_{num_agents}_agents"

    for i in range(num_agents):
        actor_path = os.path.join(models_dir, f"actor_{i}.keras")
        if os.path.exists(actor_path):
            agent.actor[i] = load_model(actor_path)
        else:
            print(f"Actor model not found at {actor_path}")

    critic_path = os.path.join(models_dir, "critic.keras")
    if os.path.exists(critic_path):
        agent.critic = load_model(critic_path)
    else:
        print(f"Critic model not found at {critic_path}")

    print(f"Models loaded from {models_dir}")


def plot_episode(env, episode, save_path=None):
    fig, ax = ox.plot_graph(env.G, node_color="gray", edge_color="lightblue", show=False, close=False)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'pink', 'yellow', 'black', 'white', 'brown']

    # Plot each agent's route
    for i, agent_name in enumerate(env.agents):
        trail_x, trail_y = zip(*[(env.G.nodes[pos]['x'], env.G.nodes[pos]['y']) for pos in env.trails[agent_name]])
        ax.plot(trail_x, trail_y, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=5, label=f'{agent_name}')

    station_x = [env.G.nodes[station]['x'] for station in env.placed_stations]
    station_y = [env.G.nodes[station]['y'] for station in env.placed_stations]
    ax.scatter(station_x, station_y, c='gold', edgecolors='black', s=120, marker='*', label='Placed Stations', zorder=5)

    central_station_x = [env.G.nodes[station]['x'] for station in env.central_stations_set]
    central_station_y = [env.G.nodes[station]['y'] for station in env.central_stations_set]
    ax.scatter(central_station_x, central_station_y, c='pink', edgecolors='black', s=120, marker='*', label='Central Stations', zorder=5)

    central_station_x = [env.G.nodes[station]['x'] for station in env.interest_points]
    central_station_y = [env.G.nodes[station]['y'] for station in env.interest_points]
    ax.scatter(central_station_x, central_station_y, c='green', edgecolors='black', s=120, marker='*', label='Interest Points', zorder=5)

    plt.title(f"Episode {episode + 1}")
    ax.legend()

    if save_path:
        filename = f"{save_path}_ep{episode + 1}.png"
        plt.savefig(filename)
        print(f"Saved image to {filename}")

    plt.show()
    plt.close(fig)