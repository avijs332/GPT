import random

from osm_env import OSMEnv
from agent import MAPPOAgent

state_size = 5
max_action_size = 8

def get_routes(city_name, bus_count, interest_points, start_locations):
    model_paths = [f"./models/actor_{i}.h5" for i in range(bus_count)]
    env = OSMEnv(location=city_name, central_stations=start_locations, interest_points=interest_points, num_agents=bus_count, run_type='test')
    agent = MAPPOAgent(state_size, max_action_size, bus_count, env.node_to_index)

    final_trail = predict(
        agent=agent,
        env=env,
        num_agents=bus_count,
        model_paths=model_paths,
        episodes=1
    )

    final_lanes = transform_trails_to_lanes(final_trail)
    print('=========')
    print(final_lanes)
    print('=========')
    final_lanes['city'] = final_lanes['lanes']['lane_1']['route'][0]

    return final_lanes


def predict(agent, env, num_agents, model_paths, episodes=1):
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
    final_lanes['lanes'] = {}

    for i, (agent_name, route) in enumerate(final_trail.items(), start=1):
        # Convert route points to the required format
        formatted_route = [{"lat": lat, "lng": lng} for lat, lng in route]
        
        # Randomly select a few stops from the route
        num_stops = min(3, len(formatted_route))  # Choose up to 3 stops or less if the route is small
        stops = random.sample(formatted_route, num_stops)
        # Construct the final structure
        final_lanes['lanes'][f"lane_{i}"] = {
            "stops": stops,
            "route": formatted_route
        }

    return final_lanes