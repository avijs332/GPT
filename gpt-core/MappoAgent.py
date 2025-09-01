import keras
import tensorflow as tf
import numpy as np
from keras.layers import Input, Dense, Softmax
from keras.models import Model
from keras.optimizers import Adam
from collections import deque

from keras.src.optimizers.schedules import ExponentialDecay

from ApplyMask import ApplyMask

lr_schedule = ExponentialDecay(
    initial_learning_rate=0.0004,
    decay_steps=2000,
    decay_rate=0.965,
    staircase=False
)

class MAPPOAgent:
    def __init__(self, state_size, max_action_size, num_agents, node_to_index, lr_schedule=0.001):
      self.state_size = state_size
      self.max_action_size = max_action_size
      self.num_agents = num_agents
      self.node_to_index = node_to_index

      # PPO hyperparameters
      self.gamma = 0.99
      self.gae_lambda = 0.95
      self.clip_epsilon = 0.2  # PPO clipping parameter
      self.entropy_weight = 0.01
      self.value_loss_coeff = 0.5
      self.max_grad_norm = 0.5  # Gradient clipping

      # Training parameters
      self.ppo_epochs = 4  # Number of PPO update epochs per batch
      self.batch_size = 64
      self.trajectory_length = 128

      # Memory for storing trajectories
      self.memory = deque(maxlen=2000)
      self.current_trajectory = []

      self.actor = {i: self.build_actor() for i in range(num_agents)}
      self.critic = self.build_critic()


      if isinstance(lr_schedule, keras.optimizers.schedules.LearningRateSchedule) or isinstance(lr_schedule, float):
          self.critic_optimizer = Adam(learning_rate=lr_schedule)
          self.actor_optimizers = {i: Adam(learning_rate=lr_schedule) for i in range(num_agents)}
      else:
           print("Warning: lr_schedule is not a standard float or LearningRateSchedule. Using default learning rate 0.001.")
           self.critic_optimizer = Adam(learning_rate=0.001)
           self.actor_optimizers = {i: Adam(learning_rate=0.001) for i in range(num_agents)}

    def build_actor(self):
        inputs = Input(shape=(self.state_size,))
        mask_input = Input(shape=(self.max_action_size,))

        x = Dense(256, activation='relu')(inputs)
        x = Dense(256, activation='relu')(x)
        logits = Dense(self.max_action_size)(x)

        masked_logits = ApplyMask()([logits, mask_input])
        action_probs = Softmax()(masked_logits)

        model = Model(inputs=[inputs, mask_input], outputs=action_probs)
        return model

    def build_critic(self):
        inputs = Input(shape=(self.state_size * self.num_agents,))
        x = Dense(256, activation='relu')(inputs)
        x = Dense(256, activation='relu')(x)
        value = Dense(self.num_agents, activation='linear')(x)
        model = Model(inputs=inputs, outputs=value)
        return model

    def get_action_and_value(self, states, agent_masks, training=False):
        global_state = np.zeros(self.state_size * self.num_agents)

        for agent_idx in states.keys():
            if 0 <= agent_idx < self.num_agents:
                start_idx = agent_idx * self.state_size
                end_idx = start_idx + self.state_size
                global_state[start_idx:end_idx] = states[agent_idx]

        global_state = np.expand_dims(global_state, axis=0)

        all_values_batch = self.critic.predict(global_state, verbose=0)
        if all_values_batch.shape[0] > 0:
            all_values = all_values_batch[0]
        else:
            # Handle case where prediction returns empty (shouldn't happen with batch_size 1)
             all_values = np.zeros(self.num_agents)
             print("[Warning] Critic predict returned empty batch.")


        values = {agent_idx: all_values[agent_idx] for agent_idx in states.keys() if 0 <= agent_idx < self.num_agents}

        actions = {}
        action_probs = {}

        # Iterate through active agents by their original indices
        for agent_idx in states.keys():
            if 0 <= agent_idx < self.num_agents:
                state = np.expand_dims(states[agent_idx], axis=0)
                mask = np.expand_dims(agent_masks[agent_idx], axis=0)

                probs_batch = self.actor[agent_idx].predict([state, mask], verbose=0)
                if probs_batch.shape[0] > 0:
                    probs = probs_batch[0]
                else:
                     probs = np.zeros(self.max_action_size)
                     print(f"[Warning] Actor {agent_idx} predict returned empty batch.")


                action_probs[agent_idx] = probs.copy()

                num_valid_actions = int(np.sum(agent_masks[agent_idx]))
                if num_valid_actions > 0:
                    valid_probs = probs[:num_valid_actions]
                    valid_probs_sum = np.sum(valid_probs)
                    if valid_probs_sum > 1e-8: # Avoid division by near zero
                         valid_probs = valid_probs / valid_probs_sum
                    else:
                         # Handle case where probabilities are all zero
                         # This should ideally not happen if mask is correctly applied in the model
                         # As a fallback, sample uniformly from valid actions
                         valid_probs = np.ones(num_valid_actions) / num_valid_actions
                         print(f"Actor {agent_idx} had zero valid probabilities, sampling uniformly.")


                    sampled_valid_action_index = np.random.choice(num_valid_actions, p=valid_probs)

                    actions[agent_idx] = sampled_valid_action_index

                else:
                    # No valid actions for this agent
                    actions[agent_idx] = -1
                    print(f"[Warning] Agent {agent_idx} had no valid actions.")


        return actions, action_probs, values

    def store_transition(self, states, actions, rewards, action_probs, values, masks, dones):
        active_agents_indices = set(states.keys())
        if not (active_agents_indices == set(actions.keys()) == set(rewards.keys()) == set(action_probs.keys()) == set(values.keys()) == set(masks.keys()) == set(dones.keys())):
             print("Data dictionaries have mismatched agent indices in store_transition.")
             # Filter keys to only include agents present in all dictionaries
             common_agents = active_agents_indices.intersection(actions.keys(), rewards.keys(), action_probs.keys(), values.keys(), masks.keys(), dones.keys())
             states = {i: states[i] for i in common_agents}
             actions = {i: actions[i] for i in common_agents}
             rewards = {i: rewards[i] for i in common_agents}
             action_probs = {i: action_probs[i] for i in common_agents}
             values = {i: values[i] for i in common_agents}
             masks = {i: masks[i] for i in common_agents}
             dones = {i: dones[i] for i in common_agents}


        transition = {
            'states': states.copy(),
            'actions': actions.copy(),
            'rewards': rewards.copy(),
            'action_probs': action_probs.copy(),
            'values': values.copy(),
            'masks': masks.copy(),
            'dones': dones.copy()
        }
        self.current_trajectory.append(transition)

        # If trajectory is complete or max length reached, process it
        # Process if any agent is done OR if the trajectory length is reached
        if any(transition['dones'].values()) or len(self.current_trajectory) >= self.trajectory_length:
            # Ensure trajectory contains data before processing
            if self.current_trajectory:
                self.process_trajectory()
                self.current_trajectory = []
            else:
                 print("[Warning] current_trajectory is empty when trying to process.")


    def process_trajectory(self):
        if len(self.current_trajectory) == 0:
            return

        trajectory = self.current_trajectory.copy()

        # Compute GAE advantages and returns for the trajectory
        # Iterate through the trajectory backwards to compute GAE
        gae = {agent_idx: 0 for agent_idx in range(self.num_agents)}
        advantages = [{} for _ in range(len(trajectory))]
        returns = [{} for _ in range(len(trajectory))]

        for t in reversed(range(len(trajectory))):
            current_transition = trajectory[t]
            next_transition = trajectory[t+1] if t + 1 < len(trajectory) else None

            # Iterate through all possible agents (0 to num_agents-1)
            for agent_idx in range(self.num_agents):
                # Check if the agent was active in the current transition
                if agent_idx in current_transition['states']:
                    reward = current_transition['rewards'][agent_idx]
                    value = current_transition['values'][agent_idx]
                    done = current_transition['dones'][agent_idx]

                    if next_transition and agent_idx in next_transition['states'] and not next_transition['dones'][agent_idx]:
                        next_value = next_transition['values'][agent_idx]
                        next_non_terminal = 1.0
                    else:
                        next_value = 0.0
                        next_non_terminal = 0.0 if done else 1.0

                    delta = reward + self.gamma * next_value * next_non_terminal - value

                    gae[agent_idx] = delta + self.gamma * self.gae_lambda * next_non_terminal * gae[agent_idx]

                    advantages[t][agent_idx] = gae[agent_idx]
                    returns[t][agent_idx] = gae[agent_idx] + value # Return = Advantage + Value


        # Add advantages and returns to each transition in the trajectory
        for t in range(len(trajectory)):
             trajectory[t]['advantages'] = {agent_idx: adv for agent_idx, adv in advantages[t].items() if agent_idx in trajectory[t]['states']}
             trajectory[t]['returns'] = {agent_idx: ret for agent_idx, ret in returns[t].items() if agent_idx in trajectory[t]['states']}


        self.memory.extend(trajectory)


    def train(self, get_valid_actions):
        if len(self.memory) < self.batch_size:
            return

        batch_size = min(len(self.memory), self.batch_size * 4)
        batch_indices = np.random.choice(len(self.memory), batch_size, replace=False)
        batch = [self.memory[i] for i in batch_indices]

        batch_data = self.prepare_batch_data(batch, get_valid_actions)

        for epoch in range(self.ppo_epochs):
            critic_loss = self.train_critic_ppo(batch_data)
            actor_losses = self.train_actors_ppo(batch_data)

            if epoch == 0:  # Print only first epoch
                print(f"Critic loss: {critic_loss:.4f}")
                for i, loss in actor_losses.items():
                    print(f"Actor {i} loss: {loss:.4f}")

    def prepare_batch_data(self, batch, get_valid_actions):
      all_agent_indices = set()
      for transition in batch:
          all_agent_indices.update(transition['states'].keys())
      sorted_agents = sorted(all_agent_indices)

      global_states = []
      for transition in batch:
          global_state = np.zeros(self.state_size * self.num_agents)

          # Fill in states for active agents
          for agent_idx in transition['states'].keys():
              start_idx = agent_idx * self.state_size
              end_idx = start_idx + self.state_size
              global_state[start_idx:end_idx] = transition['states'][agent_idx]

          global_states.append(global_state)
      global_states = np.array(global_states)

      agent_data = {}
      for agent_idx in sorted_agents:
          # Extract data for this agent from all transitions that include this agent
          agent_states = []
          agent_actions = []
          agent_old_probs = []
          agent_advantages = []
          agent_returns = []

          for transition in batch:
              if agent_idx in transition['states']:
                  agent_states.append(transition['states'][agent_idx])
                  agent_actions.append(transition['actions'][agent_idx])
                  agent_old_probs.append(transition['action_probs'][agent_idx])
                  agent_advantages.append(transition['advantages'][agent_idx])
                  agent_returns.append(transition['returns'][agent_idx])

          # Skip if no data for this agent
          if len(agent_states) == 0:
              continue

          agent_states = np.array(agent_states)
          agent_actions = np.array(agent_actions)
          agent_old_probs = np.array(agent_old_probs)
          agent_advantages = np.array(agent_advantages)
          agent_returns = np.array(agent_returns)

          # Create masks
          agent_masks = np.zeros((len(agent_states), self.max_action_size))
          for j in range(len(agent_states)):
              valid_actions = get_valid_actions(agent_idx)
              num_valid_actions = min(len(valid_actions), self.max_action_size)
              agent_masks[j, :num_valid_actions] = 1

          agent_data[agent_idx] = {
              'states': agent_states,
              'actions': agent_actions,
              'old_probs': agent_old_probs,
              'advantages': agent_advantages,
              'returns': agent_returns,
              'masks': agent_masks
          }

      return {
          'global_states': global_states,
          'agent_data': agent_data,
          'sorted_agents': sorted_agents
      }

    def train_critic_ppo(self, batch_data):
        """Train critic with PPO-style updates"""
        global_states = batch_data['global_states']
        agent_data = batch_data['agent_data']

        # Find the minimum number of samples across all agents
        min_samples = min(len(data['returns']) for data in agent_data.values())

        if min_samples == 0:
            print("No samples available for critic training")
            return 0.0

        # Take only the first min_samples from each agent and global_states
        global_states_trimmed = global_states[:min_samples]

        returns = []
        for sample_idx in range(min_samples):
            sample_returns = np.zeros(self.num_agents)  # Initialize with zeros for all agents

            for agent_idx, data in agent_data.items():
                if sample_idx < len(data['returns']):
                    sample_returns[agent_idx] = data['returns'][sample_idx]

            returns.append(sample_returns)

        returns = np.array(returns)

        with tf.GradientTape() as tape:
            values = self.critic(global_states_trimmed, training=True)
            value_loss = tf.reduce_mean(tf.square(values - returns))

        # Apply gradients with clipping
        grads = tape.gradient(value_loss, self.critic.trainable_variables)
        grads, _ = tf.clip_by_global_norm(grads, self.max_grad_norm)
        self.critic_optimizer.apply_gradients(zip(grads, self.critic.trainable_variables))

        return value_loss.numpy()

    def train_actors_ppo(self, batch_data):
        actor_losses = {}

        for agent_idx in batch_data['agent_data'].keys():
            if agent_idx >= self.num_agents:
                print(f"Warning: Agent index {agent_idx} exceeds num_agents {self.num_agents}")
                continue

            data = batch_data['agent_data'][agent_idx]

            with tf.GradientTape() as tape:
                # Get current action probabilities
                current_probs = self.actor[agent_idx]([data['states'], data['masks']], training=True)

                # Get probabilities for taken actions
                actions_onehot = tf.one_hot(data['actions'], depth=self.max_action_size)
                old_action_probs = tf.reduce_sum(actions_onehot * data['old_probs'], axis=1)
                current_action_probs = tf.reduce_sum(actions_onehot * current_probs, axis=1)

                # PPO ratio and clipping
                ratio = current_action_probs / (old_action_probs + 1e-8)
                clipped_ratio = tf.clip_by_value(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon)

                # PPO loss
                policy_loss1 = ratio * data['advantages']
                policy_loss2 = clipped_ratio * data['advantages']
                policy_loss = -tf.reduce_mean(tf.minimum(policy_loss1, policy_loss2))

                # Entropy loss (only for valid actions)
                entropy_loss = 0
                for i in range(len(current_probs)):
                    num_valid = int(np.sum(data['masks'][i]))
                    if num_valid > 0:
                        valid_probs = current_probs[i][:num_valid]
                        valid_probs = valid_probs / (tf.reduce_sum(valid_probs) + 1e-8)
                        entropy_loss += -tf.reduce_sum(valid_probs * tf.math.log(valid_probs + 1e-8))

                if len(current_probs) > 0:
                        entropy_loss = entropy_loss / len(current_probs)

                # Total loss
                total_loss = policy_loss - self.entropy_weight * entropy_loss

            # Apply gradients with clipping
            grads = tape.gradient(total_loss, self.actor[agent_idx].trainable_variables)
            grads, _ = tf.clip_by_global_norm(grads, self.max_grad_norm)
            self.actor_optimizers[agent_idx].apply_gradients(zip(grads, self.actor[agent_idx].trainable_variables))

            actor_losses[agent_idx] = total_loss.numpy()

        return actor_losses

    def get_action(self, state, agent_idx, valid_actions):
        num_valid_actions = min(len(valid_actions), self.max_action_size)
        mask = np.zeros(self.max_action_size)
        mask[:num_valid_actions] = 1

        state = np.expand_dims(state, axis=0)
        mask = np.expand_dims(mask, axis=0)

        probs = self.actor[agent_idx].predict([state, mask], verbose=0)[0]
        valid_probs = probs[:num_valid_actions]
        valid_probs /= np.sum(valid_probs)

        action = np.random.choice(num_valid_actions, p=valid_probs)
        return action

    def store(self, state, actions, rewards, next_state, dones):
        self.store_transition(state, actions, rewards, next_state, dones)