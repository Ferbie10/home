import numpy as np
import random


class MinesweeperAgent:
    def __init__(self, height, width, num_mines, learning_rate=0.1, discount_factor=0.99, exploration_rate=1.0, exploration_decay_rate=0.001):
        self.height = height
        self.width = width
        self.num_mines = num_mines
        self.num_actions = 2
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay_rate = exploration_decay_rate

        # Initialize the Q-table as a dictionary
        self.q_table = {}

    def flatten_state(self, state):

        return tuple(cell for row in state for cell in row)

    def _initialize_state(self, state_key):
        state_key_str = str(state_key)
        self.q_table[state_key_str] = np.zeros(2)

    def _state_key_exists(self, state_key):
        state_key_str = str(state_key)
        return state_key_str in self.q_table

    def choose_action(self, state):
        # Explore with probability epsilon
        if random.uniform(0, 1) < self.exploration_rate:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            action = random.randint(0, 1)  # 0 for reveal, 1 for flag
            return row, col, action

        # Exploit with probability (1 - epsilon)
        else:
            state_key = self.flatten_state(state)
            state_key_str = str(state_key)

            if not self._state_key_exists(state_key):
                self._initialize_state(state_key)

            best_action_value = -np.inf
            best_action = None

            for row in range(self.height):
                for col in range(self.width):
                    for action in range(2):  # 0 for reveal, 1 for flag
                        action_key = row * self.width + col
                        action_value = self.q_table[state_key_str][action_key]

                        if action_value > best_action_value:
                            best_action_value = action_value
                            best_action = (row, col, action)

            return best_action

    def learn(self, state, action, reward, next_state):
        state_key = self.flatten_state(state)
        next_state_key = self.flatten_state(next_state)
        row, col, action_type = action

        # Initialize the state_key in q_table if it does not exist
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(
                (self.height, self.width, self.num_actions))

        current_q_value = self.q_table[state_key][row, col, action_type]

        # Initialize the next_state_key in q_table if it does not exist
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(
                (self.height, self.width, self.num_actions))

        next_max_q_value = np.max(self.q_table[next_state_key])
        new_q_value = current_q_value + self.learning_rate * \
            (reward + self.discount_factor * next_max_q_value - current_q_value)
        self.q_table[state_key][row, col, action_type] = new_q_value

    def decay_exploration_rate(self):
        self.exploration_rate = max(
            self.exploration_rate * (1 - self.exploration_decay_rate), 0.01)

    def save(self, filename):
        np.save(filename, self.q_table)

    def load(self, filename):
        # Load the Q-table from a file
        self.q_table = np.load(filename, allow_pickle=True).item()

    def update(self, state, action, reward, next_state):
        self.learn(state, action, reward, next_state)

    def action_to_index(self, action):
        row, col, action_type = action
        return action_type
    
