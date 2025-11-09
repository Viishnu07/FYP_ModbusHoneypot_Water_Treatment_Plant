#!/usr/bin/env python3
"""
Modbus Read Script - Reconnaissance
Reads all process variables from the ICS honeypot
"""

from pymodbus.client import ModbusTcpClient
import sys

# Configuration
HONEYPOT_IP = '192.168.244.138'  # Change to your Windows host IP where Docker is running
HONEYPOT_PORT = 502

def read_registers():
    """Read all Modbus holding registers"""
    client = ModbusTcpClient(HONEYPOT_IP, port=HONEYPOT_PORT)
    
    try:
        print(f"[*] Connecting to {HONEYPOT_IP}:{HONEYPOT_PORT}...")
        client.connect()
        print("[+] Connected to Modbus server")
        
        # Register mapping
        registers = {
            0: ('CHLORINE_PPM', 'ppm ×10', 40001),
            1: ('PH_LEVEL', 'pH ×100', 40002),
            2: ('PUMP_STATUS', '0=off, 1=on', 40003),
            3: ('WATER_LEVEL', 'cm', 40004),
            4: ('FLOW_RATE', 'L/min', 40005),
            5: ('TEMPERATURE', '°C ×10', 40006),
            6: ('PRESSURE', 'PSI ×10', 40007),
            7: ('TURBIDITY', 'NTU ×10', 40008)
        }
        
        print("\n" + "=" * 60)
        print("PROCESS VARIABLES - READ OPERATION")
        print("=" * 60)
        
        # Read all holding registers
        result = client.read_holding_registers(0, 8, unit=1)
        
        if not result.isError():
            for addr, (name, unit, modbus_addr) in registers.items():
                raw_value = result.registers[addr]
                
                # Format display value
                if name == 'CHLORINE_PPM':
                    display_value = raw_value / 10.0
                    print(f"[+] {name:20s} (Addr {modbus_addr:5d}): {display_value:6.1f} {unit.split('×')[0].strip()}")
                elif name == 'PH_LEVEL':
                    display_value = raw_value / 100.0
                    print(f"[+] {name:20s} (Addr {modbus_addr:5d}): {display_value:6.2f} {unit.split('×')[0].strip()}")
                elif name == 'TEMPERATURE':
                    display_value = raw_value / 10.0
                    print(f"[+] {name:20s} (Addr {modbus_addr:5d}): {display_value:6.1f} {unit.split('×')[0].strip()}")
                elif name == 'PRESSURE':
                    display_value = raw_value / 10.0
                    print(f"[+] {name:20s} (Addr {modbus_addr:5d}): {display_value:6.1f} {unit.split('×')[0].strip()}")
                elif name == 'TURBIDITY':
                    display_value = raw_value / 10.0
                    print(f"[+] {name:20s} (Addr {modbus_addr:5d}): {display_value:6.1f} {unit.split('×')[0].strip()}")
                elif name == 'PUMP_STATUS':
                    status = "ON" if raw_value == 1 else "OFF"
                    print(f"[+] {name:20s} (Addr {modbus_addr:5d}): {status:6s} (raw: {raw_value})")
                else:
                    print(f"[+] {name:20s} (Addr {modbus_addr:5d}): {raw_value:6d} {unit}")
        else:
            print(f"[-] Error reading registers: {result}")
            return False
            
        print("=" * 60)
        print("[+] Reconnaissance complete - All registers read")
        return True
        
    except Exception as e:
        print(f"[-] Connection error: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        HONEYPOT_IP = sys.argv[1]
    if len(sys.argv) > 2:
        HONEYPOT_PORT = int(sys.argv[2])
    
    print(f"Modbus Read Script - Target: {HONEYPOT_IP}:{HONEYPOT_PORT}")
    read_registers()

