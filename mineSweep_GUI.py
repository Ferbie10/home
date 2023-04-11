import tkinter as tk
import random
import time


class Minesweeper_GUI:
    def __init__(self, height, width, mines, agent):
        self.window = tk.Tk()
        self.total_moves = 0
        self.total_games = 0
        self.best_score = None
        self.start_time = time.time()
        self.height = height
        self.width = width
        self.mines = mines
        self.revealed_cells = set()

        self.board = self.generate_board()
        self.buttons = []
        self.agent = agent
        self.move_counter = 0

        self._game_end = False
        self.window.title("Minesweeper")

        self.revealed_cells = set()
        self.create_widgets()
        self.play_agent()

        self.run()

    def create_widgets(self):
        frame1 = tk.Frame(master=self.window, width=800, height=800, bg="grey")
        frame1.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        frame2 = tk.Frame(master=self.window, width=400, bg="black")
        frame2.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        self.create_minesweeper(frame1)
        self.create_statistics(frame2)

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

    def create_minesweeper(self, frame):
        for i in range(self.height):
            row_buttons = []
            for j in range(self.width):
                button = tk.Button(frame, text="", width=3, height=1,
                                   command=lambda i=i, j=j: self.reveal_cell(
                                       i, j),
                                   highlightthickness=0)  # Add highlightthickness option
                button.bind("<Button-3>", lambda event, i=i,
                            j=j: self.toggle_flag(event, i, j))
                button.grid(row=i, column=j)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

    def toggle_flag_mode(self, event):
        self.flag_mode = not self.flag_mode

    def create_statistics(self, frame):
        self.stats_label = tk.Label(
            frame, text=self.get_statistics_text(), justify=tk.LEFT)
        self.stats_label.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

    def get_statistics_text(self):
        elapsed_time = int(time.time() - self.start_time)
        best_score = self.best_score if self.best_score is not None else "N/A"
        return f"Total games: {self.total_games}\nTotal moves: {self.total_moves}\nElapsed time: {elapsed_time}s\nBest score: {best_score}"

    def on_button_click(self, row, col):
        if self.board[row][col] == "*":
            self.reset_board()  # Reset the board if a mine cell is clicked
            return

        # Reveal the clicked button and its adjacent cells if needed
        self.reveal_cell(row, col)

        # Update the displayed board
        self.update_board()

        if self.check_win():
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
        self.window.update()
        self.window.after(10)  # 100 milliseconds delay

    def reveal_cell(self, row, col):
        if not self._game_end and self.buttons[row][col]['state'] in (tk.NORMAL, tk.ACTIVE):
            if self.board[row][col] == "*":  # Handle mine cell click
                self.reset_board()
                return

            # Convert the number to a string
            self.buttons[row][col].config(
                text=str(self.board[row][col]), width=3, height=1)  # Set the width to 3
            self.buttons[row][col].config(state=tk.DISABLED)
            self.revealed_cells.add((row, col))
            if self.board[row][col] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width and (row + i, col + j) not in self.revealed_cells:
                            self.reveal_cell(row + i, col + j)

    def reset_board(self):
        self.board = self.generate_board()
        self._game_end = False
        self.revealed_cells.clear()

        for i in range(self.height):
            for j in range(self.width):
                button = self.buttons[i][j]
                button.config(text="", state=tk.NORMAL, bg=None)
        self.window.focus_set()

        # Update the statistics label
        self.total_games += 1
        elapsed_time = int(time.time() - self.start_time)
        if self.best_score is None or self.total_moves < self.best_score:
            self.best_score = self.total_moves
        self.total_moves = 0
        self.stats_label.config(text=self.get_statistics_text())

    def toggle_flag(self, event, row, col):
        button = self.buttons[row][col]
        if button['text'] == "":
            button.config(text="F", bg="yellow")
        elif button['text'] == "F":
            button.config(text="", bg=None)

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
                print(f"Agent revealed cell ({row}, {col})")

        elif action_type == 1:  # Flag (skip this action for now)
            pass

        # Compute the reward based on the game result
        if self.check_win():
            reward = 1
        elif self.board[row][col] == "*":
            reward = -1
        else:
            reward = .02

        # Get the next state after performing the action
        next_state = self.get_current_state()

        # Update the GUI to reflect the agent's actions
        self.update_board()
        self.stats_label.config(text=self.get_statistics_text())
        self.window.update()
        print(f"Agent action: ({row}, {col}, {action_type}), Reward: {reward}")

        return self.check_win() or self.board[row][col] == "*", reward, next_state

    def update_board(self):
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in self.revealed_cells:
                    self.buttons[i][j].config(
                        text=self.board[i][j], state=tk.DISABLED)

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

    def run(self):
        self.window.mainloop()

    def check_win(self):
        non_mine_cells = self.height * self.width - self.mines
        return len(self.revealed_cells) == non_mine_cells

    @property
    def game_end(self):
        return self._game_end

    def play_agent(self):
        if not self.game_end:
            valid_action = False
            while not valid_action:
                print("Before agent chooses action")
                action = self.agent.choose_action(self.get_current_state())
                print(f"Action chosen by agent: {action}")
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
            # Schedule the next move after 100ms
            self.window.after(100, self.play_agent)
