import numpy as np
import tensorflow as tf
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from gym.spaces import Discrete, Tuple, Box


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

    def _reset(self):
        self.board = np.zeros((self.height, self.width), dtype=int)
        self.mine_locations = np.random.choice(
            self.height * self.width, self.mines, replace=False)
        for mine in self.mine_locations:
            row = mine // self.width
            col = mine % self.width
            self.board[row][col] = -1
        self.state = np.zeros((self.height, self.width), dtype=int)
        return ts.restart(self.get_observation())

    def _step(self, action):
        row, col, action_type = self._decode_action(action)

        if action_type == 0:  # Reveal
            if self.board[row][col] == -1:  # Mine
                reward = -1
                done = True
            else:
                reward = 1
                done = False
                self.state[row][col] = 1
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
