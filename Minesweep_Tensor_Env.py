import numpy as np
import tensorflow as tf
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from gym.spaces import Discrete, Tuple, Box
import random


class MinesweeperEnv(py_environment.PyEnvironment):
    def __init__(self, height, width, mines):
        self.height = height
        self.width = width
        self.mines = mines

        self.reset()

    def action_spec(self):
        return Discrete(self.height * self.width * 2)

    def observation_spec(self):
        return Box(low=0, high=2, shape=(self.height * self.width,), dtype=np.int32)

    def _encode_action(self, row, col, action_type):
        return row * self.width * 2 + col * 2 + action_type

    def _reset(self):
        self.board = self.generate_board()
        self.state = np.zeros((self.height, self.width), dtype=int)
        return ts.restart(self.get_observation())

    def _step(self, action):
        row, col, action_type = self._decode_action(action)

        if action_type == 0:  # Reveal
            if self.board[row][col] == -1:  # Mine
                reward = -1
                done = True
            else:
                revealed_cells = self.reveal_cell(row, col)
                for revealed_row, revealed_col in revealed_cells:
                    self.state[revealed_row][revealed_col] = 1
                reward = 1
                done = False

        else:  # Flag
            reward = 0
            done = False
            self.state[row][col] = 2

        next_observation = self.get_observation()

        if done:
            return ts.termination(next_observation, reward)
        else:
            return ts.transition(next_observation, reward, discount=1.0)

    def action_spec(self):
        return array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=self.height * self.width * 2 - 1, name='action'
        )

    def reveal_cell(self, row, col):
        if self.state[row][col] == 1:  # If the cell is already revealed
            return set()

        if self.board[row][col] == -1:  # If the cell is a mine
            self.reset()  # Reset the board
            return set()

        if self.board[row][col] > 0:  # If the cell is a number
            self.state[row][col] = 1  # Set the cell state to revealed
            return {(row, col)}

        if self.board[row][col] == 0:  # If the cell is a 0 cell
            self.state[row][col] = 1  # Set the cell state to revealed
            revealed_cells = {(row, col)}

            # Reveal surrounding 0 cells
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= row + i < self.height and 0 <= col + j < self.width and self.board[row + i][col + j] != -1:
                        revealed_cells |= self.reveal_cell(row + i, col + j)

            return revealed_cells
        else:
            return set()

    def observation_spec(self):
        return array_spec.BoundedArraySpec(
            shape=(self.height * self.width,), dtype=np.float32, minimum=0, maximum=2, name='observation'
        )

    def _decode_action(self, action):
        row = action // (self.width * 2)
        col = (action % (self.width * 2)) // 2
        action_type = action % 2
        return row, col, action_type

    def get_observation(self):
        return self.state.flatten().astype(np.float32)

    def close(self):
        pass

    def generate_board(self):
        board = [[0 for _ in range(self.width)] for _ in range(self.height)]

        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            if board[row][col] == 0:
                board[row][col] = -1
                mines_placed += 1

        for row in range(self.height):
            for col in range(self.width):
                if board[row][col] == -1:
                    continue

                mines_count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width:
                            if board[row + i][col + j] == -1:
                                mines_count += 1

                board[row][col] = mines_count

        return np.array(board)
