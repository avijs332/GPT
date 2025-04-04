import random

from osm_env import OSMEnv
from agent import MAPPOAgent

def get_routes():
    model_paths = [f"./models/actor_{i}.h5" for i in range(3)]

    final_trail = predict(
        agent_class=MAPPOAgent,
        env_class=OSMEnv,
        num_agents=3,
        state_size=2,
        max_action_size=8,
        model_paths=model_paths,
        episodes=1,
        show_plot=True,
        save_path="test_route"  # will save as test_route_ep1.png
    )

def predict(agent_class, env_class, num_agents, state_size, max_action_size, model_paths, episodes=1):
    env = env_class()
    agent = agent_class(state_size, max_action_size, num_agents, env.node_to_index)

    # Load trained models
    for i in range(num_agents):
        agent.actor[i].load_weights(model_paths[i])
        print(f"Loaded model for agent {i} from {model_paths[i]}")

    for episode in range(episodes):
        obs, _ = env.reset()
        done = {agent_name: False for agent_name in env.agents}
        step_count = 0

        while not all(done.values()):
            actions = {}
            for i, agent_name in enumerate(env.agents):
                valid_actions = env.get_valid_actions(i)
                if len(valid_actions) > 0 and not done[agent_name]:
                    action = agent.get_action(obs[agent_name], i, valid_actions)
                    actions[agent_name] = action
                else:
                    done[agent_name] = True
                    actions[agent_name] = -1

            next_obs, rewards, done, _ = env.step(actions, done)

            for agent_name in env.agents:
                if not done[agent_name]:
                    obs[agent_name] = next_obs[agent_name]

            step_count += 1
            if step_count > 100 * 3: # max_steps_per_episode
                print("Breaking test loop, agent possibly stuck")
                break

        final_trail = {}
        for agent_name in env.agents:
            final_trail[agent_name] = [
                (env.G.nodes[pos]['y'], env.G.nodes[pos]['x'])  # Assuming 'y' is lat and 'x' is lng
                for pos in env.trails[agent_name]
            ]

        return final_trail


def transform_trails_to_lanes(final_trail):
    final_lanes = {}

    for i, (agent_name, route) in enumerate(final_trail.items(), start=1):
        # Convert route points to the required format
        formatted_route = [{"lat": lat, "lng": lng} for lat, lng in route]
        
        # Randomly select a few stops from the route
        num_stops = min(3, len(formatted_route))  # Choose up to 3 stops or less if the route is small
        stops = random.sample(formatted_route, num_stops)

        # Construct the final structure
        final_lanes[f"lane_{i}"] = {
            "stops": stops,
            "route": formatted_route
        }

    return final_lanes