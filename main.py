import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from auth import signup, login
from db import update_user_currency, get_shop_refresh, set_shop_refresh, get_all_items, get_item, add_user_item, get_user_items, update_item_status, get_user
from games.pong import PongGame
from games.rps import RPSGame
from games.tictactoe import TicTacToe
import update
import random
from datetime import date

update.check_update()

class GameApp:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.show_login()

    def show_login(self):
        self.clear_window()
        ttk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        ttk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        ttk.Button(self.root, text="Login", command=self.do_login).pack()
        ttk.Button(self.root, text="Signup", command=self.do_signup).pack()

    def do_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, result = login(username, password)
        if success:
            self.user = result
            self.show_menu()
        else:
            messagebox.showerror("Error", result)

    def do_signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, result = signup(username, password)
        if success:
            messagebox.showinfo("Success", result)
        else:
            messagebox.showerror("Error", result)

    def show_menu(self):
        self.clear_window()
        ttk.Label(self.root, text=f"Welcome {self.user['username']}\nCurrency: {self.user['currency']}").pack()
        ttk.Button(self.root, text="Play Pong", command=self.play_pong).pack()
        ttk.Button(self.root, text="Play RPS", command=self.play_rps).pack()
        ttk.Button(self.root, text="Play Tic-Tac-Toe", command=self.play_tictactoe).pack()
        ttk.Button(self.root, text="Shop", command=self.show_shop).pack()
        ttk.Button(self.root, text="Inventory", command=self.show_inventory).pack()
        if self.user['username'] == "Owner":
            ttk.Button(self.root, text="Owner Panel", command=self.show_owner_panel).pack()
        ttk.Button(self.root, text="Logout", command=self.show_login).pack()

    def play_pong(self):
        game = PongGame()
        earned = game.play()
        self.user['currency'] += earned
        if self.user['id'] != 0:  # Not owner
            update_user_currency(self.user['id'], self.user['currency'])
        messagebox.showinfo("Game Over", f"Earned: {earned}\nTotal Currency: {self.user['currency']}")

    def play_rps(self):
        game_window = tk.Toplevel(self.root)
        game = RPSGame(game_window)
        self.root.wait_window(game_window)
        earned = game.get_score()
        self.user['currency'] += earned
        if self.user['id'] != 0:
            update_user_currency(self.user['id'], self.user['currency'])
        messagebox.showinfo("Game Over", f"Earned: {earned}\nTotal Currency: {self.user['currency']}")

    def play_tictactoe(self):
        game_window = tk.Toplevel(self.root)
        game = TicTacToe(game_window)
        self.root.wait_window(game_window)
        earned = game.get_score()
        self.user['currency'] += earned
        if self.user['id'] != 0:
            update_user_currency(self.user['id'], self.user['currency'])
        messagebox.showinfo("Game Over", f"Earned: {earned}\nTotal Currency: {self.user['currency']}")

    def show_shop(self):
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Shop")
        today = date.today().isoformat()
        refresh = get_shop_refresh(today)
        if not refresh:
            items = get_all_items()
            available = [i for i in items.data if i['status'] == 'available']
            if len(available) < 3:
                messagebox.showerror("Error", "Not enough items")
                return
            selected = random.sample(available, 3)
            set_shop_refresh(today, selected[0]['id'], selected[1]['id'], selected[2]['id'])
            refresh = {'item1_id': selected[0]['id'], 'item2_id': selected[1]['id'], 'item3_id': selected[2]['id']}
        item1 = get_item(refresh['item1_id'])
        item2 = get_item(refresh['item2_id'])
        item3 = get_item(refresh['item3_id'])
        items = [item1, item2, item3]
        for item in items:
            if item:
                frame = tk.Frame(shop_window)
                frame.pack()
                tk.Label(frame, text=f"{item['name']} - {item['price']} coins").pack(side=tk.LEFT)
                tk.Button(frame, text="Buy", command=lambda i=item: self.buy_item(i)).pack(side=tk.RIGHT)

    def buy_item(self, item):
        if self.user['currency'] >= item['price']:
            self.user['currency'] -= item['price']
            if self.user['id'] != 0:
                update_user_currency(self.user['id'], self.user['currency'])
                add_user_item(self.user['id'], item['id'])
            messagebox.showinfo("Success", f"Bought {item['name']}")
        else:
            messagebox.showerror("Error", "Not enough currency")

    def show_inventory(self):
        inv_window = tk.Toplevel(self.root)
        inv_window.title("Inventory")
        items = get_user_items(self.user['id'])
        for item in items.data:
            tk.Label(inv_window, text=f"{item['items']['name']} x{item['quantity']}").pack()

    def show_owner_panel(self):
        panel = tk.Toplevel(self.root)
        panel.title("Owner Panel")
        tk.Button(panel, text="Edit Item Status", command=self.edit_item_status).pack()
        tk.Button(panel, text="Edit User Currency", command=self.edit_user_currency).pack()

    def edit_item_status(self):
        # Simple implementation
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Item Status")
        items = get_all_items()
        for item in items.data:
            frame = tk.Frame(edit_window)
            frame.pack()
            tk.Label(frame, text=f"{item['name']} - {item['status']}").pack(side=tk.LEFT)
            status_var = tk.StringVar(value=item['status'])
            tk.OptionMenu(frame, status_var, 'available', 'limited', 'unavailable').pack(side=tk.LEFT)
            tk.Button(frame, text="Update", command=lambda i=item, s=status_var: self.update_item_status(i['id'], s.get())).pack(side=tk.RIGHT)

    def update_item_status(self, item_id, status):
        update_item_status(item_id, status)
        messagebox.showinfo("Success", "Status updated")

    def edit_user_currency(self):
        # Simple
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit User Currency")
        tk.Label(edit_window, text="Username:").pack()
        username_entry = tk.Entry(edit_window)
        username_entry.pack()
        tk.Label(edit_window, text="New Currency:").pack()
        currency_entry = tk.Entry(edit_window)
        currency_entry.pack()
        tk.Button(edit_window, text="Update", command=lambda: self.update_user_currency(username_entry.get(), currency_entry.get())).pack()

    def update_user_currency(self, username, currency):
        try:
            user = get_user(username)
            if user:
                update_user_currency(user['id'], int(currency))
                messagebox.showinfo("Success", "Currency updated")
            else:
                messagebox.showerror("Error", "User not found")
        except:
            messagebox.showerror("Error", "Invalid currency")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Arcade Game")
    root.configure(bg='#2E2E2E')
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 10), padding=5)
    style.configure('TLabel', font=('Arial', 12), background='#2E2E2E', foreground='white')
    app = GameApp(root)
    root.mainloop()