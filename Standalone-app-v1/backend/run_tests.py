import pytest
import sys

with open("test_out.txt", "w") as f:
    sys.stdout = f
    sys.stderr = f
    pytest.main(["tests/unit/estimates/test_estimate_service.py", "-v", "--tb=short", "--color=no"])
