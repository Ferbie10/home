# minesweeper_agent.py
import numpy as np
import random


class MinesweeperAgent:
    def __init__(self, height, width, num_mines, learning_rate=0.1, discount_factor=0.99, exploration_rate=1.0, exploration_decay_rate=0.001):
        self.height = height
        self.width = width
        self.num_mines = num_mines

        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay_rate = exploration_decay_rate

        # Initialize the Q-table
        # 2 actions: reveal and flag
        self.q_table = np.zeros((height, width, 2))

    def choose_action(self, state):
        # Explore with probability epsilon
        if random.uniform(0, 1) < self.exploration_rate:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            action = random.randint(0, 1)  # 0 for reveal, 1 for flag
            return row, col, action

        # Exploit with probability (1 - epsilon)
        else:
            best_action_value = -np.inf
            best_action = None

            for row in range(self.height):
                for col in range(self.width):
                    for action in range(2):  # 0 for reveal, 1 for flag
                        action_value = self.q_table[row, col, action]

                        if action_value > best_action_value:
                            best_action_value = action_value
                            best_action = (row, col, action)

            return best_action

    def learn(self, state, action, reward, next_state):
        # Unpack the state and action
        row, col, action_type = action

        # Get the current Q-value
        current_q_value = self.q_table[row, col, action_type]

        # Calculate the maximum Q-value for the next state
        max_next_q_value = np.max(self.q_table[next_state])

        # Calculate the temporal difference (TD) error
        td_error = reward + self.discount_factor * max_next_q_value - current_q_value

        # Update the Q-table
        self.q_table[row, col, action_type] += self.learning_rate * td_error

    def decay_exploration_rate(self):
        # Update the exploration rate
        self.exploration_rate = max(
            self.exploration_rate * (1 - self.exploration_decay_rate), 0.01)

    def save(self, filename):
        # Save the Q-table to a file
        np.save(filename, self.q_table)

    def load(self, filename):
        # Load the Q-table from a file
        self.q_table = np.load(filename)

    def update(self, state, action, next_state, reward, game_over):
        self.learn(state, action, reward, next_state)
        self.decay_exploration_rate()
