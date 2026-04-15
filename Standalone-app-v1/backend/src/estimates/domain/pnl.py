from decimal import Decimal


def calculate_pnl(
    start_price: Decimal,
    exit_price: Decimal,
) -> Decimal:
    """
    Calculate realized profit/loss.

    For LONG: PnL = exit_price - start_price

    Returns:
        Realized PnL (positive = profit, negative = loss)
    """
    pnl = exit_price - start_price

    return pnl.quantize(Decimal("0.0001"))
