import tkinter as tk
from mineSweep_GUI import Minesweeper_GUI
from mineSweep_agent import MinesweeperAgent

num_episodes = 2
height, width, num_mines = 15, 15, 35

agent = MinesweeperAgent(height, width, num_mines)

for episode in range(num_episodes):
    print(f"Episode {episode + 1}")
    gui = Minesweeper_GUI(height, width, num_mines, agent)

    # Don't call play_agent() here, it's already called in the __init__() method

    # Print the number of moves
    print(f"Number of moves in episode {episode + 1}: {gui.move_counter}")

    agent.decay_exploration_rate()

    # Save the Q-table every 100 episodes
    if (episode + 1) % 100 == 0:
        agent.save("q_table.npy")

    # Close the current game window
    try:
        gui.window.destroy()
    except:
        pass
