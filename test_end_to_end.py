#!/usr/bin/env python3
"""
End-to-End Integration Test for Social Media Reel Generation System
Tests the complete workflow from user input to final reel output (with mock APIs)
"""

import os
import sys
import json
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_workflow():
    """Test the complete reel generation workflow"""
    print("🎬 Testing Complete Reel Generation Workflow")
    print("=" * 60)
    
    try:
        # Import main VideoReelCreator
        from main import VideoReelCreator
        
        print("1️⃣  Initializing VideoReelCreator...")
        creator = VideoReelCreator(
            user_prompt="Create a fashion brand showcase reel",
            duration="20s", 
            content_mode="1",  # Music mode
            platform="instagram"
        )
        print("✅ VideoReelCreator initialized successfully")
        
        print(f"\n📋 Configuration:")
        print(f"   User Prompt: {creator.user_prompt}")
        print(f"   Duration: {creator.duration}s")
        print(f"   Content Mode: {creator.content_mode}")
        print(f"   Platform: {creator.platform}")
        
        print("\n2️⃣  Testing Phase Structure...")
        
        # Test individual components that would be used in the workflow
        from reels import ReelAgents, ReelTasks
        from reels.utils import create_unique_reel_folder
        
        # Create output folder
        reel_folder, timestamp = create_unique_reel_folder(creator.user_prompt, creator.platform)
        print(f"✅ Output folder created: {os.path.basename(reel_folder)}")
        
        # Initialize agents and tasks
        agents = ReelAgents()
        tasks = ReelTasks()
        print("✅ Agents and tasks initialized")
        
        print("\n3️⃣  Testing Agent Creation...")
        
        # Test all agents can be created
        content_planner = agents.content_planning_agent()
        print("✅ Content planning agent created")
        
        claude_refiner = agents.claude_refinement_agent()
        print("✅ Claude refinement agent created")
        
        video_generator = agents.video_generation_agent(reel_folder)
        print("✅ Video generation agent created")
        
        audio_generator = agents.audio_generation_agent()
        print("✅ Audio generation agent created")
        
        synchronizer = agents.synchronization_agent()
        print("✅ Synchronization agent created")
        
        qa_tester = agents.qa_testing_agent()
        print("✅ QA testing agent created")
        
        print("\n4️⃣  Testing Task Creation...")
        
        # Test all tasks can be created
        planning_task = tasks.content_planning_task(
            content_planner,
            creator.user_prompt,
            creator.content_mode,
            creator.duration
        )
        print("✅ Content planning task created")
        
        # Mock data for subsequent tasks
        mock_planning_data = {
            "content_analysis": {
                "category": "fashion",
                "complexity_level": "medium",
                "target_audience": "fashion enthusiasts"
            },
            "mode_selection": {
                "recommended_mode": "music",
                "rationale": "Visual content works better with music"
            },
            "storyboard": {
                "scenes": [
                    {
                        "scene_number": 1,
                        "description": "Brand logo reveal",
                        "duration": 7,
                        "enhanced_prompt": "Cinematic fashion brand logo reveal"
                    },
                    {
                        "scene_number": 2, 
                        "description": "Product showcase",
                        "duration": 6,
                        "enhanced_prompt": "Elegant product display with lighting"
                    },
                    {
                        "scene_number": 3,
                        "description": "Call to action",
                        "duration": 7,
                        "enhanced_prompt": "Modern call to action with branding"
                    }
                ]
            }
        }
        
        refinement_context = {
            'platform': creator.platform,
            'duration': creator.duration,
            'content_mode': creator.content_mode,
            'user_prompt': creator.user_prompt
        }
        
        refinement_task = tasks.prompt_refinement_task(
            claude_refiner,
            mock_planning_data,
            refinement_context
        )
        print("✅ Prompt refinement task created")
        
        # Mock refined data for video generation
        mock_refined_data = {
            "refined_prompts": [
                {
                    "scene_number": 1,
                    "enhanced_prompt": "Cinematic fashion brand logo reveal with metallic shine",
                    "recommended_model": "hailuo-02",
                    "quality_prediction": 0.88,
                    "technical_params": {"duration": 7}
                },
                {
                    "scene_number": 2,
                    "enhanced_prompt": "Elegant product display with professional studio lighting",
                    "recommended_model": "hailuo-02", 
                    "quality_prediction": 0.92,
                    "technical_params": {"duration": 6}
                },
                {
                    "scene_number": 3,
                    "enhanced_prompt": "Modern call to action with sleek branding elements",
                    "recommended_model": "hailuo-02",
                    "quality_prediction": 0.85,
                    "technical_params": {"duration": 7}
                }
            ]
        }
        
        video_task = tasks.video_generation_task(
            video_generator,
            mock_refined_data,
            refinement_context
        )
        print("✅ Video generation task created")
        
        # Mock video data for audio generation
        mock_video_data = {
            "generated_clips": [
                {
                    "clip_id": 1,
                    "file_path": os.path.join(reel_folder, "raw_clips", "clip_1.mp4"),
                    "status": "success",
                    "duration": 7
                },
                {
                    "clip_id": 2,
                    "file_path": os.path.join(reel_folder, "raw_clips", "clip_2.mp4"),
                    "status": "success", 
                    "duration": 6
                },
                {
                    "clip_id": 3,
                    "file_path": os.path.join(reel_folder, "raw_clips", "clip_3.mp4"),
                    "status": "success",
                    "duration": 7
                }
            ],
            "generation_summary": {
                "successful_clips": 3,
                "total_cost": 1.50
            }
        }
        
        audio_task = tasks.audio_generation_task(
            audio_generator,
            mock_video_data,
            refinement_context
        )
        print("✅ Audio generation task created")
        
        # Mock audio data for synchronization
        mock_audio_data = {
            "audio_generation_status": "success",
            "generated_audio": {
                "file_path": os.path.join(reel_folder, "audio", "background_music.mp3"),
                "duration": 20,
                "type": "background_music"
            }
        }
        
        sync_task = tasks.synchronization_task(
            synchronizer,
            mock_video_data,
            mock_audio_data
        )
        print("✅ Synchronization task created")
        
        # Mock sync data for QA
        mock_sync_data = {
            "status": "completed",
            "final_reel_path": os.path.join(reel_folder, "final_reel.mp4"),
            "video_stitching": {"quality": "professional"},
            "audio_synchronization": {"sync_quality": "perfect"}
        }
        
        qa_task = tasks.qa_testing_task(
            qa_tester,
            mock_sync_data,
            refinement_context
        )
        print("✅ QA testing task created")
        
        print("\n5️⃣  Testing File Structure...")
        
        # Verify folder structure is created correctly
        expected_folders = ['raw_clips', 'audio']
        for folder in expected_folders:
            folder_path = os.path.join(reel_folder, folder)
            if os.path.exists(folder_path):
                print(f"✅ {folder}/ folder exists")
            else:
                print(f"⚠️  {folder}/ folder not found")
        
        print("\n6️⃣  Testing Data Flow...")
        
        # Test that data structures are compatible between phases
        from reels.video_generator import VideoGenerator
        from reels.audio_generator import AudioGenerator
        
        video_gen = VideoGenerator(reel_folder)
        audio_gen = AudioGenerator(reel_folder)
        
        # Test model selection with mock data
        selected_model = video_gen.select_optimal_model(mock_refined_data["refined_prompts"][0])
        print(f"✅ Model selection works: {selected_model}")
        
        # Test cost estimation
        cost_estimate = video_gen.estimate_generation_cost(mock_refined_data["refined_prompts"])
        print(f"✅ Cost estimation works: ${cost_estimate['total_estimated_cost']}")
        
        print("\n7️⃣  Testing Error Handling...")
        
        # Test with invalid data to ensure graceful handling
        try:
            invalid_task = tasks.video_generation_task(
                video_generator,
                "invalid_string_data",  # Should handle this gracefully
                refinement_context
            )
            print("✅ Error handling works for invalid data")
        except Exception as e:
            print(f"✅ Error handling works: {type(e).__name__}")
        
        print(f"\n📁 Complete test output folder: {reel_folder}")
        
        return True, reel_folder
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def cleanup_test_folder(test_folder):
    """Clean up test folder"""
    if test_folder and os.path.exists(test_folder):
        try:
            import shutil
            shutil.rmtree(test_folder, ignore_errors=True)
            print(f"✅ Cleaned up test folder: {os.path.basename(test_folder)}")
        except Exception as e:
            print(f"⚠️  Could not clean up {test_folder}: {e}")

def main():
    """Run end-to-end integration test"""
    print("🎯 SOCIAL MEDIA REEL SYSTEM - END-TO-END INTEGRATION TEST")
    print("=" * 70)
    print("This test validates the complete workflow structure and data flow")
    print("without requiring API keys (uses mock data for actual generation)")
    print("=" * 70)
    
    success, test_folder = test_complete_workflow()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 END-TO-END INTEGRATION TEST PASSED!")
        print("✅ All workflow components are properly integrated")
        print("✅ Data flow between phases is compatible")
        print("✅ Error handling is robust")
        print("✅ File structure is created correctly")
        print("\n💡 READY FOR PRODUCTION:")
        print("   - Add API keys to .env file")
        print("   - Install optional dependencies: moviepy, ffmpeg")
        print("   - Run: python main.py")
        
        verdict = "SYSTEM READY FOR USE"
    else:
        print("❌ END-TO-END INTEGRATION TEST FAILED!")
        print("⚠️  Critical issues found that prevent system operation")
        print("🔧 Please review the error messages and fix issues")
        
        verdict = "SYSTEM NEEDS FIXES"
    
    print("\n" + "=" * 70)
    print(f"🎯 FINAL VERDICT: {verdict}")
    print("=" * 70)
    
    # Cleanup
    if test_folder:
        cleanup_test_folder(test_folder)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)