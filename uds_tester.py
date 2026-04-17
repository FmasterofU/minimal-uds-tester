#!/usr/bin/env python3
"""Minimal UDS Tester

Sends a ReadDataByIdentifier (service 0x22) request for DID 0xF194.
Supports two transport layers:
  - CAN  (ISO 15765-2 ISO-TP over python-can / python-isotp)
  - DoIP (ISO 13400 Diagnostics over IP, i.e. Ethernet)

Usage examples
--------------
CAN (virtual interface):
    python uds_tester.py can --channel vcan0 --tx-id 0x7E0 --rx-id 0x7E8

DoIP (Ethernet):
    python uds_tester.py doip --host 192.168.1.10 --target-address 0x1000
"""

import argparse
import sys

TARGET_DID = 0xF194


# ---------------------------------------------------------------------------
# CAN transport
# ---------------------------------------------------------------------------

def read_did_over_can(channel: str, interface: str, tx_id: int, rx_id: int, did: int) -> None:
    """Send ReadDataByIdentifier over CAN (ISO-TP) using python-can + python-isotp + udsoncan."""
    try:
        import can
        import isotp
        from udsoncan.connections import PythonIsoTpConnection
        from udsoncan.client import Client
    except ImportError as exc:
        print(f"[ERROR] Missing dependency for CAN transport: {exc}")
        print("Install with:  pip install python-can python-isotp udsoncan")
        sys.exit(1)

    print(f"[CAN] channel={channel!r}  interface={interface!r}  "
          f"tx=0x{tx_id:03X}  rx=0x{rx_id:03X}")

    bus = can.interface.Bus(channel=channel, bustype=interface)
    # A Notifier is required by NotifierBasedCanStack so the ISO-TP layer can
    # register itself as a listener and receive incoming CAN frames.
    notifier = can.Notifier(bus, [])
    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=tx_id, rxid=rx_id)
    stack = isotp.NotifierBasedCanStack(bus, notifier=notifier, address=tp_addr)
    conn = PythonIsoTpConnection(stack)

    config = {"exception_on_negative_response": False}
    with Client(conn, config=config) as client:
        _read_and_display_did(client, did)

    notifier.stop()
    bus.shutdown()


# ---------------------------------------------------------------------------
# DoIP (Ethernet) transport
# ---------------------------------------------------------------------------

def read_did_over_doip(
    host: str,
    port: int,
    source_address: int,
    target_address: int,
    did: int,
) -> None:
    """Send ReadDataByIdentifier over DoIP (ISO 13400) using doipclient + udsoncan."""
    try:
        from doipclient import DoIPClient
        from doipclient.connectors import DoIPClientUDSConnector
        from udsoncan.client import Client
    except ImportError as exc:
        print(f"[ERROR] Missing dependency for DoIP transport: {exc}")
        print("Install with:  pip install doipclient udsoncan")
        sys.exit(1)

    print(f"[DoIP] host={host!r}  port={port}  "
          f"source=0x{source_address:04X}  target=0x{target_address:04X}")

    doip_client = DoIPClient(host, target_address, source_address=source_address, udp_port=port, tcp_port=port)
    conn = DoIPClientUDSConnector(doip_client)

    config = {"exception_on_negative_response": False}
    with Client(conn, config=config) as client:
        _read_and_display_did(client, did)


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _read_and_display_did(client, did: int) -> None:
    print(f"Sending ReadDataByIdentifier for DID 0x{did:04X} …")
    response = client.read_data_by_identifier(did)
    if response.positive:
        raw = response.service_data.values[did]
        value = raw.hex() if isinstance(raw, (bytes, bytearray)) else str(raw)
        print(f"[OK] DID 0x{did:04X} = {value}")
    else:
        print(f"[NEGATIVE RESPONSE] code=0x{response.code:02X}  ({response.code_name})")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Minimal UDS Tester – ReadDataByIdentifier for DID 0xF194",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="transport", required=True, help="Transport layer")

    # --- CAN sub-command ---
    can_p = subparsers.add_parser(
        "can",
        help="CAN transport (ISO-TP, ISO 15765-2)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    can_p.add_argument("--channel", default="vcan0", help="CAN channel name")
    can_p.add_argument("--interface", default="socketcan", help="python-can bustype")
    can_p.add_argument(
        "--tx-id", type=lambda x: int(x, 0), default=0x7E0,
        metavar="ID", help="ISO-TP transmit CAN ID (hex or decimal)",
    )
    can_p.add_argument(
        "--rx-id", type=lambda x: int(x, 0), default=0x7E8,
        metavar="ID", help="ISO-TP receive CAN ID (hex or decimal)",
    )

    # --- DoIP sub-command ---
    doip_p = subparsers.add_parser(
        "doip",
        help="DoIP transport (ISO 13400, Ethernet)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    doip_p.add_argument("--host", required=True, help="ECU IP address or hostname")
    doip_p.add_argument("--port", type=int, default=13400, help="DoIP TCP/UDP port")
    doip_p.add_argument(
        "--source-address", type=lambda x: int(x, 0), default=0x0E00,
        metavar="ADDR", help="Tester source logical address (hex or decimal)",
    )
    doip_p.add_argument(
        "--target-address", type=lambda x: int(x, 0), default=0x1000,
        metavar="ADDR", help="ECU target logical address (hex or decimal)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.transport == "can":
        read_did_over_can(args.channel, args.interface, args.tx_id, args.rx_id, TARGET_DID)
    elif args.transport == "doip":
        read_did_over_doip(
            args.host, args.port, args.source_address, args.target_address, TARGET_DID
        )


if __name__ == "__main__":
    main()
