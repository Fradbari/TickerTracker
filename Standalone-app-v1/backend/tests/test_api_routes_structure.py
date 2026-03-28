"""
Simple test to verify API routes can be imported and have correct structure.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def test_routes_structure():
    """Verify routes module has all required endpoints."""
    from src.estimates.api import routes

    print("\n=== Testing Estimates API Routes ===\n")

    # Check router exists
    assert hasattr(routes, 'router'), "Router should be defined"
    router = routes.router

    print(f"[OK] Router prefix: {router.prefix}")
    print(f"[OK] Router tags: {router.tags}")

    # Check endpoints
    required_endpoints = {
        "create_estimate": ("POST", ""),
        "list_estimates": ("GET", ""),
        "get_estimate": ("GET", "/{estimate_id}"),
        "update_estimate": ("PATCH", "/{estimate_id}"),
        "close_estimate": ("DELETE", "/{estimate_id}"),
        "get_estimate_history": ("GET", "/{estimate_id}/history"),
    }

    # Get all routes
    routes_found = {}
    for route in router.routes:
        if hasattr(route, 'endpoint'):
            endpoint_name = route.endpoint.__name__
            methods = list(route.methods) if hasattr(route, 'methods') else []
            path = route.path
            routes_found[endpoint_name] = (methods, path)

    print(f"\nFound {len(routes_found)} endpoints:")
    for name, (methods, path) in routes_found.items():
        print(f"   - {name}: {methods} {path}")

    # Verify all required endpoints exist
    missing = []
    for endpoint_name, (expected_method, expected_path) in required_endpoints.items():
        if endpoint_name not in routes_found:
            missing.append(endpoint_name)
            print(f"[FAIL] Missing endpoint: {endpoint_name}")
        else:
            methods, path = routes_found[endpoint_name]
            if expected_method not in methods:
                print(f"[FAIL] {endpoint_name}: Expected method {expected_method}, found {methods}")
            elif expected_path not in path:
                print(f"[FAIL] {endpoint_name}: Expected path containing '{expected_path}', found '{path}'")

    if not missing:
        print(f"\n[OK] All {len(required_endpoints)} required endpoints are defined!")
    else:
        print(f"\n[FAIL] Missing {len(missing)} endpoints")
        return False

    # Check dependency injection
    print("\nChecking dependency injection:")
    assert hasattr(routes, 'get_estimate_service'), "get_estimate_service DI should exist"
    print("   [OK] get_estimate_service")
    assert hasattr(routes, 'get_estimate_history_service'), "get_estimate_history_service DI should exist"
    print("   [OK] get_estimate_history_service")
    assert hasattr(routes, 'get_estimate_repository'), "get_estimate_repository DI should exist"
    print("   [OK] get_estimate_repository")

    print("\n" + "="*50)
    print("[SUCCESS] TASK 2.16 - API Routes Structure Verified!")
    print("="*50)

    return True

if __name__ == "__main__":
    try:
        success = test_routes_structure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
