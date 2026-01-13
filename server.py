from flask import Flask, request, jsonify
from flask_cors import CORS
import config
from supabase import create_client, Client
import datetime
import json

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for client-server communication

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

# Middleware to check authentication (assuming JWT from Supabase Auth)
def get_user_id():
    token = request.headers.get('Authorization')
    if token:
        user = supabase.auth.get_user(token.split()[1])  # Bearer token
        return user.user.id if user else None
    return None

@app.route('/api/init', methods=['GET'])
def init():
    # Refresh daily shop
    supabase.rpc('refresh_daily_shop').execute()
    return jsonify({'status': 'ok'})

# Shop endpoints
@app.route('/api/shop/daily', methods=['GET'])
def get_daily_shop():
    data = supabase.table('daily_shop').select('*, shop_items(*)').eq('date', datetime.date.today().isoformat()).execute()
    return jsonify(data.data)

@app.route('/api/shop/buy', methods=['POST'])
def buy_item():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    item_id = request.json.get('item_id')
    # Validate if item is in daily shop
    daily = supabase.table('daily_shop').select('*').eq('item_id', item_id).eq('date', datetime.date.today().isoformat()).execute()
    if not daily.data:
        return jsonify({'error': 'Item not available today'}), 400
    # Buy logic
    item = supabase.table('shop_items').select('*').eq('id', item_id).single().execute().data
    profile = supabase.table('profiles').select('*').eq('id', user_id).single().execute().data
    if profile['currency'] &gt;= item['price'] and item['status'] == 'available':
        new_currency = profile['currency'] - item['price']
        inventory = profile['inventory'] + [item['name']]
        supabase.table('profiles').update({'currency': new_currency, 'inventory': json.dumps(inventory)}).eq('id', user_id).execute()
        return jsonify({'success': True})
    return jsonify({'error': 'Insufficient funds or item unavailable'}), 400

# Trading endpoints
@app.route('/api/trades/create', methods=['POST'])
def create_trade():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    to_user = data['to_user']  # username or id
    offer = data['offer']
    request_items = data['request']
    # Resolve to_user id if username
    to_profile = supabase.table('profiles').select('id').eq('username', to_user).single().execute().data
    if not to_profile:
        return jsonify({'error': 'User not found'}), 404
    supabase.table('trades').insert({
        'from_user': user_id,
        'to_user': to_profile['id'],
        'offer': json.dumps(offer),
        'request': json.dumps(request_items)
    }).execute()
    return jsonify({'success': True})

@app.route('/api/trades/accept', methods=['POST'])
def accept_trade():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    trade_id = request.json.get('trade_id')
    trade = supabase.table('trades').select('*').eq('id', trade_id).eq('to_user', user_id).eq('status', 'pending').single().execute().data
    if not trade:
        return jsonify({'error': 'Invalid trade'}), 400
    # Perform trade: swap items/currency
    from_profile = supabase.table('profiles').select('*').eq('id', trade['from_user']).single().execute().data
    to_profile = supabase.table('profiles').select('*').eq('id', trade['to_user']).single().execute().data
    
    # Validate from_user has offer items/currency
    from_inventory = set(from_profile['inventory'])
    offer_items = set(offer.get('items', []))
    if not offer_items.issubset(from_inventory) or from_profile['currency'] < offer.get('currency', 0):
        return jsonify({'error': 'Invalid offer'}), 400
    
    # Validate to_user has request items
    request_items_set = set(trade['request'].get('items', []))
    if not request_items_set.issubset(set(to_profile['inventory'])) or to_profile['currency'] < trade['request'].get('currency', 0):
        return jsonify({'error': 'Invalid request'}), 400
    
    # Execute trade
    # Update from_user
    new_from_inventory = list(from_inventory - offer_items) + list(request_items_set)
    new_from_currency = from_profile['currency'] - offer.get('currency', 0) + trade['request'].get('currency', 0)
    supabase.table('profiles').update({'inventory': json.dumps(new_from_inventory), 'currency': new_from_currency}).eq('id', trade['from_user']).execute()
    
    # Update to_user
    new_to_inventory = list(set(to_profile['inventory']) - request_items_set) + list(offer_items)
    new_to_currency = to_profile['currency'] - trade['request'].get('currency', 0) + offer.get('currency', 0)
    supabase.table('profiles').update({'inventory': json.dumps(new_to_inventory), 'currency': new_to_currency}).eq('id', trade['to_user']).execute()
    
    supabase.table('trades').update({'status': 'accepted'}).eq('id', trade_id).execute()
    return jsonify({'success': True})

# Similar endpoints for decline, list trades, etc.

# Live trades
@app.route('/api/live_trades/create', methods=['POST'])
def create_live_trade():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    offering = data['offering']
    wanting = data['wanting']
    supabase.table('live_trades').insert({
        'user_id': user_id,
        'offering': json.dumps(offering),
        'wanting': json.dumps(wanting)
    }).execute()
    return jsonify({'success': True})

@app.route('/api/live_trades/list', methods=['GET'])
def list_live_trades():
    data = supabase.table('live_trades').select('*').eq('status', 'open').execute()
    return jsonify(data.data)

# Endpoint for offering on live trade, accept offer, etc. Similar to above.

# Multiplayer game endpoints
@app.route('/api/games/create_room', methods=['POST'])
def create_game_room():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    game_type = request.json.get('game_type')
    room = supabase.table('game_rooms').insert({
        'game_type': game_type,
        'players': json.dumps([user_id]),
        'state': json.dumps({})  # Initial state
    }).execute()
    return jsonify({'room_id': room.data[0]['id']})

@app.route('/api/games/join_room', methods=['POST'])
def join_game_room():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    room_id = request.json.get('room_id')
    room = supabase.table('game_rooms').select('*').eq('id', room_id).single().execute().data
    players = json.loads(room['players'])
    if len(players) < 2 and user_id not in players:  # Assuming 2 players
        players.append(user_id)
        supabase.table('game_rooms').update({'players': json.dumps(players)}).eq('id', room_id).execute()
        return jsonify({'success': True})
    return jsonify({'error': 'Room full or already joined'}), 400

# Update game state, etc. For realtime, use Supabase Realtime subscriptions on client-side.

# Owner panel endpoints
@app.route('/api/owner/set_item_status', methods=['POST'])
def owner_set_item_status():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    profile = supabase.table('profiles').select('is_owner').eq('id', user_id).single().execute().data
    if not profile['is_owner']:
        return jsonify({'error': 'Not owner'}), 403
    item_id = request.json.get('item_id')
    status = request.json.get('status')
    supabase.table('shop_items').update({'status': status}).eq('id', item_id).execute()
    return jsonify({'success': True})

@app.route('/api/owner/edit_user_currency', methods=['POST'])
def owner_edit_user_currency():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    profile = supabase.table('profiles').select('is_owner').eq('id', user_id).single().execute().data
    if not profile['is_owner']:
        return jsonify({'error': 'Not owner'}), 403
    target_user = request.json.get('target_user')
    amount = request.json.get('amount')
    supabase.table('profiles').update({'currency': amount}).eq('id', target_user).execute()
    return jsonify({'success': True})

# More owner endpoints as needed

# Game result for currency (server-validated if possible)
@app.route('/api/games/report_win', methods=['POST'])
def report_game_win():
    user_id = get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    game_type = request.json.get('game_type')
    won = request.json.get('won')
    # For simplicity, trust client; in production, validate with game state or server simulation
    currency = 100 if won else 10  # Example
    supabase.table('profiles').update({'currency': supabase.raw('currency + %s' % currency)}).eq('id', user_id).execute()
    return jsonify({'success': True, 'currency_earned': currency})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
