-- Database schema for the arcade game

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    currency INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('cosmetic', 'boost', 'vip')),
    price INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'limited', 'unavailable')),
    rarity VARCHAR(20) DEFAULT 'common'
);

CREATE TABLE user_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    item_id INTEGER REFERENCES items(id),
    quantity INTEGER DEFAULT 1
);

CREATE TABLE shop_refresh (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    item1_id INTEGER REFERENCES items(id),
    item2_id INTEGER REFERENCES items(id),
    item3_id INTEGER REFERENCES items(id)
);

CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id),
    receiver_id INTEGER REFERENCES users(id),
    offered_items JSONB,
    requested_items JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected'))
);

CREATE TABLE live_trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    offered_items JSONB,
    requested_items JSONB,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed'))
);

CREATE TABLE game_sessions (
    id SERIAL PRIMARY KEY,
    game_type VARCHAR(20),
    player1_id INTEGER REFERENCES users(id),
    player2_id INTEGER REFERENCES users(id),
    state JSONB,
    status VARCHAR(20) DEFAULT 'waiting' CHECK (status IN ('waiting', 'playing', 'finished'))
);