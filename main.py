#!/usr/bin/env python3
"""
main.py — entry point for the minimal UDS tester.

Usage
-----
    python main.py                   # use transport from config.py
    python main.py --transport can   # force CAN
    python main.py --transport doip  # force DoIP

To run a different action, change the `action` variable below (or extend it
with your own subclass of UDSAction).
"""

from __future__ import annotations

import argparse
import logging
import sys

import config
from uds_tester.actions.read_did import ReadDIDAction
from uds_tester.runner import Runner
from uds_tester.transport.can_transport import CanTransport
from uds_tester.transport.doip_transport import DoIPTransport


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _build_transport(name: str):
    name = name.lower()
    if name == "can":
        return CanTransport(config)
    if name == "doip":
        return DoIPTransport(config)
    raise ValueError(f"Unknown transport '{name}'. Choose 'can' or 'doip'.")


def main() -> int:
    _setup_logging()

    parser = argparse.ArgumentParser(description="Minimal UDS tester")
    parser.add_argument(
        "--transport",
        default=config.TRANSPORT,
        choices=["can", "doip"],
        help="Transport to use (default: value of TRANSPORT in config.py)",
    )
    args = parser.parse_args()

    # ── Core logic ────────────────────────────────────────────────────────────
    # To change what the tester does, replace ReadDIDAction with any other
    # UDSAction subclass (or create your own).
    action = ReadDIDAction(did=0xF194)
    # ─────────────────────────────────────────────────────────────────────────

    transport = _build_transport(args.transport)

    runner = Runner(
        transport=transport,
        action=action,
        request_timeout=config.REQUEST_TIMEOUT,
    )

    log = logging.getLogger(__name__)
    try:
        result = runner.run()
        log.info("DID 0xF194 value: %s", result)
        print(f"DID 0xF194 = {result!r}")
        return 0
    except Exception as exc:  # noqa: BLE001
        log.error("Test failed: %s", exc, exc_info=True)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
