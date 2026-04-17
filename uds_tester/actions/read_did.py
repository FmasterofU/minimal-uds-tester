"""
uds_tester/actions/read_did.py

Concrete UDS action: ReadDataByIdentifier (service 0x22) for DID 0xF194.

DID 0xF194 is typically "ECU Software Version Number" (ISO 14229 / OEM-defined).
Change DID_TO_READ to target a different DID, or subclass ReadDIDAction to read
multiple DIDs in one go.
"""

from __future__ import annotations

import udsoncan
from udsoncan import Client

from .base import UDSAction

# ── Configuration ──────────────────────────────────────────────────────────────
DID_TO_READ: int = 0xF194   # Change this to read a different DID


class ReadDIDAction(UDSAction):
    """Read a single DID with UDS service ReadDataByIdentifier (0x22).

    Parameters
    ----------
    did:
        The 16-bit Data Identifier to read.  Defaults to :data:`DID_TO_READ`.
    codec:
        Optional :class:`udsoncan.DidCodec` used to decode the raw response
        bytes.  When ``None`` the raw bytes are returned as-is.
    """

    def __init__(
        self,
        did: int = DID_TO_READ,
        codec: "udsoncan.DidCodec | None" = None,
    ) -> None:
        self.did = did
        self.codec = codec

    def run(self, client: Client):
        """Send ReadDataByIdentifier and return the response value."""
        codecs = {self.did: self.codec} if self.codec is not None else None
        response = client.read_data_by_identifier(
            self.did,
            didconfig=codecs,
        )
        value = response.service_data.values.get(self.did)
        return value
