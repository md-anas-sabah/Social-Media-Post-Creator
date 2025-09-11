#!/usr/bin/env python3
"""
Test script to verify folder creation fix
"""

import os
import sys
sys.path.append('.')

from reels.utils import create_unique_reel_folder

def test_folder_creation():
    print("🧪 Testing folder creation fix...")
    
    # Test folder creation
    user_prompt = "Behind the scenes at coffee roastery"
    platform = "instagram"
    
    reel_folder, timestamp = create_unique_reel_folder(user_prompt, platform)
    
    print(f"📁 Created folder: {reel_folder}")
    print(f"🕐 Timestamp: {timestamp}")
    
    # Check if all required subdirectories exist
    required_dirs = ['raw_clips', 'audio']
    
    for subdir in required_dirs:
        subdir_path = os.path.join(reel_folder, subdir)
        if os.path.exists(subdir_path):
            print(f"✅ {subdir}/ directory exists")
        else:
            print(f"❌ {subdir}/ directory missing")
            return False
    
    print(f"\n📂 Complete folder structure:")
    for root, dirs, files in os.walk(reel_folder):
        level = root.replace(reel_folder, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print(f"\n✅ Folder creation test PASSED!")
    print(f"🎯 Video generation should now work with folder: {reel_folder}")
    
    return True, reel_folder

if __name__ == "__main__":
    try:
        success, folder_path = test_folder_creation()
        if success:
            print(f"\n🚀 SUCCESS: Folder structure is now correct!")
            print(f"   Path: {folder_path}")
        else:
            print(f"\n❌ FAILED: Folder structure creation failed")
    except Exception as e:
        print(f"❌ ERROR: {e}")