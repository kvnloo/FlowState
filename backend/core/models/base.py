"""Base SQLAlchemy Models and Mixins.

This module provides the declarative base for all database models and common
mixins for shared functionality across models. The TimestampMixin adds automatic
created_at and updated_at tracking to all models that inherit from it.

The Base class should be imported by all model modules to ensure consistent
schema management and model registration with SQLAlchemy.

Examples
--------
Creating a new model with timestamp tracking::

    from backend.core.models.base import Base, TimestampMixin
    from sqlalchemy import Column, Integer, String

    class MyModel(Base, TimestampMixin):
        __tablename__ = 'my_models'

        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)

The model will automatically have created_at and updated_at fields::

    >>> obj = MyModel(name="Example")
    >>> session.add(obj)
    >>> session.commit()
    >>> print(obj.created_at)  # Automatically set to current UTC time
    2023-11-08 14:30:25.123456

See Also
--------
:mod:`backend.core.models.health_metrics` : Health data models using Base
:mod:`sqlalchemy.ext.declarative` : SQLAlchemy declarative base documentation
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()
"""SQLAlchemy declarative base class.

All database models must inherit from this base to be managed by SQLAlchemy.
The Base provides table mapping, query interface, and ORM functionality.

Attributes
----------
metadata : MetaData
    Contains information about all tables, constraints, and indexes.
    Used for schema creation and migration.

Examples
--------
Create tables from all models::

    from backend.core.models.base import Base
    from sqlalchemy import create_engine

    engine = create_engine('postgresql://user:pass@localhost/db')
    Base.metadata.create_all(engine)

Query using the Base::

    session.query(Base.metadata.tables['users']).all()
"""

class TimestampMixin:
    """Mixin to add automatic timestamp tracking to models.

    This mixin adds created_at and updated_at columns to any model that inherits from it.
    Timestamps are automatically managed:
    - created_at is set once when the record is created
    - updated_at is set on creation and updated every time the record is modified

    Attributes
    ----------
    created_at : datetime
        UTC timestamp when the record was created. Set automatically on insert.
    updated_at : datetime
        UTC timestamp when the record was last modified. Set automatically on
        insert and update.

    Examples
    --------
    Add timestamps to a model::

        from backend.core.models.base import Base, TimestampMixin
        from sqlalchemy import Column, Integer, String

        class User(Base, TimestampMixin):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            email = Column(String, nullable=False)

    The User model now tracks creation and modification times::

        >>> user = User(email="user@example.com")
        >>> session.add(user)
        >>> session.commit()
        >>> print(user.created_at)  # Auto-set
        2023-11-08 14:30:25.123456
        >>> print(user.updated_at)  # Auto-set
        2023-11-08 14:30:25.123456

        >>> user.email = "newemail@example.com"
        >>> session.commit()
        >>> print(user.updated_at)  # Auto-updated
        2023-11-08 14:35:10.654321

    Notes
    -----
    - All timestamps use UTC timezone to ensure consistency across deployments
    - The updated_at field uses SQLAlchemy's onupdate parameter for automatic updates
    - Timestamps are stored as naive datetime objects in UTC
    - Application should handle timezone conversion for display purposes
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
