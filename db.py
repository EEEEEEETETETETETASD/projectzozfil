from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# User functions
def create_user(username, password_hash):
    return supabase.table('users').insert({'username': username, 'password_hash': password_hash}).execute()

def get_user(username):
    result = supabase.table('users').select('*').eq('username', username).execute()
    return result.data[0] if result.data else None

def update_user_currency(user_id, currency):
    return supabase.table('users').update({'currency': currency}).eq('id', user_id).execute()

# Item functions
def get_all_items():
    return supabase.table('items').select('*').execute()

def get_item(item_id):
    result = supabase.table('items').select('*').eq('id', item_id).execute()
    return result.data[0] if result.data else None

def update_item_status(item_id, status):
    return supabase.table('items').update({'status': status}).eq('id', item_id).execute()

# User items
def get_user_items(user_id):
    return supabase.table('user_items').select('*, items(*)').eq('user_id', user_id).execute()

def add_user_item(user_id, item_id, quantity=1):
    return supabase.table('user_items').insert({'user_id': user_id, 'item_id': item_id, 'quantity': quantity}).execute()

def remove_user_item(user_id, item_id, quantity=1):
    # Assuming quantity handling
    current = supabase.table('user_items').select('quantity').eq('user_id', user_id).eq('item_id', item_id).execute()
    if current.data:
        new_qty = current.data[0]['quantity'] - quantity
        if new_qty <= 0:
            return supabase.table('user_items').delete().eq('user_id', user_id).eq('item_id', item_id).execute()
        else:
            return supabase.table('user_items').update({'quantity': new_qty}).eq('user_id', user_id).eq('item_id', item_id).execute()

# Shop
def get_shop_refresh(date):
    result = supabase.table('shop_refresh').select('*').eq('date', date).execute()
    return result.data[0] if result.data else None

def set_shop_refresh(date, item1_id, item2_id, item3_id):
    return supabase.table('shop_refresh').insert({'date': date, 'item1_id': item1_id, 'item2_id': item2_id, 'item3_id': item3_id}).execute()

# Trades
def create_trade(sender_id, receiver_id, offered, requested):
    return supabase.table('trades').insert({'sender_id': sender_id, 'receiver_id': receiver_id, 'offered_items': offered, 'requested_items': requested}).execute()

def get_trades_for_user(user_id):
    return supabase.table('trades').select('*').or_('sender_id.eq.' + str(user_id) + ',receiver_id.eq.' + str(user_id)).execute()

def update_trade_status(trade_id, status):
    return supabase.table('trades').update({'status': status}).eq('id', trade_id).execute()

# Live trades
def create_live_trade(user_id, offered, requested):
    return supabase.table('live_trades').insert({'user_id': user_id, 'offered_items': offered, 'requested_items': requested}).execute()

def get_live_trades():
    return supabase.table('live_trades').select('*, users(username)').eq('status', 'open').execute()

def close_live_trade(trade_id):
    return supabase.table('live_trades').update({'status': 'closed'}).eq('id', trade_id).execute()

# Game sessions
def create_game_session(game_type, player1_id, player2_id=None):
    data = {'game_type': game_type, 'player1_id': player1_id}
    if player2_id:
        data['player2_id'] = player2_id
        data['status'] = 'playing'
    return supabase.table('game_sessions').insert(data).execute()

def get_game_session(session_id):
    result = supabase.table('game_sessions').select('*').eq('id', session_id).execute()
    return result.data[0] if result.data else None

def update_game_state(session_id, state):
    return supabase.table('game_sessions').update({'state': state}).eq('id', session_id).execute()

def finish_game_session(session_id):
    return supabase.table('game_sessions').update({'status': 'finished'}).eq('id', session_id).execute()