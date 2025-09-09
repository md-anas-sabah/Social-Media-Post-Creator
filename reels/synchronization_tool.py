"""
CrewAI tool for professional video synchronization and editing
Integrates with VideoSynchronizer class for MoviePy operations
"""

import os
import json
from typing import Dict, Any, Type
from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from .synchronizer import VideoSynchronizer


class SynchronizationTool(BaseTool):
    name: str = "Professional Synchronization Tool"
    description: str = """
    Professional video editing and audio synchronization tool using MoviePy.
    
    This tool provides comprehensive video editing capabilities including:
    - Video clip stitching with professional transitions
    - Audio-video synchronization with intelligent timing
    - Professional enhancements and effects
    - Quality optimization for social media platforms
    
    Input format:
    {
        "action": "stitch_and_sync",  # Required: stitch_and_sync, stitch_only, sync_only
        "video_clips": [...],         # Required: List of video clip data from Phase 4
        "audio_data": {...},          # Optional: Audio data from Phase 5
        "output_folder": "path",      # Required: Output folder path
        "platform": "instagram",     # Optional: Target platform
        "quality": "professional"    # Optional: Quality level
    }
    
    Returns comprehensive processing results with file paths and metadata.
    """
    
    def _run(self, action: str, video_clips: list, output_folder: str, 
             audio_data: dict = None, platform: str = "instagram", 
             quality: str = "professional") -> str:
        """
        Execute video synchronization and editing operations
        
        Args:
            action: Type of operation (stitch_and_sync, stitch_only, sync_only)
            video_clips: List of video clip data from Phase 4
            output_folder: Output folder path
            audio_data: Optional audio data from Phase 5
            platform: Target platform (instagram, tiktok, facebook)
            quality: Quality level (professional, standard, fast)
            
        Returns:
            JSON string with processing results
        """
        try:
            # Initialize synchronizer
            synchronizer = VideoSynchronizer(output_folder)
            
            results = {
                'action': action,
                'platform': platform,
                'quality': quality,
                'processing_steps': [],
                'files_created': [],
                'status': 'processing'
            }
            
            if action in ['stitch_and_sync', 'stitch_only']:
                # Step 1: Stitch video clips
                print(f"🎬 Stitching {len(video_clips)} video clips...")
                stitch_result = synchronizer.stitch_video_clips(video_clips)
                results['video_stitching'] = stitch_result
                results['processing_steps'].append('video_stitching_completed')
                
                if stitch_result.get('file_path'):
                    results['files_created'].append(stitch_result['file_path'])
                
                print(f"✅ Video stitching completed: {stitch_result.get('status')}")
            
            if action in ['stitch_and_sync', 'sync_only'] and audio_data:
                # Step 2: Synchronize audio
                video_data = results.get('video_stitching', {'file_path': None})
                
                print(f"🎵 Synchronizing audio with video...")
                sync_result = synchronizer.synchronize_audio(video_data, audio_data)
                results['audio_synchronization'] = sync_result
                results['processing_steps'].append('audio_synchronization_completed')
                
                if sync_result.get('file_path'):
                    results['files_created'].append(sync_result['file_path'])
                
                print(f"✅ Audio synchronization completed: {sync_result.get('status')}")
            
            # Step 3: Apply final enhancements
            if results.get('video_stitching'):
                enhancement_result = synchronizer.apply_transitions(results['video_stitching'])
                results['enhancements'] = enhancement_result
                results['processing_steps'].append('enhancements_applied')
                
                print(f"✨ Professional enhancements applied")
            
            # Step 4: Save processing metadata
            metadata = synchronizer.save_processing_metadata()
            results['metadata'] = metadata
            results['processing_steps'].append('metadata_saved')
            
            # Final status
            results['status'] = 'completed'
            results['final_reel_path'] = synchronizer.final_reel_path
            
            # Create comprehensive summary
            summary = self._create_processing_summary(results)
            results['summary'] = summary
            
            print(f"🎉 Synchronization completed successfully!")
            print(f"📁 Final reel: {synchronizer.final_reel_path}")
            
            return json.dumps(results, indent=2)
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'action': action,
                'platform': platform,
                'files_created': results.get('files_created', [])
            }
            print(f"❌ Error in synchronization: {str(e)}")
            return json.dumps(error_result, indent=2)
    
    def _create_processing_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive processing summary"""
        summary = {
            'status': results.get('status', 'unknown'),
            'total_processing_steps': len(results.get('processing_steps', [])),
            'files_created_count': len(results.get('files_created', [])),
            'final_output_available': bool(results.get('final_reel_path'))
        }
        
        # Video stitching summary
        if 'video_stitching' in results:
            video_data = results['video_stitching']
            summary['video_summary'] = {
                'clips_processed': video_data.get('clips_used', 0),
                'total_duration': video_data.get('total_duration', 0),
                'resolution': video_data.get('resolution', 'unknown'),
                'transitions_applied': video_data.get('transitions_applied', False),
                'quality': video_data.get('quality', 'unknown')
            }
        
        # Audio synchronization summary
        if 'audio_synchronization' in results:
            audio_data = results['audio_synchronization']
            summary['audio_summary'] = {
                'sync_quality': audio_data.get('sync_quality', 'unknown'),
                'audio_mode': audio_data.get('audio_mode', 'unknown'),
                'duration_matched': audio_data.get('video_duration', 0) == audio_data.get('audio_duration', 0),
                'enhancements_applied': audio_data.get('audio_enhancements_applied', False)
            }
        
        # Enhancement summary
        if 'enhancements' in results:
            enhancement_data = results['enhancements']
            summary['enhancement_summary'] = {
                'transitions_applied': enhancement_data.get('transitions_applied', []),
                'effects_applied': enhancement_data.get('effects_applied', []),
                'professional_grade': True
            }
        
        return summary


# Auto-detect folder context for easier tool usage
def get_reel_folder_from_context():
    """Auto-detect the current reel output folder"""
    current_dir = os.getcwd()
    
    # Look for reels folder structure
    reels_dir = os.path.join(current_dir, 'reels')
    if os.path.exists(reels_dir):
        # Find the most recent reel folder
        reel_folders = [f for f in os.listdir(reels_dir) if f.startswith('reel_') and os.path.isdir(os.path.join(reels_dir, f))]
        if reel_folders:
            latest_folder = sorted(reel_folders)[-1]  # Get most recent by name
            return os.path.join(reels_dir, latest_folder)
    
    return None


# Helper function for tool integration
def create_synchronization_request(video_clips, audio_data=None, action="stitch_and_sync"):
    """Helper function to create properly formatted synchronization requests"""
    
    # Auto-detect output folder
    output_folder = get_reel_folder_from_context()
    if not output_folder:
        raise Exception("Could not auto-detect reel output folder")
    
    return {
        "action": action,
        "video_clips": video_clips,
        "audio_data": audio_data,
        "output_folder": output_folder,
        "platform": "instagram",
        "quality": "professional"
    }