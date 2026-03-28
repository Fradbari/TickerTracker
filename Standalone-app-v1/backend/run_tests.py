import sys

import pytest

with open("test_out.txt", "w") as f:
    sys.stdout = f
    sys.stderr = f
    pytest.main(["tests/integration/test_estimates_api.py", "-v", "--tb=short", "--color=no"])
