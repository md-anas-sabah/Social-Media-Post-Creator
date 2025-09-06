"""
Custom CrewAI tool for audio generation using FAL AI F5 TTS
"""

from crewai.tools.base_tool import BaseTool
from typing import Type, Dict, List, Any
from pydantic import BaseModel, Field
import json
import os
from .audio_generator import AudioGenerator


class AudioGenerationInput(BaseModel):
    """Input schema for audio generation tool"""
    video_generation_result: str = Field(
        description="JSON string containing video generation results from Phase 4"
    )
    content_mode: str = Field(
        description="Content mode: 'music' for background music or 'narration' for TTS",
        default="music"
    )
    script_content: str = Field(
        description="Script content for narration mode (ignored in music mode)",
        default=""
    )
    audio_theme: str = Field(
        description="Theme for audio generation (e.g., 'upbeat', 'professional', 'cinematic')",
        default="upbeat"
    )
    context: str = Field(
        description="Context data (JSON string) with platform, duration, etc.",
        default=""
    )


class AudioGenerationTool(BaseTool):
    name: str = "Advanced Audio Generation Tool"
    description: str = (
        "Generates professional audio for video reels using FAL AI F5 TTS for narration "
        "or creates background music for music mode. Handles timing synchronization "
        "with video clips and produces high-quality audio optimized for social media."
    )
    args_schema: Type[BaseModel] = AudioGenerationInput

    def _run(self, video_generation_result: str, content_mode: str = "music", 
             script_content: str = "", audio_theme: str = "upbeat", context: str = "") -> str:
        """Execute audio generation using FAL AI F5 TTS and music generation"""
        
        try:
            # Parse context
            try:
                context_dict = json.loads(context) if isinstance(context, str) and context else {}
            except json.JSONDecodeError:
                context_dict = {}
            
            # Set default context values
            context_dict.setdefault('platform', 'instagram')
            context_dict.setdefault('duration', 20)
            context_dict.setdefault('user_prompt', 'video content')
            
            # Parse video generation result to get output folder and video info
            try:
                if isinstance(video_generation_result, str):
                    video_data = json.loads(video_generation_result)
                else:
                    video_data = video_generation_result
                
                # Get output folder from video generation result
                if 'next_phase_data' in video_data and 'clips_folder' in video_data['next_phase_data']:
                    clips_folder = video_data['next_phase_data']['clips_folder']
                    # Get parent folder (reel folder) by removing 'raw_clips'
                    output_folder = os.path.dirname(clips_folder)
                else:
                    # Auto-detect reel folder
                    reel_folders = [d for d in os.listdir('reels') if d.startswith('reel_') and os.path.isdir(os.path.join('reels', d))]
                    if reel_folders:
                        latest_folder = max(reel_folders, key=lambda x: os.path.getctime(os.path.join('reels', x)))
                        output_folder = os.path.join('reels', latest_folder)
                    else:
                        return json.dumps({
                            'audio_generation_status': 'failed',
                            'error': 'Could not determine output folder from video generation result'
                        })
                
                # Get video duration and clip count
                video_clips = video_data.get('generated_clips', [])
                successful_clips = [c for c in video_clips if c.get('status') in ['success', 'mock']]
                total_duration = context_dict.get('duration', 20)
                
            except Exception as parse_error:
                print(f"⚠️  Error parsing video generation result: {parse_error}")
                # Use context to determine output folder
                output_folder = context_dict.get('reel_folder', '')
                if not output_folder:
                    return json.dumps({
                        'audio_generation_status': 'failed',
                        'error': f'Could not parse video data: {str(parse_error)}'
                    })
                successful_clips = []
                total_duration = context_dict.get('duration', 20)
            
            print(f"\n🎵 PHASE 5: Audio Generation Starting")
            print(f"   🎭 Content mode: {content_mode}")
            print(f"   📁 Output folder: {output_folder}")
            print(f"   ⏱️  Target duration: {total_duration}s")
            print(f"   🎨 Audio theme: {audio_theme}")
            
            # Initialize audio generator
            audio_gen = AudioGenerator(output_folder)
            
            # Generate audio based on content mode
            if content_mode == 'narration':
                print(f"   🎙️  Generating TTS narration...")
                
                # Create narration script if not provided
                if not script_content:
                    script_content = self._create_narration_script(context_dict, successful_clips)
                
                print(f"   📝 Script: {script_content[:100]}...")
                
                # Estimate cost
                cost_estimate = audio_gen.estimate_audio_cost('narration', len(script_content))
                print(f"   💰 Estimated cost: ${cost_estimate['total_cost']:.3f}")
                
                # Generate TTS narration
                audio_result = audio_gen.generate_narration(
                    script=script_content,
                    duration=total_duration,
                    voice_style='professional'
                )
                
            else:  # music mode
                print(f"   🎵 Generating background music...")
                
                # Estimate cost (free for now)
                cost_estimate = audio_gen.estimate_audio_cost('music')
                print(f"   💰 Estimated cost: ${cost_estimate['total_cost']:.3f}")
                
                # Generate background music
                audio_result = audio_gen.generate_background_music(
                    theme=audio_theme,
                    duration=total_duration,
                    mood=self._determine_mood_from_theme(audio_theme)
                )
            
            # Process audio for synchronization
            print(f"   🔧 Processing audio for synchronization...")
            final_audio = audio_gen.process_audio_for_sync(audio_result, total_duration)
            
            # Determine overall status
            if audio_result.get('status') == 'success':
                overall_status = 'success'
            elif audio_result.get('status') == 'mock':
                overall_status = 'mock'
            else:
                overall_status = 'failed'
            
            # Build comprehensive result
            result = {
                'audio_generation_status': overall_status,
                'content_mode': content_mode,
                'generated_audio': audio_result,
                'processed_audio': final_audio,
                'generation_summary': {
                    'audio_type': content_mode,
                    'duration': total_duration,
                    'theme': audio_theme,
                    'cost': cost_estimate['total_cost'],
                    'status': overall_status
                },
                'quality_assessment': {
                    'audio_quality_score': 0.9 if overall_status == 'success' else 0.7,
                    'sync_ready': True,
                    'format_compliance': True,
                    'ready_for_synchronization': overall_status in ['success', 'mock']
                },
                'next_phase_data': {
                    'audio_folder': audio_gen.audio_folder,
                    'final_audio_file': final_audio.get('filename', ''),
                    'audio_duration': total_duration,
                    'video_clips': len(successful_clips),
                    'ready_for_phase_6': overall_status in ['success', 'mock']
                },
                'script_content': script_content if content_mode == 'narration' else None
            }
            
            # Print summary
            print(f"\n🎯 AUDIO GENERATION COMPLETE!")
            print(f"   ✅ Status: {overall_status}")
            print(f"   🎭 Mode: {content_mode}")
            print(f"   💰 Cost: ${cost_estimate['total_cost']:.3f}")
            print(f"   🚀 Ready for Phase 6: {result['quality_assessment']['ready_for_synchronization']}")
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                'audio_generation_status': 'failed',
                'error': str(e),
                'message': f'Audio generation failed: {str(e)}'
            }
            print(f"❌ Audio generation error: {str(e)}")
            return json.dumps(error_result, indent=2)
    
    def _create_narration_script(self, context: Dict, video_clips: List) -> str:
        """Create a narration script based on context and video clips"""
        user_prompt = context.get('user_prompt', 'video content')
        duration = context.get('duration', 20)
        
        # Create educational narration based on user prompt
        if 'tutorial' in user_prompt.lower() or 'how to' in user_prompt.lower():
            script = f"In this tutorial, we'll explore {user_prompt}. Follow along as we break down the key steps and techniques you need to know."
        elif 'fashion' in user_prompt.lower():
            script = f"Discover the latest trends in {user_prompt}. From style inspiration to must-have pieces, let's dive into what's trending now."
        elif 'fitness' in user_prompt.lower():
            script = f"Ready to transform your fitness journey? Here's your guide to {user_prompt} with practical tips you can start using today."
        elif 'cooking' in user_prompt.lower() or 'recipe' in user_prompt.lower():
            script = f"Let's create something delicious! This {user_prompt} recipe is perfect for beginners and packed with flavor."
        else:
            script = f"Welcome to this comprehensive guide on {user_prompt}. We'll cover everything you need to know in the next {duration} seconds."
        
        # Adjust script length for duration (roughly 150 words per minute)
        target_words = int((duration / 60) * 150)
        current_words = len(script.split())
        
        if current_words < target_words * 0.7:  # If too short, expand
            script += f" We'll break this down step by step, ensuring you understand each concept thoroughly. By the end of this video, you'll have a clear understanding of the key principles and be ready to apply them yourself."
        
        return script
    
    def _determine_mood_from_theme(self, theme: str) -> str:
        """Determine mood based on audio theme"""
        theme_lower = theme.lower()
        
        if 'upbeat' in theme_lower or 'energetic' in theme_lower:
            return 'energetic'
        elif 'cinematic' in theme_lower or 'dramatic' in theme_lower:
            return 'dramatic'
        elif 'professional' in theme_lower or 'corporate' in theme_lower:
            return 'inspiring'
        elif 'calm' in theme_lower or 'ambient' in theme_lower:
            return 'calm'
        else:
            return 'cheerful'  # Default mood