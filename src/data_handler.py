"""
Data Handler Module
Manages data storage and retrieval for system monitoring and AI training
"""

import sqlite3
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading

class DataHandler:
    def __init__(self, db_path: str = 'system_data.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create system_stats table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        cpu_percent REAL,
                        memory_percent REAL,
                        memory_used_gb REAL,
                        memory_total_gb REAL,
                        disk_percent REAL,
                        disk_used_gb REAL,
                        disk_total_gb REAL,
                        network_bytes_sent INTEGER,
                        network_bytes_recv INTEGER,
                        uptime_hours REAL,
                        cpu_count INTEGER,
                        cpu_freq REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create processes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        pid INTEGER,
                        name TEXT,
                        cpu_percent REAL,
                        memory_percent REAL,
                        memory_mb REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create predictions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        prediction_type TEXT,
                        prediction_value REAL,
                        confidence REAL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_stats(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_process_timestamp ON processes(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_prediction_timestamp ON predictions(timestamp)')
                
                conn.commit()
                print("Database initialized successfully")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            
    def log_system_data(self, system_stats: Dict, processes: List[Dict]):
        """Log system statistics and process data"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Insert system stats
                    cursor.execute('''
                        INSERT INTO system_stats (
                            timestamp, cpu_percent, memory_percent, memory_used_gb,
                            memory_total_gb, disk_percent, disk_used_gb, disk_total_gb,
                            network_bytes_sent, network_bytes_recv, uptime_hours,
                            cpu_count, cpu_freq
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        system_stats.get('timestamp'),
                        system_stats.get('cpu_percent'),
                        system_stats.get('memory_percent'),
                        system_stats.get('memory_used_gb'),
                        system_stats.get('memory_total_gb'),
                        system_stats.get('disk_percent'),
                        system_stats.get('disk_used_gb'),
                        system_stats.get('disk_total_gb'),
                        system_stats.get('network_bytes_sent'),
                        system_stats.get('network_bytes_recv'),
                        system_stats.get('uptime_hours'),
                        system_stats.get('cpu_count'),
                        system_stats.get('cpu_freq')
                    ))
                    
                    # Insert top processes (limit to top 10 to avoid too much data)
                    top_processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
                    
                    for process in top_processes:
                        cursor.execute('''
                            INSERT INTO processes (
                                timestamp, pid, name, cpu_percent, memory_percent, memory_mb
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            process.get('timestamp'),
                            process.get('pid'),
                            process.get('name'),
                            process.get('cpu_percent'),
                            process.get('memory_percent'),
                            process.get('memory_mb')
                        ))
                    
                    conn.commit()
                    
        except Exception as e:
            print(f"Error logging system data: {e}")
            
    def log_prediction(self, prediction_type: str, value: float, confidence: float = 0.0, metadata: Dict = None):
        """Log AI prediction results"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO predictions (
                            timestamp, prediction_type, prediction_value, confidence, metadata
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().timestamp(),
                        prediction_type,
                        value,
                        confidence,
                        json.dumps(metadata) if metadata else None
                    ))
                    
                    conn.commit()
                    
        except Exception as e:
            print(f"Error logging prediction: {e}")
            
    def get_recent_data(self, limit: int = 100) -> pd.DataFrame:
        """Get recent system data for analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM system_stats 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                '''
                df = pd.read_sql_query(query, conn, params=(limit,))
                return df.sort_values('timestamp')  # Sort ascending for time series
                
        except Exception as e:
            print(f"Error getting recent data: {e}")
            return pd.DataFrame()
            
    def get_training_data(self, days: int = 7) -> pd.DataFrame:
        """Get historical data for AI training"""
        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM system_stats 
                    WHERE timestamp > ?
                    ORDER BY timestamp ASC
                '''
                df = pd.read_sql_query(query, conn, params=(cutoff_time,))
                return df
                
        except Exception as e:
            print(f"Error getting training data: {e}")
            return pd.DataFrame()
            
    def get_process_history(self, process_name: str = None, hours: int = 24) -> pd.DataFrame:
        """Get process history data"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                if process_name:
                    query = '''
                        SELECT * FROM processes 
                        WHERE timestamp > ? AND name LIKE ?
                        ORDER BY timestamp ASC
                    '''
                    df = pd.read_sql_query(query, conn, params=(cutoff_time, f'%{process_name}%'))
                else:
                    query = '''
                        SELECT * FROM processes 
                        WHERE timestamp > ?
                        ORDER BY timestamp ASC
                    '''
                    df = pd.read_sql_query(query, conn, params=(cutoff_time,))
                    
                return df
                
        except Exception as e:
            print(f"Error getting process history: {e}")
            return pd.DataFrame()
            
    def get_predictions_history(self, prediction_type: str = None, hours: int = 24) -> pd.DataFrame:
        """Get prediction history"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                if prediction_type:
                    query = '''
                        SELECT * FROM predictions 
                        WHERE timestamp > ? AND prediction_type = ?
                        ORDER BY timestamp ASC
                    '''
                    df = pd.read_sql_query(query, conn, params=(cutoff_time, prediction_type))
                else:
                    query = '''
                        SELECT * FROM predictions 
                        WHERE timestamp > ?
                        ORDER BY timestamp ASC
                    '''
                    df = pd.read_sql_query(query, conn, params=(cutoff_time,))
                    
                return df
                
        except Exception as e:
            print(f"Error getting predictions history: {e}")
            return pd.DataFrame()
            
    def has_sufficient_data(self, min_records: int = 20) -> bool:
        """Check if we have sufficient data for AI training"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM system_stats')
                count = cursor.fetchone()[0]
                return count >= min_records
                
        except Exception as e:
            print(f"Error checking data sufficiency: {e}")
            return False
            
    def export_logs(self, filename: str = None) -> bool:
        """Export system logs to CSV"""
        try:
            if not filename:
                filename = f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
            with sqlite3.connect(self.db_path) as conn:
                # Export system stats
                system_df = pd.read_sql_query('SELECT * FROM system_stats ORDER BY timestamp', conn)
                system_filename = filename.replace('.csv', '_system.csv')
                system_df.to_csv(system_filename, index=False)
                
                # Export processes
                process_df = pd.read_sql_query('SELECT * FROM processes ORDER BY timestamp', conn)
                process_filename = filename.replace('.csv', '_processes.csv')
                process_df.to_csv(process_filename, index=False)
                
                # Export predictions
                pred_df = pd.read_sql_query('SELECT * FROM predictions ORDER BY timestamp', conn)
                pred_filename = filename.replace('.csv', '_predictions.csv')
                pred_df.to_csv(pred_filename, index=False)
                
                print(f"Logs exported to {system_filename}, {process_filename}, {pred_filename}")
                return True
                
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
            
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data to prevent database from growing too large"""
        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()
            
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Delete old system stats
                    cursor.execute('DELETE FROM system_stats WHERE timestamp < ?', (cutoff_time,))
                    
                    # Delete old processes
                    cursor.execute('DELETE FROM processes WHERE timestamp < ?', (cutoff_time,))
                    
                    # Delete old predictions
                    cursor.execute('DELETE FROM predictions WHERE timestamp < ?', (cutoff_time,))
                    
                    conn.commit()
                    
                    # Vacuum to reclaim space
                    cursor.execute('VACUUM')
                    
                    print(f"Cleaned up data older than {days} days")
                    
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records in each table
                cursor.execute('SELECT COUNT(*) FROM system_stats')
                system_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM processes')
                process_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM predictions')
                prediction_count = cursor.fetchone()[0]
                
                # Get database size
                db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
                
                # Get date range
                cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM system_stats')
                min_time, max_time = cursor.fetchone()
                
                return {
                    'system_records': system_count,
                    'process_records': process_count,
                    'prediction_records': prediction_count,
                    'database_size_mb': round(db_size, 2),
                    'data_start_date': datetime.fromtimestamp(min_time).strftime('%Y-%m-%d %H:%M:%S') if min_time else 'N/A',
                    'data_end_date': datetime.fromtimestamp(max_time).strftime('%Y-%m-%d %H:%M:%S') if max_time else 'N/A'
                }
                
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}