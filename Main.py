import tkinter as tk
from mineSweep_GUI import MinesweeperGUI
from mineSweep_agent import MinesweeperAgent

num_episodes = 1000
height, width, num_mines = 10, 10, 10

agent = MinesweeperAgent(height, width, num_mines)

for episode in range(num_episodes):
    print(f"Episode {episode + 1}")
    gui = MinesweeperGUI(height, width, num_mines, agent)

    num_moves = 0  # Initialize the number of moves counter

    while not gui.game_end:
        state = gui.get_current_state()
        action = agent.choose_action(state)
        result, reward, next_state = gui.perform_action(action)
        agent.learn(state, action, reward, next_state)

        num_moves += 1  # Increment the number of moves counter

    # Print the number of moves
    print(f"Number of moves in episode {episode + 1}: {num_moves}")

    agent.decay_exploration_rate()

    # Save the Q-table every 100 episodes
    if (episode + 1) % 100 == 0:
        agent.save("q_table.npy")

    # Close the current game window
    gui.root.destroy()

# Save the final Q-table
agent.save("q_table.npy")
