"""
Custom CrewAI tool for audio generation using FAL.AI F5 TTS
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
        description="JSON string containing video generation result from Phase 4"
    )
    content_mode: str = Field(
        description="Content mode for audio generation ('narration' or 'music')",
        default="music"
    )
    audio_theme: str = Field(
        description="Audio theme/style (professional, casual, energetic, upbeat, cinematic)",
        default="professional"
    )
    context: str = Field(
        description="Context data (JSON string) with platform, duration, user_prompt info",
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

    def _run(self, video_generation_result: str, content_mode: str = "music", audio_theme: str = "professional", context: str = "") -> str:
        """Execute audio generation using FAL.AI F5 TTS and music generation"""
        try:
            # Parse context
            try:
                context_dict = json.loads(context) if isinstance(context, str) and context else {}
            except json.JSONDecodeError:
                context_dict = {}
            
            # Set audio theme in context
            context_dict['audio_theme'] = audio_theme
            context_dict.setdefault('platform', 'instagram')
            context_dict.setdefault('duration', 20)
            context_dict.setdefault('user_prompt', 'video content')
            
            # Auto-determine output folder from video generation result
            try:
                video_data = json.loads(video_generation_result) if isinstance(video_generation_result, str) else video_generation_result
                clips_folder = video_data.get('next_phase_data', {}).get('clips_folder', '')
                
                if clips_folder:
                    # Extract parent folder from clips_folder path
                    # clips_folder format: /path/to/reels/reel_folder/raw_clips
                    output_folder = os.path.dirname(clips_folder) if clips_folder.endswith('/raw_clips') else clips_folder
                else:
                    # Try to find current reel folder
                    reel_folders = [d for d in os.listdir('reels') if d.startswith('reel_') and os.path.isdir(os.path.join('reels', d))]
                    if reel_folders:
                        # Get the most recent reel folder
                        latest_folder = max(reel_folders, key=lambda x: os.path.getctime(os.path.join('reels', x)))
                        output_folder = os.path.join('reels', latest_folder)
                    else:
                        return json.dumps({
                            'audio_generation_status': 'failed',
                            'error': 'No output folder found and could not auto-detect reel folder'
                        })
            except Exception as folder_error:
                print(f"⚠️  Output folder detection error: {folder_error}")
                return json.dumps({
                    'audio_generation_status': 'failed',
                    'error': f'Output folder detection failed: {str(folder_error)}'
                })
            
            print(f"\n🎵 PHASE 5: Audio Generation Tool Starting")
            print(f"   🎚️  Content mode: {content_mode}")
            print(f"   🎨 Audio theme: {audio_theme}")
            print(f"   📁 Output folder: {output_folder}")
            
            # Initialize audio generator
            audio_gen = AudioGenerator(output_folder)
            
            # Execute audio generation
            try:
                result = audio_gen.generate_audio_content(
                    video_generation_result=video_data if 'video_data' in locals() else video_generation_result,
                    content_mode=content_mode,
                    context=context_dict
                )
                
                # Force tool completion to prevent CrewAI hanging
                if not result:
                    raise Exception("No audio generated - forcing tool completion")
                    
            except Exception as gen_error:
                print(f"   ❌ Audio generation error: {gen_error}")
                # Create fallback result to prevent CrewAI hanging
                result = {
                    'audio_generation_status': 'failed',
                    'content_mode': content_mode,
                    'generated_audio': {
                        'file_path': None,
                        'filename': None,
                        'duration': context_dict.get('duration', 20),
                        'type': content_mode,
                        'status': 'failed',
                        'error': str(gen_error)
                    },
                    'generation_summary': {
                        'audio_type': content_mode,
                        'duration': context_dict.get('duration', 20),
                        'theme': audio_theme,
                        'cost': 0.0,
                        'status': 'failed',
                        'error': str(gen_error)
                    },
                    'quality_assessment': {
                        'audio_quality_score': 0.0,
                        'sync_ready': False,
                        'format_compliance': False,
                        'ready_for_synchronization': False,
                        'validation_notes': f'Generation failed: {str(gen_error)}'
                    },
                    'next_phase_data': {
                        'audio_folder': os.path.join(output_folder, 'audio'),
                        'final_audio_file': '',
                        'audio_duration': context_dict.get('duration', 20),
                        'video_clips': 0,
                        'ready_for_phase_6': False
                    },
                    'error': str(gen_error)
                }
            
            # Print comprehensive summary
            audio_status = result.get('audio_generation_status', 'unknown')
            generated_audio = result.get('generated_audio', {})
            quality_assessment = result.get('quality_assessment', {})
            
            print(f"\n🎯 AUDIO GENERATION TOOL COMPLETE!")
            print(f"   ✅ Status: {audio_status}")
            print(f"   🎧 Audio type: {content_mode}")
            print(f"   📊 Quality score: {quality_assessment.get('audio_quality_score', 0.0):.2f}")
            print(f"   💰 Cost: ${result.get('generation_summary', {}).get('cost', 0.0):.3f}")
            print(f"   🚀 Ready for Phase 6: {quality_assessment.get('ready_for_synchronization', False)}")
            
            # Add script content to output if narration mode
            if content_mode == 'narration' and 'script_content' in result:
                print(f"   📝 Script: {result['script_content'][:100]}..." if len(result.get('script_content', '')) > 100 else f"   📝 Script: {result.get('script_content', '')}")
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                'audio_generation_status': 'failed',
                'error': str(e),
                'message': f'Audio generation failed: {str(e)}'
            }
            print(f"❌ Audio generation tool error: {str(e)}")
            return json.dumps(error_result, indent=2)