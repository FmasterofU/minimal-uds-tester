# minimal-uds-tester

A minimal, extensible UDS (ISO 14229) tester written in Python.
Supports **CAN** (ISO-TP, via [python-can](https://python-can.readthedocs.io/) + [can-isotp](https://can-isotp.readthedocs.io/)) and **DoIP** (ISO 13400, via [doipclient](https://github.com/jacobschaer/python-doip-client)), and works on both **Windows** and **Linux** — including with a **Vector box**.

Out of the box it reads DID **0xF194** (ECU Software Version Number).  
The "core logic" is fully decoupled so you can swap in any other UDS operation in seconds.

---

## Project layout

```
minimal-uds-tester/
├── config.py                   ← all runtime parameters (transport, addresses, …)
├── main.py                     ← CLI entry point
├── requirements.txt
└── uds_tester/
    ├── transport/
    │   ├── base.py             ← abstract transport interface
    │   ├── can_transport.py    ← CAN + ISO-TP (Vector, SocketCAN, …)
    │   └── doip_transport.py   ← DoIP over TCP/IP
    └── actions/
        ├── base.py             ← abstract UDS action interface  ← plug-in point
        └── read_did.py         ← ReadDataByIdentifier (0x22) for DID 0xF194
```

---

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **Vector driver note (Windows):** The Vector XL Driver Library must be installed
> separately from [vector.com](https://www.vector.com/int/en/products/products-a-z/software/xl-driver-library/).
> python-can picks it up automatically.

### 2. Configure

Edit **`config.py`** to match your setup:

```python
# Pick the transport
TRANSPORT = "can"           # or "doip"

# CAN / Vector
CAN_INTERFACE = "vector"    # 'socketcan' on Linux, 'vector' on Windows
CAN_CHANNEL   = 0           # Vector channel index (or 'can0' / 'vcan0' for socketcan)
CAN_BITRATE   = 500_000
CAN_TX_ID     = 0x7E0       # tester → ECU
CAN_RX_ID     = 0x7E8       # ECU → tester

# DoIP
DOIP_HOST           = "192.168.1.10"
DOIP_TARGET_ADDRESS = 0x0001
```

### 3. Run

```bash
# Use whatever transport is set in config.py
python main.py

# Force a specific transport on the command line
python main.py --transport can
python main.py --transport doip
```

---

## Changing the core logic

The test logic lives entirely in **`uds_tester/actions/`**.  
Each action is a class that inherits from `UDSAction` and implements a single method:

```python
def run(self, client: udsoncan.Client):
    ...
```

### Example — read a different DID

```python
from uds_tester.actions.read_did import ReadDIDAction

action = ReadDIDAction(did=0xF190)   # ECU serial number
```

### Example — write a DID

```python
from uds_tester.actions.base import UDSAction

class WriteDIDAction(UDSAction):
    def run(self, client):
        client.write_data_by_identifier(0x1234, b'\x01\x02')
```

### Example — run a full sequence

```python
from uds_tester.actions.base import UDSAction

class DiagSessionThenReadDID(UDSAction):
    def run(self, client):
        client.change_session(3)                        # extended session
        return client.read_data_by_identifier(0xF194)
```

Then in **`main.py`**, replace the `action = ReadDIDAction(...)` line with an
instance of your new action — everything else stays the same.

---

## Supported CAN interfaces

| Interface       | `CAN_INTERFACE` value | OS            |
|-----------------|----------------------|---------------|
| Vector box      | `vector`             | Windows, Linux|
| SocketCAN       | `socketcan`          | Linux         |
| Kvaser          | `kvaser`             | Windows, Linux|
| PEAK PCAN       | `pcan`               | Windows, Linux|
| Virtual (test)  | `virtual`            | Any           |

---

## Dependencies

| Package       | Purpose                                 |
|---------------|-----------------------------------------|
| `python-can`  | CAN bus access (Vector, SocketCAN, …)   |
| `can-isotp`   | ISO-TP transport layer over CAN         |
| `udsoncan`    | UDS protocol (services, client)         |
| `doipclient`  | DoIP transport (ISO 13400)              |
