#!/usr/bin/env python3
"""
Performance Monitor
------------------
This script monitors your application's performance in real-time,
tracking memory usage, CPU utilization, and response times.

Usage:
1. Run in your GitHub Codespace
2. Point it to your running application
3. Get insights on performance bottlenecks
"""

import os
import sys
import time
import psutil
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import threading
import json

class PerformanceMonitor:
    def __init__(self, app_url="http://localhost:3000", endpoints=None):
        self.app_url = app_url
        self.endpoints = endpoints or ["/", "/api/health"]
        self.metrics = {
            "memory": [],
            "cpu": [],
            "response_times": {},
            "timestamps": []
        }
        for endpoint in self.endpoints:
            self.metrics["response_times"][endpoint] = []
    
    def monitor(self, duration_seconds=300, interval_seconds=5):
        """Monitor application performance metrics for a specified duration"""
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        print(f"Starting performance monitoring for {duration_seconds} seconds...")
        print(f"Monitoring application at {self.app_url}")
        print(f"Press Ctrl+C to stop monitoring early")
        
        try:
            while time.time() < end_time:
                self._collect_metrics()
                time.sleep(interval_seconds)
                
            self._generate_report()
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            self._generate_report()
    
    def _collect_metrics(self):
        """Collect a single snapshot of metrics"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.metrics["timestamps"].append(timestamp)
        
        # Collect system metrics
        process = psutil.Process(os.getpid())
        self.metrics["memory"].append(process.memory_info().rss / 1024 / 1024)  # MB
        self.metrics["cpu"].append(psutil.cpu_percent())
        
        # Collect response time metrics
        for endpoint in self.endpoints:
            try:
                start = time.time()
                response = requests.get(f"{self.app_url}{endpoint}", timeout=5)
                end = time.time()
                response_time = (end - start) * 1000  # ms
                
                self.metrics["response_times"][endpoint].append(response_time)
                print(f"[{timestamp}] {endpoint}: {response_time:.2f}ms (Status: {response.status_code})")
            except Exception as e:
                print(f"[{timestamp}] {endpoint}: Error - {str(e)}")
                self.metrics["response_times"][endpoint].append(None)
    
    def _generate_report(self):
        """Generate performance report with charts"""
        print("\nGenerating performance report...")
        
        # Create a monitoring directory if it doesn't exist
        os.makedirs("monitoring", exist_ok=True)
        
        # Save raw metrics as JSON
        with open("monitoring/performance_metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)
        
        # Generate charts
        plt.figure(figsize=(12, 10))
        
        # Memory usage chart
        plt.subplot(3, 1, 1)
        plt.plot(self.metrics["timestamps"], self.metrics["memory"])
        plt.title("Memory Usage")
        plt.xlabel("Time")
        plt.ylabel("Memory (MB)")
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # CPU usage chart
        plt.subplot(3, 1, 2)
        plt.plot(self.metrics["timestamps"], self.metrics["cpu"])
        plt.title("CPU Usage")
        plt.xlabel("Time")
        plt.ylabel("CPU (%)")
        plt.xticks(rotation=45)
        plt.grid(True)
        
        # Response time chart
        plt.subplot(3, 1, 3)
        for endpoint, times in self.metrics["response_times"].items():
            # Filter out None values
            valid_indices = [i for i, x in enumerate(times) if x is not None]
            valid_times = [times[i] for i in valid_indices]
            valid_timestamps = [self.metrics["timestamps"][i] for i in valid_indices]
            
            if valid_times:
                plt.plot(valid_timestamps, valid_times, label=endpoint)
        
        plt.title("Response Times")
        plt.xlabel("Time")
        plt.ylabel("Response Time (ms)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig("monitoring/performance_charts.png")
        
        # Generate summary report
        with open("monitoring/performance_report.md", "w") as f:
            f.write("# Application Performance Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            if self.metrics["memory"]:
                f.write(f"- **Average Memory Usage**: {sum(self.metrics['memory']) / len(self.metrics['memory']):.2f} MB\n")
                f.write(f"- **Peak Memory Usage**: {max(self.metrics['memory']):.2f} MB\n")
            if self.metrics["cpu"]:
                f.write(f"- **Average CPU Usage**: {sum(self.metrics['cpu']) / len(self.metrics['cpu']):.2f}%\n")
                f.write(f"- **Peak CPU Usage**: {max(self.metrics['cpu']):.2f}%\n")
            
            f.write("\n## Response Times\n\n")
            for endpoint, times in self.metrics["response_times"].items():
                valid_times = [t for t in times if t is not None]
                if valid_times:
                    f.write(f"### {endpoint}\n")
                    f.write(f"- **Average**: {sum(valid_times) / len(valid_times):.2f} ms\n")
                    f.write(f"- **Minimum**: {min(valid_times):.2f} ms\n")
                    f.write(f"- **Maximum**: {max(valid_times):.2f} ms\n")
                    f.write(f"- **Failed Requests**: {times.count(None)} of {len(times)}\n\n")
            
            f.write("\n## Performance Chart\n\n")
            f.write("![Performance Charts](performance_charts.png)\n")
        
        print(f"Report saved to: monitoring/performance_report.md")
        print(f"Charts saved to: monitoring/performance_charts.png")
        print(f"Raw metrics saved to: monitoring/performance_metrics.json")

if __name__ == "__main__":
    print("Application Performance Monitor")
    print("------------------------------")
    
    # Parse arguments
    app_url = "http://localhost:3000"
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
    
    # Default endpoints to monitor
    default_endpoints = ["/", "/api/health", "/api/status"]
    
    monitor = PerformanceMonitor(app_url, default_endpoints)
    monitor.monitor(duration_seconds=60, interval_seconds=2)