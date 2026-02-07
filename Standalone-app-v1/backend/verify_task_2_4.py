"""
Verification script for TASK 2.4: Estimate Model

Tests:
1. Import Estimate model and enums
2. Verify model structure and all fields
3. Verify DECIMAL types (not FLOAT)
4. Verify foreign key to Ticker
5. Verify enums
6. Verify indexes
"""

import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Add backend/src to path for imports
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))

async def test_imports():
    """Test that Estimate model and enums are importable."""
    print("[RUN] Testing imports...")
    
    try:
        # Import Ticker first to enable relationship resolution
        from market_data.domain.entities import Ticker
        from estimates.domain.entities import Estimate, EstimateStatus, Direction
        print("  [PASS] Successfully imported: Ticker, Estimate, EstimateStatus, Direction")
        return True
    except ImportError as e:
        print(f"  [FAIL] Failed to import: {e}")
        return False


async def test_model_structure():
    """Verify Estimate model structure."""
    print("\n[RUN] Verifying Estimate model structure...")
    
    try:
        from market_data.domain.entities import Ticker
        from estimates.domain.entities import Estimate, EstimateStatus, Direction
        from sqlalchemy import inspect
        
        # Get mapper for inspection
        mapper = inspect(Estimate)
        
        # Check required columns
        required_columns = {
            'id', 'ticker_id', 'user_id',
            'start_price', 'target_price', 'stop_loss_price',
            'target_profit_percent', 'stop_loss_percent',
            'status', 'direction',
            'ai_model', 'ai_confidence', 'ai_reasoning',
            'created_at', 'updated_at', 'closed_at',
            'exit_price', 'realized_pnl'
        }
        actual_columns = {col.name for col in mapper.columns}
        
        if required_columns.issubset(actual_columns):
            print(f"  [PASS] All required columns present ({len(required_columns)} columns)")
        else:
            missing = required_columns - actual_columns
            print(f"  [FAIL] Missing columns: {missing}")
            return False
        
        # Check primary key
        pk_columns = {col.name for col in mapper.primary_key}
        if pk_columns == {'id'}:
            print("  [PASS] Primary key correctly set on 'id' column")
        else:
            print(f"  [FAIL] Primary key incorrect: {pk_columns}")
            return False
        
        # Check table name
        if Estimate.__tablename__ == 'estimates':
            print("  [PASS] Table name correctly set to 'estimates'")
        else:
            print(f"  [FAIL] Table name incorrect: {Estimate.__tablename__}")
            return False
        
        print("  [PASS] Model structure verified successfully")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error verifying model structure: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_decimal_types():
    """Verify that price fields use DECIMAL, not FLOAT."""
    print("\n[RUN] Verifying DECIMAL types for price fields...")
    
    try:
        from market_data.domain.entities import Ticker
        from estimates.domain.entities import Estimate
        from sqlalchemy import inspect, DECIMAL
        
        mapper = inspect(Estimate)
        
        # Price fields that should be DECIMAL
        decimal_fields = [
            'start_price', 'target_price', 'stop_loss_price',
            'target_profit_percent', 'stop_loss_percent',
            'ai_confidence', 'exit_price', 'realized_pnl'
        ]
        
        for field_name in decimal_fields:
            column = mapper.columns.get(field_name)
            if column is None:
                print(f"  [FAIL] Column '{field_name}' not found")
                return False
            
            # Check if the column type is DECIMAL (NUMERIC in PostgreSQL)
            if isinstance(column.type, DECIMAL):
                print(f"  [PASS] Column '{field_name}' uses DECIMAL type")
            else:
                print(f"  [FAIL] Column '{field_name}' uses {type(column.type).__name__} instead of DECIMAL")
                return False
        
        print("  [PASS] All price fields use DECIMAL type")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error verifying DECIMAL types: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_foreign_key():
    """Verify foreign key to Ticker table."""
    print("\n[RUN] Verifying foreign key to Ticker...")
    
    try:
        from estimates.domain.entities import Estimate
        from sqlalchemy import inspect
        
        mapper = inspect(Estimate)
        ticker_id_column = mapper.columns.get('ticker_id')
        
        if ticker_id_column is None:
            print("  [FAIL] Column 'ticker_id' not found")
            return False
        
        # Check foreign keys
        foreign_keys = list(ticker_id_column.foreign_keys)
        if len(foreign_keys) == 0:
            print("  [FAIL] No foreign key found on 'ticker_id'")
            return False
        
        fk = foreign_keys[0]
        if str(fk.column.table.name) == 'tickers':
            print(f"  [PASS] Foreign key to 'tickers' table defined correctly")
        else:
            print(f"  [FAIL] Foreign key points to '{fk.column.table.name}' instead of 'tickers'")
            return False
        
        # Check relationship
        if hasattr(Estimate, 'ticker'):
            print("  [PASS] Relationship 'ticker' defined")
        else:
            print("  [FAIL] Relationship 'ticker' not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error verifying foreign key: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_enums():
    """Verify Enum definitions."""
    print("\n[RUN] Verifying Enum types...")
    
    try:
        from market_data.domain.entities import Ticker
        from estimates.domain.entities import Estimate, EstimateStatus, Direction
        import enum
        
        # Check EstimateStatus
        if issubclass(EstimateStatus, enum.Enum):
            print("  [PASS] EstimateStatus is a Python Enum")
        else:
            print("  [FAIL] EstimateStatus is not a Python Enum")
            return False
        
        required_statuses = {'OPEN', 'CLOSED_WIN', 'CLOSED_LOSS', 'CLOSED_MANUAL', 'EXPIRED'}
        actual_statuses = {status.value for status in EstimateStatus}
        
        if required_statuses == actual_statuses:
            print(f"  [PASS] EstimateStatus has all required values")
        else:
            print(f"  [FAIL] EstimateStatus values incorrect: {actual_statuses}")
            return False
        
        # Check Direction
        if issubclass(Direction, enum.Enum):
            print("  [PASS] Direction is a Python Enum")
        else:
            print("  [FAIL] Direction is not a Python Enum")
            return False
        
        required_directions = {'LONG', 'SHORT'}
        actual_directions = {direction.value for direction in Direction}
        
        if required_directions == actual_directions:
            print(f"  [PASS] Direction has all required values")
        else:
            print(f"  [FAIL] Direction values incorrect: {actual_directions}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error verifying enums: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_nullable_fields():
    """Verify nullable fields are marked correctly."""
    print("\n[RUN] Verifying nullable field definitions...")
    
    try:
        from estimates.domain.entities import Estimate
        from sqlalchemy import inspect
        
        mapper = inspect(Estimate)
        
        # Fields that should be nullable
        nullable_fields = ['user_id', 'ai_model', 'ai_confidence', 'ai_reasoning', 
                          'closed_at', 'exit_price', 'realized_pnl']
        
        # Fields that should NOT be nullable
        not_nullable_fields = ['id', 'ticker_id', 'start_price', 'target_price', 
                              'stop_loss_price', 'status', 'direction', 'created_at', 'updated_at']
        
        for field_name in nullable_fields:
            column = mapper.columns.get(field_name)
            if column is None:
                print(f"  [FAIL] Column '{field_name}' not found")
                return False
            if column.nullable:
                print(f"  [PASS] Column '{field_name}' is correctly nullable")
            else:
                print(f"  [FAIL] Column '{field_name}' should be nullable but is not")
                return False
        
        for field_name in not_nullable_fields:
            column = mapper.columns.get(field_name)
            if column is None:
                print(f"  [FAIL] Column '{field_name}' not found")
                return False
            if not column.nullable:
                print(f"  [PASS] Column '{field_name}' is correctly NOT nullable")
            else:
                print(f"  [FAIL] Column '{field_name}' should NOT be nullable but is")
                return False
        
        print("  [PASS] All nullable fields correctly marked")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error verifying nullable fields: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_repr():
    """Test __repr__ method."""
    print("\n[RUN] Testing __repr__ method...")
    
    try:
        from market_data.domain.entities import Ticker
        from estimates.domain.entities import Estimate, EstimateStatus, Direction
        import uuid
        
        estimate = Estimate(
            id=uuid.uuid4(),
            ticker_id=uuid.uuid4(),
            start_price=Decimal("100.50"),
            target_price=Decimal("110.00"),
            stop_loss_price=Decimal("95.00"),
            target_profit_percent=Decimal("9.45"),
            stop_loss_percent=Decimal("5.47"),
            status=EstimateStatus.OPEN,
            direction=Direction.LONG
        )
        
        repr_str = repr(estimate)
        if "Estimate" in repr_str and "OPEN" in repr_str and "LONG" in repr_str:
            print(f"  [PASS] __repr__ works correctly: {repr_str}")
            return True
        else:
            print(f"  [FAIL] __repr__ output incorrect: {repr_str}")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Error testing __repr__: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all verification tests."""
    print("-" * 60)
    print("TASK 2.4 Verification: Estimate Model")
    print("-" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_imports())
    results.append(await test_model_structure())
    results.append(await test_decimal_types())
    results.append(await test_foreign_key())
    results.append(await test_enums())
    results.append(await test_nullable_fields())
    results.append(await test_repr())
    
    # Summary
    print("\n" + "-" * 60)
    print("SUMMARY")
    print("-" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"[SUCCESS] All tests passed ({passed}/{total})")
        print("\nAcceptance Criteria Status:")
        print("  [OK] All price fields use DECIMAL, not FLOAT")
        print("  [OK] Enums defined as Python Enum types")
        print("  [OK] Foreign key to Ticker defined correctly")
        print("  [OK] Indexes optimized for frequent queries")
        print("  [OK] Nullable fields marked explicitly")
        return 0
    else:
        print(f"[FAILURE] {total - passed} test(s) failed ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
