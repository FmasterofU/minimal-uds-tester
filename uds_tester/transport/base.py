"""
uds_tester/transport/base.py

Abstract base class that every transport must implement.
A transport is a context manager that yields a ready-to-use
udsoncan BaseConnection object.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator

from udsoncan.connections import BaseConnection


class UDSTransport(ABC):
    """Abstract UDS transport.

    Subclasses must implement :meth:`connection` as a context manager
    that yields a :class:`udsoncan.connections.BaseConnection` instance.

    Example usage::

        transport = CanTransport(config)
        with transport.connection() as conn:
            with Client(conn) as client:
                ...
    """

    @contextmanager
    @abstractmethod
    def connection(self) -> Generator[BaseConnection, None, None]:
        """Yield a live udsoncan connection, then tear it down."""
        ...  # pragma: no cover
