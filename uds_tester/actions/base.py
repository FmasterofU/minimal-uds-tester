"""
uds_tester/actions/base.py

Abstract base class for UDS test actions.

To add a new action:
  1. Create a new module in uds_tester/actions/
  2. Subclass UDSAction and implement run(client).
  3. Pass an instance of your action to Runner in main.py.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from udsoncan import Client


class UDSAction(ABC):
    """A single UDS test action executed against an open UDS client.

    Override :meth:`run` with whatever UDS service calls you need.
    The method should return a result object (or None) and raise an
    exception on failure — the runner will catch and log it.
    """

    @abstractmethod
    def run(self, client: Client):
        """Execute the action.

        Parameters
        ----------
        client:
            An already-connected and open :class:`udsoncan.Client` instance.

        Returns
        -------
        object
            Any result value that the runner should display/log.
            Return ``None`` if there is nothing meaningful to report.
        """
        ...  # pragma: no cover
