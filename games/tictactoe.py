import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.score = 0
        self.create_ui()

    def create_ui(self):
        self.buttons = [[tk.Button(self.root, text='', font=('Arial', 20), width=5, height=2, command=lambda r=r, c=c: self.click(r, c)) for c in range(3)] for r in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].grid(row=r, column=c)

    def click(self, r, c):
        if self.board[r][c] == '' and self.current_player == 'X':
            self.board[r][c] = 'X'
            self.buttons[r][c].config(text='X')
            if self.check_winner():
                self.score += 10
                messagebox.showinfo("Win", "You win!")
                self.reset()
                return
            if self.is_full():
                self.score += 5
                messagebox.showinfo("Draw", "Draw!")
                self.reset()
                return
            self.current_player = 'O'
            self.ai_move()

    def ai_move(self):
        best_score = -float('inf')
        best_move = None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    self.board[r][c] = 'O'
                    score = self.minimax(self.board, 0, False)
                    self.board[r][c] = ''
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        if best_move:
            r, c = best_move
            self.board[r][c] = 'O'
            self.buttons[r][c].config(text='O')
            if self.check_winner():
                messagebox.showinfo("Lose", "You lose!")
                self.reset()
                return
            if self.is_full():
                self.score += 5
                messagebox.showinfo("Draw", "Draw!")
                self.reset()
                return
            self.current_player = 'X'

    def minimax(self, board, depth, is_maximizing):
        winner = self.check_winner_board(board)
        if winner == 'O':
            return 1
        elif winner == 'X':
            return -1
        elif self.is_full_board(board):
            return 0
        if is_maximizing:
            best_score = -float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == '':
                        board[r][c] = 'O'
                        score = self.minimax(board, depth + 1, False)
                        board[r][c] = ''
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == '':
                        board[r][c] = 'X'
                        score = self.minimax(board, depth + 1, True)
                        board[r][c] = ''
                        best_score = min(score, best_score)
            return best_score

    def check_winner(self):
        return self.check_winner_board(self.board)

    def check_winner_board(self, board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '':
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != '':
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != '':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != '':
            return board[0][2]
        return None

    def is_full(self):
        return self.is_full_board(self.board)

    def is_full_board(self, board):
        return all(board[r][c] != '' for r in range(3) for c in range(3))

    def reset(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text='')

    def get_score(self):
        return self.score

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tic Tac Toe")
    game = TicTacToe(root)
    root.mainloop()
    print(f"Total earned: {game.get_score()}")