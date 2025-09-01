from OSMEnv import OSMEnv
from MappoAgent import MAPPOAgent
import numpy as np
from TrainingUtils import load_models, plot_episode, plot_metrics, save_models
from consts import *

# experiment
experiment = experiments['beer_sheva']

num_agents= experiment['num_agents']
location = experiment['location']
central_stations = experiment['central_stations']
interest_points = experiment['interest_points']


print("Loading OSM graph...")
env = OSMEnv(location=location, central_stations=central_stations, interest_points=interest_points, num_agents=num_agents)
print("OSM graph loaded.")

state_size = 6
action_size = 8
total_reward_history = []
episode_length_history = []
critic_loss_history = []
per_agent_reward_history = {agent: [] for agent in env.agents}

agent = MAPPOAgent(state_size, action_size, num_agents, env.node_to_index)
print("Agent Initialized")

def start():
    for episode in range(num_episodes):
        obs, _ = env.reset()
        done = {agent_name: False for agent_name in env.agents}
        episode_reward = 0
        step_count = 0
        per_agent_rewards = {agent_name: 0 for agent_name in env.agents}

        while not all(done.values()):
            valid_actions_per_agent = {}
            active_states = {}
            active_masks = {}

            for i, agent_name in enumerate(env.agents):
                valid_actions = env.get_valid_actions(i)
                valid_actions_per_agent[agent_name] = valid_actions

                if not done[agent_name] and len(valid_actions) > 0:
                    active_states[i] = obs[agent_name]
                    mask = np.zeros(action_size)
                    num_valid = min(len(valid_actions), action_size)
                    mask[:num_valid] = 1
                    active_masks[i] = mask

            if len(active_states) == 0:
                break

            actions_mappo, action_probs, values = agent.get_action_and_value(
                active_states, active_masks, training=True
            )

            actions = {}
            for i, agent_name in enumerate(env.agents):
                if i in actions_mappo:
                    actions[agent_name] = actions_mappo[i]
                else:
                    actions[agent_name] = -1
                    done[agent_name] = True

            next_obs, rewards, done, _ = env.step(actions, done, valid_actions_per_agent)

            if len(active_states) > 0:
                rewards_indexed = {i: rewards[env.agents[i]] for i in active_states.keys()}
                dones_indexed = {i: done[env.agents[i]] for i in active_states.keys()}

                values_indexed = {i: values[i] for i in active_states.keys()}

                agent.store_transition(
                    states=active_states,
                    actions=actions_mappo,
                    rewards=rewards_indexed,
                    action_probs=action_probs,
                    values=values_indexed,
                    masks=active_masks,
                    dones=dones_indexed
                )

            # Update observations and rewards
            for i, agent_name in enumerate(env.agents):
                if not done[agent_name]:
                    obs[agent_name] = next_obs[agent_name]
                per_agent_rewards[agent_name] += rewards[agent_name]

            episode_reward += sum(rewards.values())
            step_count += 1

            if step_count > max_steps_per_episode * 3:
                print("Breaking loop, possible stuck")
                break

        agent.train(env.get_valid_actions)

        total_reward_history.append(episode_reward)
        episode_length_history.append(step_count)
        for agent_name in env.agents:
            per_agent_reward_history[agent_name].append(per_agent_rewards[agent_name])

        print(f"Episode {episode + 1}/{num_episodes}, Total Reward: {episode_reward:.2f}, Steps: {step_count}")
        for agent_name in env.agents:
          print(f"  {agent_name} reward: {per_agent_rewards[agent_name]:.2f}")

        if (episode + 1) % PLOT_EPISODE_INTERVAL == 0:
            plot_episode(env, episode)

        env.render(episode)


    env.save_video(video_filename)

if LOAD_PRETRAINED_MODELS:
    load_models(agent, location, num_agents)

start()
save_models(agent, location, num_agents)
plot_metrics(total_reward_history, episode_length_history, per_agent_reward_history)