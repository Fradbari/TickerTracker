"""Debug script for E2E testing."""
import asyncio
from src.market_data.api.dependencies import get_market_data_provider


async def test():
    """Test provider inline."""
    try:
        print("Getting provider...")
        provider = get_market_data_provider()
        print(f"Provider type: {type(provider).__name__}")
        
        print("\nFetching AAPL current price...")
        price = await provider.get_current_price('AAPL')
        
        print(f"\n✓ SUCCESS!")
        print(f"  Symbol: {price.symbol}")
        print(f"  Close: ${price.close}")
        print(f"  Date: {price.date}")
        print(f"  Source: {price.source}")
        
    except Exception as e:
        print(f"\n✗ FAILED!")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {e}")
        import traceback
        print(f"\nFull stack trace:")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test())
