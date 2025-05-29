"""
SteamAPIs Python Library Examples
=================================

This file contains examples demonstrating how to use the SteamAPIs Python library
for various Steam market data operations.

Make sure to install the required dependencies:
    pip install requests

And set your API key before running these examples.
"""

import os
import json
from datetime import datetime
from steamapis import SteamAPIs, create_client, SteamAPIsError, RateLimitError

# Set your API key here or use environment variable
API_KEY = os.environ.get('STEAMAPIS_API_KEY', 'YOUR_API_KEY_HERE')

# Common Steam IDs and App IDs for examples
EXAMPLE_STEAM_ID = '76561197993496553'
CSGO_APP_ID = 730
DOTA2_APP_ID = 570
TF2_APP_ID = 440


def example_basic_usage():
    """Example 1: Basic usage and initialization"""
    print("=== Example 1: Basic Usage ===")
    
    # Method 1: Direct initialization
    client = SteamAPIs(API_KEY)
    
    # Method 2: Using create_client helper
    client2 = create_client(API_KEY, timeout=60)
    
    # Method 3: Using context manager (recommended)
    with SteamAPIs(API_KEY) as client:
        # Client will automatically close when exiting the context
        profile = client.get_user_profile(EXAMPLE_STEAM_ID)
        print(f"User Profile: {profile.get('personaname', 'Unknown')}")
    
    print("✓ Basic usage examples completed\n")


def example_market_statistics():
    """Example 2: Getting market statistics"""
    print("=== Example 2: Market Statistics ===")
    
    with SteamAPIs(API_KEY) as client:
        try:
            # Get market statistics
            stats = client.get_market_stats()
            
            print(f"Total items tracked: {stats['count']:,}")
            print(f"Total spent: ${stats['stats']['totalSpent']:,.2f}")
            print(f"Total count: {stats['stats']['totalCount']:,}")
            print(f"Total apps: {stats['stats']['totalApps']:,}")
            
            # Calculate average price per item
            avg_price = stats['stats']['totalSpent'] / stats['stats']['totalCount']
            print(f"Average price per item: ${avg_price:.2f}")
            
        except SteamAPIsError as e:
            print(f"Error getting market stats: {e}")
    
    print("✓ Market statistics example completed\n")


def example_app_operations():
    """Example 3: Working with app data"""
    print("=== Example 3: App Operations ===")
    
    with SteamAPIs(API_KEY) as client:
        try:
            # Get single app details
            app_details = client.get_app_details(CSGO_APP_ID)
            print(f"App Name: {app_details['name']}")
            print(f"Type: {app_details['type']}")
            print(f"Is Free: {app_details['is_free']}")
            if 'price_overview' in app_details:
                print(f"Price: {app_details['price_overview']['final_formatted']}")
            print(f"Developers: {', '.join(app_details.get('developers', []))}")
            print(f"Publishers: {', '.join(app_details.get('publishers', []))}")
            
            # Get all apps
            all_apps = client.get_all_apps()
            print(f"\nTotal apps in database: {len(all_apps)}")
            
            # Show first 5 paid apps
            paid_apps = [app for app in all_apps if not app.get('is_free', True)][:5]
            print("\nFirst 5 paid apps:")
            for app in paid_apps:
                price = app.get('price_overview', {}).get('final_formatted', 'N/A')
                print(f"- {app['name']} ({app['appID']}): {price}")
            
        except SteamAPIsError as e:
            print(f"Error with app operations: {e}")
    
    print("✓ App operations completed\n")


def example_inventory_operations():
    """Example 4: Working with inventories"""
    print("=== Example 4: Inventory Operations ===")
    
    with SteamAPIs(API_KEY) as client:
        try:
            # Get CS:GO inventory
            inventory = client.get_inventory(EXAMPLE_STEAM_ID, CSGO_APP_ID, context_id=2)
            
            print(f"Total items in inventory: {len(inventory.get('items', []))}")
            
            # Display first 5 items
            for i, item in enumerate(inventory.get('items', [])[:5]):
                print(f"{i+1}. {item.get('name', 'Unknown Item')} - {item.get('type', 'Unknown Type')}")
            
            # Get inventory value
            inventory_value = client.get_inventory_value(EXAMPLE_STEAM_ID, CSGO_APP_ID)
            print(f"\nTotal inventory value: ${inventory_value.get('total_value', 0):.2f}")
            
        except SteamAPIsError as e:
            print(f"Error getting inventory: {e}")
    
    print("✓ Inventory operations completed\n")


def example_item_details():
    """Example 5: Getting detailed item information"""
    print("=== Example 5: Item Details ===")
    
    with SteamAPIs(API_KEY) as client:
        # Example item
        item_name = "AK-47 | Redline (Field-Tested)"
        
        try:
            # Get item details with 30 days of median history
            item_details = client.get_item_details(CSGO_APP_ID, item_name, median_history_days=30)
            
            print(f"Item: {item_details['market_name']}")
            print(f"Name ID: {item_details['nameID']}")
            print(f"Border Color: {item_details['border_color']}")
            print(f"Type: {item_details['assets']['type']}")
            
            # Histogram data
            histogram = item_details.get('histogram', {})
            print(f"\nMarket Overview:")
            print(f"Lowest sell order: ${histogram.get('lowest_sell_order', 'N/A')}")
            print(f"Highest buy order: ${histogram.get('highest_buy_order', 'N/A')}")
            print(f"Buy orders: {histogram.get('buy_order_summary', {}).get('quantity', 0):,}")
            print(f"Sell orders: {histogram.get('sell_order_summary', {}).get('quantity', 0):,}")
            
            # Median price history
            print(f"\nMedian price history (last 5 days):")
            for entry in item_details.get('median_avg_prices_15days', [])[-5:]:
                date, price, volume = entry
                print(f"  {date}: ${price:.2f} (volume: {volume})")
            
        except SteamAPIsError as e:
            print(f"Error getting item details: {e}")
    
    print("✓ Item details example completed\n")


def example_items_with_format():
    """Example 6: Getting items with different formats"""
    print("=== Example 6: Items with Format Options ===")
    
    with SteamAPIs(API_KEY) as client:
        try:
            # Get full item data
            print("Getting full item data...")
            items_full = client.get_items_for_app(CSGO_APP_ID)
            print(f"Total items: {len(items_full['data'])}")
            
            # Show first item details
            if items_full['data']:
                first_item = items_full['data'][0]
                print(f"\nFirst item details:")
                print(f"Name: {first_item['market_name']}")
                print(f"Safe price: ${first_item['prices']['safe']:.2f}")
                print(f"Latest price: ${first_item['prices']['latest']:.2f}")
                print(f"Unstable: {first_item['prices']['unstable']}")
                if first_item['prices']['unstable']:
                    print(f"Unstable reason: {first_item['prices']['unstable_reason']}")
            
            # Get compact format with safe prices
            print("\n\nGetting compact format with safe prices...")
            prices_safe = client.get_items_for_app(CSGO_APP_ID, format='compact')
            
            # Show first 5 items with prices
            print("First 5 items (safe prices):")
            for i, (name, price) in enumerate(list(prices_safe.items())[:5]):
                if price is not None:
                    print(f"{i+1}. {name}: ${price:.2f}")
                else:
                    print(f"{i+1}. {name}: No price data")
            
            # Get compact format with latest prices
            print("\n\nGetting compact format with latest prices...")
            prices_latest = client.get_items_for_app(CSGO_APP_ID, format='compact', compact_value='latest')
            
            # Compare safe vs latest prices for first 3 items
            print("Comparing safe vs latest prices:")
            for i, name in enumerate(list(prices_safe.keys())[:3]):
                safe_price = prices_safe.get(name)
                latest_price = prices_latest.get(name)
                if safe_price is not None and latest_price is not None:
                    diff = latest_price - safe_price
                    print(f"{i+1}. {name}:")
                    print(f"   Safe: ${safe_price:.2f}, Latest: ${latest_price:.2f}, Diff: ${diff:.2f}")
            
        except SteamAPIsError as e:
            print(f"Error getting items: {e}")
    
    print("✓ Items format example completed\n")


def example_trading_cards():
    """Example 7: Working with Steam trading cards"""
    print("=== Example 7: Trading Cards ===")
    
    with SteamAPIs(API_KEY) as client:
        try:
            # Get all trading cards
            all_cards = client.get_all_cards()
            
            data = all_cards['data']
            print(f"Total games with cards: {data['games']:,}")
            print(f"Total normal cards: {data['cards']:,}")
            print(f"Total foil cards: {data['foils']:,}")
            
            # Show first 5 game sets
            print("\nFirst 5 game card sets:")
            for i, card_set in enumerate(data['sets'][:5]):
                game = card_set['game']
                normal = card_set['normal']
                foil = card_set.get('foil', {})
                
                print(f"\n{i+1}. {game} (App ID: {card_set['appid']})")
                print(f"   Normal cards: {normal['count']} - Avg: ${normal['avg']:.2f}")
                print(f"   Set price: ${normal['price']:.2f}")
                if foil:
                    print(f"   Foil cards: {foil.get('count', 0)} - Avg: ${foil.get('avg', 0):.2f}")
                    print(f"   Foil set price: ${foil.get('price', 0):.2f}")
            
        except SteamAPIsError as e:
            print(f"Error getting trading cards: {e}")
    
    print("✓ Trading cards example completed\n")
def example_search_operations():
   """Example 8: Searching the market"""
   print("=== Example 8: Market Search ===")
   
   with SteamAPIs(API_KEY) as client:
       try:
           # Search for AK-47 skins
           search_results = client.get_market_search(CSGO_APP_ID, "ak-47", count=10)
           
           print("Search results for 'ak-47':")
           for i, item in enumerate(search_results.get('results', [])[:10]):
               name = item.get('name', 'Unknown')
               price = item.get('sell_price', 0) / 100
               print(f"{i+1}. {name} - ${price:.2f}")
           
           # Get popular items
           popular_items = client.get_popular_items(CSGO_APP_ID, count=5)
           print("\nTop 5 popular items:")
           for i, item in enumerate(popular_items.get('items', [])):
               print(f"{i+1}. {item.get('name', 'Unknown')}")
           
           # Get recent items
           recent_items = client.get_recent_items(CSGO_APP_ID, count=5)
           print("\n5 recently listed items:")
           for i, item in enumerate(recent_items.get('items', [])):
               print(f"{i+1}. {item.get('name', 'Unknown')}")
           
       except SteamAPIsError as e:
           print(f"Error searching market: {e}")
   
   print("✓ Search operations completed\n")


def example_bulk_operations():
   """Example 9: Bulk operations for multiple items"""
   print("=== Example 9: Bulk Operations ===")
   
   with SteamAPIs(API_KEY) as client:
       # List of items to check prices for
       items = [
           "AK-47 | Redline (Field-Tested)",
           "AWP | Dragon Lore (Factory New)",
           "M4A4 | Howl (Factory New)",
           "Karambit | Doppler (Factory New)"
       ]
       
       try:
           # Get prices for multiple items at once
           price_data = client.get_price_overview(CSGO_APP_ID, items)
           
           print("Bulk price check:")
           for item_name, data in price_data.get('items', {}).items():
               price = data.get('lowest_price', 'N/A')
               print(f"- {item_name}: ${price}")
           
       except SteamAPIsError as e:
           print(f"Error in bulk operations: {e}")
   
   print("✓ Bulk operations completed\n")


def example_float_values():
   """Example 10: Getting float values for CS:GO items"""
   print("=== Example 10: Float Values (CS:GO) ===")
   
   with SteamAPIs(API_KEY) as client:
       # Example inspect link (this is just a placeholder)
       inspect_link = "steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561198084749846A12345678910D12345678987654321"
       
       try:
           float_info = client.get_float_value(inspect_link)
           
           print(f"Float Value: {float_info.get('float_value', 'N/A')}")
           print(f"Paint Seed: {float_info.get('paint_seed', 'N/A')}")
           print(f"Paint Index: {float_info.get('paint_index', 'N/A')}")
           print(f"Wear Tier: {float_info.get('wear_tier', 'N/A')}")
           
       except SteamAPIsError as e:
           print(f"Error getting float value: {e}")
   
   print("✓ Float value examples completed\n")


def example_error_handling():
   """Example 11: Proper error handling"""
   print("=== Example 11: Error Handling ===")
   
   with SteamAPIs(API_KEY) as client:
       try:
           # This might fail if the user's inventory is private
           inventory = client.get_inventory('invalid_steam_id', CSGO_APP_ID)
           
       except RateLimitError as e:
           print(f"Rate limit exceeded: {e}")
           print("Waiting before retrying...")
           # Implement exponential backoff or wait strategy
           
       except SteamAPIsError as e:
           print(f"Steam API error: {e}")
           # Log the error or handle it appropriately
       
       except Exception as e:
           print(f"Unexpected error: {e}")
           # Handle unexpected errors
   
   print("✓ Error handling examples completed\n")


def example_advanced_usage():
   """Example 12: Advanced usage patterns"""
   print("=== Example 12: Advanced Usage ===")
   
   # Custom configuration
   client = SteamAPIs(
       api_key=API_KEY,
       base_url='https://api.steamapis.com',  # Custom base URL if needed
       timeout=60  # Custom timeout
   )
   
   try:
       # Analyzing item price stability
       print("Analyzing item price stability...")
       items = client.get_items_for_app(CSGO_APP_ID)
       
       unstable_items = []
       stable_items = []
       
       for item in items['data'][:50]:  # Check first 50 items
           if item['prices']['unstable']:
               unstable_items.append({
                   'name': item['market_name'],
                   'reason': item['prices']['unstable_reason']
               })
           else:
               stable_items.append(item['market_name'])
       
       print(f"\nUnstable items ({len(unstable_items)}):")
       for item in unstable_items[:5]:
           print(f"- {item['name']}: {item['reason']}")
       
       print(f"\nStable items: {len(stable_items)}")
       
       # Get app details for multiple games
       app_ids = [730, 570, 440]  # CS:GO, Dota 2, TF2
       print("\n\nComparing popular Valve games:")
       
       for app_id in app_ids:
           app = client.get_app_details(app_id)
           print(f"\n{app['name']}:")
           print(f"  Type: {app['type']}")
           print(f"  Free: {app['is_free']}")
           print(f"  Recommendations: {app.get('recommendations', {}).get('total', 0):,}")
           
   except SteamAPIsError as e:
       print(f"Error in advanced usage: {e}")
   
   finally:
       client.close()
   
   print("✓ Advanced usage examples completed\n")


def example_real_world_scenario():
   """Example 13: Real-world scenario - Market analysis tool"""
   print("=== Example 13: Market Analysis Tool ===")
   
   with SteamAPIs(API_KEY) as client:
       try:
           # Get market statistics
           stats = client.get_market_stats()
           print(f"Market Overview:")
           print(f"Total items: {stats['count']:,}")
           print(f"Total value: ${stats['stats']['totalSpent']:,.2f}")
           
           # Analyze CS:GO market
           print(f"\n\nCS:GO Market Analysis:")
           
           # Get all CS:GO items in compact format
           cs_prices = client.get_items_for_app(CSGO_APP_ID, format='compact')
           
           # Filter out items with no price
           priced_items = {k: v for k, v in cs_prices.items() if v is not None}
           
           # Calculate statistics
           prices = list(priced_items.values())
           if prices:
               avg_price = sum(prices) / len(prices)
               max_price = max(prices)
               min_price = min(prices)
               
               print(f"Total items with prices: {len(priced_items)}")
               print(f"Average price: ${avg_price:.2f}")
               print(f"Highest price: ${max_price:.2f}")
               print(f"Lowest price: ${min_price:.2f}")
               
               # Find most expensive items
               sorted_items = sorted(priced_items.items(), key=lambda x: x[1], reverse=True)
               print(f"\nTop 5 most expensive items:")
               for i, (name, price) in enumerate(sorted_items[:5]):
                   print(f"{i+1}. {name}: ${price:.2f}")
               
               # Price ranges
               print(f"\nPrice distribution:")
               ranges = {
                   "Under $1": len([p for p in prices if p < 1]),
                   "$1-$10": len([p for p in prices if 1 <= p < 10]),
                   "$10-$100": len([p for p in prices if 10 <= p < 100]),
                   "$100-$1000": len([p for p in prices if 100 <= p < 1000]),
                   "Over $1000": len([p for p in prices if p >= 1000])
               }
               
               for range_name, count in ranges.items():
                   percentage = (count / len(prices)) * 100
                   print(f"  {range_name}: {count} items ({percentage:.1f}%)")
           
       except SteamAPIsError as e:
           print(f"Error in market analysis: {e}")
   
   print("✓ Market analysis completed\n")


def example_portfolio_tracker():
   """Example 14: Portfolio tracker with multiple users"""
   print("=== Example 14: Portfolio Tracker ===")
   
   # Track multiple users' inventories
   users = [
       {'steam_id': '76561197993496553', 'name': 'User1'},
       {'steam_id': '76561198084749846', 'name': 'User2'},
   ]
   
   with SteamAPIs(API_KEY) as client:
       portfolio_value = 0
       all_items = []
       
       for user in users:
           try:
               # Get inventory value for each user
               value_data = client.get_inventory_value(user['steam_id'], CSGO_APP_ID)
               user_value = value_data.get('total_value', 0)
               portfolio_value += user_value
               
               print(f"{user['name']}: ${user_value:.2f}")
               
               # Get inventory items
               inventory = client.get_inventory(user['steam_id'], CSGO_APP_ID)
               items = inventory.get('items', [])
               
               # Add user info to items
               for item in items:
                   item['owner'] = user['name']
                   all_items.append(item)
               
               # Show top 3 most valuable items
               sorted_items = sorted(items, key=lambda x: x.get('price', 0), reverse=True)[:3]
               
               print(f"  Top 3 items:")
               for item in sorted_items:
                   print(f"    - {item.get('name', 'Unknown')}: ${item.get('price', 0):.2f}")
               
           except SteamAPIsError as e:
               print(f"  Error getting data for {user['name']}: {e}")
           
           print()
       
       print(f"Total Portfolio Value: ${portfolio_value:.2f}")
       
       # Find most common items across all users
       item_counts = {}
       for item in all_items:
           name = item.get('name', 'Unknown')
           item_counts[name] = item_counts.get(name, 0) + 1
       
       print(f"\nMost common items in portfolio:")
       sorted_counts = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
       for name, count in sorted_counts:
           print(f"- {name}: {count} copies")
   
   print("✓ Portfolio tracker completed\n")


def main():
   """Run all examples"""
   print("SteamAPIs Python Library Examples")
   print("=================================\n")
   
   # Check if API key is set
   if API_KEY == 'YOUR_API_KEY_HERE':
       print("ERROR: Please set your API key before running examples!")
       print("You can set it in the code or as an environment variable:")
       print("export STEAMAPIS_API_KEY='your_actual_key'")
       return
   
   # Run all examples
   examples = [
       example_basic_usage,
       example_market_statistics,
       example_app_operations,
       example_inventory_operations,
       example_item_details,
       example_items_with_format,
       example_trading_cards,
       example_search_operations,
       example_bulk_operations,
       example_float_values,
       example_error_handling,
       example_advanced_usage,
       example_real_world_scenario,
       example_portfolio_tracker
   ]
   
   for example in examples:
       try:
           example()
       except Exception as e:
           print(f"Example failed: {e}\n")
           continue
   
   print("All examples completed!")


if __name__ == "__main__":
   main()
