"""
Test the enhanced Yahoo provider with better rate limit handling.
"""

import asyncio
import sys
sys.path.insert(0, ".")

from src.market_data.services.yahoo_provider_enhanced import EnhancedYahooMarketDataProvider

async def test_enhanced_provider():
    """Test enhanced provider."""
    print("=" * 80)
    print("TESTING ENHANCED YAHOO PROVIDER")
    print("=" * 80)
    
    provider = EnhancedYahooMarketDataProvider(
        timeout=30,
        min_delay=2.0  # 2 second delay between requests
    )
    
    # Test 1: Current price
    print("\n1. Testing current price for AAPL...")
    try:
        price = await provider.get_current_price("AAPL")
        print(f"   ✓ SUCCESS!")
        print(f"   - Symbol: {price.symbol}")
        print(f"   - Close: ${price.close}")
        print(f"   - Date: {price.date}")
        print(f"   - Source: {price.source}")
    except Exception as e:
        print(f"   ✗ FAILED: {type(e).__name__}: {e}")
    
    # Test 2: Different ticker
    print("\n2. Testing current price for MSFT...")
    try:
        price = await provider.get_current_price("MSFT")
        print(f"   ✓ SUCCESS!")
        print(f"   - Symbol: {price.symbol}")
        print(f"   - Close: ${price.close}")
    except Exception as e:
        print(f"   ✗ FAILED: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_enhanced_provider())
