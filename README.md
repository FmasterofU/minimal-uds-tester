# minimal-uds-tester

A minimal Python UDS (Unified Diagnostic Services) tester that sends a
**ReadDataByIdentifier (service 0x22)** request for DID **0xF194** over two
transport layers:

| Transport | Standard | CLI sub-command |
|-----------|----------|-----------------|
| CAN bus   | ISO 15765-2 (ISO-TP) | `can`  |
| Ethernet  | ISO 13400 (DoIP)     | `doip` |

---

## Requirements

Python 3.8+ and the packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Usage

### CAN transport

```bash
python uds_tester.py can \
    --channel   vcan0     \   # CAN channel (default: vcan0)
    --interface socketcan \   # python-can bustype (default: socketcan)
    --tx-id     0x7E0     \   # ISO-TP transmit CAN ID (default: 0x7E0)
    --rx-id     0x7E8         # ISO-TP receive  CAN ID (default: 0x7E8)
```

Quick start with a virtual CAN interface (Linux):

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up
python uds_tester.py can
```

### DoIP (Ethernet) transport

```bash
python uds_tester.py doip \
    --host           192.168.1.10 \   # ECU IP address (required)
    --port           13400        \   # DoIP port (default: 13400)
    --source-address 0x0E00       \   # Tester logical address (default: 0x0E00)
    --target-address 0x1000           # ECU logical address   (default: 0x1000)
```

---

## Output

On a positive response the tool prints the raw hex value of DID 0xF194:

```
[DoIP] host='192.168.1.10'  port=13400  source=0x0E00  target=0x1000
Sending ReadDataByIdentifier for DID 0xF194 …
[OK] DID 0xF194 = 303132333435
```

On a negative response:

```
[NEGATIVE RESPONSE] code=0x31  (requestOutOfRange)
```