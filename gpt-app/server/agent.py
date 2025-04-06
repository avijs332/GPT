from tensorflow.keras.optimizers import Adam # type: ignore
from collections import deque
import tensorflow as tf
from tensorflow.keras.optimizers.schedules import ExponentialDecay # type: ignore
from tensorflow.keras.layers import Input, Dense, Softmax, Lambda # type: ignore
from tensorflow.keras.models import Model # type: ignore
import numpy as np

lr_schedule = ExponentialDecay(
    initial_learning_rate=0.0001,  # Initial LR
    decay_steps=1000,  # How often to decay
    decay_rate=0.96,  # Decay factor
    staircase=True  # Decay at discrete steps
)
actor_loss_history = {}

class MAPPOAgent:
    def __init__(self, state_size, max_action_size, num_agents, node_to_index):
        self.state_size = state_size
        self.max_action_size = max_action_size
        self.num_agents = num_agents
        self.node_to_index = node_to_index
        self.gamma = 0.9
        self.entropy_weight = 0.01  # Tweak this — try 0.01 to start
        self.memory = deque(maxlen=2000)
        self.actor = {i: self.build_actor() for i in range(num_agents)}
        self.critic = self.build_critic()
        self.critic_optimizer = Adam(learning_rate=lr_schedule)
        self.actor_optimizers = {i: Adam(learning_rate=lr_schedule) for i in range(num_agents)}

    def build_actor(self):
        inputs = Input(shape=(self.state_size,))
        mask_input = Input(shape=(self.max_action_size,))  # Action mask input

        x = Dense(256, activation='relu')(inputs)
        x = Dense(256, activation='relu')(x)
        logits = Dense(self.max_action_size)(x)  # Fixed output size

        masked_logits = Lambda(self.apply_mask)([logits, mask_input])  # Apply mask in a Lambda layer
        action_probs = Softmax()(masked_logits)

        model = Model(inputs=[inputs, mask_input], outputs=action_probs)
        model.compile(optimizer=Adam(learning_rate=lr_schedule), loss='categorical_crossentropy')
        return model

    def apply_mask(self, inputs):
        logits, mask_input = inputs
        return tf.where(mask_input > 0, logits, -1e9)  # Mask invalid actions

    def build_critic(self):
        inputs = Input(shape=(self.state_size * self.num_agents,))
        dense = Dense(256, activation='relu')(inputs)
        dense = Dense(256, activation='relu')(dense)
        value = Dense(1, activation='linear')(dense)
        model = Model(inputs=inputs, outputs=value)
        model.compile(optimizer=Adam(learning_rate=lr_schedule), loss='mse')
        return model


    def get_action(self, state, agent_idx, valid_actions):
      num_valid_actions = min(len(valid_actions), self.max_action_size)

      # Create mask
      mask = np.zeros(self.max_action_size)
      mask[:num_valid_actions] = 1

      state = np.expand_dims(state, axis=0)
      mask = np.expand_dims(mask, axis=0)

      # Predict action probabilities (masked)
      probs = self.actor[agent_idx].predict([state, mask], verbose=0)[0]

      # Slice to valid portion
      valid_probs = probs[:num_valid_actions]
      valid_probs /= np.sum(valid_probs)  # Normalize

      # Sample from valid action distribution
      action = np.random.choice(num_valid_actions, p=valid_probs)

      return action


    def store(self, state, actions, rewards, next_state, dones):
        self.memory.append((state, actions.copy(), rewards, next_state, dones))


    def train(self, get_valid_actions):
        if len(self.memory) < 64:
            return
        batch = list(self.memory)#[-64:]  # Take the last 64 entries in order
        states, actions, rewards, next_states, dones = zip(*batch)
        sorted_agents = sorted(rewards[0].keys())  # Get consistent order

        rewards = np.array([[r[agent] for agent in sorted_agents] for r in rewards])
        dones   = np.array([[d[agent] for agent in sorted_agents] for d in dones])
        states = np.vstack([np.concatenate([s[agent] for agent in sorted_agents]) for s in states])
        next_states = np.vstack([np.concatenate([s[agent] for agent in sorted_agents]) for s in next_states])

        values = self.critic.predict(states, verbose=0).reshape(-1, 1)
        next_values = self.critic.predict(next_states, verbose=0).reshape(-1, 1)
        advantages = rewards + self.gamma * next_values * (1 - dones) - values
        advantages = (advantages - np.mean(advantages)) / (np.std(advantages) + 1e-8)
        targets = rewards + self.gamma * next_values * (1 - dones)
        targets = np.clip(targets, -1.0, 1.0)
        self.critic.fit(states, targets, verbose=0)
        critic_loss = self.critic.evaluate(states, targets, verbose=0)
        print(f"Critic loss: {critic_loss:.4f}")


        actions_list = []
        for action_dict in actions:
            agent_actions = []
            for agent in sorted(action_dict.keys()):
                agent_actions.append(action_dict[agent])
            actions_list.append(agent_actions)

        actions_array = np.array(actions_list)

        for i in range(self.num_agents):
            start_col = i * self.state_size
            end_col = start_col + self.state_size
            agent_states = states[:, start_col:end_col]  # Extract the agent's state using slicing

            agent_masks = np.zeros((len(batch), self.max_action_size))  # Initialize with all zeros
            for j in range(len(batch)):
                valid_actions = get_valid_actions(i)  # Get valid actions for agent
                num_valid_actions = min(len(valid_actions), self.max_action_size)

                agent_masks[j, :num_valid_actions] = 1  # Mask valid actions

            agent_actions = actions_array[:, i]
            agent_actions_onehot = tf.one_hot(agent_actions, depth=self.max_action_size)
            agent_advantages = advantages[:, i]

            with tf.GradientTape() as tape:
                  probs = self.actor[i]([agent_states, agent_masks], training=True)
                  log_probs = tf.math.log(probs + 1e-8)

                  # Cross-entropy loss (policy gradient)
                  pg_loss = -tf.reduce_sum(agent_actions_onehot * log_probs, axis=1)

                  entropies = []
                  probs_np = probs.numpy()

                  for j in range(len(probs_np)):
                      num_valid_actions = int(np.sum(agent_masks[j]))  # Count valid actions
                      valid_probs = probs_np[j][:num_valid_actions]
                      valid_probs = valid_probs / np.sum(valid_probs + 1e-8)  # Normalize just in case
                      entropy_j = -np.sum(valid_probs * np.log(valid_probs + 1e-8))
                      entropies.append(entropy_j)

                  entropy = tf.convert_to_tensor(entropies, dtype=tf.float32)
                  print(f"Agent {i} avg entropy: {np.mean(entropy.numpy()):.4f}")


                  # Combine with advantage
                  weighted_loss = pg_loss * agent_advantages - self.entropy_weight * entropy

                  # Final loss (mean)
                  total_loss = tf.reduce_mean(weighted_loss)

                  if i not in actor_loss_history:
                    actor_loss_history[agent_name] = []
                  actor_loss_history[agent_name].append(total_loss.numpy())

              # Backprop
            grads = tape.gradient(total_loss, self.actor[i].trainable_variables)
            self.actor_optimizers[i].apply_gradients(zip(grads, self.actor[i].trainable_variables))
            self.entropy_weight = max(0.001, self.entropy_weight * 0.995)

        return critic_loss
