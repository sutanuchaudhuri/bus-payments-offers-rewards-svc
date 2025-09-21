"""
Simulator Manager
Manages and coordinates simulator services
"""
import subprocess
import time
import requests
from datetime import datetime
import os

class SimulatorManager:
    def __init__(self):
        self.services = {
            'travel': {
                'script': 'travel_booking.py',
                'port': 5002,
                'name': 'Travel Booking Service',
                'base_url': 'http://localhost:5002',
                'process': None
            },
            'hotel': {
                'script': 'hotel_booking.py', 
                'port': 5003,
                'name': 'Hotel Booking Service',
                'base_url': 'http://localhost:5003',
                'process': None
            },
            'shopping': {
                'script': 'shopping.py',
                'port': 5004,
                'name': 'Shopping Service',
                'base_url': 'http://localhost:5004',
                'process': None
            }
        }
        self.base_dir = os.path.dirname(__file__)
    
    def start_service(self, service_name, python_path=None):
        """Start a specific simulator service"""
        if service_name not in self.services:
            raise ValueError(f"Unknown service: {service_name}")
        
        service = self.services[service_name]
        script_path = os.path.join(self.base_dir, 'services', service['script'])
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Service script not found: {script_path}")
        
        # Use provided Python path or default
        python_cmd = python_path or 'python'
        
        try:
            process = subprocess.Popen(
                [python_cmd, script_path],
                cwd=os.path.join(self.base_dir, 'services'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            service['process'] = process
            
            # Wait for service to start
            time.sleep(2)
            
            # Check if service is responsive
            if self.check_health(service_name):
                print(f"✅ {service['name']} started successfully on port {service['port']}")
                return True
            else:
                print(f"❌ {service['name']} failed to start properly")
                self.stop_service(service_name)
                return False
                
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")
            return False
    
    def stop_service(self, service_name):
        """Stop a specific simulator service"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        if service['process']:
            service['process'].terminate()
            service['process'].wait()
            service['process'] = None
            print(f"🛑 {service['name']} stopped")
            return True
        return False
    
    def start_all_services(self, python_path=None):
        """Start all simulator services"""
        print("Starting all simulator services...")
        success_count = 0
        
        for service_name in self.services:
            if self.start_service(service_name, python_path):
                success_count += 1
        
        print(f"\n{success_count}/{len(self.services)} services started successfully")
        return success_count == len(self.services)
    
    def stop_all_services(self):
        """Stop all simulator services"""
        print("Stopping all simulator services...")
        for service_name in self.services:
            self.stop_service(service_name)
    
    def check_health(self, service_name):
        """Check if a service is healthy"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        try:
            response = requests.get(f"{service['base_url']}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_service_status(self):
        """Get status of all services"""
        status = {}
        for service_name, service in self.services.items():
            status[service_name] = {
                'name': service['name'],
                'port': service['port'],
                'running': service['process'] is not None and service['process'].poll() is None,
                'healthy': self.check_health(service_name),
                'base_url': service['base_url']
            }
        return status
    
    def make_request(self, service_name, endpoint, method='GET', **kwargs):
        """Make a request to a simulator service"""
        if service_name not in self.services:
            raise ValueError(f"Unknown service: {service_name}")
        
        service = self.services[service_name]
        if not self.check_health(service_name):
            raise ConnectionError(f"{service['name']} is not available")
        
        url = f"{service['base_url']}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, **kwargs)
            elif method.upper() == 'PUT':
                response = requests.put(url, **kwargs)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to {service['name']}: {e}")

if __name__ == '__main__':
    import sys
    
    manager = SimulatorManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            python_path = sys.argv[2] if len(sys.argv) > 2 else None
            manager.start_all_services(python_path)
        elif command == 'stop':
            manager.stop_all_services()
        elif command == 'status':
            status = manager.get_service_status()
            print("\nSimulator Services Status:")
            print("-" * 50)
            for name, info in status.items():
                status_icon = "🟢" if info['healthy'] else "🔴"
                print(f"{status_icon} {info['name']} (:{info['port']}) - {'Healthy' if info['healthy'] else 'Offline'}")
        else:
            print("Usage: python simulator_manager.py [start|stop|status] [python_path]")
    else:
        print("Usage: python simulator_manager.py [start|stop|status] [python_path]")