#!/usr/bin/env python3
"""
Manual script to run users sync from Snipe-IT.
Usage: python run_users_sync.py
"""

import sys
import os

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.sync import sync_snipeit_users, sync_all

def main():
    print("🚀 Starting manual users sync...")
    try:
        sync_snipeit_users()
        print("✅ Users sync completed successfully!")
        print("💡 You can now check the /api/users endpoint to see the synced users.")
    except Exception as e:
        print(f"❌ Users sync failed: {e}")
        sys.exit(1)

def full_sync():
    print("🚀 Starting full sync (assets + users)...")
    try:
        sync_all()
        print("✅ Full sync completed successfully!")
    except Exception as e:
        print(f"❌ Full sync failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        full_sync()
    else:
        main() 