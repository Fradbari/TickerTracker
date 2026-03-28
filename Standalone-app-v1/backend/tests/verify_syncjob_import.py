"""
Test for importing the SyncJob model.
"""

def test_syncjob_import():
    try:
        from sync.domain.entities import SyncJob, SyncJobStatus, SyncJobType
    except ImportError as e:
        raise AssertionError(f"Failed to import SyncJob or related components: {e}")

    assert SyncJob is not None, "SyncJob class is not defined."
    assert SyncJobType is not None, "SyncJobType enum is not defined."
    assert SyncJobStatus is not None, "SyncJobStatus enum is not defined."
