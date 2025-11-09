#!/usr/bin/env python3
"""
ICS Honeypot - Modbus Process Simulator
Simulates a water treatment plant with writable process variables.
Logs all read/write operations for security analysis.
"""

import logging
import json
import time
from datetime import datetime
from threading import Thread, Lock
from pymodbus.server import StartTcpServer
# The corrected code
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/modbus_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Process variable register mappings
REGISTERS = {
    'CHLORINE_PPM': 40001,      # Holding register - Chlorine level (ppm)
    'PH_LEVEL': 40002,           # Holding register - pH level (×100, so 700 = 7.00)
    'PUMP_STATUS': 40003,       # Holding register - Pump on/off (0=off, 1=on)
    'WATER_LEVEL': 40004,       # Holding register - Water level (cm)
    'FLOW_RATE': 40005,         # Holding register - Flow rate (L/min)
    'TEMPERATURE': 40006,       # Holding register - Temperature (°C ×10)
    'PRESSURE': 40007,          # Holding register - Pressure (PSI ×10)
    'TURBIDITY': 40008,         # Holding register - Turbidity (NTU ×10)
}

class ProcessSimulator:
    """Simulates realistic process behavior based on register values."""
    
    def __init__(self, context):
        self.context = context
        self.running = True
        self.lock = Lock()
        self.process_thread = None
        
    def start(self):
        """Start the process simulation loop."""
        self.process_thread = Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        logger.info("Process simulator started")
        
    def stop(self):
        """Stop the process simulation."""
        self.running = False
        if self.process_thread:
            self.process_thread.join(timeout=2)
            
    def _process_loop(self):
        """Simulate realistic process behavior."""
        while self.running:
            try:
                with self.lock:
                    # Read current values
                    store = self.context[0]
                    chlorine = store.getValues(3, REGISTERS['CHLORINE_PPM'] - 40001, 1)[0]
                    ph = store.getValues(3, REGISTERS['PH_LEVEL'] - 40001, 1)[0]
                    pump = store.getValues(3, REGISTERS['PUMP_STATUS'] - 40001, 1)[0]
                    level = store.getValues(3, REGISTERS['WATER_LEVEL'] - 40001, 1)[0]
                    
                    # Simulate realistic process dynamics
                    # If pump is on, water level decreases, flow rate increases
                    if pump == 1:
                        # Decrease water level (simulate outflow)
                        new_level = max(0, level - 1)
                        store.setValues(3, REGISTERS['WATER_LEVEL'] - 40001, [new_level])
                        
                        # Set flow rate based on pump status
                        flow_rate = 150  # L/min when pump is on
                        store.setValues(3, REGISTERS['FLOW_RATE'] - 40001, [flow_rate])
                    else:
                        # Water level slowly increases (simulate inflow)
                        new_level = min(1000, level + 0.5)
                        store.setValues(3, REGISTERS['WATER_LEVEL'] - 40001, [int(new_level)])
                        
                        # No flow when pump is off
                        store.setValues(3, REGISTERS['FLOW_RATE'] - 40001, [0])
                    
                    # Temperature varies slightly (simulate ambient)
                    temp = store.getValues(3, REGISTERS['TEMPERATURE'] - 40001, 1)[0]
                    temp_variation = (temp % 10) - 5  # Small variation
                    new_temp = max(200, min(300, temp + temp_variation))  # 20-30°C
                    store.setValues(3, REGISTERS['TEMPERATURE'] - 40001, [int(new_temp)])
                    
                    # Pressure correlates with water level
                    pressure = int(level * 0.1 + 50)  # PSI calculation
                    store.setValues(3, REGISTERS['PRESSURE'] - 40001, [pressure])
                    
                    # Turbidity varies with flow
                    if pump == 1:
                        turbidity = 15 + (level % 10)  # NTU
                    else:
                        turbidity = 10 + (level % 5)
                    store.setValues(3, REGISTERS['TURBIDITY'] - 40001, [turbidity])
                    
            except Exception as e:
                logger.error(f"Error in process loop: {e}")
            
            time.sleep(2)  # Update every 2 seconds

class LoggingModbusSlaveContext(ModbusDeviceContext):
    """Custom Modbus slave context that logs all operations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_store_ref = None
    
    def setValues(self, fx, address, values):
        """Override setValues to log write operations."""
        client_addr = get_client_address()
        if self._data_store_ref:
            self._data_store_ref.log_operation('WRITE', address, values if isinstance(values, list) else [values], client_addr)
        return super().setValues(fx, address, values)
    
    def getValues(self, fx, address, count=1):
        """Override getValues to log read operations."""
        values = super().getValues(fx, address, count)
        client_addr = get_client_address()
        if self._data_store_ref:
            self._data_store_ref.log_operation('READ', address, list(values) if hasattr(values, '__iter__') else [values], client_addr)
        return values

class ModbusDataStore:
    """Custom data store with logging for all operations."""
    
    def __init__(self):
        self.store = LoggingModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0]*100),      # Discrete Inputs
            co=ModbusSequentialDataBlock(0, [0]*100),      # Coils
            hr=ModbusSequentialDataBlock(0, [0]*1000),     # Holding Registers
            ir=ModbusSequentialDataBlock(0, [0]*100)       # Input Registers
        )
        
        # Set reference for logging
        self.store._data_store_ref = self
        
        # Initialize default values
        self.store.setValues(3, REGISTERS['CHLORINE_PPM'] - 40001, [25])      # 2.5 ppm
        self.store.setValues(3, REGISTERS['PH_LEVEL'] - 40001, [700])         # 7.00 pH
        self.store.setValues(3, REGISTERS['PUMP_STATUS'] - 40001, [0])        # Pump off
        self.store.setValues(3, REGISTERS['WATER_LEVEL'] - 40001, [500])      # 500 cm
        self.store.setValues(3, REGISTERS['FLOW_RATE'] - 40001, [0])          # 0 L/min
        self.store.setValues(3, REGISTERS['TEMPERATURE'] - 40001, [250])      # 25.0°C
        self.store.setValues(3, REGISTERS['PRESSURE'] - 40001, [100])         # 10.0 PSI
        self.store.setValues(3, REGISTERS['TURBIDITY'] - 40001, [12])         # 1.2 NTU
        
        logger.info("Modbus data store initialized with default values")
        
    def log_operation(self, operation, address, values, client_address):
        """Log all Modbus operations for security analysis."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'address': address,
            'values': values,
            'client_ip': client_address[0] if client_address else 'unknown',
            'client_port': client_address[1] if client_address else 'unknown',
            'register_name': self._get_register_name(address)
        }
        
        # Write to JSON log file
        try:
            with open('logs/modbus_operations.json', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
        
        logger.info(f"{operation.upper()}: {log_entry['register_name']} (addr {address}) = {values} from {log_entry['client_ip']}:{log_entry['client_port']}")
        
    def _get_register_name(self, address):
        """Get human-readable register name."""
        for name, reg_addr in REGISTERS.items():
            if reg_addr == address + 40001:
                return name
        return f"REG_{address + 40001}"

# Thread-local storage for client addresses
_client_address = threading.local()

def get_client_address():
    """Get current client address from thread-local storage."""
    return getattr(_client_address, 'address', ('unknown', 0))

def set_client_address(address):
    """Set current client address in thread-local storage."""
    _client_address.address = address

def run_modbus_server():
    """Start the Modbus TCP server."""
    # Create custom data store
    data_store = ModbusDataStore()
    
    # Store reference for logging
    data_store.store._data_store = data_store
    
    # Create server context
    context = ModbusServerContext(data_store.store, single=True)
    
    # Start process simulator
    simulator = ProcessSimulator(context)
    simulator.start()
    
    try:
        logger.info("Starting Modbus TCP server on 0.0.0.0:502")
        logger.info("Process variables available:")
        for name, addr in REGISTERS.items():
            logger.info(f"  {name}: Register {addr}")
        
        # Note: Client IP logging is limited in pymodbus sync server
        # For better client IP capture, consider using async server or
        # implementing a custom request handler
        
        # Start server
        StartTcpServer(
            context=context,
            address=("0.0.0.0", 502),
        )
    except KeyboardInterrupt:
        logger.info("Shutting down Modbus server...")
        simulator.stop()
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        simulator.stop()

if __name__ == "__main__":
    import os
    os.makedirs('logs', exist_ok=True)
    run_modbus_server()

