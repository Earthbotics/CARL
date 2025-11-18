#!/usr/bin/env python3
"""
Quick Fix for Fresh Startup Issues

Run this script after performing fresh startup deletions to automatically:
1. Fix the settings_current.ini file
2. Recreate knowledge files
3. Verify everything is working

Usage: python fix_fresh_startup.py
"""

import subprocess
import sys

def main():
    """Run the fresh startup handler."""
    print("🔧 Quick Fix for Fresh Startup Issues")
    print("=" * 50)
    
    try:
        # Run the comprehensive fresh startup handler
        result = subprocess.run([sys.executable, 'fresh_startup_handler.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Fresh startup fix completed successfully!")
            print("🎉 CARL is ready to start!")
            return True
        else:
            print("❌ Fresh startup fix failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running fresh startup fix: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
