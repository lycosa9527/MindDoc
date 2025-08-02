#!/usr/bin/env python3
"""
Simple log viewer utility for MindDoc application
"""

import os
import sys
from datetime import datetime
from app.services.debug_logger import DebugLogger

def view_recent_logs(lines: int = 50):
    """View recent log entries"""
    print(f"📋 Recent Log Entries (Last {lines} lines)")
    print("=" * 60)
    
    recent_logs = DebugLogger.get_recent_logs(lines)
    
    if not recent_logs:
        print("❌ No log file found. Make sure the application has been run.")
        return
    
    for line in recent_logs:
        print(line.rstrip())
    
    print("\n" + "=" * 60)

def view_log_stats():
    """View log statistics"""
    print("📊 Log Statistics")
    print("=" * 60)
    
    log_file = DebugLogger.get_log_file_path()
    
    if not os.path.exists(log_file):
        print("❌ Log file not found")
        return
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        file_size = os.path.getsize(log_file)
        
        # Count log levels
        level_counts = {}
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    level = parts[2].strip()
                    level_counts[level] = level_counts.get(level, 0) + 1
        
        print(f"📁 Log File: {log_file}")
        print(f"📏 File Size: {file_size:,} bytes")
        print(f"📄 Total Lines: {total_lines:,}")
        print(f"📅 Last Modified: {datetime.fromtimestamp(os.path.getmtime(log_file))}")
        
        print("\n📈 Log Level Distribution:")
        for level, count in sorted(level_counts.items()):
            percentage = (count / total_lines) * 100
            print(f"   {level}: {count:,} ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def clear_logs():
    """Clear all log files"""
    print("🗑️  Clearing Log Files")
    print("=" * 60)
    
    try:
        DebugLogger.clear_logs()
        print("✅ Log files cleared successfully")
    except Exception as e:
        print(f"❌ Error clearing logs: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stats":
            view_log_stats()
        elif command == "clear":
            clear_logs()
        elif command == "recent":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            view_recent_logs(lines)
        else:
            print("❌ Unknown command. Available commands:")
            print("   python view_logs.py recent [lines]  - View recent logs")
            print("   python view_logs.py stats          - View log statistics")
            print("   python view_logs.py clear          - Clear log files")
    else:
        # Default: show recent logs
        view_recent_logs(30)
        
        print("\n💡 Usage:")
        print("   python view_logs.py recent [lines]  - View recent logs")
        print("   python view_logs.py stats          - View log statistics")
        print("   python view_logs.py clear          - Clear log files")

if __name__ == "__main__":
    main() 