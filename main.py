#!/usr/bin/env python3
"""
AI-Powered OS Optimizer
A desktop application that monitors system performance and uses AI/ML to suggest optimizations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import os

# Import custom modules
from src.system_monitor import SystemMonitor
from src.ai_predictor import AIPredictor
from src.optimizer import SystemOptimizer
from src.data_handler import DataHandler
from src.ui_components import ModernUI

class OSOptimizerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI-Powered OS Optimizer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.data_handler = DataHandler()
        self.ai_predictor = AIPredictor(self.data_handler)
        self.optimizer = SystemOptimizer()
        self.ui = ModernUI(self.root)
        
        # State variables
        self.monitoring = False
        self.selected_process = None
        
        self.setup_ui()
        self.start_monitoring()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        # Create main frames
        self.create_header()
        self.create_system_stats()
        self.create_process_list()
        self.create_ai_panel()
        self.create_control_panel()
        
    def create_header(self):
        """Create the header section"""
        header_frame = self.ui.create_frame(self.root, height=60)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        title_label = self.ui.create_label(
            header_frame, 
            "🤖 AI-Powered OS Optimizer", 
            font=('Arial', 18, 'bold'),
            fg='#4CAF50'
        )
        title_label.pack(side='left', padx=20, pady=15)
        
        # Status indicator
        self.status_label = self.ui.create_label(
            header_frame, 
            "● Monitoring Active", 
            font=('Arial', 10),
            fg='#4CAF50'
        )
        self.status_label.pack(side='right', padx=20, pady=15)
        
    def create_system_stats(self):
        """Create system statistics section"""
        stats_frame = self.ui.create_frame(self.root, height=120)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # CPU Usage
        cpu_frame = self.ui.create_frame(stats_frame)
        cpu_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.ui.create_label(cpu_frame, "CPU Usage", font=('Arial', 12, 'bold')).pack()
        self.cpu_progress = self.ui.create_progressbar(cpu_frame)
        self.cpu_progress.pack(fill='x', padx=10, pady=5)
        self.cpu_label = self.ui.create_label(cpu_frame, "0%")
        self.cpu_label.pack()
        
        # RAM Usage
        ram_frame = self.ui.create_frame(stats_frame)
        ram_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.ui.create_label(ram_frame, "RAM Usage", font=('Arial', 12, 'bold')).pack()
        self.ram_progress = self.ui.create_progressbar(ram_frame)
        self.ram_progress.pack(fill='x', padx=10, pady=5)
        self.ram_label = self.ui.create_label(ram_frame, "0%")
        self.ram_label.pack()
        
        # Disk Usage
        disk_frame = self.ui.create_frame(stats_frame)
        disk_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.ui.create_label(disk_frame, "Disk Usage", font=('Arial', 12, 'bold')).pack()
        self.disk_progress = self.ui.create_progressbar(disk_frame)
        self.disk_progress.pack(fill='x', padx=10, pady=5)
        self.disk_label = self.ui.create_label(disk_frame, "0%")
        self.disk_label.pack()
        
    def create_process_list(self):
        """Create process list section"""
        process_frame = self.ui.create_frame(self.root)
        process_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left side - Process list
        left_frame = self.ui.create_frame(process_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.ui.create_label(left_frame, "Running Processes", font=('Arial', 12, 'bold')).pack(pady=(0, 5))
        
        # Treeview for processes
        columns = ('PID', 'Name', 'CPU%', 'Memory%', 'Memory MB')
        self.process_tree = self.ui.create_treeview(left_frame, columns)
        self.process_tree.pack(fill='both', expand=True)
        
        # Bind selection event
        self.process_tree.bind('<<TreeviewSelect>>', self.on_process_select)
        
    def create_ai_panel(self):
        """Create AI predictions panel"""
        # Right side - AI Panel
        ai_frame = self.ui.create_frame(self.root.winfo_children()[-1])  # Get the process_frame
        ai_frame.pack(side='right', fill='y', padx=(5, 0))
        
        self.ui.create_label(ai_frame, "🧠 AI Insights", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Prediction display
        pred_frame = self.ui.create_frame(ai_frame, width=300)
        pred_frame.pack(fill='x', pady=5)
        pred_frame.pack_propagate(False)
        
        self.prediction_text = tk.Text(
            pred_frame, 
            height=8, 
            width=35,
            bg='#3c3c3c', 
            fg='#ffffff',
            font=('Arial', 9),
            wrap='word'
        )
        self.prediction_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Suggestions
        self.ui.create_label(ai_frame, "💡 Suggestions", font=('Arial', 11, 'bold')).pack(pady=(10, 5))
        
        self.suggestions_text = tk.Text(
            ai_frame, 
            height=6, 
            width=35,
            bg='#3c3c3c', 
            fg='#ffffff',
            font=('Arial', 9),
            wrap='word'
        )
        self.suggestions_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def create_control_panel(self):
        """Create control buttons panel"""
        control_frame = self.ui.create_frame(self.root, height=80)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Kill Process button
        self.kill_btn = self.ui.create_button(
            control_frame, 
            "🗑️ Kill Selected Process", 
            self.kill_selected_process,
            state='disabled'
        )
        self.kill_btn.pack(side='left', padx=10, pady=20)
        
        # Optimize button
        self.optimize_btn = self.ui.create_button(
            control_frame, 
            "⚡ One-Click Optimize", 
            self.optimize_system
        )
        self.optimize_btn.pack(side='left', padx=10, pady=20)
        
        # Export logs button
        self.export_btn = self.ui.create_button(
            control_frame, 
            "📊 Export Logs", 
            self.export_logs
        )
        self.export_btn.pack(side='left', padx=10, pady=20)
        
        # Refresh button
        self.refresh_btn = self.ui.create_button(
            control_frame, 
            "🔄 Refresh", 
            self.manual_refresh
        )
        self.refresh_btn.pack(side='right', padx=10, pady=20)
        
    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get system stats
                stats = self.system_monitor.get_system_stats()
                processes = self.system_monitor.get_processes()
                
                # Update UI
                self.root.after(0, self.update_ui, stats, processes)
                
                # Log data for AI
                self.data_handler.log_system_data(stats, processes)
                
                # Get AI predictions
                if self.data_handler.has_sufficient_data():
                    predictions = self.ai_predictor.get_predictions()
                    suggestions = self.optimizer.get_suggestions(stats, processes)
                    self.root.after(0, self.update_ai_panel, predictions, suggestions)
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
                
    def update_ui(self, stats, processes):
        """Update the UI with new data"""
        # Update progress bars
        self.cpu_progress['value'] = stats['cpu_percent']
        self.cpu_label.config(text=f"{stats['cpu_percent']:.1f}%")
        
        self.ram_progress['value'] = stats['memory_percent']
        self.ram_label.config(text=f"{stats['memory_percent']:.1f}%")
        
        self.disk_progress['value'] = stats['disk_percent']
        self.disk_label.config(text=f"{stats['disk_percent']:.1f}%")
        
        # Update process list
        self.update_process_list(processes)
        
    def update_process_list(self, processes):
        """Update the process list"""
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
            
        # Add new processes (top 20 by CPU usage)
        sorted_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:20]
        
        for proc in sorted_processes:
            self.process_tree.insert('', 'end', values=(
                proc['pid'],
                proc['name'][:25],  # Truncate long names
                f"{proc['cpu_percent']:.1f}",
                f"{proc['memory_percent']:.1f}",
                f"{proc['memory_mb']:.1f}"
            ))
            
    def update_ai_panel(self, predictions, suggestions):
        """Update AI predictions and suggestions"""
        # Update predictions
        self.prediction_text.delete(1.0, tk.END)
        pred_text = f"🔮 System Performance Forecast:\n\n"
        
        if predictions:
            if predictions.get('slowdown_risk', 0) > 0.7:
                pred_text += f"⚠️ HIGH RISK: System slowdown likely in {predictions.get('time_to_slowdown', 'unknown')} minutes\n\n"
            elif predictions.get('slowdown_risk', 0) > 0.4:
                pred_text += f"⚡ MEDIUM RISK: Potential performance issues detected\n\n"
            else:
                pred_text += f"✅ LOW RISK: System running optimally\n\n"
                
            pred_text += f"CPU Trend: {predictions.get('cpu_trend', 'stable')}\n"
            pred_text += f"Memory Trend: {predictions.get('memory_trend', 'stable')}\n"
        else:
            pred_text += "Collecting data for predictions...\n"
            pred_text += "Please wait a few minutes for AI analysis."
            
        self.prediction_text.insert(1.0, pred_text)
        
        # Update suggestions
        self.suggestions_text.delete(1.0, tk.END)
        if suggestions:
            sugg_text = "\n".join([f"• {sugg}" for sugg in suggestions])
        else:
            sugg_text = "No specific suggestions at this time.\nSystem appears to be running well!"
            
        self.suggestions_text.insert(1.0, sugg_text)
        
    def on_process_select(self, event):
        """Handle process selection"""
        selection = self.process_tree.selection()
        if selection:
            item = self.process_tree.item(selection[0])
            self.selected_process = {
                'pid': int(item['values'][0]),
                'name': item['values'][1]
            }
            self.kill_btn.config(state='normal')
        else:
            self.selected_process = None
            self.kill_btn.config(state='disabled')
            
    def kill_selected_process(self):
        """Kill the selected process"""
        if not self.selected_process:
            return
            
        result = messagebox.askyesno(
            "Confirm Kill Process",
            f"Are you sure you want to kill process '{self.selected_process['name']}'?\n"
            f"PID: {self.selected_process['pid']}"
        )
        
        if result:
            success = self.optimizer.kill_process(self.selected_process['pid'])
            if success:
                messagebox.showinfo("Success", f"Process {self.selected_process['name']} terminated successfully.")
            else:
                messagebox.showerror("Error", f"Failed to terminate process {self.selected_process['name']}.")
                
    def optimize_system(self):
        """Perform one-click system optimization"""
        result = messagebox.askyesno(
            "Confirm Optimization",
            "This will terminate high-resource processes and clear system cache.\n"
            "Continue with optimization?"
        )
        
        if result:
            optimizations = self.optimizer.optimize_system()
            
            message = "System Optimization Complete!\n\n"
            message += f"Processes terminated: {optimizations.get('killed_processes', 0)}\n"
            message += f"Memory freed: {optimizations.get('memory_freed', 0):.1f} MB\n"
            message += f"Cache cleared: {'Yes' if optimizations.get('cache_cleared') else 'No'}"
            
            messagebox.showinfo("Optimization Complete", message)
            
    def export_logs(self):
        """Export system logs"""
        filename = f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        success = self.data_handler.export_logs(filename)
        
        if success:
            messagebox.showinfo("Export Complete", f"Logs exported to {filename}")
        else:
            messagebox.showerror("Export Failed", "Failed to export logs.")
            
    def manual_refresh(self):
        """Manually refresh the display"""
        try:
            stats = self.system_monitor.get_system_stats()
            processes = self.system_monitor.get_processes()
            self.update_ui(stats, processes)
            
            # Flash the refresh button
            original_color = self.refresh_btn.cget('bg')
            self.refresh_btn.config(bg='#4CAF50')
            self.root.after(200, lambda: self.refresh_btn.config(bg=original_color))
            
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh data: {e}")
            
    def on_closing(self):
        """Handle application closing"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)
        self.root.destroy()
        
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    # Create src directory if it doesn't exist
    if not os.path.exists('src'):
        os.makedirs('src')
        
    app = OSOptimizerApp()
    app.run()