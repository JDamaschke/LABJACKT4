# LABJACKT4

Python module for controlling a LabJack T4 via Ethernet using Modbus TCP.

## Project

`LABJACKT4.py` provides a simple Python class for communication with a LabJack T4.

The module uses the LabJack T4's native Modbus TCP interface and does not require the LabJack LJM library.

## Supported functions

* DAC0 / DAC1 – set and read analogue output voltage
* AIN0 ... AIN11 – read analogue input voltage
* Internal device temperature
* Air/environment temperature
* DIO4 ... DIO11 – digital I/O
* Manual control of the STATUS LED for special operating conditions

## Requirements

* LabJack T4
* Ethernet connection to the LabJack T4
* Python 3.11 or later
* `pymodbus`

## Installation

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python package:

```bash
pip install -r requirements.txt
```

## Example

```python
from LABJACKT4 import LABJACKT4

t4 = LABJACKT4("192.168.178.204")

if t4.connect():
    print("LabJack T4 connected")

    t4.set_dac(0, 3.3)

    print(f"DAC0 = {t4.get_dac(0):.3f} V")
    print(f"AIN0 = {t4.get_ain(0):.3f} V")
    print(f"Temperature = {t4.get_temperature():.2f} °C")

    t4.disconnect()
else:
    print("Connection to LabJack T4 failed")
```

## Communication

Communication is performed via Modbus TCP over Ethernet.

Default Modbus TCP port:

```text
502
```

Default device ID:

```text
1
```

## Notes

The actual maximum DAC output voltage depends on the LabJack supply voltage and electrical load.

The STATUS LED is normally controlled automatically by the LabJack. Manual LED control is intended only for special operating conditions.

## Project status

## Project status

Version 1.0.0 – initial working version.

The module has been tested on:

* Raspberry Pi 4
* Debian 12 (Bookworm)
* Python 3.11
* ARM64 / aarch64
* LabJack T4 via Ethernet / Modbus TCP
