# Game Architecture

## Overview
This is a Python-based arcade game collection with currency system, shop, trading, and owner controls. Uses Supabase for database, Pygame for games, Tkinter for UI.

## Key Components

### Database Schema (Supabase)
- users: id, username, password_hash, currency, created_at
- items: id, name, type (cosmetic/boost/vip), price, status (available/limited/unavailable), rarity
- user_items: user_id, item_id, quantity
- shop_refresh: date, item1_id, item2_id, item3_id
- trades: id, sender_id, receiver_id, offered_items, requested_items, status (pending/accepted/rejected)
- live_trades: id, user_id, offered_items, requested_items, status

### Modules
- main.py: Entry point, handles login/signup, main menu
- auth.py: Authentication functions
- db.py: Database operations
- games/: pong.py, snake.py, tetris.py (each with single-player CPU and local multiplayer)
- shop.py: Shop logic, daily refresh
- trading.py: Trading systems
- owner_panel.py: Owner controls
- update.py: Auto-update from GitHub
- config.py: Constants, API keys

### Features
- Arcade Games: Pong, Rock Paper Scissors, Tic-Tac-Toe with CPU and online multiplayer
- Currency: Earned from games
- Shop: Daily 3 random items
- Inventory: Each user has their own inventory, viewable at any time
- Owner Panel: Control shop, edit inventories
- Trading: Direct requests, live trade board
- Updates: push_update.py commits and pushes to GitHub repo, game pulls latest on launch
- Security: Password hashing, input validation, server-side checks

### UI
- Tkinter for menus, login, shop, trading
- Pygame for games

### Multiplayer
Online multiplayer via Supabase realtime for state synchronization.

### Updates
- push_update.py: Commits and pushes changes to GitHub repo
- Game performs git pull on launch to update