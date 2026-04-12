"""
Domain service for evaluating target hits (Take Profit, Stop Loss) and timeouts
for trading estimates. Only supports LONG direction and uses a conservative approach
when extreme volatility hits both target and stop-loss within the same candlestick.
"""

from datetime import UTC, datetime
from decimal import Decimal

from src.estimates.domain.entities import Direction, Estimate, EstimateStatus


class TargetEvaluationResult:
    """Result of evaluating a target."""
    def __init__(self, hit: bool, reason: str = None, exit_price: Decimal = None, exit_date: datetime = None):
        self.hit = hit
        self.reason = reason  # "take_profit", "stop_loss", "timeout"
        self.exit_price = exit_price
        self.exit_date = exit_date


class TargetEvaluationService:
    """
    Evaluates if an estimate has hit its target, stop loss, or timeout.
    Specifically designed for the LONG approach and historical downtime recovery.
    """

    @staticmethod
    def evaluate_estimate(estimate: Estimate, ohlcv_data: list[dict], duration_days: int) -> TargetEvaluationResult:
        """
        Evaluate an estimate against historical daily OHLCV candles to see if it should close.

        Args:
            estimate: The open estimate to evaluate.
            ohlcv_data: A chronological list of daily dictionary records with
                        keys: 'date', 'open', 'high', 'low', 'close'
            duration_days: The maximum lifetime of the estimate in calendar days.

        Returns:
            TargetEvaluationResult indicating if the estimate should be closed.
        """
        if estimate.status != EstimateStatus.OPEN:
            return TargetEvaluationResult(hit=False)

        # Assure we only evaluate LONG direction logic mathematically
        if estimate.direction != Direction.LONG:
            # We ignore short for now as requested.
            return TargetEvaluationResult(hit=False)

        start_date = estimate.created_at

        # Timeout Check - calculated by strict calendar days from creation
        current_time = datetime.now(UTC)
        days_passed = (current_time - start_date).days

        if days_passed >= duration_days:
            # Close by Timeout
            # We must use the last available close price if OHLCV data is provided
            exit_price = estimate.start_price
            if ohlcv_data:
                # Take the very last available close price
                exit_price = Decimal(str(ohlcv_data[-1].get("close", exit_price)))

            return TargetEvaluationResult(
                hit=True,
                reason="timeout",
                exit_price=exit_price,
                exit_date=current_time
            )

        # Start processing candlesticks looking forward from start_date
        # Ensure chronological order (oldest first)
        sorted_data = sorted(ohlcv_data, key=lambda x: x["date"])

        for candle in sorted_data:
            # Exclude the exact insertion day to strictly match legacy logic
            # where currentPrice handled the first day and dayHigh/Low were skipped.
            # Compare dates (YYYY-MM-DD)
            if candle["date"].date() <= start_date.date():
                continue

            low_price = Decimal(str(candle.get("low", estimate.start_price)))
            high_price = Decimal(str(candle.get("high", estimate.start_price)))

            # Prevent division by zero
            if estimate.start_price <= 0:
                continue

            # Mathematics for LONG position:
            low_change = ((low_price - estimate.start_price) / estimate.start_price) * 100
            high_change = ((high_price - estimate.start_price) / estimate.start_price) * 100

            hit_stop = low_change <= -abs(estimate.stop_loss_percent)
            hit_target = high_change >= abs(estimate.target_profit_percent)

            candle_datetime = candle["date"]
            if not candle_datetime.tzinfo:
                # Naive to aware UTC assumption
                candle_datetime = candle_datetime.replace(tzinfo=UTC)

            # CONSERVATIVE APPROACH:
            # If BOTH are hit in the same candlestick, STOP LOSS wins.
            if hit_stop and hit_target:
                return TargetEvaluationResult(
                    hit=True,
                    reason="stop_loss",
                    exit_price=estimate.stop_loss_price,
                    exit_date=candle_datetime
                )

            if hit_stop:
                return TargetEvaluationResult(
                    hit=True,
                    reason="stop_loss",
                    exit_price=estimate.stop_loss_price,
                    exit_date=candle_datetime
                )

            if hit_target:
                return TargetEvaluationResult(
                    hit=True,
                    reason="take_profit",
                    exit_price=estimate.target_price,
                    exit_date=candle_datetime
                )

        return TargetEvaluationResult(hit=False)
