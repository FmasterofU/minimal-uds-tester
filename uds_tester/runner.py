"""
uds_tester/runner.py

Wires a transport and an action together and executes the test.
"""

from __future__ import annotations

import logging

from udsoncan import Client

from .actions.base import UDSAction
from .transport.base import UDSTransport

logger = logging.getLogger(__name__)


class Runner:
    """Execute a :class:`UDSAction` over a :class:`UDSTransport`.

    Parameters
    ----------
    transport:
        A configured transport (CanTransport or DoIPTransport).
    action:
        The UDS action to run.
    request_timeout:
        Seconds to wait for each UDS response.
    """

    def __init__(
        self,
        transport: UDSTransport,
        action: UDSAction,
        request_timeout: float = 2.0,
    ) -> None:
        self._transport = transport
        self._action = action
        self._timeout = request_timeout

    def run(self):
        """Open the transport, create a UDS client, and execute the action.

        Returns the result from the action, or raises on failure.
        """
        logger.info("Opening transport: %s", type(self._transport).__name__)
        with self._transport.connection() as conn:
            logger.info("Transport open.  Creating UDS client …")
            with Client(conn, request_timeout=self._timeout) as client:
                logger.info(
                    "Running action: %s", type(self._action).__name__
                )
                result = self._action.run(client)
                logger.info("Action complete.  Result: %s", result)
                return result
