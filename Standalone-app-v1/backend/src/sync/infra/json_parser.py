
import json
import logging
from datetime import date, datetime
from decimal import Decimal

from src.sync.infra.legacy_models import LegacyEstimateRow

logger = logging.getLogger(__name__)

class LegacyJsonParser:
    """
    Parser for legacy TickerTracker JSON backup format (Version 4.0+).
    """

    def parse_backup_json(self, content: str) -> list[LegacyEstimateRow]:
        """
        Parse legacy JSON backup into LegacyEstimateRow objects.

        Args:
            content: JSON content as string

        Returns:
            List of LegacyEstimateRow objects
        """
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            raise ValueError(f"Invalid JSON format: {e}")

        # Handle both list format (older) and dict format with 'estimates' key (v4.0+)
        if isinstance(data, list):
            estimates_data = data
        elif isinstance(data, dict) and "estimates" in data:
            estimates_data = data["estimates"]
        else:
            logger.warning("JSON backup has unrecognized structure, trying to find list of objects")
            # Fallback: find any list and hope it's the estimates
            estimates_data = []
            for val in data.values():
                if isinstance(val, list):
                    estimates_data = val
                    break

        rows = []
        for item in estimates_data:
            try:
                # Mapping JSON keys to LegacyEstimateRow
                # Handle status transition
                raw_status = str(item.get("status", "OPEN")).lower()
                status = "OPEN"
                if "negative" in raw_status or "loss" in raw_status:
                    status = "CLOSED_LOSS"
                elif "positive" in raw_status or "win" in raw_status:
                    status = "CLOSED_WIN"
                elif "completed" in raw_status or "manual" in raw_status:
                    status = "CLOSED_MANUAL"
                elif "expired" in raw_status:
                    status = "EXPIRED"

                # Start Date parsing
                start_date_str = item.get("startDate", "")
                start_date = date.today()
                if start_date_str:
                    try:
                        # Handle ISO format with Z
                        start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")).date()
                    except ValueError:
                        pass

                # Prices and Percents
                start_price = Decimal(str(item.get("startPrice", 0)))
                target_pct = Decimal(str(item.get("profitTarget", 0)))
                stop_pct = Decimal(str(item.get("stopLoss", 0)))

                # Calculate absolute target/stop if missing but percents present
                target_price = Decimal(str(item.get("targetPrice", 0)))
                if target_price == 0 and start_price > 0 and target_pct != 0:
                    target_price = start_price * (1 + target_pct / 100)

                stop_loss_price = Decimal(str(item.get("stopLossPrice", 0)))
                if stop_loss_price == 0 and start_price > 0 and stop_pct != 0:
                    stop_loss_price = start_price * (1 + stop_pct / 100)

                legacy_row = LegacyEstimateRow(
                    ticker=str(item.get("ticker", "UNKNOWN")).upper(),
                    start_date=start_date,
                    start_price=start_price,
                    target_price=target_price,
                    stop_loss_price=stop_loss_price,
                    target_profit_percent=target_pct,
                    stop_loss_percent=stop_pct,
                    direction=str(item.get("direction", "LONG")).upper(),
                    status=status,
                    ai_model=item.get("aiName") or item.get("aiModel"),
                    ai_confidence=Decimal(str(item.get("aiConfidence", 0))) if item.get("aiConfidence") else None,
                    realized_pnl_percent=Decimal(str(item.get("profitLossPercent", 0))) if item.get("profitLossPercent") else None,
                    exit_price=Decimal(str(item.get("endPrice", 0))) if item.get("endPrice") else None,
                    close_date=None, # Extract if present
                    current_price=Decimal(str(item.get("currentPrice", 0))) if item.get("currentPrice") else None,
                )

                # Extract end date if present
                end_date_str = item.get("endDate")
                if end_date_str:
                    try:
                        legacy_row.close_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00")).date()
                    except ValueError:
                        pass

                rows.append(legacy_row)
            except Exception as e:
                logger.warning(f"Failed to parse JSON estimate: {e}")
                continue

        return rows
