import tkinter as tk
from mineSweep_GUI import Minesweeper_GUI
from mineSweep_agent import MinesweeperAgent

num_episodes = 2
height, width, num_mines = 15, 15, 35

agent = MinesweeperAgent(height, width, num_mines)
gui = Minesweeper_GUI(height, width, num_mines, agent, num_episodes)
gui.start_game(num_episodes)
