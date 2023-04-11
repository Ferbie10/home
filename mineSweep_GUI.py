import tkinter as tk
import random


class MinesweeperGUI:
    def __init__(self, height, width, mines, agent):
        self.height = height
        self.width = width
        self.mines = mines
        self._game_end = False
        self.episode_moves = []

        self.board = self.generate_board()
        self.root = tk.Tk()
        self.root.title("Minesweeper")
        self.agent = agent
        self.revealed_cells = set()

        self.canvas = tk.Canvas(self.root)
        self.canvas.grid(row=0, column=self.width+1,
                         rowspan=self.height, sticky=tk.N + tk.S + tk.E + tk.W)

        self.scrollbar = tk.Scrollbar(self.root, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=self.width+2,
                            rowspan=self.height, sticky=tk.N + tk.S)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)

        self.episode_moves_label = tk.Label(
            self.frame, text='', justify=tk.LEFT)
        self.episode_moves_label.pack()

        self.buttons = [
            [tk.Button(self.root, text='', command=lambda row=i, col=j: self.on_button_click(row, col), width=2, height=1, font=("Arial", 10))
             for j in range(self.width)] for i in range(self.height)]
        for i in range(self.height):
            for j in range(self.width):
                self.buttons[i][j].grid(row=i, column=j)
                self.root.grid_columnconfigure(j, weight=0, minsize=0)
                self.root.grid_rowconfigure(i, weight=0, minsize=0)

        self.move_counter = 0
        self.move_label = tk.Label(
            self.root, text=f'Moves: {self.move_counter}')
        self.move_label.grid(row=self.height, column=0,
                             columnspan=self.width, sticky=tk.W)
        self.round_counter = 1
        self.round_label = tk.Label(
            self.root, text=f'Round: {self.round_counter}')
        self.round_label.grid(row=self.height, column=5,
                              columnspan=self.width, sticky=tk.E)
        self.play_agent()

        self.run()

    # The rest of the code remains unchanged

    # Add this method to update the canvas scrollregion
    def update_scrollregion(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def generate_board(self):
        board = [[0 for _ in range(self.width)] for _ in range(self.height)]

        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            if board[row][col] == 0:
                board[row][col] = "*"
                mines_placed += 1

        for row in range(self.height):
            for col in range(self.width):
                if board[row][col] == "*":
                    continue

                mines_count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width:
                            if board[row + i][col + j] == "*":
                                mines_count += 1

                board[row][col] = mines_count

        return board

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_button_click(self, row, col):
        # Reveal the clicked button and its adjacent cells if needed
        self.reveal_cell(row, col)

        # Update the displayed board
        self.update_board()

        # Check if the game has ended (win or lose)
        if self.check_win() or self.board[row][col] == "*":
            self._game_end = True

            # Show the mines
            for i in range(self.height):
                for j in range(self.width):
                    if self.board[i][j] == "*":
                        self.buttons[i][j].config(
                            text="*", state="disabled", bg="red")

            # Disable all buttons
            for i in range(self.height):
                for j in range(self.width):
                    self.buttons[i][j].config(state="disabled")
            self.root.update()
            self.root.after(10)  # 100 milliseconds delay

    def reveal_cell(self, row, col):
        if not self._game_end and self.board[row][col] != '*' and self.buttons[row][col]['state'] in (tk.NORMAL, tk.ACTIVE):
            # Convert the number to a string
            self.buttons[row][col].config(
                text=str(self.board[row][col]), width=2, height=1)
            self.buttons[row][col].config(state=tk.DISABLED)
            self.revealed_cells.add((row, col))
            if self.board[row][col] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width:
                            self.reveal_cell(row + i, col + j)

    def get_current_state(self):
        current_state = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                if (i, j) in self.revealed_cells:
                    row.append(self.board[i][j])
                else:
                    row.append(-1)
            current_state.append(row)
        return current_state

    def perform_action(self, action):
        # Unpack the action (row, col, action_type) chosen by the agent
        row, col, action_type = action

        if action_type == 0:  # Reveal
            if self.buttons[row][col]['state'] in (tk.NORMAL, tk.ACTIVE):
                self.on_button_click(row, col)
        elif action_type == 1:  # Flag (skip this action for now)
            pass

        # Compute the reward based on the game result
        if self.check_win():
            reward = 10
        elif self.board[row][col] == "*":
            reward = -10
        else:
            reward = .02

        # Get the next state after performing the action
        next_state = self.get_current_state()

        return self.check_win() or self.board[row][col] == "*", reward, next_state

    def update_board(self):
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in self.revealed_cells:
                    self.buttons[i][j].config(
                        text=self.board[i][j], state=tk.DISABLED)

    def update_episode_moves_label(self):
        episode_moves_text = '\n'.join(
            [f'Episode {i + 1}: {moves}' for i, moves in enumerate(self.episode_moves)])
        self.episode_moves_label.config(text=episode_moves_text)

    def reset_board(self):
        # Destroy all the buttons
        for row in self.buttons:
            for button in row:
                button.destroy()
        self._game_end = False

        # Update the episode_moves_label text
        self.episode_moves.append(self.move_counter)
        self.update_episode_moves_label()

        # Reset the move counter and update the label
        self.move_counter = 0
        self.move_label.config(text=f'Moves: {self.move_counter}')

        # Increment the round counter and update the round label
        self.round_counter += 1
        self.round_label.config(text=f'Round: {self.round_counter}')

        # Create a new board
        self.board = self.generate_board()

        # Recreate the buttons
        self.buttons = [
            [tk.Button(self.root, text='', command=lambda row=i, col=j: self.on_button_click(row, col), width=2, height=1, font=("Arial", 10))
             for j in range(self.width)] for i in range(self.height)]

        for i in range(self.height):
            for j in range(self.width):
                self.buttons[i][j].grid(
                    row=i, column=j, sticky=tk.N + tk.S + tk.E + tk.W)

    def update_episode_moves_label(self):
        episode_moves_text = '\n'.join(
            [f'Episode {i + 1}: {moves}' for i, moves in enumerate(self.episode_moves)])
        self.episode_moves_label.config(text=episode_moves_text)
        # Update the scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.frame.update_idletasks()

    def check_win(self):
        non_mine_cells = self.height * self.width - self.mines
        return len(self.revealed_cells) == non_mine_cells

    @property
    def game_end(self):
        return self._game_end

    def run(self):
        self.root.mainloop()

    def play_agent(self):
        while True:  # Change the outer loop condition to True
            while not self.game_end:
                valid_action = False
                while not valid_action:
                    action = self.agent.choose_action(self.get_current_state())
                    game_over, reward, next_state = self.perform_action(action)
                    if self.buttons[action[0]][action[1]]['state'] == tk.DISABLED:
                        valid_action = True
                    else:
                        valid_action = False
                        reward = -0.1  # Provide a small negative reward for invalid actions

                    if valid_action:
                        self.move_counter += 1  # Increment the move counter only for valid actions

                self.agent.update(self.get_current_state(), action,
                                  next_state, reward, game_over)
                # Update the move label
                self.move_label.config(text=f'Moves: {self.move_counter}')
                self.root.update()
                self.root.after(100)  # 100 milliseconds delay

            # Reset the game when the game ends
            self.reset_board()
            self.revealed_cells.clear()
