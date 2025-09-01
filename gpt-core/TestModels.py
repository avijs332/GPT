from MappoAgent import MAPPOAgent 
import tensorflow as tf
from OSMEnv import OSMEnv
import os
from TrainingUtils import plot_episode
from consts import *
import keras

def load_models(location, num_agents, state_size, action_size, node_to_index):
    models_dir = f"trained_models/{location.replace(' ', '_')}_{num_agents}_agents"
    agent = MAPPOAgent(state_size, action_size, num_agents, node_to_index)
    for i in range(num_agents):
        agent.actor[i] = keras.models.load_model(os.path.join(models_dir, f"actor_{i}.h5"))
    agent.critic = keras.models.load_model(os.path.join(models_dir, "critic.h5"), custom_objects={'mse': tf.keras.losses.MeanSquaredError()}) #add custom objects
    print(f"Models loaded from {models_dir}")
    return agent

def test(agent_class, num_agents, location ,central_stations, interest_points, state_size, max_action_size, model_paths, episodes=1, show_plot=True, save_path=None):
    env = OSMEnv(location=location, central_stations=central_stations, interest_points=interest_points, num_agents=num_agents)
    agent = agent_class(state_size, max_action_size, num_agents, env.node_to_index)

    for i in range(num_agents):
        agent.actor[i].load_weights(model_paths[i])
        print(f"Loaded model for agent {i} from {model_paths[i]}")

    for episode in range(episodes):
        obs, _ = env.reset()
        done = {agent_name: False for agent_name in env.agents}
        step_count = 0

        while not all(done.values()):
            valid_actions_per_agent = {}
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
        plot_episode(env, episode, save_path)

        return env.trails


experiment = experiments['beer_sheva']

num_agents= experiment['num_agents']
location = experiment['location']
central_stations = experiment['central_stations']
interest_points = experiment['interest_points']
model_paths = [f"/content/trained_models/Old_City,_Beersheba,_Israel_6_agents/actor_{i}.keras" for i in range(num_agents)]

trails = test(
    agent_class=MAPPOAgent,
    num_agents=num_agents,
    location=location,
    central_stations=central_stations,
    interest_points=interest_points,
    state_size=6,
    max_action_size=8,
    model_paths=model_paths,
    episodes=1,
    show_plot=True,
    save_path="test_route"
)
print(trails)