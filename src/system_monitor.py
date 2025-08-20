"""
System Monitor Module
Handles real-time system performance monitoring using psutil
"""

import psutil
import time
from typing import Dict, List

class SystemMonitor:
    def __init__(self):
        self.last_cpu_times = None
        
    def get_system_stats(self) -> Dict:
        """Get current system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            return {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_gb': memory_used_gb,
                'memory_total_gb': memory_total_gb,
                'disk_percent': disk_percent,
                'disk_used_gb': disk_used_gb,
                'disk_total_gb': disk_total_gb,
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv,
                'uptime_hours': uptime / 3600,
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0
            }
            
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return self._get_default_stats()
            
    def get_processes(self) -> List[Dict]:
        """Get list of running processes with their resource usage"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    
                    # Skip system processes with no name
                    if not proc_info['name']:
                        continue
                        
                    # Calculate memory in MB
                    memory_mb = 0
                    if proc_info['memory_info']:
                        memory_mb = proc_info['memory_info'].rss / (1024 * 1024)
                    
                    process_data = {
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'] or 0,
                        'memory_percent': proc_info['memory_percent'] or 0,
                        'memory_mb': memory_mb,
                        'timestamp': time.time()
                    }
                    
                    processes.append(process_data)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process might have terminated or we don't have access
                    continue
                    
        except Exception as e:
            print(f"Error getting processes: {e}")
            
        return processes
        
    def get_top_processes(self, limit: int = 10, sort_by: str = 'cpu') -> List[Dict]:
        """Get top processes sorted by CPU or memory usage"""
        processes = self.get_processes()
        
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
        return processes[:limit]
        
    def get_system_load(self) -> Dict:
        """Get system load averages (Unix-like systems)"""
        try:
            if hasattr(psutil, 'getloadavg'):
                load1, load5, load15 = psutil.getloadavg()
                return {
                    'load_1min': load1,
                    'load_5min': load5,
                    'load_15min': load15
                }
        except (AttributeError, OSError):
            # Not available on Windows
            pass
            
        return {'load_1min': 0, 'load_5min': 0, 'load_15min': 0}
        
    def get_temperature_info(self) -> Dict:
        """Get system temperature information if available"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get CPU temperature if available
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        if entries:
                            return {
                                'cpu_temp': entries[0].current,
                                'cpu_temp_high': entries[0].high,
                                'cpu_temp_critical': entries[0].critical
                            }
        except (AttributeError, OSError):
            pass
            
        return {'cpu_temp': 0, 'cpu_temp_high': 0, 'cpu_temp_critical': 0}
        
    def _get_default_stats(self) -> Dict:
        """Return default stats in case of error"""
        return {
            'timestamp': time.time(),
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_used_gb': 0,
            'memory_total_gb': 8,  # Default assumption
            'disk_percent': 0,
            'disk_used_gb': 0,
            'disk_total_gb': 100,  # Default assumption
            'network_bytes_sent': 0,
            'network_bytes_recv': 0,
            'uptime_hours': 0,
            'cpu_count': 4,  # Default assumption
            'cpu_freq': 2400  # Default assumption
        }