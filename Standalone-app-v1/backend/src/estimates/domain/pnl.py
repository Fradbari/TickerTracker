from decimal import Decimal


def calculate_pnl(
    start_price: Decimal,
    exit_price: Decimal,
    direction: str,
) -> Decimal:
    """
    Calculate realized profit/loss.

    For LONG: PnL = exit_price - start_price
    For SHORT: PnL = start_price - exit_price

    Returns:
        Realized PnL (positive = profit, negative = loss)
    """
    if direction == "LONG":
        pnl = exit_price - start_price
    else:  # SHORT
        pnl = start_price - exit_price

    return pnl.quantize(Decimal("0.0001"))
