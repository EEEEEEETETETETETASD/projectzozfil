import tkinter as tk
from tkinter import messagebox
import random

class RPSGame:
    def __init__(self, root):
        self.root = root
        self.choices = ['rock', 'paper', 'scissors']
        self.beats = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
        self.score = 0
        self.create_ui()

    def create_ui(self):
        self.label = tk.Label(self.root, text="Choose your move:")
        self.label.pack()
        for choice in self.choices:
            btn = tk.Button(self.root, text=choice.capitalize(), command=lambda c=choice: self.play(c))
            btn.pack()

    def play(self, player_choice):
        cpu_choice = random.choice(self.choices)
        if player_choice == cpu_choice:
            result = "Draw"
            earned = 2
        elif self.beats[player_choice] == cpu_choice:
            result = "You Win!"
            earned = 5
        else:
            result = "You Lose!"
            earned = 0
        messagebox.showinfo("Result", f"You: {player_choice.capitalize()}\nCPU: {cpu_choice.capitalize()}\n{result}\nEarned: {earned}")
        self.score += earned
        if not messagebox.askyesno("Continue?", "Play again?"):
            self.root.quit()

    def get_score(self):
        return self.score

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Rock Paper Scissors")
    game = RPSGame(root)
    root.mainloop()
    print(f"Total earned: {game.get_score()}")