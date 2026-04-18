"""
Domain service for evaluating target hits (Take Profit, Stop Loss) and timeouts
for trading estimates. Supports LONG and SHORT directions and uses a conservative approach
when extreme volatility hits both target and stop-loss within the same candlestick.
"""

from datetime import UTC, datetime
from decimal import Decimal

from src.estimates.domain.entities import Estimate, EstimateStatus


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

        start_date = estimate.created_at

        # Timeout Check - calculated by strict calendar days from creation
        current_time = datetime.now(UTC)
        days_passed = (current_time - start_date).days

        if days_passed >= duration_days:
            # Close by Timeout
            exit_price = estimate.start_price
            if ohlcv_data:
                exit_price = Decimal(str(ohlcv_data[-1].get("close", exit_price)))

            return TargetEvaluationResult(
                hit=True,
                reason="timeout",
                exit_price=exit_price,
                exit_date=current_time
            )

        sorted_data = sorted(ohlcv_data, key=lambda x: x["date"])

        for candle in sorted_data:
            if candle["date"].date() <= start_date.date():
                continue

            low_price = Decimal(str(candle.get("low", estimate.start_price)))
            high_price = Decimal(str(candle.get("high", estimate.start_price)))

            if estimate.start_price <= 0:
                continue

            low_change = ((low_price - estimate.start_price) / estimate.start_price) * 100
            high_change = ((high_price - estimate.start_price) / estimate.start_price) * 100

            hit_stop = low_change <= -abs(estimate.stop_loss_percent)
            hit_target = high_change >= abs(estimate.target_profit_percent)

            candle_datetime = candle["date"]
            if not candle_datetime.tzinfo:
                candle_datetime = candle_datetime.replace(tzinfo=UTC)

            # CONSERVATIVE APPROACH
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
