"""
Verification script for Task 2.7: User and Role models with RBAC.

Tests:
1. test_imports - User, Role, RoleType, user_roles
2. test_user_model_structure - 6 fields
3. test_role_model_structure - 3 fields
4. test_enum_roletype - 3 values
5. test_many_to_many_relationship - user_roles table
6. test_unique_constraints - email, role name
7. test_indexes - User.email index, User.is_active index
8. test_repr - repr methods
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import inspect

from shared.domain import Role, RoleType, User, user_roles


def test_imports():
    """Test that all required imports work."""
    print("✓ Test 1: Imports successful")
    assert User is not None
    assert Role is not None
    assert RoleType is not None
    assert user_roles is not None
    print("  - User, Role, RoleType, user_roles imported successfully")


def test_user_model_structure():
    """Test User model has 6 required fields."""
    print("\n✓ Test 2: User model structure")
    mapper = inspect(User)
    columns = {col.key for col in mapper.columns}

    required_fields = {'id', 'email', 'hashed_password', 'is_active', 'created_at', 'updated_at'}
    assert required_fields.issubset(columns), f"Missing fields: {required_fields - columns}"
    print(f"  - User model has {len(columns)} fields: {columns}")
    print(f"  - Required 6 fields present: {required_fields}")


def test_role_model_structure():
    """Test Role model has 3 required fields."""
    print("\n✓ Test 3: Role model structure")
    mapper = inspect(Role)
    columns = {col.key for col in mapper.columns}

    required_fields = {'id', 'name', 'description'}
    assert required_fields.issubset(columns), f"Missing fields: {required_fields - columns}"
    print(f"  - Role model has {len(columns)} fields: {columns}")
    print(f"  - Required 3 fields present: {required_fields}")


def test_enum_roletype():
    """Test RoleType enum has 3 required values."""
    print("\n✓ Test 4: RoleType enum")
    enum_values = {e.value for e in RoleType}

    required_values = {'admin', 'user', 'readonly'}
    assert required_values == enum_values, f"Expected {required_values}, got {enum_values}"
    print(f"  - RoleType has 3 values: {enum_values}")


def test_many_to_many_relationship():
    """Test user_roles association table exists."""
    print("\n✓ Test 5: Many-to-many relationship")
    assert user_roles.name == "user_roles"

    columns = {col.name for col in user_roles.columns}
    assert 'user_id' in columns
    assert 'role_id' in columns
    print(f"  - user_roles table exists with columns: {columns}")

    # Check foreign keys
    fks = [fk for col in user_roles.columns for fk in col.foreign_keys]
    assert len(fks) == 2, f"Expected 2 foreign keys, got {len(fks)}"
    print(f"  - user_roles has {len(fks)} foreign keys to users.id and roles.id")


def test_unique_constraints():
    """Test unique constraints on User.email and Role.name."""
    print("\n✓ Test 6: Unique constraints")

    # Check User.email unique
    user_mapper = inspect(User)
    email_col = user_mapper.columns['email']
    assert email_col.unique, "User.email should be unique"
    print("  - User.email has unique constraint")

    # Check Role.name unique
    role_mapper = inspect(Role)
    name_col = role_mapper.columns['name']
    assert name_col.unique, "Role.name should be unique"
    print("  - Role.name has unique constraint")


def test_indexes():
    """Test indexes on User.email and User.is_active."""
    print("\n✓ Test 7: Indexes")

    # Check User table indexes
    user_table = User.__table__
    indexes = user_table.indexes
    index_names = {idx.name for idx in indexes}

    # Check email index
    email_indexed = any('email' in idx.name.lower() for idx in indexes) or User.__table__.columns['email'].index
    assert email_indexed, "User.email should have an index"
    print("  - User.email has index")

    # Check is_active index
    is_active_indexed = any('is_active' in idx.name.lower() for idx in indexes)
    assert is_active_indexed, "User.is_active should have an index"
    print("  - User.is_active has index (found: ix_user_is_active)")
    print(f"  - Total indexes found: {index_names}")


def test_repr():
    """Test repr methods are defined."""
    print("\n✓ Test 8: Repr methods")

    # Create mock instances
    from uuid import uuid4
    user = User(id=uuid4(), email="test@example.com", is_active=True)
    role = Role(id=uuid4(), name=RoleType.USER)

    user_repr = repr(user)
    role_repr = repr(role)

    assert 'User' in user_repr
    assert 'test@example.com' in user_repr
    print(f"  - User repr: {user_repr}")

    assert 'Role' in role_repr
    assert 'RoleType.USER' in role_repr or 'user' in role_repr
    print(f"  - Role repr: {role_repr}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("VERIFICATION: Task 2.7 - User and Role Models (RBAC)")
    print("=" * 60)

    try:
        test_imports()
        test_user_model_structure()
        test_role_model_structure()
        test_enum_roletype()
        test_many_to_many_relationship()
        test_unique_constraints()
        test_indexes()
        test_repr()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Task 2.7 verified successfully!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
