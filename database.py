from supabase import create_client, Client
import config

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

def init_db():
    # Call this to ensure daily shop is refreshed
    supabase.rpc('refresh_daily_shop').execute()

# User Profiles
def get_profile(user_id):
    return supabase.table('profiles').select('*').eq('id', user_id).single().execute()

def update_currency(user_id, amount):
    current = get_profile(user_id).data['currency']
    supabase.table('profiles').update({'currency': current + amount}).eq('id', user_id).execute()

def update_inventory(user_id, new_inventory):
    supabase.table('profiles').update({'inventory': new_inventory}).eq('id', user_id).execute()

# Shop
def get_shop_items():
    return supabase.table('shop_items').select('*').execute()

def get_daily_shop():
    return supabase.table('daily_shop').select('*, shop_items(*)').eq('date', 'CURRENT_DATE').execute()

def buy_item(user_id, item_id):
    item = supabase.table('shop_items').select('*').eq('id', item_id).single().execute().data
    profile = get_profile(user_id).data
    if profile['currency'] >= item['price']:
        update_currency(user_id, -item['price'])
        inventory = profile['inventory'] + [item['name']]
        update_inventory(user_id, inventory)
        return True
    return False

# Trades
def create_trade(from_user, to_user, offer, request):
    supabase.table('trades').insert({
        'from_user': from_user,
        'to_user': to_user,
        'offer': offer,
        'request': request
    }).execute()

def accept_trade(trade_id):
    trade = supabase.table('trades').select('*').eq('id', trade_id).single().execute().data
    # Validate and swap items/currency
    # This needs full implementation with checks
    supabase.table('trades').update({'status': 'accepted'}).eq('id', trade_id).execute()

# Similar for live trades...

# Owner functions
def set_item_status(item_id, status):
    supabase.table('shop_items').update({'status': status}).eq('id', item_id).execute()

def edit_user_currency(user_id, new_amount):
    supabase.table('profiles').update({'currency': new_amount}).eq('id', user_id).execute()

# More functions as needed for games, multiplayer, etc.
