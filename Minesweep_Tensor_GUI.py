import tkinter as tk
from tkinter import messagebox


class MinesweeperGUI(tk.Tk):
    def __init__(self, env):
        super().__init__()

        # Initialize the environment
        self.env = env

        # Create the game grid and buttons
        self.buttons = [[tk.Button(self, text="", width=3, height=1,
                                   command=lambda row=row, col=col: self.perform_action(row, col, 0))
                         for col in range(self.env.width)] for row in range(self.env.height)]

        for row in range(self.env.height):
            for col in range(self.env.width):
                self.buttons[row][col].grid(row=row, column=col)
                self.buttons[row][col].bind(
                    '<Button-3>', lambda event, row=row, col=col: self.right_click(event, row, col))

    def perform_action(self, row, col, action_type):
        observation, reward, done, _ = self.env.step((row, col, action_type))
        self.update_buttons()
        if done:
            if reward < 0:
                messagebox.showinfo("Game Over", "You hit a mine!")
            else:
                messagebox.showinfo("Congratulations",
                                    "You cleared the minefield!")

    def update_buttons(self):
        for row in range(self.env.height):
            for col in range(self.env.width):
                if self.env.state[row][col] == 1:
                    if self.env.board[row][col] == -1:
                        self.buttons[row][col].config(text="M")
                    else:
                        self.buttons[row][col].config(
                            text=str(self.env.board[row][col]))
                elif self.env.state[row][col] == 2:
                    self.buttons[row][col].config(text="F")
                else:
                    self.buttons[row][col].config(text="")

    def right_click(self, event, row, col):
        if self.env.state[row][col] != 1:
            self.perform_action(row, col, 1)

    def update(self, agent_action=None):
        if agent_action is not None:
            row, col = agent_action // self.env.width, agent_action % self.env.width
            self.perform_action(row, col, 0)
        self.update_buttons()

    def reset(self):
        self.env.reset()
        self.update_buttons()
