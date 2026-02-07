"""
User and Role domain models (basic RBAC) for TickerTracker.

Defines:
- RoleType enum
- User model
- Role model
- user_roles association table (many-to-many)

Passwords are stored as hashes in `hashed_password` (never plain text).
"""

from __future__ import annotations

from enum import Enum as PyEnum
from uuid import uuid4
from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Table,
    ForeignKey,
    Index,
    func as sa_func,
    Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from shared.infra.database import Base


class RoleType(PyEnum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


# Association table for many-to-many User <-> Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """User model.

    - Passwords must be stored hashed in `hashed_password`.
    - Users can have multiple roles via `roles` relationship.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True, doc="Password hash; never store plain text")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=sa_func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=sa_func.now(), onupdate=sa_func.now())

    # Many-to-many roles
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="select")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, active={self.is_active})>"


class Role(Base):
    """Role model.

    - `name` uses `RoleType` enum for allowed role names.
    - Roles can be assigned to multiple users via `users`.
    """

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    name = Column(SAEnum(RoleType, name="role_type"), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    users = relationship("User", secondary=user_roles, back_populates="roles", lazy="select")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
