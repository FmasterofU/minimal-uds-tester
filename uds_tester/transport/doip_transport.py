"""
uds_tester/transport/doip_transport.py

DoIP (Diagnostics over IP, ISO 13400) transport using doipclient + udsoncan.
Works on both Windows and Linux over any standard TCP/IP stack.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector

from .base import UDSTransport

if TYPE_CHECKING:
    from udsoncan.connections import BaseConnection


class DoIPTransport(UDSTransport):
    """DoIP transport wrapping a :class:`doipclient.DoIPClient`.

    Parameters
    ----------
    cfg:
        A module (or any object) that exposes the DOIP_* constants
        defined in config.py.
    """

    def __init__(self, cfg) -> None:
        self._cfg = cfg

    @contextmanager
    def connection(self) -> Generator[BaseConnection, None, None]:
        cfg = self._cfg
        doip_client = DoIPClient(
            cfg.DOIP_HOST,
            cfg.DOIP_TARGET_ADDRESS,
            source_address=cfg.DOIP_SOURCE_ADDRESS,
            udp_port=cfg.DOIP_PORT,
            tcp_port=cfg.DOIP_PORT,
        )
        try:
            conn = DoIPClientUDSConnector(doip_client)
            yield conn
        finally:
            doip_client.close()
