import tkinter as tk
from mineSweep_GUI import Minesweeper_GUI
from mineSweep_agent import MinesweeperAgent


def main():
    # num_episodes = int(input("How many trainging epsiodes: "))
    # height = int(input("\nHeight: "))
    # width = int(input("\nWidth: "))
    # num_mines = int(input('\nNum of mines: '))
    num_episodes = 10
    height = 15
    width = 15
    num_mines = 25
    agent = MinesweeperAgent(height, width, num_mines)
    gui = Minesweeper_GUI(height, width, num_mines, agent, num_episodes)
    gui.start_game(num_episodes)
    filename = 'test.ecsv'
    # agent.save(filename)


if __name__ == "__main__":
    main()
