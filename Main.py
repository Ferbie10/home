import tkinter as tk
from mineSweep_GUI import MinesweeperGUI
from mineSweep_agent import MinesweeperAgent

num_episodes = 1000
height, width, num_mines = 10, 10, 20

agent = MinesweeperAgent(height, width, num_mines)

for episode in range(num_episodes):
    print(f"Episode {episode + 1}")
    gui = MinesweeperGUI(height, width, num_mines, agent)

    gui.play_agent()  # Call the play_agent method

    # Print the number of moves
    print(f"Number of moves in episode {episode + 1}: {gui.move_counter}")

    agent.decay_exploration_rate()

    # Save the Q-table every 100 episodes
    if (episode + 1) % 100 == 0:
        agent.save("q_table.npy")

    # Close the current game window
    gui.root.destroy()

# Save the final Q-table
agent.save("q_table.npy")
