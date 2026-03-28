"""
Verification script for TASK 2.8 and TASK 2.9: SyncJob and AiModelRun Models

Tests for TASK 2.8 (SyncJob):
1. Import SyncJob model and Enums
2. Verify SyncJob model structure and fields
3. Verify Enums values
4. Verify index on started_at

Tests for TASK 2.9 (AiModelRun):
1. Import AiModelRun model
2. Verify AiModelRun model structure and fields
3. Verify JSONB field
4. Verify index on model_name and created_at
"""

import asyncio
import sys
from pathlib import Path

# Add backend/src to path for imports
backend_src = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_src))

async def test_sync_job_model():
    """Verify SyncJob model and enums."""
    print("\n[RUN] Verifying SyncJob model (TASK 2.8)...")

    try:
        from sqlalchemy import inspect

        from sync.domain.entities import SyncJob, SyncJobStatus, SyncJobType

        # Verify Enums
        print("  [INFO] Checking SyncJob Enums...")
        expected_types = {'INITIAL_IMPORT', 'DAILY_HISTORY_UPDATE', 'ON_ESTIMATE_SAVE', 'MANUAL_SYNC'}
        actual_types = {t.name for t in SyncJobType}
        if not expected_types.issubset(actual_types):
             print(f"  [FAIL] Missing SyncJobType values. Expected {expected_types}, got {actual_types}")
             return False

        expected_statuses = {'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'PARTIAL'}
        actual_statuses = {s.name for s in SyncJobStatus}
        if not expected_statuses.issubset(actual_statuses):
             print(f"  [FAIL] Missing SyncJobStatus values. Expected {expected_statuses}, got {actual_statuses}")
             return False

        # Verify Model
        print("  [INFO] Checking SyncJob Model Structure...")
        mapper = inspect(SyncJob)
        required_columns = {
            'id', 'job_type', 'status', 'started_at', 'finished_at',
            'error_message', 'filename', 'checksum_before', 'checksum_after',
            'records_processed', 'records_failed'
        }
        actual_columns = {col.name for col in mapper.columns}

        if not required_columns.issubset(actual_columns):
            missing = required_columns - actual_columns
            print(f"  [FAIL] Missing columns in SyncJob: {missing}")
            return False

        # Verify Index
        indexes = {idx.name for idx in SyncJob.__table__.indexes}
        if "ix_sync_jobs_started_at" not in indexes:
             print("  [FAIL] Missing index 'ix_sync_jobs_started_at'")
             return False

        print("  [PASS] SyncJob model verified successfully")
        return True

    except ImportError as e:
        print(f"  [FAIL] Failed to import SyncJob components: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Error validating SyncJob: {e}")
        return False

async def test_ai_model_run_model():
    """Verify AiModelRun model."""
    print("\n[RUN] Verifying AiModelRun model (TASK 2.9)...")

    try:
        from sqlalchemy import inspect
        from sqlalchemy.dialects.postgresql import JSONB

        from analytics.domain.entities import AiModelRun

        # Verify Model
        print("  [INFO] Checking AiModelRun Model Structure...")
        mapper = inspect(AiModelRun)
        required_columns = {
            'id', 'estimate_id', 'model_name', 'model_version',
            'prompt_hash', 'prompt_tokens', 'completion_tokens',
            'latency_ms', 'output_summary', 'raw_response', 'created_at'
        }
        actual_columns = {col.name for col in mapper.columns}

        if not required_columns.issubset(actual_columns):
            missing = required_columns - actual_columns
            print(f"  [FAIL] Missing columns in AiModelRun: {missing}")
            return False

        # Verify JSONB
        raw_response_col = mapper.columns['raw_response']
        if not isinstance(raw_response_col.type, JSONB):
             print("  [FAIL] 'raw_response' column is not JSONB")
             return False

        # Verify Index
        indexes = {idx.name for idx in AiModelRun.__table__.indexes}
        if "ix_ai_model_runs_model_name_created_at" not in indexes:
             print("  [FAIL] Missing index 'ix_ai_model_runs_model_name_created_at'")
             return False

        print("  [PASS] AiModelRun model verified successfully")
        return True

    except ImportError as e:
        print(f"  [FAIL] Failed to import AiModelRun components: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Error validating AiModelRun: {e}")
        return False

async def main():
    """Run verification tests."""
    print("-" * 60)
    print("Verification Script for Task 2.8 and 2.9")
    print("-" * 60)

    results = []
    results.append(await test_sync_job_model())
    results.append(await test_ai_model_run_model())

    print("-" * 60)
    if all(results):
        print("[SUCCESS] All tasks verified successfully!")
        return 0
    else:
        print("[FAILURE] Some tasks failed verification.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
