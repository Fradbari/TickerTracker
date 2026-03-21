import pytest
from decimal import Decimal
from hypothesis import given, settings, assume, example
from hypothesis import strategies as st

from src.estimates.domain.pnl import calculate_pnl

# Custom strategy for generating reasonable price values
price_strategy = st.decimals(
    min_value="0.01",
    max_value="9999.99",
    places=4,
    allow_nan=False,
    allow_infinity=False
)

pytestmark = pytest.mark.properties

class TestPnLProperties:
    @settings(max_examples=500)
    @given(entry=price_strategy, exit_price=price_strategy)
    @example(entry=Decimal('0.01'), exit_price=Decimal('0.01'))
    @example(entry=Decimal('100.00'), exit_price=Decimal('0.01'))
    @example(entry=Decimal('0.01'), exit_price=Decimal('9999.99'))
    def test_pnl_symmetry(self, entry: Decimal, exit_price: Decimal):
        """Property: P&L long(entry, exit) == -P&L short(entry, exit)"""
        pnl_long = calculate_pnl(entry, exit_price, "LONG")
        pnl_short = calculate_pnl(entry, exit_price, "SHORT")
        
        # Long PnL should be the exact opposite of Short PnL
        assert pnl_long == -pnl_short

    @settings(max_examples=500)
    @given(entry=price_strategy)
    @example(entry=Decimal('0.01'))
    def test_pnl_zero_when_entry_equals_exit(self, entry: Decimal):
        """Property: P&L = 0 when entry == exit"""
        assume(entry > 0)
        
        pnl_long = calculate_pnl(entry, entry, "LONG")
        pnl_short = calculate_pnl(entry, entry, "SHORT")
        
        assert pnl_long == Decimal("0.0000")
        assert pnl_short == Decimal("0.0000")

    @settings(max_examples=500)
    @given(
        entry=price_strategy,
        point_a=price_strategy,
        point_b=price_strategy
    )
    def test_pnl_additivity(self, entry: Decimal, point_a: Decimal, point_b: Decimal):
        """Property: P&L chain is additive (entry->A) + (A->B) == (entry->B)"""
        
        pnl_entry_to_a = calculate_pnl(entry, point_a, "LONG")
        pnl_a_to_b = calculate_pnl(point_a, point_b, "LONG")
        pnl_entry_to_b = calculate_pnl(entry, point_b, "LONG")
        
        # PnL sum should equal the total PnL
        # Using quantize to avoid any obscure floating point/decimal precision issues
        total_chained = (pnl_entry_to_a + pnl_a_to_b).quantize(Decimal("0.0001"))
        assert total_chained == pnl_entry_to_b

    @settings(max_examples=500)
    @given(entry=price_strategy, exit_price=price_strategy)
    def test_pnl_percentage_relation(self, entry: Decimal, exit_price: Decimal):
        """Property: P&L% * entry_price ≈ P&L absolute"""
        assume(entry > 0)
        
        pnl_absolute = calculate_pnl(entry, exit_price, "LONG")
        
        # Compute P&L percentage dynamically
        pnl_percentage = (exit_price - entry) / entry
        
        # Re-derive absolute P&L from percentage
        derived_pnl = (pnl_percentage * entry).quantize(Decimal("0.0001"))
        
        # Verify it matches the calculated absolute P&L
        assert derived_pnl == pnl_absolute
