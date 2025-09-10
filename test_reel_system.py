#!/usr/bin/env python3
"""
Test script for the Social Media Reel Generation System
Validates basic functionality without requiring API keys
"""

import os
import sys
import json
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from reels import ReelAgents, ReelTasks
        print("✅ ReelAgents and ReelTasks imported successfully")
        
        from reels.utils import parse_duration, create_unique_reel_folder, save_reel_metadata
        print("✅ Utility functions imported successfully")
        
        from reels.video_generator import VideoGenerator
        print("✅ VideoGenerator imported successfully")
        
        from reels.audio_generator import AudioGenerator
        print("✅ AudioGenerator imported successfully")
        
        from reels.synchronizer import VideoSynchronizer
        print("✅ VideoSynchronizer imported successfully")
        
        from main import VideoReelCreator
        print("✅ VideoReelCreator imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_utility_functions():
    """Test utility functions"""
    print("\n🧪 Testing utility functions...")
    
    try:
        from reels.utils import parse_duration, create_unique_reel_folder
        
        # Test parse_duration
        duration = parse_duration("20s")
        assert duration == 20, f"Expected 20, got {duration}"
        print("✅ parse_duration works correctly")
        
        # Test create_unique_reel_folder
        folder, timestamp = create_unique_reel_folder("test fashion reel", "instagram")
        assert os.path.exists(folder), f"Folder {folder} was not created"
        print(f"✅ create_unique_reel_folder works correctly: {os.path.basename(folder)}")
        
        return True, folder
    except Exception as e:
        print(f"❌ Utility function error: {e}")
        return False, None

def test_video_generator_initialization():
    """Test VideoGenerator initialization"""
    print("\n🧪 Testing VideoGenerator initialization...")
    
    try:
        from reels.video_generator import VideoGenerator
        
        # Create test folder
        test_folder = "/tmp/test_reel_folder"
        os.makedirs(test_folder, exist_ok=True)
        
        # This should work without FAL_KEY (will use mock mode)
        generator = VideoGenerator(test_folder)
        print("✅ VideoGenerator initialized successfully")
        
        # Test model selection
        test_prompt_data = {
            'enhanced_prompt': 'Test prompt',
            'recommended_model': 'hailuo-02',
            'content_analysis': {'category': 'educational'}
        }
        
        selected_model = generator.select_optimal_model(test_prompt_data)
        assert selected_model in generator.models, f"Invalid model selected: {selected_model}"
        print(f"✅ Model selection works: {selected_model}")
        
        return True
    except Exception as e:
        print(f"❌ VideoGenerator error: {e}")
        return False

def test_audio_generator_initialization():
    """Test AudioGenerator initialization"""
    print("\n🧪 Testing AudioGenerator initialization...")
    
    try:
        from reels.audio_generator import AudioGenerator
        
        # Create test folder
        test_folder = "/tmp/test_reel_folder"
        os.makedirs(test_folder, exist_ok=True)
        
        # This should work without FAL_KEY (will use mock mode)
        generator = AudioGenerator(test_folder)
        print("✅ AudioGenerator initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ AudioGenerator error: {e}")
        return False

def test_agent_initialization():
    """Test CrewAI agents initialization"""
    print("\n🧪 Testing CrewAI agents initialization...")
    
    try:
        from reels import ReelAgents
        
        agents = ReelAgents()
        
        # Test content planning agent
        content_agent = agents.content_planning_agent()
        assert hasattr(content_agent, 'role'), "Content agent missing role attribute"
        print("✅ Content planning agent initialized")
        
        # Test other agents
        claude_agent = agents.claude_refinement_agent()
        print("✅ Claude refinement agent initialized")
        
        video_agent = agents.video_generation_agent("/tmp/test")
        print("✅ Video generation agent initialized")
        
        audio_agent = agents.audio_generation_agent()
        print("✅ Audio generation agent initialized")
        
        sync_agent = agents.synchronization_agent()
        print("✅ Synchronization agent initialized")
        
        qa_agent = agents.qa_testing_agent()
        print("✅ QA testing agent initialized")
        
        return True
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False

def test_task_creation():
    """Test CrewAI task creation"""
    print("\n🧪 Testing CrewAI task creation...")
    
    try:
        from reels import ReelAgents, ReelTasks
        
        agents = ReelAgents()
        tasks = ReelTasks()
        
        # Test content planning task
        content_agent = agents.content_planning_agent()
        planning_task = tasks.content_planning_task(
            content_agent, 
            "Fashion brand showcase", 
            "music", 
            20
        )
        assert hasattr(planning_task, 'description'), "Task missing description"
        print("✅ Content planning task created")
        
        # Test other task creation (without execution)
        claude_agent = agents.claude_refinement_agent()
        refinement_task = tasks.prompt_refinement_task(
            claude_agent,
            {"test": "data"},
            {"platform": "instagram"}
        )
        print("✅ Prompt refinement task created")
        
        return True
    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return False

def test_video_reel_creator_initialization():
    """Test VideoReelCreator class initialization"""
    print("\n🧪 Testing VideoReelCreator initialization...")
    
    try:
        from main import VideoReelCreator
        
        creator = VideoReelCreator(
            user_prompt="Test fashion reel",
            duration="20s",
            content_mode="1",
            platform="instagram"
        )
        
        assert creator.user_prompt == "Test fashion reel"
        assert creator.duration == 20
        assert creator.content_mode == "music"
        assert creator.platform == "instagram"
        
        print("✅ VideoReelCreator initialized correctly")
        return True
    except Exception as e:
        print(f"❌ VideoReelCreator error: {e}")
        return False

def cleanup_test_files():
    """Clean up test files and folders"""
    print("\n🧹 Cleaning up test files...")
    
    try:
        # Clean up any test reel folders
        import shutil
        for root, dirs, files in os.walk(os.getcwd()):
            for dir_name in dirs:
                if dir_name.startswith('reel_instagram_test'):
                    test_path = os.path.join(root, dir_name)
                    shutil.rmtree(test_path, ignore_errors=True)
                    print(f"✅ Cleaned up: {dir_name}")
        
        # Clean up tmp folder
        if os.path.exists("/tmp/test_reel_folder"):
            shutil.rmtree("/tmp/test_reel_folder", ignore_errors=True)
            print("✅ Cleaned up temp folders")
            
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def main():
    """Run all tests"""
    print("🎬 Social Media Reel System Test Suite")
    print("=" * 50)
    
    test_results = []
    test_folder = None
    
    # Test 1: Imports
    result = test_imports()
    test_results.append(("Imports", result))
    
    if result:
        # Test 2: Utility Functions
        result, test_folder = test_utility_functions()
        test_results.append(("Utility Functions", result))
        
        # Test 3: VideoGenerator
        result = test_video_generator_initialization()
        test_results.append(("VideoGenerator", result))
        
        # Test 4: AudioGenerator
        result = test_audio_generator_initialization()
        test_results.append(("AudioGenerator", result))
        
        # Test 5: Agents
        result = test_agent_initialization()
        test_results.append(("Agent Initialization", result))
        
        # Test 6: Tasks
        result = test_task_creation()
        test_results.append(("Task Creation", result))
        
        # Test 7: VideoReelCreator
        result = test_video_reel_creator_initialization()
        test_results.append(("VideoReelCreator", result))
    
    # Print results
    print("\n" + "=" * 50)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    # Cleanup
    cleanup_test_files()
    
    # Final verdict
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for basic usage.")
        print("💡 Note: Full functionality requires API keys (FAL_KEY, CLAUDE_API_KEY, OPENAI_API_KEY)")
        return True
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED! Please fix issues before using the system.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)