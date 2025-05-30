"""
SteamAPIs Python Library
========================

A comprehensive Python library for interacting with the SteamAPIs service.
This library provides easy access to Steam market data, inventory information,
and various Steam-related endpoints.

Author: Your Name
License: MIT
Version: 1.1.0
"""

import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin, quote
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SteamAPIsError(Exception):
    """Base exception class for SteamAPIs errors"""
    pass


class APIKeyError(SteamAPIsError):
    """Raised when there's an issue with the API key"""
    pass


class APIResponseError(SteamAPIsError):
    """Raised when the API returns an error response"""
    pass


class RateLimitError(SteamAPIsError):
    """Raised when rate limit is exceeded"""
    pass


class SteamAPIs:
    """
    Main class for interacting with the SteamAPIs service.
    
    This class provides methods to access various Steam market data endpoints
    including inventory retrieval, item information, market prices, and more.
    
    Attributes:
        base_url (str): Base URL for the API endpoints
        timeout (int): Request timeout in seconds
        session (requests.Session): Persistent session for API requests
    """
    
    def __init__(self, api_key: str, base_url: str = 'https://api.steamapis.com', timeout: int = 30):
        """
        Initialize the SteamAPIs client.
        
        Args:
            api_key (str): Your SteamAPIs API key
            base_url (str, optional): Base URL for the API. Defaults to 'https://api.steamapis.com'
            timeout (int, optional): Request timeout in seconds. Defaults to 30
            
        Raises:
            APIKeyError: If the API key is invalid or missing
        """
        if not api_key:
            raise APIKeyError("API key is required")
            
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Create a persistent session with the API key pre-configured in default params
        self.session = requests.Session()
        self.session.params = {'api_key': api_key}  # Set API key as default parameter for all requests
        self.session.headers.update({
            'User-Agent': 'SteamAPIs-Python/1.1.0'
        })
        
        logger.info(f"SteamAPIs client initialized with base URL: {self.base_url}")
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                      data: Optional[Dict] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Make a request to the API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            params (Dict, optional): Query parameters
            data (Dict, optional): Request body data
            
        Returns:
            Union[Dict, List]: API response data
            
        Raises:
            APIResponseError: If the API returns an error
            RateLimitError: If rate limit is exceeded
        """
        # No need to add API key to params as it's already in the session's default params
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            # Check for rate limiting
            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise APIResponseError(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise APIResponseError(f"Invalid JSON response: {str(e)}")
    
    def get_market_stats(self) -> Dict[str, Any]:
        """
        Get market statistics displayed on the frontpage.
        
        Returns:
            Dict: Market statistics including count, total spent, total count, total apps
            
        Example:
            >>> stats = client.get_market_stats()
            >>> print(f"Total items: {stats['count']}")
            >>> print(f"Total spent: ${stats['stats']['totalSpent']:,.2f}")
            >>> print(f"Total apps: {stats['stats']['totalApps']}")
        """
        endpoint = '/market/stats'
        return self._make_request('GET', endpoint)
    
    def get_inventory(self, steam_id: str, app_id: int, context_id: int = 2, 
                      count: Optional[int] = None, start_assetid: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a user's Steam inventory.
        
        Args:
            steam_id (str): The Steam ID of the user
            app_id (int): The app ID (e.g., 730 for CS:GO)
            context_id (int, optional): Context ID. Defaults to 2
            count (int, optional): Number of items to retrieve
            start_assetid (str, optional): Asset ID to start from (for pagination)
            
        Returns:
            Dict: Inventory data including items and descriptions
            
        Example:
            >>> client = SteamAPIs('YOUR_API_KEY')
            >>> inventory = client.get_inventory('76561197993496553', 730, 2)
        """
        endpoint = f'/steam/inventory/{steam_id}/{app_id}/{context_id}'
        params = {}
        
        if count:
            params['count'] = count
        if start_assetid:
            params['start_assetid'] = start_assetid
            
        return self._make_request('GET', endpoint, params=params)
    
    def get_items_for_app(self, app_id: int, format: Optional[str] = None,
                          compact_value: str = 'safe') -> Union[Dict[str, Any], Dict[str, float]]:
        """
        Get all items for a specific app/game with price details.
        
        Args:
            app_id (int): The app ID (e.g., 730 for CS:GO)
            format (str, optional): 'compact' for name=>price format, None for full data
            compact_value (str, optional): Value to use when format='compact'. 
                Options: 'latest', 'min', 'avg', 'max', 'mean', 'safe', 
                'safe_ts.last_24h', 'safe_ts.last_7d', 'safe_ts.last_30d', 
                'safe_ts.last_90d', 'unstable', 'unstable_reason'
                Defaults to 'safe'
            
        Returns:
            Dict: List of items with their details and prices, or name=>price mapping if format='compact'
            
        Example:
            >>> # Get full item data
            >>> items = client.get_items_for_app(730)
            >>> 
            >>> # Get compact format with safe prices
            >>> prices = client.get_items_for_app(730, format='compact')
            >>> 
            >>> # Get compact format with latest prices
            >>> latest_prices = client.get_items_for_app(730, format='compact', compact_value='latest')
        """
        endpoint = f'/market/items/{app_id}'
        params = {}
        
        if format:
            params['format'] = format
            params['compact_value'] = compact_value
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_all_cards(self) -> Dict[str, Any]:
        """
        Get all Steam trading cards across all games.
        
        Returns:
            Dict: Contains data about games, cards count, foils count, and sets array
            
        Example:
            >>> cards = client.get_all_cards()
            >>> print(f"Total games: {cards['data']['games']}")
            >>> print(f"Total cards: {cards['data']['cards']}")
            >>> print(f"Total foils: {cards['data']['foils']}")
        """
        endpoint = '/market/items/cards'
        return self._make_request('GET', endpoint)
    
    def get_item_details(self, app_id: int, market_hash_name: str, 
                         median_history_days: int = 15) -> Dict[str, Any]:
        """
        Get detailed information about a specific item.
        
        Args:
            app_id (int): The app ID
            market_hash_name (str): The market hash name of the item
            median_history_days (int, optional): How many median prices to return. Defaults to 15
            
        Returns:
            Dict: Detailed item information including prices, volume, histogram, etc.
            
        Example:
            >>> details = client.get_item_details(730, 'AK-47 | Redline (Field-Tested)')
            >>> print(f"Lowest sell order: ${details['histogram']['lowest_sell_order']}")
            >>> print(f"Highest buy order: ${details['histogram']['highest_buy_order']}")
        """
        # URL encode the market hash name
        encoded_name = quote(market_hash_name, safe='')
        endpoint = f'/market/item/{app_id}/{encoded_name}'
        params = {'median_history_days': median_history_days}
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_price_history(self, app_id: int, market_hash_name: str, 
                          days: int = 30) -> Dict[str, Any]:
        """
        Get price history for a specific item.
        
        Args:
            app_id (int): The app ID
            market_hash_name (str): The market hash name of the item
            days (int, optional): Number of days of history. Defaults to 30
            
        Returns:
            Dict: Price history data with timestamps and prices
            
        Example:
            >>> history = client.get_price_history(730, 'AK-47 | Redline (Field-Tested)')
        """
        encoded_name = quote(market_hash_name, safe='')
        endpoint = f'/market/history/{app_id}/{encoded_name}'
        params = {'days': days}
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_user_profile(self, steam_id: str) -> Dict[str, Any]:
        """
        Get Steam user profile information.
        
        Args:
            steam_id (str): The Steam ID of the user
            
        Returns:
            Dict: User profile data
            
        Example:
            >>> profile = client.get_user_profile('76561197993496553')
        """
        endpoint = f'/steam/user/{steam_id}'
        return self._make_request('GET', endpoint)
    
    def get_market_search(self, app_id: int, query: str, start: int = 0, 
                          count: int = 100, sort_by: str = 'popular', 
                          sort_order: str = 'desc') -> Dict[str, Any]:
        """
        Search the Steam market for items.
        
        Args:
            app_id (int): The app ID
            query (str): Search query
            start (int, optional): Starting offset. Defaults to 0
            count (int, optional): Number of results. Defaults to 100
            sort_by (str, optional): Sort field. Defaults to 'popular'
            sort_order (str, optional): Sort order ('asc' or 'desc'). Defaults to 'desc'
            
        Returns:
            Dict: Search results
            
        Example:
            >>> results = client.get_market_search(730, 'ak-47')
        """
        endpoint = f'/market/search/{app_id}'
        params = {
            'query': query,
            'start': start,
            'count': count,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_item_listings(self, app_id: int, market_hash_name: str, 
                          start: int = 0, count: int = 100) -> Dict[str, Any]:
        """
        Get current market listings for an item.
        
        Args:
            app_id (int): The app ID
            market_hash_name (str): The market hash name of the item
            start (int, optional): Starting offset. Defaults to 0
            count (int, optional): Number of listings. Defaults to 100
            
        Returns:
            Dict: Market listings data
            
        Example:
            >>> listings = client.get_item_listings(730, 'AK-47 | Redline (Field-Tested)')
        """
        encoded_name = quote(market_hash_name, safe='')
        endpoint = f'/market/listings/{app_id}/{encoded_name}'
        params = {
            'start': start,
            'count': count
        }
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_item_orders(self, app_id: int, market_hash_name: str) -> Dict[str, Any]:
        """
        Get buy and sell orders for an item.
        
        Args:
            app_id (int): The app ID
            market_hash_name (str): The market hash name of the item
            
        Returns:
            Dict: Buy and sell order data
            
        Example:
            >>> orders = client.get_item_orders(730, 'AK-47 | Redline (Field-Tested)')
        """
        encoded_name = quote(market_hash_name, safe='')
        endpoint = f'/market/orders/{app_id}/{encoded_name}'
        
        return self._make_request('GET', endpoint)
    
    def get_popular_items(self, app_id: int, count: int = 100) -> Dict[str, Any]:
        """
        Get popular items for an app.
        
        Args:
            app_id (int): The app ID
            count (int, optional): Number of items. Defaults to 100
            
        Returns:
            Dict: List of popular items
            
        Example:
            >>> popular = client.get_popular_items(730)
        """
        endpoint = f'/market/popular/{app_id}'
        params = {'count': count}
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_recent_items(self, app_id: int, count: int = 100) -> Dict[str, Any]:
        """
        Get recently listed items for an app.
        
        Args:
            app_id (int): The app ID
            count (int, optional): Number of items. Defaults to 100
            
        Returns:
            Dict: List of recent items
            
        Example:
            >>> recent = client.get_recent_items(730)
        """
        endpoint = f'/market/recent/{app_id}'
        params = {'count': count}
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_price_overview(self, app_id: int, market_hash_names: List[str]) -> Dict[str, Any]:
        """
        Get price overview for multiple items at once.
        
        Args:
            app_id (int): The app ID
            market_hash_names (List[str]): List of market hash names
            
        Returns:
            Dict: Price data for all requested items
            
        Example:
            >>> prices = client.get_price_overview(730, ['AK-47 | Redline (Field-Tested)', 
            ...                                           'AWP | Dragon Lore (Factory New)'])
        """
        endpoint = f'/market/prices/{app_id}'
        data = {'items': market_hash_names}
        
        return self._make_request('POST', endpoint, data=data)
    
    def get_float_value(self, inspect_link: str) -> Dict[str, Any]:
        """
        Get float value for a CS:GO item using its inspect link.
        
        Args:
            inspect_link (str): The inspect link of the item
            
        Returns:
            Dict: Float value and other item details
            
        Example:
            >>> float_info = client.get_float_value('steam://rungame/730/...')
        """
        endpoint = '/market/float'
        params = {'inspect_link': inspect_link}
        
        return self._make_request('GET', endpoint, params=params)
    
    def get_app_details(self, app_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific app.
        
        Args:
            app_id (int): The app ID
            
        Returns:
            Dict: Detailed app information including name, type, description, 
                  price, platforms, categories, genres, screenshots, etc.
            
        Example:
            >>> details = client.get_app_details(730)
            >>> print(f"Game: {details['name']}")
            >>> print(f"Price: {details['price_overview']['final_formatted']}")
        """
        endpoint = f'/market/app/{app_id}'
        return self._make_request('GET', endpoint)
    
    def get_all_apps(self) -> List[Dict[str, Any]]:
        """
        Get list of all Steam apps/games.
        
        Returns:
            List[Dict]: List of all Steam applications with basic info
            
        Example:
            >>> apps = client.get_all_apps()
            >>> print(f"Total apps: {len(apps)}")
            >>> # Show first 5 apps
            >>> for app in apps[:5]:
            ...     print(f"{app['appID']}: {app['name']} - {app.get('price_overview', {}).get('final_formatted', 'Free')}")
        """
        endpoint = '/market/apps'
        return self._make_request('GET', endpoint)
    
    def get_inventory_value(self, steam_id: str, app_id: int, 
                            context_id: int = 2) -> Dict[str, Any]:
        """
        Calculate the total value of a user's inventory.
        
        Args:
            steam_id (str): The Steam ID of the user
            app_id (int): The app ID
            context_id (int, optional): Context ID. Defaults to 2
            
        Returns:
            Dict: Total inventory value and item breakdown
            
        Example:
            >>> value = client.get_inventory_value('76561197993496553', 730)
        """
        endpoint = f'/steam/inventory/value/{steam_id}/{app_id}/{context_id}'
        
        return self._make_request('GET', endpoint)
    
    def close(self):
        """
        Close the session and clean up resources.
        
        Example:
            >>> client.close()
        """
        self.session.close()
        logger.info("SteamAPIs client session closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Create a global client instance that can be imported and used directly
_default_client = None


def configure(api_key: str, **kwargs) -> SteamAPIs:
    """
    Configure the global SteamAPIs client instance.
    
    Args:
        api_key (str): Your SteamAPIs API key
        **kwargs: Additional arguments to pass to SteamAPIs constructor
        
    Returns:
        SteamAPIs: Configured client instance
        
    Example:
        >>> import steamapis
        >>> steamapis.configure('YOUR_API_KEY')
        >>> # Now you can use any function directly
        >>> stats = steamapis.get_market_stats()
    """
    global _default_client
    _default_client = SteamAPIs(api_key, **kwargs)
    return _default_client


def get_client() -> SteamAPIs:
    """
    Get the configured SteamAPIs client instance.
    
    Returns:
        SteamAPIs: Configured client instance
        
    Raises:
        APIKeyError: If the client hasn't been configured yet
        
    Example:
        >>> client = steamapis.get_client()
    """
    if _default_client is None:
        raise APIKeyError("SteamAPIs client hasn't been configured. Call configure() first.")
    return _default_client


# Convenience function to create a standalone client
def create_client(api_key: str, **kwargs) -> SteamAPIs:
    """
    Create a SteamAPIs client instance.
    
    Args:
        api_key (str): Your SteamAPIs API key
        **kwargs: Additional arguments to pass to SteamAPIs constructor
        
    Returns:
        SteamAPIs: Client instance
        
    Example:
        >>> client = create_client('YOUR_API_KEY')
    """
    return SteamAPIs(api_key, **kwargs)


# Proxy methods for the global client to enable direct module-level access
def get_market_stats() -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_market_stats using the global client"""
    return get_client().get_market_stats()


def get_inventory(steam_id: str, app_id: int, context_id: int = 2, 
                  count: Optional[int] = None, start_assetid: Optional[str] = None) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_inventory using the global client"""
    return get_client().get_inventory(steam_id, app_id, context_id, count, start_assetid)


def get_items_for_app(app_id: int, format: Optional[str] = None,
                      compact_value: str = 'safe') -> Union[Dict[str, Any], Dict[str, float]]:
    """Proxy for SteamAPIs.get_items_for_app using the global client"""
    return get_client().get_items_for_app(app_id, format, compact_value)


def get_all_cards() -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_all_cards using the global client"""
    return get_client().get_all_cards()


def get_item_details(app_id: int, market_hash_name: str, 
                     median_history_days: int = 15) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_item_details using the global client"""
    return get_client().get_item_details(app_id, market_hash_name, median_history_days)


def get_price_history(app_id: int, market_hash_name: str, 
                      days: int = 30) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_price_history using the global client"""
    return get_client().get_price_history(app_id, market_hash_name, days)


def get_user_profile(steam_id: str) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_user_profile using the global client"""
    return get_client().get_user_profile(steam_id)


def get_market_search(app_id: int, query: str, start: int = 0, 
                      count: int = 100, sort_by: str = 'popular', 
                      sort_order: str = 'desc') -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_market_search using the global client"""
    return get_client().get_market_search(app_id, query, start, count, sort_by, sort_order)


def get_item_listings(app_id: int, market_hash_name: str, 
                      start: int = 0, count: int = 100) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_item_listings using the global client"""
    return get_client().get_item_listings(app_id, market_hash_name, start, count)


def get_item_orders(app_id: int, market_hash_name: str) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_item_orders using the global client"""
    return get_client().get_item_orders(app_id, market_hash_name)


def get_popular_items(app_id: int, count: int = 100) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_popular_items using the global client"""
    return get_client().get_popular_items(app_id, count)


def get_recent_items(app_id: int, count: int = 100) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_recent_items using the global client"""
    return get_client().get_recent_items(app_id, count)


def get_price_overview(app_id: int, market_hash_names: List[str]) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_price_overview using the global client"""
    return get_client().get_price_overview(app_id, market_hash_names)


def get_float_value(inspect_link: str) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_float_value using the global client"""
    return get_client().get_float_value(inspect_link)


def get_app_details(app_id: int) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_app_details using the global client"""
    return get_client().get_app_details(app_id)


def get_all_apps() -> List[Dict[str, Any]]:
    """Proxy for SteamAPIs.get_all_apps using the global client"""
    return get_client().get_all_apps()


def get_inventory_value(steam_id: str, app_id: int, 
                        context_id: int = 2) -> Dict[str, Any]:
    """Proxy for SteamAPIs.get_inventory_value using the global client"""
    return get_client().get_inventory_value(steam_id, app_id, context_id)


def close():
    """Proxy for SteamAPIs.close using the global client"""
    if _default_client is not None:
        _default_client.close()
