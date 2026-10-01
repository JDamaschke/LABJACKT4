##########################################################

"""
File:	LABJACKT4.py
Type:	Modul
Start:	28.9.2026
Update:	01.10.2026

Folder: '/home/admin/PYTHON/MODUL'

Methods:
--------
    
(1.)	DACx
(2.)	AINx
(3.)	Temperature
(4.)	DIO
(5.)	Status-LED

"""


import struct
from pymodbus.client import ModbusTcpClient

DEVICE_ID = 1

class LABJACKT4:

    def __init__(self, ip, port=502, device_id=DEVICE_ID):
        self.ip = ip
        self.port = port
        self.device_id = device_id

        self.client = ModbusTcpClient(
            host=self.ip,
            port=self.port
        )

    def connect(self):
        return self.client.connect()

    def disconnect(self):
        self.client.close()
  
  
  
    #  UINT32-Read and Write Functions
    # -----------------------------------

    def write_u32(self, address, value):
        high = (value >> 16) & 0xFFFF
        low = value & 0xFFFF

        result = self.client.write_registers(
            address=address,
            values=[high, low],
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(
                f"Write error address {address}: {result}"
            )

        

    # Read 32 Bit Register 
    #---------------------

    def read_u32(self, address):
        result = self.client.read_holding_registers(
            address=address,
            count=2,
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(
                f"Read error address {address}: {result}"
            )

        return (
            (result.registers[0] << 16)
            | result.registers[1]
        )

        
        
    # (1) Set DACx output voltage
    # ----------------------------
        
    def set_dac(self, DacNr, voltage):

        if DacNr not in (0, 1):
            raise ValueError(
                "DAC channel must be 0 or 1."
            )

        if not 0.0 <= voltage <= 5.0:
            raise ValueError(
                "DAC voltage range is 0.0 ... 5.0 V."
            )

        high, low = float_to_modbus(voltage)

        result = self.client.write_registers(
            address=1000 + 2 * DacNr,
            values=[high, low],
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(
                f"Error while writing DAC{DacNr}: {result}"
            )

        return self.get_dac(DacNr)
 
     # Read DACx value
     # ---------------
 
    def get_dac(self, DacNr):

        if DacNr not in (0, 1):
            raise ValueError(
                "DAC channel must be 0 or 1."
            )

        result = self.client.read_holding_registers(
            address=1000 + 2 * DacNr,
            count=2,
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(
                f"Error while reading DAC{DacNr}: {result}"
            )

        return modbus_to_float(
            result.registers[0],
            result.registers[1]
        )


    # (2) Voltage measuring on AINx input
    # -----------------------------------
    
    
    def get_ain(self, channel):
        if not 0 <= channel <= 11:
            raise ValueError("AIN-channel in range: 0 ... 11.")

        result = self.client.read_holding_registers(
            address=channel * 2,
            count=2,
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(f"Error while reading AIN{channel}: {result}")

        high = result.registers[0]
        low = result.registers[1]

        return modbus_to_float(high, low)
    
    
    # (3) Get Labjack device temperature
    # ----------------------------------

    def get_temperature(self, sensor="device", unit="C"):
        """
        Reading device temperature of LabJack T4.

        sensor:
            "device" = internal temp
            "air"    = environmemt temp

        unit:
            "K" = Kelvin
            "C" = Celsius
            "F" = Fahrenheit
        """

        if sensor == "device":
            address = 60052

        elif sensor == "air":
            address = 60050

        else:
            raise ValueError(
                "sensor type: only 'device' or 'air'."
            )

        result = self.client.read_holding_registers(
            address=address,
            count=2,
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(
                f"Error while reading temp: {result}"
            )

        kelvin = modbus_to_float(
            result.registers[0],
            result.registers[1]
        )

        if unit.upper() == "K":
            return kelvin

        elif unit.upper() == "C":
            return kelvin - 273.15

        elif unit.upper() == "F":
            return kelvin * 1.8 - 459.67

        else:
            raise ValueError(
                "unit only 'K', 'C' or 'F'."
            )


    # (4) Setup DIO-Pin FI4...7 set as digital IO
    # -------------------------------------------


    def set_dio_output(self, dio):

        if not 4 <= dio <= 11:
            raise ValueError("DIO in range: 4 <= dio <= 11")

        bit = 1 << dio

        # Nur diesen DIO freigeben
        inhibit = 0xFFFFFFFF ^ bit

        self.write_u32(2900, inhibit)
        self.write_u32(2850, bit)

        # Danach wieder alle DIO sperren
        self.write_u32(2900, 0)
        
        
        
        # Set single DIO output value
        # ---------------------------

    def set_dio(self, dio, state):

        if not 4 <= dio <= 11:
            raise ValueError("DIO in range: 4 <= dio <= 11")

        self.set_dio_output(dio)

        bit = 1 << dio

        # Nur diesen DIO freigeben
        inhibit = 0xFFFFFFFF ^ bit
        self.write_u32(2900, inhibit)

        if state:
            self.write_u32(2800, bit)
        else:
            self.write_u32(2800, 0)

        # Schutz wieder aktivieren
        self.write_u32(2900, 0)
        
        
        # Read current value (high/low) on DIO pin
        # ----------------------------------------

    def get_dio(self, dio):

        if not 4 <= dio <= 11:
            raise ValueError("DIO in range: 4 <= dio <= 11")

        state = self.read_u32(2800)

        return bool(state & (1 << dio))



        # (5) Set Status LED
        # ------------------

    def set_status_led(self, state):
        
        # state:
        #   True  = EIN
        #   False = AUS

        # LED-Steuerung auf "Manual" stellen
        result = self.client.write_register(
            address=48006,
            value=4,
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(
                f"Error while activated LED-Modus: {result}"
            )

        # STATUS-LED schalten
        value = 1 if state else 0

        result = self.client.write_register(
            address=2991,
            value=value,
            device_id=self.device_id
        )

        if result.isError():
            raise RuntimeError(
                f"Error while set STATUS-LED: {result}"
            )


  


# Global Functions #################################################
####################################################################

#FLOAT32 -> Two Modbus-Registers.

def float_to_modbus(value):
    data = struct.pack(">f", value)
    return struct.unpack(">HH", data)


# Two Modbus-Register -> FLOAT32.

def modbus_to_float(high, low):
    data = struct.pack(">HH", high, low)
    return struct.unpack(">f", data)[0]
