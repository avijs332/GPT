import os
import tensorflow as tf
from keras.models import load_model
from .agent import MAPPOAgent
from .osm_env import OSMEnv, max_steps_per_episode

def test(agent_class, num_agents, location ,central_stations, interest_points, state_size, max_action_size, model_paths, episodes=1, show_plot=True, save_path=None):
    env = OSMEnv(location=location, central_stations=central_stations, interest_points=interest_points, num_agents=num_agents)
    agent = agent_class(state_size, max_action_size, num_agents, env.node_to_index)

    # Check if model file is empty or unreadable
    for path in model_paths:
        try:
            if not os.path.exists(path):
                print(f"File does not exist: {path}")
            elif os.path.getsize(path) == 0:
                print(f"File is empty: {path}")
            else:
                with open(path, 'rb') as fileObject:
                    first_bytes = fileObject.read(128)
                    print(f"Successfully read file: {path}, first 128 bytes: {first_bytes[:32]} ...")
        except Exception as e:
            print(f"Error reading file {path}: {e}")

    print(model_paths)
    # Load trained models
    for i in range(num_agents):
        print(f"about to load model for agent {i} from {model_paths[i]}")
        agent.actor[i].load_weights(model_paths[i])
        print(f"Loaded model for agent {i} from {model_paths[i]}")

    for episode in range(episodes):
        obs, _ = env.reset()
        done = {agent_name: False for agent_name in env.agents}
        step_count = 0

        while not all(done.values()):
            # Get valid actions for each agent
            valid_actions_per_agent = {}
            active_states = {}
            active_masks = {}
            actions = {}

            for i, agent_name in enumerate(env.agents):
                valid_actions = env.get_valid_actions(i)
                valid_actions_per_agent[agent_name] = valid_actions

                if len(valid_actions) > 0 and not done[agent_name]:
                    action = agent.get_action(obs[agent_name], i, valid_actions)
                    actions[agent_name] = action
                else:
                    done[agent_name] = True
                    actions[agent_name] = -1

            next_obs, rewards, done, _ = env.step(actions, done, valid_actions_per_agent)

            for agent_name in env.agents:
                if not done[agent_name]:
                    obs[agent_name] = next_obs[agent_name]

            step_count += 1
            if step_count > max_steps_per_episode * 3:
                print("Breaking test loop, agent possibly stuck")
                break

        # Plot the trails
        # plot_episode(env, episode, save_path)

        return env