# SteamAPIs Python Library

A comprehensive Python library for interacting with the SteamAPIs service, providing easy access to Steam market data, inventory information, and various Steam-related endpoints.

## Features

- 🎮 **Complete Steam Market Data Access** - Get real-time prices, listings, and market statistics
- 📦 **Inventory Management** - Retrieve and analyze Steam inventories with ease
- 💰 **Price Tracking** - Monitor item prices, historical data, and market trends
- 🃏 **Trading Cards Support** - Access data for all Steam trading cards
- 🔍 **Advanced Search** - Search items, get popular/recent items, and more
- 🛡️ **Robust Error Handling** - Custom exceptions for different error scenarios
- 🚀 **Performance Optimized** - Persistent sessions and efficient API calls
- 📊 **Market Analytics** - Get market statistics and perform bulk operations
- 🔑 **Simplified Authentication** - Configure your API key once and use throughout your application

## Installation

```bash
# Clone the repository
git clone https://github.com/Sat-14/steamapi.git
cd steamapi.py

# Install dependencies
pip install requests
```

## Quick Start

### Method 1: Global Configuration (Recommended for Scripts)

```python
import steamapis

# Configure once at the beginning of your application
steamapis.configure('YOUR_API_KEY')

# Use module-level functions without needing to pass the API key again
stats = steamapis.get_market_stats()
print(f"Total items tracked: {stats['count']:,}")

# Get item details
item = steamapis.get_item_details(730, 'AK-47 | Redline (Field-Tested)')
print(f"Current price: ${item['histogram']['lowest_sell_order']}")

# Clean up when your application is done
steamapis.close()
```

### Method 2: Client Instance

```python
from steamapis import SteamAPIs

# Initialize the client
client = SteamAPIs('YOUR_API_KEY')

# Use the client
stats = client.get_market_stats()
print(f"Total items tracked: {stats['count']:,}")

# Always close the client when done
client.close()
```

### Method 3: Context Manager

```python
from steamapis import SteamAPIs

with SteamAPIs('YOUR_API_KEY') as client:
    # Client will automatically close when exiting the context
    inventory = client.get_inventory('76561197993496553', 730)
    print(f"Total items: {len(inventory.get('items', []))}")
```

## API Key

Get your API key from SteamAPIs.com to use this library.

## Available Methods

All methods are available both as module-level functions (after calling `steamapis.configure()`) and as instance methods on a `SteamAPIs` client object.

### Market Operations

- `get_market_stats()` - Get overall market statistics
- `get_item_details(app_id, market_hash_name, median_history_days=15)` - Get detailed item information
- `get_items_for_app(app_id, format=None, compact_value='safe')` - Get all items for an app
- `get_price_history(app_id, market_hash_name, days=30)` - Get item price history
- `get_item_listings(app_id, market_hash_name, start=0, count=100)` - Get current market listings
- `get_item_orders(app_id, market_hash_name)` - Get buy/sell orders
- `get_market_search(app_id, query, start=0, count=100, sort_by='popular', sort_order='desc')` - Search market
- `get_popular_items(app_id, count=100)` - Get popular items
- `get_recent_items(app_id, count=100)` - Get recently listed items
- `get_price_overview(app_id, market_hash_names)` - Bulk price check

### Inventory Operations

- `get_inventory(steam_id, app_id, context_id=2, count=None, start_assetid=None)` - Get user inventory
- `get_inventory_value(steam_id, app_id, context_id=2)` - Calculate inventory value

### App Operations

- `get_app_details(app_id)` - Get detailed app information
- `get_all_apps()` - Get list of all Steam apps

### Trading Cards

- `get_all_cards()` - Get all Steam trading cards data

### Other Operations

- `get_user_profile(steam_id)` - Get Steam user profile
- `get_float_value(inspect_link)` - Get CS:GO float values

## Examples

### Global Configuration (Module-level Functions)

```python
import steamapis

# Configure once
steamapis.configure('YOUR_API_KEY')

# Get market statistics
stats = steamapis.get_market_stats()
print(f"Total spent: ${stats['stats']['totalSpent']:,.2f}")
print(f"Total items: {stats['stats']['totalCount']:,}")

# Get inventory
inventory = steamapis.get_inventory('76561197993496553', 730)
print(f"Total items: {len(inventory.get('items', []))}")

# Clean up
steamapis.close()
```

### Get Item Prices in Different Formats

```python
import steamapis

# Configure once
steamapis.configure('YOUR_API_KEY')

# Full data format
items = steamapis.get_items_for_app(730)
for item in items['data'][:5]:
    print(f"{item['market_name']}: ${item['prices']['safe']}")

# Compact format (name => price)
prices = steamapis.get_items_for_app(730, format='compact')
print(prices['AK-47 | Redline (Field-Tested)'])
```

### Search and Track Items

```python
import steamapis

# Configure once
steamapis.configure('YOUR_API_KEY')

# Search for items
results = steamapis.get_market_search(730, 'butterfly knife')

# Get item details with price history
item = steamapis.get_item_details(730, 'Butterfly Knife | Fade (Factory New)', 
                                median_history_days=30)

# Check current orders
print(f"Buy orders: {item['histogram']['buy_order_summary']['quantity']}")
print(f"Sell orders: {item['histogram']['sell_order_summary']['quantity']}")
```

### Portfolio Analysis

```python
import steamapis

# Configure once
steamapis.configure('YOUR_API_KEY')

# Get inventory value
value = steamapis.get_inventory_value('76561197993496553', 730)
print(f"Total value: ${value['total_value']:.2f}")

# Get trading cards
cards = steamapis.get_all_cards()
print(f"Total games with cards: {cards['data']['games']:,}")
```

## Error Handling

The library provides custom exceptions for different error scenarios:

```python
import steamapis
from steamapis import APIKeyError, RateLimitError, APIResponseError

try:
    # Configure once
    steamapis.configure('YOUR_API_KEY')
    
    # Use module-level functions
    data = steamapis.get_inventory('invalid_id', 730)
    
except APIKeyError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except APIResponseError as e:
    print(f"API error: {e}")
```

## Advanced Usage

### Custom Configuration

#### Global Client with Custom Settings

```python
import steamapis

# Configure with custom settings
steamapis.configure(
    api_key='YOUR_API_KEY',
    base_url='https://api.steamapis.com',  # Custom base URL
    timeout=60  # Custom timeout in seconds
)
```

#### Custom Client Instance

```python
from steamapis import SteamAPIs

# Create a client with custom settings
client = SteamAPIs(
    api_key='YOUR_API_KEY',
    base_url='https://api.steamapis.com',  # Custom base URL
    timeout=60  # Custom timeout in seconds
)
```

### Bulk Operations

```python
import steamapis

# Configure once
steamapis.configure('YOUR_API_KEY')

# Check prices for multiple items at once
items = [
    "AK-47 | Redline (Field-Tested)",
    "AWP | Dragon Lore (Factory New)",
    "Karambit | Fade (Factory New)"
]

prices = steamapis.get_price_overview(730, items)
```

### Using Multiple Clients with Different Settings

```python
from steamapis import create_client

# Create different clients for different purposes
default_client = create_client('YOUR_API_KEY')
fast_client = create_client('YOUR_API_KEY', timeout=5)  # Short timeout
backup_client = create_client('YOUR_API_KEY', base_url='https://backup-api.example.com')

# Use them independently
stats = default_client.get_market_stats()
search_results = fast_client.get_market_search(730, 'knife')
```

## Testing

Run the test suite to verify all endpoints:

```bash
# Set API key at the top of the file or use --api-key parameter
python test_endpoints.py

# Test specific category
python test_endpoints.py --category market_stats
```

Run the examples:

```bash
# Set API key at the top of the file or use environment variable
python examples.py
```

## Requirements

- Python 3.6+
- requests library

## Rate Limits

Please be mindful of rate limits when using the API. The library will raise RateLimitError when limits are exceeded.

## License

MIT License - see LICENSE file for details

## Support

- Documentation: SteamAPIs Docs
- Issues: GitHub Issues
- API Support: SteamAPIs Support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This library is not affiliated with Valve Corporation or Steam. All trademarks are property of their respective owners.
