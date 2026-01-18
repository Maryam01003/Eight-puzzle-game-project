import tkinter as tk
from tkinter import messagebox
import json
import os
import time
import copy
from solver import solve_puzzle, scramble_state, GOAL_STATE, find_zero

class EightPuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle")
        self.geometry("500x600")

        self.state = [[0]*3 for _ in range(3)]
        self.moves = 0
        self.start_time = None
        self.high_scores = self.load_scores()
        self.solver_path = []
        self.undo_stack = []

        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        tk.Label(self, text="8-Puzzle", font=('Arial', 16, 'bold')).pack(pady=10)

        stats = tk.Frame(self)
        stats.pack()
        self.moves_label = tk.Label(stats, text="Moves: 0")
        self.moves_label.pack(side='left')
        self.time_label = tk.Label(stats, text="Time: 0s")
        self.time_label.pack(side='left')
        self.status_label = tk.Label(stats, text="Scramble to start!")
        self.status_label.pack(side='left')

        board = tk.Frame(self)
        board.pack(pady=10)
        self.tiles = [[None]*3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                tile = tk.Label(board, text="", width=5, height=2, font=('Arial', 20, 'bold'), relief='raised', bd=2)
                tile.grid(row=i, column=j, padx=2, pady=2)
                tile.bind('<Button-1>', lambda e, x=i, y=j: self.move_tile(x, y))
                self.tiles[i][j] = tile

        btns = tk.Frame(self)
        btns.pack(pady=10)
        tk.Button(btns, text="Scramble", command=self.new_game).pack(side='left')
        tk.Button(btns, text="Solve", command=self.auto_solve).pack(side='left')
        tk.Button(btns, text="Undo", command=self.undo_move).pack(side='left')

        tk.Label(self, text="High Scores").pack()
        self.scores_list = tk.Listbox(self, height=5)
        self.scores_list.pack(pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()
        tk.Button(self, text="Save Score", command=self.save_score).pack()
        tk.Button(self, text="Help", command=self.show_help).pack()

        self.update_board()
        self.update_scores()

    def new_game(self):
        self.state = scramble_state()
        self.moves = 0
        self.start_time = time.time()
        self.solver_path = []
        self.undo_stack = []
        self.status_label.config(text="Solve!")
        self.update_board()
        self.update_stats()

    def move_tile(self, i, j):
        if self.start_time is None:
            return
        zi, zj = find_zero(self.state)
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            if zi + di == i and zj + dj == j:
                self.undo_stack.append(copy.deepcopy(self.state))
                self.state[zi][zj], self.state[i][j] = self.state[i][j], self.state[zi][zj]
                self.moves += 1
                self.update_board()
                self.update_stats()
                if self.is_solved():
                    self.win_game()
                return

    def is_solved(self):
        return self.state == GOAL_STATE

    def win_game(self):
        elapsed = int(time.time() - self.start_time)
        self.status_label.config(text="You won!")
        messagebox.showinfo("Win!", f"{self.moves} moves, {elapsed}s")
        self.start_time = None

    def update_board(self):
        for i in range(3):
            for j in range(3):
                num = self.state[i][j]
                self.tiles[i][j].config(text="" if num == 0 else str(num), bg='gray' if num == 0 else 'white')

    def update_stats(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.time_label.config(text=f"Time: {elapsed}s")
        self.moves_label.config(text=f"Moves: {self.moves}")

    def auto_solve(self):
        path = solve_puzzle(copy.deepcopy(self.state))
        if path:
            self.solver_path = path[1:]
            self.animate_solve()
        else:
            messagebox.showerror("Error", "Unsolvable")

    def animate_solve(self):
        if self.solver_path:
            self.state = self.solver_path.pop(0)
            self.moves += 1
            self.update_board()
            self.update_stats()
            self.after(200, self.animate_solve)
        else:
            self.status_label.config(text="AI Solved!")

    def undo_move(self):
        if self.undo_stack:
            self.state = self.undo_stack.pop()
            self.moves = max(0, self.moves - 1)
            self.update_board()
            self.update_stats()

    def load_scores(self):
        try:
            if os.path.exists('data/scores.json'):
                with open('data/scores.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_score(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name required")
            return
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        score = {'name': name, 'moves': self.moves, 'time': elapsed}
        self.high_scores.append(score)
        self.high_scores.sort(key=lambda x: (x['moves'], x['time']))
        self.high_scores = self.high_scores[:5]
        with open('data/scores.json', 'w') as f:
            json.dump(self.high_scores, f)
        self.name_entry.delete(0, 'end')
        self.update_scores()
        messagebox.showinfo("OK", "Saved")

    def update_scores(self):
        self.scores_list.delete(0, 'end')
        for s in self.high_scores:
            self.scores_list.insert('end', f"{s['name']} - {s['moves']} moves - {s['time']}s")

    def show_help(self):
        messagebox.showinfo("Help", "Click tiles to move. Scramble new game. Solve with AI.")

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    app = EightPuzzleApp()
    app.mainloop()