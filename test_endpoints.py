"""
SteamAPIs Endpoint Test Suite
=============================

This file tests all endpoints to ensure they're working correctly.
Just set your API key below and run this file to test all endpoints.

Usage:
    python test_endpoints.py
    
    # Or test specific categories
    python test_endpoints.py --category market_stats
    python test_endpoints.py --category all
"""

import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Any

# ===== SET YOUR API KEY HERE =====
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
# =================================

# If you prefer not to have your API key in the code, you can leave it blank
# and set the STEAMAPIS_API_KEY environment variable instead

# Test configuration
TEST_STEAM_ID = '76561197993496553'
TEST_APP_ID = 730  # CS:GO
TEST_ITEM_NAME = 'AK-47 | Redline (Field-Tested)'
TEST_INSPECT_LINK = 'steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561198084749846A12345678910D12345678987654321'

# Import steamapis library - we'll use the new simplified interface
import steamapis
from steamapis import SteamAPIsError, APIKeyError, RateLimitError

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class EndpointTester:
    """Test suite for all SteamAPIs endpoints"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
        # Configure the global client - only need to set API key once
        steamapis.configure(api_key)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up the global client
        steamapis.close()
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    def print_test_result(self, test_name: str, success: bool, message: str = "", 
                         response_time: float = 0, data_preview: Any = None):
        """Print formatted test result"""
        self.total_tests += 1
        
        if success:
            self.passed_tests += 1
            status = f"{Colors.OKGREEN}✓ PASSED{Colors.ENDC}"
        else:
            self.failed_tests += 1
            status = f"{Colors.FAIL}✗ FAILED{Colors.ENDC}"
        
        print(f"\n{Colors.BOLD}Test:{Colors.ENDC} {test_name}")
        print(f"{Colors.BOLD}Status:{Colors.ENDC} {status}")
        
        if response_time > 0:
            print(f"{Colors.BOLD}Response Time:{Colors.ENDC} {response_time:.2f}s")
        
        if message:
            print(f"{Colors.BOLD}Message:{Colors.ENDC} {message}")
        
        if data_preview:
            print(f"{Colors.BOLD}Data Preview:{Colors.ENDC}")
            if isinstance(data_preview, dict):
                for key, value in list(data_preview.items())[:3]:
                    print(f"  - {key}: {value}")
            elif isinstance(data_preview, list):
                print(f"  - List with {len(data_preview)} items")
                if data_preview:
                    print(f"  - First item: {data_preview[0]}")
        
        print("-" * 60)
    
    def test_endpoint(self, test_name: str, endpoint_func, *args, **kwargs) -> Tuple[bool, Any]:
        """Test a single endpoint"""
        try:
            start_time = time.time()
            result = endpoint_func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Validate response
            if result is None:
                self.print_test_result(test_name, False, "Received None response")
                return False, None
            
            self.print_test_result(test_name, True, "Endpoint responded successfully", 
                                 response_time, result)
            return True, result
            
        except RateLimitError as e:
            self.print_test_result(test_name, False, f"Rate limit exceeded: {e}")
            self.skipped_tests += 1
            return False, None
            
        except SteamAPIsError as e:
            self.print_test_result(test_name, False, f"API Error: {e}")
            return False, None
            
        except Exception as e:
            self.print_test_result(test_name, False, f"Unexpected error: {type(e).__name__}: {e}")
            return False, None
    
    def test_market_stats(self):
        """Test market statistics endpoint"""
        success, data = self.test_endpoint(
            "Market Statistics",
            steamapis.get_market_stats
        )
        
        if success and data:
            # Validate response structure
            required_fields = ['count', 'stats']
            for field in required_fields:
                if field not in data:
                    print(f"{Colors.WARNING}Warning: Missing field '{field}' in response{Colors.ENDC}")
    
    def test_app_operations(self):
        """Test app-related endpoints"""
        # Test single app details
        success, data = self.test_endpoint(
            "App Details (CS:GO)",
            steamapis.get_app_details,
            TEST_APP_ID
        )
        
        if success and data:
            # Validate response
            if 'name' in data:
                print(f"  {Colors.OKBLUE}App Name: {data['name']}{Colors.ENDC}")
        
        # Test all apps (limited preview)
        success, data = self.test_endpoint(
            "All Apps",
            steamapis.get_all_apps
        )
        
        if success and data:
            print(f"  {Colors.OKBLUE}Total apps: {len(data)}{Colors.ENDC}")
    
    def test_item_operations(self):
        """Test item-related endpoints"""
        # Test single item details
        success, data = self.test_endpoint(
            "Item Details",
            steamapis.get_item_details,
            TEST_APP_ID,
            TEST_ITEM_NAME,
            median_history_days=7
        )
        
        # Test items for app (full format)
        success, data = self.test_endpoint(
            "Items for App (Full Format)",
            steamapis.get_items_for_app,
            TEST_APP_ID
        )
        
        if success and data:
            print(f"  {Colors.OKBLUE}Total items: {len(data.get('data', []))}{Colors.ENDC}")
        
        # Test items for app (compact format)
        success, data = self.test_endpoint(
            "Items for App (Compact Format)",
            steamapis.get_items_for_app,
            TEST_APP_ID,
            format='compact'
        )
        
        if success and data:
            print(f"  {Colors.OKBLUE}Items with prices: {sum(1 for v in data.values() if v is not None)}{Colors.ENDC}")
    
    def test_inventory_operations(self):
        """Test inventory-related endpoints"""
        # Test get inventory
        success, data = self.test_endpoint(
            "Get Inventory",
            steamapis.get_inventory,
            TEST_STEAM_ID,
            TEST_APP_ID,
            count=10
        )
        
        # Test inventory value
        success, data = self.test_endpoint(
            "Get Inventory Value",
            steamapis.get_inventory_value,
            TEST_STEAM_ID,
            TEST_APP_ID
        )
    
    def test_market_operations(self):
        """Test market search and related endpoints"""
        # Test market search
        success, data = self.test_endpoint(
            "Market Search",
            steamapis.get_market_search,
            TEST_APP_ID,
            "ak-47",
            count=5
        )
        
        # Test popular items
        success, data = self.test_endpoint(
            "Popular Items",
            steamapis.get_popular_items,
            TEST_APP_ID,
            count=5
        )
        
        # Test recent items
        success, data = self.test_endpoint(
            "Recent Items",
            steamapis.get_recent_items,
            TEST_APP_ID,
            count=5
        )
        
        # Test item listings
        success, data = self.test_endpoint(
            "Item Listings",
            steamapis.get_item_listings,
            TEST_APP_ID,
            TEST_ITEM_NAME,
            count=5
        )
        
        # Test item orders
        success, data = self.test_endpoint(
            "Item Orders",
            steamapis.get_item_orders,
            TEST_APP_ID,
            TEST_ITEM_NAME
        )
    
    def test_trading_cards(self):
        """Test trading cards endpoint"""
        success, data = self.test_endpoint(
            "Trading Cards",
            steamapis.get_all_cards
        )
        
        if success and data:
            card_data = data.get('data', {})
            print(f"  {Colors.OKBLUE}Total games: {card_data.get('games', 0)}{Colors.ENDC}")
            print(f"  {Colors.OKBLUE}Total cards: {card_data.get('cards', 0)}{Colors.ENDC}")
    
    def test_other_operations(self):
        """Test miscellaneous endpoints"""
        # Test user profile
        success, data = self.test_endpoint(
            "User Profile",
            steamapis.get_user_profile,
            TEST_STEAM_ID
        )
        
        # Test float value (CS:GO specific)
        success, data = self.test_endpoint(
            "Float Value",
            steamapis.get_float_value,
            TEST_INSPECT_LINK
        )
        
        # Test price history
        success, data = self.test_endpoint(
            "Price History",
            steamapis.get_price_history,
            TEST_APP_ID,
            TEST_ITEM_NAME,
            days=7
        )
    
    def test_bulk_operations(self):
        """Test bulk operations"""
        items = [
            "AK-47 | Redline (Field-Tested)",
            "AWP | Dragon Lore (Factory New)"
        ]
        
        success, data = self.test_endpoint(
            "Bulk Price Overview",
            steamapis.get_price_overview,
            TEST_APP_ID,
            items
        )
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        self.print_header("SteamAPIs Endpoint Test Suite")
        
        print(f"{Colors.BOLD}API Key:{Colors.ENDC} {'*' * (len(self.api_key) - 4)}{self.api_key[-4:]}")
        print(f"{Colors.BOLD}Test Started:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.BOLD}Test Steam ID:{Colors.ENDC} {TEST_STEAM_ID}")
        print(f"{Colors.BOLD}Test App ID:{Colors.ENDC} {TEST_APP_ID}")
        
        # Run test categories
        test_categories = [
            ("Market Statistics", self.test_market_stats),
            ("App Operations", self.test_app_operations),
            ("Item Operations", self.test_item_operations),
            ("Inventory Operations", self.test_inventory_operations),
            ("Market Operations", self.test_market_operations),
            ("Trading Cards", self.test_trading_cards),
            ("Other Operations", self.test_other_operations),
            ("Bulk Operations", self.test_bulk_operations),
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n{Colors.OKCYAN}{Colors.BOLD}Testing {category_name}...{Colors.ENDC}")
            try:
                test_func()
                time.sleep(0.5)  # Small delay between categories to avoid rate limits
            except Exception as e:
                print(f"{Colors.FAIL}Category test failed: {e}{Colors.ENDC}")
        
        # Print summary
        self.print_summary()
    
    def run_specific_category(self, category_name: str):
        """Run a specific test category"""
        self.print_header(f"Testing {category_name}")
        
        # Map category names to test functions
        category_map = {
            "market_stats": self.test_market_stats,
            "app": self.test_app_operations,
            "item": self.test_item_operations,
            "inventory": self.test_inventory_operations,
            "market": self.test_market_operations,
            "cards": self.test_trading_cards,
            "other": self.test_other_operations,
            "bulk": self.test_bulk_operations,
        }
        
        if category_name.lower() not in category_map:
            print(f"{Colors.FAIL}Unknown category: {category_name}{Colors.ENDC}")
            print(f"Available categories: {', '.join(category_map.keys())}")
            return
            
        try:
            test_func = category_map[category_name.lower()]
            test_func()
        except Exception as e:
            print(f"{Colors.FAIL}Category test failed: {e}{Colors.ENDC}")
            
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total = self.total_tests
        passed = self.passed_tests
        failed = self.failed_tests
        skipped = self.skipped_tests
        
        print(f"{Colors.BOLD}Total Tests:{Colors.ENDC} {total}")
        print(f"{Colors.OKGREEN}Passed:{Colors.ENDC} {passed}")
        print(f"{Colors.FAIL}Failed:{Colors.ENDC} {failed}")
        print(f"{Colors.WARNING}Skipped:{Colors.ENDC} {skipped}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"\n{Colors.BOLD}Success Rate:{Colors.ENDC} {success_rate:.1f}%")
            
            if success_rate == 100:
                print(f"\n{Colors.OKGREEN}{Colors.BOLD}All tests passed! ✨{Colors.ENDC}")
            elif success_rate >= 80:
                print(f"\n{Colors.WARNING}{Colors.BOLD}Most tests passed, but some issues detected.{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}{Colors.BOLD}Many tests failed. Please check your API key and connection.{Colors.ENDC}")


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Test SteamAPIs endpoints')
    parser.add_argument('--api-key', type=str, help='API key (overrides default)')
    parser.add_argument('--category', type=str, help='Test specific category')
    
    args = parser.parse_args()
    
    # Get API key - priority: command line > environment var > hardcoded
    import os
    api_key = args.api_key or os.environ.get('STEAMAPIS_API_KEY') or API_KEY
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print(f"{Colors.FAIL}Error: No API key provided!{Colors.ENDC}")
        print("Please either:")
        print("1. Edit this file and set your API key at the top")
        print("2. Provide an API key using --api-key")
        print("3. Set STEAMAPIS_API_KEY environment variable")
        sys.exit(1)
    
    # Run tests
    try:
        with EndpointTester(api_key) as tester:
            if args.category:
                tester.run_specific_category(args.category)
            else:
                tester.run_all_tests()
    except APIKeyError:
        print(f"{Colors.FAIL}Error: Invalid API key!{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
