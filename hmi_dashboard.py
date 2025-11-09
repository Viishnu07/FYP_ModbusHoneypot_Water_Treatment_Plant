#!/usr/bin/env python3
"""
ICS Honeypot - HMI Dashboard
Web interface for water treatment plant monitoring.
Reads Modbus registers and displays process variables.
"""

import os
import logging
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hmi_access.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Modbus configuration
MODBUS_HOST = os.getenv('MODBUS_HOST', 'localhost')
MODBUS_PORT = int(os.getenv('MODBUS_PORT', 502))

# Register mappings (same as modbus_process_sim.py)
REGISTERS = {
    'CHLORINE_PPM': 40001,
    'PH_LEVEL': 40002,
    'PUMP_STATUS': 40003,
    'WATER_LEVEL': 40004,
    'FLOW_RATE': 40005,
    'TEMPERATURE': 40006,
    'PRESSURE': 40007,
    'TURBIDITY': 40008,
}

def read_modbus_register(client, register_address):
    """Read a single holding register from Modbus."""
    try:
        # Convert 4xxxx address to 0-based index
        address = register_address - 40001
        result = client.read_holding_registers(address, 1, unit=1)
        if result.isError():
            logger.error(f"Modbus error reading register {register_address}: {result}")
            return None
        return result.registers[0]
    except ModbusException as e:
        logger.error(f"Modbus exception reading register {register_address}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading register {register_address}: {e}")
        return None

def read_all_registers():
    """Read all process variables from Modbus."""
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    
    try:
        if not client.connect():
            logger.error(f"Failed to connect to Modbus at {MODBUS_HOST}:{MODBUS_PORT}")
            return None
            
        data = {}
        for name, address in REGISTERS.items():
            value = read_modbus_register(client, address)
            if value is not None:
                data[name] = value
                
        return data
    finally:
        client.close()

@app.route('/')
def index():
    """Main dashboard page."""
    # Log access
    client_ip = request.remote_addr
    logger.info(f"HMI dashboard accessed from {client_ip}")
    
    # Log to JSON file
    try:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'hmi_access',
            'client_ip': client_ip,
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'path': request.path
        }
        with open('logs/hmi_access.json', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        logger.error(f"Failed to write access log: {e}")
    
    return render_template('dashboard.html')

@app.route('/api/data')
def api_data():
    """API endpoint to get current process data."""
    data = read_all_registers()
    
    if data is None:
        return jsonify({'error': 'Failed to read Modbus data'}), 500
    
    # Format data for frontend
    formatted_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'chlorine_ppm': data.get('CHLORINE_PPM', 0) / 10.0,  # Convert to actual ppm
        'ph_level': data.get('PH_LEVEL', 700) / 100.0,       # Convert to actual pH
        'pump_status': 'ON' if data.get('PUMP_STATUS', 0) == 1 else 'OFF',
        'pump_status_raw': data.get('PUMP_STATUS', 0),
        'water_level_cm': data.get('WATER_LEVEL', 0),
        'flow_rate_lmin': data.get('FLOW_RATE', 0),
        'temperature_c': data.get('TEMPERATURE', 250) / 10.0,  # Convert to °C
        'pressure_psi': data.get('PRESSURE', 100) / 10.0,      # Convert to PSI
        'turbidity_ntu': data.get('TURBIDITY', 12) / 10.0,     # Convert to NTU
    }
    
    return jsonify(formatted_data)

@app.route('/api/history')
def api_history():
    """API endpoint for historical data (simplified - returns recent values)."""
    # In a real implementation, this would query a time-series database
    # For now, return current data as "history"
    data = read_all_registers()
    
    if data is None:
        return jsonify({'error': 'Failed to read Modbus data'}), 500
    
    # Generate fake history for demonstration
    history = []
    now = datetime.utcnow()
    for i in range(20):
        timestamp = now - timedelta(minutes=20-i)
        history.append({
            'timestamp': timestamp.isoformat(),
            'chlorine_ppm': (data.get('CHLORINE_PPM', 0) / 10.0) + (i % 3) * 0.1,
            'ph_level': (data.get('PH_LEVEL', 700) / 100.0) + (i % 2) * 0.01,
            'water_level_cm': data.get('WATER_LEVEL', 0) + (i % 5),
        })
    
    return jsonify(history)

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)

