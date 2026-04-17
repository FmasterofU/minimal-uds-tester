"""
config.py — single place to change every runtime parameter.

Switch transport by setting TRANSPORT to 'can' or 'doip'.
"""

# ── Transport selection ────────────────────────────────────────────────────────
# 'can'  → ISO-TP over CAN  (python-can + can-isotp)
# 'doip' → Diagnostics over IP  (DoIP / ISO 13400)
TRANSPORT = "can"

# ── CAN settings ──────────────────────────────────────────────────────────────
# On Windows with a Vector box use interface='vector'.
# On Linux with a SocketCAN interface (e.g. vcan0) use interface='socketcan'.
CAN_INTERFACE = "vector"        # 'vector' | 'socketcan' | 'kvaser' | …
CAN_CHANNEL = 0                 # Vector: integer channel index; SocketCAN: 'vcan0'
CAN_BITRATE = 500_000           # bits/s — ignored by socketcan (set via ip link)
CAN_APP_NAME = "UDSTester"      # Vector only: application name in Vector Hardware Config
CAN_TX_ID = 0x7E0               # UDS request CAN ID  (tester → ECU)
CAN_RX_ID = 0x7E8               # UDS response CAN ID (ECU → tester)

# ── DoIP settings ─────────────────────────────────────────────────────────────
DOIP_HOST = "192.168.1.10"      # ECU IP address
DOIP_PORT = 13400               # Default DoIP port
DOIP_SOURCE_ADDRESS = 0x0E00    # Tester logical address
DOIP_TARGET_ADDRESS = 0x0001    # ECU logical address

# ── UDS client settings ───────────────────────────────────────────────────────
REQUEST_TIMEOUT = 2.0           # seconds to wait for a UDS response
