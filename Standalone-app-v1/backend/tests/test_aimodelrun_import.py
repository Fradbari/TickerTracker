"""
Test for importing the AiModelRun model.
"""

def test_aimodelrun_import():
    try:
        from analytics.domain.entities import AiModelRun
    except ImportError as e:
        assert False, f"Failed to import AiModelRun: {e}"

    assert AiModelRun is not None, "AiModelRun class is not defined."