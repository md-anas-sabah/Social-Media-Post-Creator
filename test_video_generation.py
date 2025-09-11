#!/usr/bin/env python3
"""
Test video generation with proper data structure
"""

import os
import json
import sys
sys.path.append('.')

from reels.utils import create_unique_reel_folder
from reels.video_generation_tool import VideoGenerationTool

def test_video_generation():
    print("🧪 Testing video generation with complete data...")
    
    # Create folder structure
    user_prompt = "Behind the scenes at coffee roastery"
    platform = "instagram"
    
    reel_folder, timestamp = create_unique_reel_folder(user_prompt, platform)
    print(f"📁 Created folder: {reel_folder}")
    
    # Create complete Claude refinement result (matching the actual structure from the execution)
    claude_refinement_result = {
        "status": "success",
        "refined_prompts": [
            {
                "scene_number": 1,
                "original_description": "Showcasing the coffee beans being roasted in the roastery.",
                "enhanced_prompt": "Cinematic vertical video in 9:16 aspect ratio (1080x1920) featuring artisanal coffee roasting. Close-up of glossy dark coffee beans tumbling in a vintage copper roaster, golden warm lighting casting dancing shadows. Slow-motion capture of beans transforming from green to rich brown, with subtle smoke wisps. Depth of field effect emphasizing texture. Industrial-chic aesthetic with exposed brick background, soft bokeh effects. Text overlay in elegant Helvetica: 'The Art of Roasting'",
                "quality_prediction": 0.88,
                "recommended_model": "hailuo-02",
                "technical_params": {
                    "resolution": "1080x1920",
                    "duration": 8,
                    "style": "cinematic_documentary",
                    "camera_movement": "slow_drift",
                    "lighting": "warm_ambient",
                    "color_grade": "coffee_tones"
                },
                "alternative_prompts": [
                    "Vertical format (9:16) extreme macro shot of single coffee bean roasting transformation, golden hour lighting, minimal industrial setting, focus on texture and color change, cinematic grade",
                    "Vertical video (1080x1920) showing master roaster's hands adjusting controls of vintage roaster, steam rising, beans cascading, moody lighting with copper highlights"
                ]
            },
            {
                "scene_number": 2,
                "original_description": "Featuring skilled baristas preparing specialty coffee drinks.",
                "enhanced_prompt": "Professional vertical video (9:16, 1080x1920) capturing expert barista crafting latte art. Dramatic overhead shot of pristine white ceramic cup, rich espresso streaming in perfect ribbon, microfoam milk creating intricate rosetta pattern. Modern minimalist cafe setting, soft natural lighting, shallow depth of field. Focus on hands and precise movements. Text overlay appears elegantly: 'Crafted with Passion'",
                "quality_prediction": 0.92,
                "recommended_model": "runway-gen3",
                "technical_params": {
                    "resolution": "1080x1920",
                    "duration": 7,
                    "style": "premium_lifestyle",
                    "camera_movement": "subtle_track",
                    "lighting": "natural_diffused",
                    "color_grade": "premium_warm"
                },
                "alternative_prompts": [
                    "Vertical format (9:16) close-up sequence of espresso extraction, golden crema forming in slow motion, professional barista environment, cinematic mood lighting",
                    "Vertical video (1080x1920) showing barista's eye view of milk steaming, focus on texture transformation, steam swirls, modern cafe aesthetic"
                ]
            }
        ]
    }
    
    # Test video generation tool
    print(f"\n🎬 Testing video generation tool...")
    
    video_tool = VideoGenerationTool()
    
    # Prepare data for the tool
    refined_prompts_data = json.dumps(claude_refinement_result)
    output_folder = os.path.join(reel_folder, 'raw_clips')
    context = json.dumps({
        'platform': platform,
        'duration': 20,
        'content_mode': 'music',
        'user_prompt': user_prompt
    })
    
    print(f"📋 Prompts: {len(claude_refinement_result['refined_prompts'])} scenes")
    print(f"📁 Output: {output_folder}")
    
    try:
        result = video_tool._run(
            refined_prompts_data=refined_prompts_data,
            output_folder=output_folder,
            context=context
        )
        
        print(f"\n✅ Video generation completed!")
        print(f"📊 Result: {result[:200]}...")
        
        # Parse and display result summary
        result_data = json.loads(result)
        status = result_data.get('video_generation_status', 'unknown')
        
        if status == 'success' or status == 'partial':
            clips = result_data.get('generated_clips', [])
            print(f"\n🎯 SUCCESS SUMMARY:")
            print(f"   Status: {status}")
            print(f"   Clips generated: {len(clips)}")
            for clip in clips:
                print(f"   - {clip.get('filename', 'N/A')}: {clip.get('status', 'N/A')}")
        else:
            error = result_data.get('error', 'Unknown error')
            print(f"\n❌ FAILURE:")
            print(f"   Status: {status}")
            print(f"   Error: {error}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_video_generation()
    if success:
        print(f"\n🚀 SUCCESS: Video generation test completed!")
    else:
        print(f"\n❌ FAILED: Video generation test failed")