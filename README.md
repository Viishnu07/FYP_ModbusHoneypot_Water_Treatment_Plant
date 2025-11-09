# 🏭 Modbus Water Treatment Plant Simulator

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-Educational-green.svg)](LICENSE)

A realistic Modbus TCP simulator for water treatment plant process monitoring with an interactive HMI dashboard. Perfect for ICS security training, testing, and research.


</div>

---

## ⚠️ Disclaimer

**This project is for educational and research purposes only.**

- ⚠️ Only test on systems you own or have explicit permission to test
- ⚠️ Never connect to or test against real industrial control systems
- ⚠️ Deploy only in isolated, controlled network environments
- ⚠️ The author is not responsible for any misuse or damage

---

## 🚀 Features

### 🎯 High-Interaction Modbus TCP Server
- Fully writable holding registers (read/write support)
- Realistic process variable simulation
- Dynamic behavior modeling (pump control affects water level, flow rate, etc.)
- Standard Modbus TCP protocol (port 502)

### 📊 Interactive HMI Dashboard
- Beautiful real-time web interface
- Auto-updating process data (2-second refresh)
- Visual alerts for out-of-range values
- Responsive design

### 📝 Comprehensive Logging
- All Modbus operations logged to JSON
- Client IP and timestamp tracking
- HMI access logging
- Perfect for security analysis and anomaly detection

### 🐳 Docker-Based Deployment
- One-command setup with Docker Compose
- Lightweight architecture (~200MB)
- Isolated services
- Easy to deploy and tear down

---

## 🎯 Use Cases

- **🔒 ICS Security Training** - Learn Modbus protocol vulnerabilities and attack techniques
- **🧪 Security Testing** - Test IDS/IPS rules, SIEM detections, and security tools
- **💻 Software Development** - Develop and test Modbus clients and HMI applications
- **🔬 Research** - Study ICS protocols, attack patterns, and anomaly detection

---

## 📋 Process Variables

The simulator exposes 8 realistic process variables via Modbus holding registers:

| Register | Address | Description | Unit | Normal Range |
|----------|---------|-------------|------|--------------|
| **CHLORINE_PPM** | 40001 | Chlorine level | ppm ×10 | 0.5-4.0 ppm |
| **PH_LEVEL** | 40002 | pH level | pH ×100 | 6.5-8.5 pH |
| **PUMP_STATUS** | 40003 | Pump on/off | 0=OFF, 1=ON | - |
| **WATER_LEVEL** | 40004 | Water level | cm | 0-1000 cm |
| **FLOW_RATE** | 40005 | Flow rate | L/min | 0-200 L/min |
| **TEMPERATURE** | 40006 | Temperature | °C ×10 | 20-30°C |
| **PRESSURE** | 40007 | Pressure | PSI ×10 | 5-15 PSI |
| **TURBIDITY** | 40008 | Turbidity | NTU ×10 | 1-3 NTU |

### Process Dynamics
- **Pump ON**: Water level decreases, flow rate increases to 150 L/min
- **Pump OFF**: Water level slowly increases, flow rate drops to 0
- **Pressure**: Calculated based on water level
- **Turbidity**: Varies with pump status and water level

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/get-started) and Docker Compose
- Git (optional, for cloning)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Viishnu07/FYP_ModbusHoneypot_Water_Treatment_Plant.git
   cd FYP_ModbusHoneypot_Water_Treatment_Plant
   ```

2. **Create log directories:**
   ```bash
   mkdir -p logs/modbus logs/hmi
   ```

3. **Start the services:**

   **Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   **Windows (PowerShell):**
   ```powershell
   .\start.ps1
   ```

   **Or manually:**
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

5. **Access the HMI Dashboard:**
   
   Open your browser to: **http://localhost:5000**

---

## 📖 Usage

### View Real-Time Process Data

Access the HMI dashboard at `http://localhost:5000` to monitor:
- Live process variables
- Pump status indicator
- Alerts for out-of-range values
- Auto-updating display

### Read Modbus Registers

**Using Python:**
```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('localhost', port=502)
client.connect()

# Read all 8 registers
result = client.read_holding_registers(0, 8, unit=1)
print(f"Registers: {result.registers}")

client.close()
```

**Using modbus-cli:**
```bash
modbus read localhost:502 40001 8
```

### Write Modbus Registers

**Control the pump:**
```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('localhost', port=502)
client.connect()

# Turn pump ON (register 40003)
client.write_register(2, 1, unit=1)

# Turn pump OFF
client.write_register(2, 0, unit=1)

client.close()
```

**Adjust chlorine level:**
```python
# Set chlorine to 2.5 ppm (value = 25, since unit is ppm ×10)
client.write_register(0, 25, unit=1)
```

All operations are automatically logged! ✅

---

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs -f modbus_simulator
docker-compose logs -f hmi_dashboard

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild containers
docker-compose up -d --build
```

---

## 📁 Project Structure

```
.
├── docker-compose.yml          # Docker services configuration
├── Dockerfile.modbus           # Modbus simulator image
├── Dockerfile.hmi              # HMI dashboard image
├── requirements.txt            # Python dependencies
├── modbus_process_sim.py       # Modbus TCP simulator
├── hmi_dashboard.py            # Flask HMI web interface
├── templates/
│   └── dashboard.html          # HMI dashboard template
├── logs/                       # Auto-generated logs
│   ├── modbus/                 # Modbus operation logs
│   └── hmi/                    # HMI access logs
├── kali_scripts/               # Attack/testing scripts
│   ├── modbus_read.py          # Read all registers
│   ├── modbus_attack.py        # Attack simulation
│   └── hmi_test.py             # HMI testing
├── start.sh                    # Linux/Mac startup
└── start.ps1                   # Windows startup
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [kali_scripts/README.md](kali_scripts/README.md) | Attack script documentation |

---

## 🔍 Logging

All operations are logged to JSON files for security analysis:

### Modbus Operations Log
**Location:** `logs/modbus/modbus_operations.json`

```json
{
  "timestamp": "2025-11-08T10:30:45.123456",
  "operation": "WRITE",
  "address": 2,
  "values": [1],
  "client_ip": "172.18.0.1",
  "client_port": 54321,
  "register_name": "PUMP_STATUS"
}
```

### HMI Access Log
**Location:** `logs/hmi/hmi_access.json`

```json
{
  "timestamp": "2025-11-08T10:30:45.123456",
  "event": "hmi_access",
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "path": "/"
}
```

---

## 🧪 Testing

### Pre-built Attack Scripts

The project includes ready-to-use attack scripts:

```bash
# Read all registers
python kali_scripts/modbus_read.py

# Run attack simulation
python kali_scripts/modbus_attack.py

# Test HMI access
python kali_scripts/hmi_test.py

# Network scanning
bash kali_scripts/network_scan.sh
```

---

## 🐛 Troubleshooting

### Port 502 already in use
```bash
# Linux/Mac
sudo netstat -tulpn | grep :502

# Windows
netstat -ano | findstr "502"
```

### Modbus connection refused
- Verify container is running: `docker-compose ps`
- Check logs: `docker-compose logs modbus_simulator`
- Ensure port 502 is accessible

### HMI dashboard shows errors
- Check if Modbus simulator is running
- Verify network connectivity: `docker network ls`
- Check logs: `docker-compose logs hmi_dashboard`

---

## 💻 Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run Modbus simulator
python modbus_process_sim.py

# Run HMI dashboard (in another terminal)
python hmi_dashboard.py
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📜 License

This project is for **educational and research purposes only**. 

---

## 🙏 Acknowledgments

- Built with [PyModbus](https://github.com/pymodbus-dev/pymodbus)
- Web interface powered by [Flask](https://flask.palletsprojects.com/)
- Designed for ICS security research and education

---

## 📧 Contact

For questions, issues, or suggestions:
- Open an [Issue](https://github.com/Viishnu07/FYP_ModbusHoneypot_Water_Treatment_Plant/issues)
- Pull Requests are welcome!

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for ICS Security

</div>

