"""
uds_tester/transport/can_transport.py

ISO-TP over CAN transport using python-can + can-isotp + udsoncan.

Supported hardware (set CAN_INTERFACE in config.py):
  Windows / Vector box  → interface='vector'
  Linux SocketCAN       → interface='socketcan'
  Kvaser                → interface='kvaser'
  PCAN                  → interface='pcan'
  Virtual (testing)     → interface='virtual'
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

import can
import isotp
from udsoncan.connections import PythonIsoTpConnection

from .base import UDSTransport

if TYPE_CHECKING:
    from udsoncan.connections import BaseConnection


def _build_bus_kwargs(cfg) -> dict:
    """Build python-can Bus keyword arguments from *cfg*."""
    kwargs: dict = {"interface": cfg.CAN_INTERFACE}

    if cfg.CAN_INTERFACE == "vector":
        kwargs["channel"] = cfg.CAN_CHANNEL
        kwargs["bitrate"] = cfg.CAN_BITRATE
        kwargs["app_name"] = cfg.CAN_APP_NAME
    elif cfg.CAN_INTERFACE == "socketcan":
        # On Linux the channel is a string like 'can0' or 'vcan0'.
        # Bitrate is configured at OS level (ip link set can0 type can bitrate …).
        channel = cfg.CAN_CHANNEL
        if isinstance(channel, int):
            channel = f"can{channel}"
        kwargs["channel"] = channel
    else:
        # Catch-all for kvaser, pcan, usb2can, virtual, …
        kwargs["channel"] = cfg.CAN_CHANNEL
        kwargs["bitrate"] = cfg.CAN_BITRATE

    return kwargs


class CanTransport(UDSTransport):
    """CAN transport: ISO-TP over a python-can Bus.

    Parameters
    ----------
    cfg:
        A module (or any object) that exposes the CAN_* constants
        defined in config.py.
    """

    def __init__(self, cfg) -> None:
        self._cfg = cfg

    @contextmanager
    def connection(self) -> Generator[BaseConnection, None, None]:
        cfg = self._cfg
        bus_kwargs = _build_bus_kwargs(cfg)

        bus = can.Bus(**bus_kwargs)
        try:
            addr = isotp.Address(
                isotp.AddressingMode.Normal_11bits,
                txid=cfg.CAN_TX_ID,
                rxid=cfg.CAN_RX_ID,
            )
            stack = isotp.CanStack(bus=bus, address=addr)
            conn = PythonIsoTpConnection(stack)
            yield conn
        finally:
            bus.shutdown()
