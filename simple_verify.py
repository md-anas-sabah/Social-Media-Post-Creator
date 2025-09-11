#!/usr/bin/env python3
"""
Simple verification of the fix
"""

import os
import sys
sys.path.append('.')

from reels.utils import create_unique_reel_folder

def simple_verify():
    print("🔍 Simple verification of folder creation fix...")
    
    # Test folder creation
    reel_folder, _ = create_unique_reel_folder("Behind the scenes at coffee roastery", "instagram")
    
    # Check required subdirectories exist  
    raw_clips_path = os.path.join(reel_folder, 'raw_clips')
    audio_path = os.path.join(reel_folder, 'audio')
    
    print(f"📁 Main folder: {os.path.exists(reel_folder)}")
    print(f"📂 raw_clips/: {os.path.exists(raw_clips_path)}")  
    print(f"🎵 audio/: {os.path.exists(audio_path)}")
    
    if os.path.exists(raw_clips_path) and os.path.exists(audio_path):
        print(f"\n✅ SUCCESS: Folder creation issue is FIXED!")
        print(f"   The video generation error should no longer occur")
        print(f"   Path: {reel_folder}")
        return True
    else:
        print(f"\n❌ FAILED: Folder structure still incomplete")
        return False

if __name__ == "__main__":
    simple_verify()