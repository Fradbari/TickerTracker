"""
Diagnostic script to test yfinance directly and identify Yahoo API issues.
"""

import yfinance as yf
import sys

def test_yfinance_directly():
    """Test yfinance package directly."""
    print("=" * 80)
    print("YFINANCE DIAGNOSTIC TEST")
    print("=" * 80)
    
    # Check version
    print(f"\n1. yfinance version: {yf.__version__}")
    
    # Test simple ticker creation
    print("\n2. Creating ticker object...")
    try:
        ticker = yf.Ticker("AAPL")
        print(f"   ✓ Ticker object created: {ticker}")
    except Exception as e:
        print(f"   ✗ ERROR creating ticker: {e}")
        return
    
    # Test history fetch
    print("\n3. Fetching history (2d)...")
    try:
        hist = ticker.history(period="2d", interval="1d")
        print(f"   ✓ History returned")
        print(f"   - Shape: {hist.shape}")
        print(f"   - Empty: {hist.empty}")
        if not hist.empty:
            print(f"   - Columns: {hist.columns.tolist()}")
            print(f"   - Last row:\n{hist.tail(1)}")
        else:
            print("   ⚠ WARNING: History DataFrame is EMPTY")
    except Exception as e:
        print(f"   ✗ ERROR fetching history: {e}")
        import traceback
        traceback.print_exc()
    
    # Test info endpoint
    print("\n4. Fetching info...")
    try:
        info = ticker.info
        if info:
            print(f"   ✓ Info returned")
            print(f"   - Symbol: {info.get('symbol', 'N/A')}")
            print(f"   - Name: {info.get('longName', 'N/A')}")
            print(f"   - Current Price: {info.get('currentPrice', 'N/A')}")
        else:
            print("   ⚠ WARNING: No info data")
    except Exception as e:
        print(f"   ✗ ERROR fetching info: {e}")
    
    # Test alternative ticker
    print("\n5. Testing alternative ticker (MSFT)...")
    try:
        msft = yf.Ticker("MSFT")
        msft_hist = msft.history(period="1d")
        print(f"   - MSFT history shape: {msft_hist.shape}")
        print(f"   - MSFT history empty: {msft_hist.empty}")
    except Exception as e:
        print(f"   ✗ ERROR with MSFT: {e}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_yfinance_directly()
