"""
System Optimizer Module
Provides system optimization tools and suggestions
"""

import psutil
import os
import subprocess
import platform
from typing import Dict, List, Optional
import time

class SystemOptimizer:
    def __init__(self):
        self.system = platform.system().lower()
        
        # Process alternatives mapping
        self.alternatives = {
            'chrome.exe': 'Consider using Firefox or Edge for lower memory usage',
            'firefox.exe': 'Consider using Chrome or Edge for better performance',
            'code.exe': 'Consider using VS Code Insiders or Sublime Text',
            'slack.exe': 'Consider using web version or Discord',
            'teams.exe': 'Consider using web version',
            'spotify.exe': 'Consider using web player or lighter music apps',
            'discord.exe': 'Consider using web version or lighter chat apps',
            'steam.exe': 'Close when not gaming to save resources',
            'origin.exe': 'Close when not gaming to save resources',
            'photoshop.exe': 'Consider using GIMP or Canva for lighter tasks',
            'illustrator.exe': 'Consider using Inkscape or Figma',
            'premiere.exe': 'Consider using DaVinci Resolve or lighter video editors'
        }
        
        # High resource process patterns
        self.resource_heavy_patterns = [
            'chrome', 'firefox', 'edge', 'safari',  # Browsers
            'photoshop', 'illustrator', 'premiere', 'after effects',  # Adobe
            'steam', 'origin', 'epic', 'battle.net',  # Gaming platforms
            'slack', 'teams', 'discord', 'zoom',  # Communication
            'spotify', 'itunes', 'vlc',  # Media
            'android studio', 'intellij', 'pycharm',  # IDEs
            'blender', '3ds max', 'maya'  # 3D software
        ]
        
    def get_suggestions(self, system_stats: Dict, processes: List[Dict]) -> List[str]:
        """Generate optimization suggestions based on current system state"""
        suggestions = []
        
        try:
            # CPU-based suggestions
            if system_stats.get('cpu_percent', 0) > 80:
                suggestions.append("High CPU usage detected. Consider closing unnecessary applications.")
                
                # Find CPU-heavy processes
                cpu_heavy = [p for p in processes if p.get('cpu_percent', 0) > 20]
                if cpu_heavy:
                    top_process = max(cpu_heavy, key=lambda x: x.get('cpu_percent', 0))
                    suggestions.append(f"'{top_process['name']}' is using {top_process['cpu_percent']:.1f}% CPU.")
                    
            # Memory-based suggestions
            if system_stats.get('memory_percent', 0) > 85:
                suggestions.append("High memory usage detected. Consider closing memory-intensive applications.")
                
                # Find memory-heavy processes
                memory_heavy = [p for p in processes if p.get('memory_mb', 0) > 500]
                if memory_heavy:
                    top_process = max(memory_heavy, key=lambda x: x.get('memory_mb', 0))
                    suggestions.append(f"'{top_process['name']}' is using {top_process['memory_mb']:.0f} MB RAM.")
                    
            # Disk-based suggestions
            if system_stats.get('disk_percent', 0) > 90:
                suggestions.append("Disk space is running low. Consider cleaning temporary files.")
                suggestions.append("Run disk cleanup or remove unused applications.")
                
            # Process-specific suggestions
            for process in processes:
                process_name = process.get('name', '').lower()
                
                # Check for alternatives
                for pattern, suggestion in self.alternatives.items():
                    if pattern.replace('.exe', '') in process_name:
                        if process.get('memory_mb', 0) > 1000:  # Only suggest if using >1GB
                            suggestions.append(f"{process['name']}: {suggestion}")
                            break
                            
            # General optimization suggestions
            if len(processes) > 100:
                suggestions.append("Many processes running. Consider disabling startup programs.")
                
            # System-specific suggestions
            if self.system == 'windows':
                suggestions.extend(self._get_windows_suggestions(system_stats))
            elif self.system == 'darwin':  # macOS
                suggestions.extend(self._get_macos_suggestions(system_stats))
            else:  # Linux
                suggestions.extend(self._get_linux_suggestions(system_stats))
                
            # If no specific suggestions, provide general ones
            if not suggestions:
                suggestions = [
                    "System is running well! No immediate optimizations needed.",
                    "Consider restarting your computer if it's been running for days.",
                    "Keep your system updated for optimal performance."
                ]
                
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            suggestions = ["Unable to generate suggestions at this time."]
            
        return suggestions[:8]  # Limit to 8 suggestions
        
    def _get_windows_suggestions(self, stats: Dict) -> List[str]:
        """Windows-specific optimization suggestions"""
        suggestions = []
        
        if stats.get('memory_percent', 0) > 80:
            suggestions.append("Run Windows Memory Diagnostic to check for memory issues.")
            suggestions.append("Disable visual effects in Performance Options.")
            
        if stats.get('disk_percent', 0) > 85:
            suggestions.append("Run Disk Cleanup to free up space.")
            suggestions.append("Consider enabling Storage Sense for automatic cleanup.")
            
        return suggestions
        
    def _get_macos_suggestions(self, stats: Dict) -> List[str]:
        """macOS-specific optimization suggestions"""
        suggestions = []
        
        if stats.get('memory_percent', 0) > 80:
            suggestions.append("Check Activity Monitor for memory pressure.")
            suggestions.append("Consider reducing visual effects in Accessibility settings.")
            
        if stats.get('disk_percent', 0) > 85:
            suggestions.append("Use 'About This Mac > Storage > Optimize' for cleanup.")
            suggestions.append("Empty Trash and clear Downloads folder.")
            
        return suggestions
        
    def _get_linux_suggestions(self, stats: Dict) -> List[str]:
        """Linux-specific optimization suggestions"""
        suggestions = []
        
        if stats.get('memory_percent', 0) > 80:
            suggestions.append("Consider using a lighter desktop environment.")
            suggestions.append("Check for memory leaks with 'htop' or 'free -h'.")
            
        if stats.get('disk_percent', 0) > 85:
            suggestions.append("Use 'sudo apt autoremove' to clean packages (Ubuntu/Debian).")
            suggestions.append("Clear package cache and temporary files.")
            
        return suggestions
        
    def kill_process(self, pid: int) -> bool:
        """Kill a process by PID"""
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                process.kill()
                
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"Error killing process {pid}: {e}")
            return False
            
    def optimize_system(self) -> Dict:
        """Perform comprehensive system optimization"""
        optimization_results = {
            'killed_processes': 0,
            'memory_freed': 0,
            'cache_cleared': False,
            'errors': []
        }
        
        try:
            # Get initial memory usage
            initial_memory = psutil.virtual_memory().used / (1024**2)  # MB
            
            # Kill resource-heavy processes
            killed_count = self._kill_resource_heavy_processes()
            optimization_results['killed_processes'] = killed_count
            
            # Clear system cache
            cache_cleared = self._clear_system_cache()
            optimization_results['cache_cleared'] = cache_cleared
            
            # Calculate memory freed
            time.sleep(2)  # Wait for processes to fully terminate
            final_memory = psutil.virtual_memory().used / (1024**2)  # MB
            optimization_results['memory_freed'] = max(0, initial_memory - final_memory)
            
        except Exception as e:
            optimization_results['errors'].append(str(e))
            
        return optimization_results
        
    def _kill_resource_heavy_processes(self) -> int:
        """Kill processes that are using excessive resources"""
        killed_count = 0
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    
                    # Skip system processes
                    if proc_info['pid'] < 10:
                        continue
                        
                    # Skip current process
                    if proc_info['pid'] == os.getpid():
                        continue
                        
                    # Kill if using excessive resources
                    if (proc_info['cpu_percent'] and proc_info['cpu_percent'] > 50) or \
                       (proc_info['memory_percent'] and proc_info['memory_percent'] > 20):
                        
                        # Check if it's a non-essential process
                        if self._is_safe_to_kill(proc_info['name']):
                            if self.kill_process(proc_info['pid']):
                                killed_count += 1
                                print(f"Killed process: {proc_info['name']} (PID: {proc_info['pid']})")
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"Error in kill_resource_heavy_processes: {e}")
            
        return killed_count
        
    def _is_safe_to_kill(self, process_name: str) -> bool:
        """Check if a process is safe to kill"""
        if not process_name:
            return False
            
        process_name = process_name.lower()
        
        # Never kill these critical processes
        critical_processes = [
            'system', 'kernel', 'init', 'systemd', 'explorer.exe', 'finder',
            'dwm.exe', 'winlogon.exe', 'csrss.exe', 'smss.exe', 'wininit.exe',
            'services.exe', 'lsass.exe', 'svchost.exe', 'python', 'python.exe'
        ]
        
        for critical in critical_processes:
            if critical in process_name:
                return False
                
        # Safe to kill these resource-heavy applications
        safe_to_kill = [
            'chrome', 'firefox', 'edge', 'safari',
            'spotify', 'steam', 'discord', 'slack', 'teams',
            'photoshop', 'illustrator', 'premiere'
        ]
        
        for safe in safe_to_kill:
            if safe in process_name:
                return True
                
        return False
        
    def _clear_system_cache(self) -> bool:
        """Clear system cache and temporary files"""
        try:
            if self.system == 'windows':
                return self._clear_windows_cache()
            elif self.system == 'darwin':
                return self._clear_macos_cache()
            else:
                return self._clear_linux_cache()
                
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
            
    def _clear_windows_cache(self) -> bool:
        """Clear Windows cache and temporary files"""
        try:
            # Clear temp files
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp')
            ]
            
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        for file in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                    except (PermissionError, FileNotFoundError):
                        continue
                        
            return True
            
        except Exception as e:
            print(f"Error clearing Windows cache: {e}")
            return False
            
    def _clear_macos_cache(self) -> bool:
        """Clear macOS cache"""
        try:
            # Clear user cache
            cache_dir = os.path.expanduser('~/Library/Caches')
            if os.path.exists(cache_dir):
                subprocess.run(['find', cache_dir, '-type', 'f', '-delete'], 
                             capture_output=True, timeout=30)
                             
            return True
            
        except Exception as e:
            print(f"Error clearing macOS cache: {e}")
            return False
            
    def _clear_linux_cache(self) -> bool:
        """Clear Linux cache"""
        try:
            # Clear package cache (if available)
            try:
                subprocess.run(['sudo', 'apt', 'clean'], 
                             capture_output=True, timeout=30, check=False)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
                
            # Clear user cache
            cache_dir = os.path.expanduser('~/.cache')
            if os.path.exists(cache_dir):
                subprocess.run(['find', cache_dir, '-type', 'f', '-delete'], 
                             capture_output=True, timeout=30)
                             
            return True
            
        except Exception as e:
            print(f"Error clearing Linux cache: {e}")
            return False
            
    def get_optimization_score(self, system_stats: Dict) -> int:
        """Calculate system optimization score (0-100)"""
        try:
            cpu_score = max(0, 100 - system_stats.get('cpu_percent', 0))
            memory_score = max(0, 100 - system_stats.get('memory_percent', 0))
            disk_score = max(0, 100 - system_stats.get('disk_percent', 0))
            
            # Weighted average
            total_score = (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
            
            return int(total_score)
            
        except Exception as e:
            print(f"Error calculating optimization score: {e}")
            return 50  # Default score