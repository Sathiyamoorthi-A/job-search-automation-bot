import time
import subprocess
import os
from datetime import datetime

OPTIMAL_SCAN_TIMES = ["09:15", "14:15", "18:30"]

def run_main():
    print(f"\n[Scheduler Trigger] Running job radar scan at {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}...")
    script_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.run(["python", script_path], check=False)

def main():
    print("==========================================================")
    print("🚀 Java Full Stack Job Radar Daemon Started")
    print(f"Scheduled Daily Scan Hours (IST): {', '.join(OPTIMAL_SCAN_TIMES)}")
    print("==========================================================")
    
    last_triggered_minute = ""
    
    # Run an immediate initial scan on startup
    run_main()
    
    while True:
        now_str = datetime.now().strftime("%H:%M")
        if now_str in OPTIMAL_SCAN_TIMES and now_str != last_triggered_minute:
            last_triggered_minute = now_str
            run_main()
            
        time.sleep(30)

if __name__ == "__main__":
    main()
