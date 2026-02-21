import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Ensure project src on path
sys.path.insert(0, 'src')

print('Using Python:', sys.executable)

# Test 1: DataSource enum
from src.shared.domain.lineage import DataSource, LineageTracked
assert DataSource.YAHOO_FINANCE.value == 'yahoo_finance'
assert DataSource.from_legacy('yahoo') == DataSource.YAHOO_FINANCE
assert DataSource.from_legacy('manual') == DataSource.MANUAL_ENTRY
assert DataSource.from_legacy('xxxxunknown') == DataSource.YAHOO_FINANCE
print('✅ DataSource enum OK')

# Test 2: LineageTracked mixin basic import check
expected = {'data_source', 'source_timestamp', 'ingestion_timestamp', 'quality_score'}
# best-effort introspection: check attributes on class dict and presence of compute_quality_score
mixin_keys = set(k for k in LineageTracked.__dict__.keys())
print(f'  LineageTracked keys (sample): {sorted(list(mixin_keys))[:10]}')
assert hasattr(LineageTracked, 'compute_quality_score')
print('✅ LineageTracked mixin importato OK')

# Test 3: MarketData inherits from LineageTracked
from src.market_data.domain.market_data import MarketData
assert issubclass(MarketData, LineageTracked), 'MarketData deve ereditare LineageTracked'
print('✅ MarketData eredita LineageTracked OK')

# Test 4: compute_quality_score - dato fresco
obj = LineageTracked.__new__(LineageTracked)
score_fresh = obj.compute_quality_score(source_ts=datetime.utcnow())
assert score_fresh >= Decimal('0.80'), f'Atteso >= 0.80, got {score_fresh}'
print(f'✅ Quality score dato fresco: {score_fresh}')

# Test 5: compute_quality_score - dato vecchio
score_stale = obj.compute_quality_score(source_ts=datetime.utcnow() - timedelta(days=30))
assert score_stale < Decimal('0.70'), f'Atteso < 0.70, got {score_stale}'
print(f'✅ Quality score dato stale: {score_stale}')

# Test 6: DataSource as str
val = DataSource.YAHOO_FINANCE
assert val == 'yahoo_finance', 'DataSource deve essere str-comparabile'
print('✅ DataSource str-comparabile OK')

print('\n🎉 Tutti i check statici passati')
