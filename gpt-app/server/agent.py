from tensorflow.keras.optimizers import Adam # type: ignore
from collections import deque
import tensorflow as tf
from tensorflow.keras.optimizers.schedules import ExponentialDecay # type: ignore
from tensorflow.keras.layers import Input, Dense, Softmax, Lambda # type: ignore
from tensorflow.keras.models import Model # type: ignore
import numpy as np

lr_schedule = ExponentialDecay(
    initial_learning_rate=0.0005,  # Initial LR
    decay_steps=1000,  # How often to decay
    decay_rate=0.96,  # Decay factor
    staircase=True  # Decay at discrete steps
)

class MAPPOAgent:
    def __init__(self, state_size, max_action_size, num_agents, node_to_index):
        self.state_size = state_size
        self.max_action_size = max_action_size
        self.num_agents = num_agents
        self.node_to_index = node_to_index
        self.gamma = 0.9
        self.lr = 0.0005
        self.epsilon = 0.1
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
      """
      Returns the index into valid_actions list.
      So if valid_actions = [1234, 5678, 9012], and action=1, that means 5678.
      The environment will handle that mapping.
      """
      num_valid_actions = min(len(valid_actions), self.max_action_size)

      # Create mask (1 for valid, 0 for invalid)
      mask = np.zeros(self.max_action_size)
      mask[:num_valid_actions] = 1

      # Expand dims for model input
      state = np.expand_dims(state, axis=0)
      mask = np.expand_dims(mask, axis=0)

      # Epsilon-greedy
      if np.random.rand() < self.epsilon:
          action = np.random.choice(num_valid_actions)  # Random among valid
      else:
          probs = self.actor[agent_idx].predict([state, mask], verbose=0)[0]

          # Slice to valid part only
          valid_probs = probs[:num_valid_actions]

          # Normalize again just to be safe
          valid_probs /= np.sum(valid_probs)

          action = np.random.choice(num_valid_actions, p=valid_probs)

      # Decay epsilon
      self.epsilon = max(0.01, self.epsilon * 0.995)


      return action  # index into valid_actions


    def store(self, state, actions, rewards, next_state, dones):
        # print(state)
        self.memory.append((state, actions.copy(), rewards, next_state, dones))


    def train(self, get_valid_actions):
        if len(self.memory) < 64:
            return
        batch = list(self.memory)#[-64:]  # Take the last 64 entries in order
        states, actions, rewards, next_states, dones = zip(*batch)
        states = np.vstack([np.concatenate(list(s.values())) for s in states])
        next_states = np.vstack([np.concatenate(list(s.values())) for s in next_states])
        rewards = np.array([list(r.values()) for r in rewards])
        dones = np.array([list(d.values()) for d in dones])
        values = self.critic.predict(states, verbose=0).reshape(-1, 1)
        next_values = self.critic.predict(next_states, verbose=0).reshape(-1, 1)
        advantages = rewards + self.gamma * next_values * (1 - dones) - values
        targets = rewards + self.gamma * next_values * (1 - dones)
        self.critic.fit(states, targets, verbose=0)

        print('actions', actions)

        actions_list = []
        for action_dict in actions:
            agent_actions = []
            for agent in sorted(action_dict.keys()):
                agent_actions.append(action_dict[agent])
            actions_list.append(agent_actions)


        print(actions_list)
        actions_array = np.array(actions_list)

        for i in range(self.num_agents):
            start_col = i * 2  # Calculate the starting column for the agent's state
            end_col = start_col + 2  # Calculate the ending column for the agent's state
            agent_states = states[:, start_col:end_col]  # Extract the agent's state using slicing

            agent_masks = np.zeros((len(batch), self.max_action_size))  # Initialize with all zeros
            for j in range(len(batch)):
                valid_actions = get_valid_actions(i)  # Get valid actions for agent
                num_valid_actions = min(len(valid_actions), self.max_action_size)

                agent_masks[j, :num_valid_actions] = 1  # Mask valid actions

            agent_actions = actions_array[:, i]
            agent_actions = tf.one_hot(agent_actions, depth=self.max_action_size).numpy()
            agent_advantages = advantages[:, i]

            self.actor[i].fit([agent_states, agent_masks], agent_actions, sample_weight=agent_advantages, verbose=0)