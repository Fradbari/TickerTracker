import asyncio
import uuid
from decimal import Decimal
from datetime import datetime, timezone

from src.estimates.domain.entities import Estimate, EstimateStatus, Direction
from src.estimates.domain.services.target_checker import TargetEvaluationService

# Ensure all models are loaded
from src.market_data.domain.entities import Ticker
from src.market_data.domain.market_data import MarketData

def run_tests():
    print("Running TargetEvaluationService checks...")
    
    start_date = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    
    est = Estimate(
        id=uuid.uuid4(),
        ticker_id=uuid.uuid4(),
        start_price=Decimal("100.0"),
        target_price=Decimal("110.0"),
        stop_loss_price=Decimal("90.0"),
        target_profit_percent=Decimal("10.0"),
        stop_loss_percent=Decimal("-10.0"),
        status=EstimateStatus.OPEN,
        direction=Direction.LONG,
        created_at=start_date
    )

    # 1. Test timeout
    result = TargetEvaluationService.evaluate_estimate(est, [], duration_days=60)
    print(f"Timeout Test Output: hit={result.hit}, reason={result.reason}")

    # 2. Hit target next day
    ohlcv = [
        {"date": datetime(2026, 1, 2, tzinfo=timezone.utc), "low": 98.0, "high": 111.0, "close": 110.0}
    ]
    result2 = TargetEvaluationService.evaluate_estimate(est, ohlcv, duration_days=60)
    print(f"Target Hit Test Output: hit={result2.hit}, reason={result2.reason}")

    # 3. Hit Stop Loss next day
    ohlcv_stop = [
        {"date": datetime(2026, 1, 2, tzinfo=timezone.utc), "low": 89.0, "high": 105.0, "close": 90.0}
    ]
    result3 = TargetEvaluationService.evaluate_estimate(est, ohlcv_stop, duration_days=60)
    print(f"Stop Loss Hit Test Output: hit={result3.hit}, reason={result3.reason}")

    # 4. Same day insertion ignored
    ohlcv_same = [
        {"date": datetime(2026, 1, 1, 14, 0, tzinfo=timezone.utc), "low": 80.0, "high": 120.0, "close": 100.0}
    ]
    result4 = TargetEvaluationService.evaluate_estimate(est, ohlcv_same, duration_days=60)
    print(f"Same Day Insertion check Output: hit={result4.hit}, reason={result4.reason}")

    # 5. Extreme volatility conservative approach (Hit both)
    ohlcv_both = [
        {"date": datetime(2026, 1, 3, tzinfo=timezone.utc), "low": 80.0, "high": 120.0, "close": 100.0}
    ]
    result5 = TargetEvaluationService.evaluate_estimate(est, ohlcv_both, duration_days=60)
    print(f"Extreme Volatility Test Output: hit={result5.hit}, reason={result5.reason}")


if __name__ == "__main__":
    run_tests()
