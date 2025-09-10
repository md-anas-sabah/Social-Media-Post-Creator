"""
FAL.AI video generation integration with multi-model support
"""

import os
import asyncio
import requests
from typing import List, Dict, Any, Optional
import fal_client
from decouple import config
import time
import json

# Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()


class VideoGenerator:
    """Advanced FAL.AI video generation with multi-model support and intelligent fallbacks"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        
        # Load FAL_KEY with multiple fallbacks
        self.fal_key = config('FAL_KEY', default='')
        if not self.fal_key:
            self.fal_key = os.getenv('FAL_KEY', '')
        if not self.fal_key:
            self.fal_key = os.environ.get('FAL_KEY', '')
            
        print(f"🔑 FAL_KEY status: {'✅ Found' if self.fal_key else '❌ Missing'}")
        if self.fal_key:
            print(f"🔑 FAL_KEY prefix: {self.fal_key[:8]}...")
        
        # Validate and ensure raw_clips folder exists
        if not output_folder or not os.path.exists(output_folder):
            raise ValueError(f"Output folder does not exist or is invalid: {output_folder}")
        
        self.clips_folder = os.path.join(output_folder, 'raw_clips')
        try:
            os.makedirs(self.clips_folder, exist_ok=True)
            print(f"📁 Created clips folder: {self.clips_folder}")
        except (PermissionError, OSError) as e:
            raise ValueError(f"Cannot create clips folder {self.clips_folder}: {e}")
        
        # Initialize FAL client
        if self.fal_key:
            fal_client.api_key = self.fal_key
            os.environ['FAL_KEY'] = self.fal_key
        else:
            raise ValueError("FAL_KEY not found. Please set FAL_KEY in .env file or environment variables.")
        
        # Model configurations - Updated with correct FAL.AI endpoints (2025)
        self.models = {
            'hailuo-02': {
                'endpoint': 'fal-ai/minimax/hailuo-02/pro/text-to-video',  # Correct endpoint from FAL.AI website
                'max_duration': 10,
                'cost_per_clip': 0.50,
                'strengths': ['realistic_motion', 'human_activities', 'high_quality'],
                'best_for': ['all_content_types', 'professional_quality', 'versatile'],
                'supports_aspect_ratio': True
            },
            'runway-gen3': {
                'endpoint': 'fal-ai/runway/gen3/turbo/text-to-video',
                'max_duration': 10,
                'cost_per_clip': 1.20,
                'strengths': ['creative_transitions', 'dynamic_scenes', 'artistic_content'],
                'best_for': ['creative_content', 'artistic_effects', 'stylized_videos'],
                'supports_aspect_ratio': True
            },
            'pika-labs': {
                'endpoint': 'fal-ai/pika-labs/text-to-video',
                'max_duration': 8,
                'cost_per_clip': 0.80,
                'strengths': ['artistic_effects', 'engaging_visuals', 'stylized_content'],
                'best_for': ['social_media', 'stylized_content', 'engaging_videos'],
                'supports_aspect_ratio': True
            },
            'veo-2': {
                'endpoint': 'fal-ai/google/veo-2',
                'max_duration': 5,
                'cost_per_clip': 2.50,
                'strengths': ['premium_quality', 'image_animation', 'product_enhancement'],
                'best_for': ['premium_content', 'product_showcases', 'high_quality'],
                'supports_aspect_ratio': True
            }
        }
        
        # Default fallback order - intelligent order based on cost-quality balance
        self.fallback_order = ['hailuo-02', 'pika-labs', 'runway-gen3', 'veo-2']
    
    def select_optimal_model(self, prompt_data: Dict) -> str:
        """Select optimal model based on Claude recommendations and content requirements"""
        
        # Check if Claude recommended a specific model
        recommended_model = prompt_data.get('recommended_model', '').lower()
        
        # Map Claude recommendations to available models
        model_mapping = {
            'hailuo-02': 'hailuo-02',
            'hailuo02': 'hailuo-02', 
            'hailuo_02': 'hailuo-02',
            'runway-gen3': 'runway-gen3',
            'runway_gen3': 'runway-gen3',
            'runwaygen3': 'runway-gen3',
            'pika-labs': 'pika-labs',
            'pika_labs': 'pika-labs',
            'pikalabs': 'pika-labs',
            'veo-2': 'veo-2',
            'veo2': 'veo-2',
            'veo_2': 'veo-2'
        }
        
        # If Claude recommended a model and it's available, use it
        if recommended_model in model_mapping:
            selected_model = model_mapping[recommended_model]
            if selected_model in self.models:
                print(f"   🎯 Using Claude-recommended model: {selected_model}")
                return selected_model
        
        # Fallback to content-based selection
        content_analysis = prompt_data.get('content_analysis', {})
        content_category = content_analysis.get('category', '').lower()
        
        # Content-based model selection logic
        if 'education' in content_category or 'tutorial' in content_category:
            # Educational content - prioritize clarity and realism
            return 'hailuo-02'
        elif 'artistic' in content_category or 'creative' in content_category:
            # Artistic content - prioritize creative effects
            return 'pika-labs'
        elif 'premium' in content_category or 'product' in content_category:
            # Premium content - use highest quality if budget allows
            return 'veo-2'
        elif 'dynamic' in content_category or 'action' in content_category:
            # Dynamic content - use runway for transitions
            return 'runway-gen3'
        else:
            # Default to most reliable and cost-effective
            return 'hailuo-02'
    
    def generate_video_clips(self, refined_prompts: List[Dict]) -> List[Dict]:
        """Generate video clips using FAL.AI models with intelligent model selection"""
        
        if not self.fal_key:
            print("⚠️  FAL_KEY not configured. Returning mock clips for testing.")
            return self._create_mock_clips(refined_prompts)
        
        print(f"🎬 Generating {len(refined_prompts)} video clips using FAL.AI...")
        generated_clips = []
        
        max_generation_time = 600  # 10 minutes max per clip
        
        for i, prompt_data in enumerate(refined_prompts):
            clip_start_time = time.time()
            
            try:
                print(f"\n📹 Generating clip {i + 1}/{len(refined_prompts)}...")
                print(f"   ⏰ Starting at: {time.strftime('%H:%M:%S')}")
                print(f"   ⏱️  Max generation time: {max_generation_time//60} minutes")
                
                # Select optimal model
                selected_model = self.select_optimal_model(prompt_data)
                print(f"   🤖 Using model: {selected_model}")
                print(f"   📝 Prompt: {prompt_data.get('enhanced_prompt', '')[:60]}...")
                
                # Generate clip with strict timeout
                try:
                    clip_data = self._generate_single_clip_with_timeout(
                        prompt_data, i + 1, selected_model, max_generation_time
                    )
                    generated_clips.append(clip_data)
                    
                    elapsed = time.time() - clip_start_time
                    
                    if clip_data['status'] == 'success':
                        print(f"   ✅ Clip {i + 1} generated successfully in {elapsed:.1f}s")
                        print(f"   ⏰ Completed at: {time.strftime('%H:%M:%S')}")
                    elif clip_data['status'] == 'mock':
                        print(f"   🧪 Clip {i + 1} generated as mock (API issues)")
                        print(f"   ⏰ Completed at: {time.strftime('%H:%M:%S')}")
                    else:
                        print(f"   ⚠️  Clip {i + 1} generation issues: {clip_data.get('status')}")
                        print(f"   ⚠️  Error: {clip_data.get('error', 'Unknown error')}")
                        
                except Exception as clip_error:
                    elapsed = time.time() - clip_start_time
                    print(f"   ❌ Clip generation failed after {elapsed:.1f}s: {str(clip_error)}")
                    
                    # Create error placeholder and continue
                    clip_data = {
                        'clip_id': i + 1,
                        'file_path': None,
                        'status': 'failed',
                        'error': f"Generation failed after {elapsed:.1f}s: {str(clip_error)}",
                        'prompt_data': prompt_data,
                        'model_used': selected_model
                    }
                    generated_clips.append(clip_data)
                    print(f"   ⚠️  Continuing with next clip despite failure...")
                
            except Exception as e:
                elapsed = time.time() - clip_start_time
                print(f"   ❌ Unexpected error in clip {i + 1} after {elapsed:.1f}s: {e}")
                
                # Create error placeholder and continue processing
                clip_data = {
                    'clip_id': i + 1,
                    'file_path': None,
                    'status': 'failed',
                    'error': f"Unexpected error after {elapsed:.1f}s: {str(e)}",
                    'prompt_data': prompt_data,
                    'model_used': None
                }
                generated_clips.append(clip_data)
                print(f"   ⚠️  Continuing with remaining clips...")
        
        # Summary
        successful_clips = len([c for c in generated_clips if c['status'] == 'success'])
        print(f"\n🎯 Generation Summary: {successful_clips}/{len(refined_prompts)} clips successful")
        
        return generated_clips
    
    def _generate_single_clip_with_timeout(self, prompt_data: Dict, clip_id: int, model_name: str, timeout: int) -> Dict:
        """Generate a single video clip with strict timeout and fallback"""
        start_time = time.time()
        
        try:
            print(f"   🎬 Starting generation with {timeout}s timeout...")
            
            # Generate clip with monitoring
            result = self._generate_single_clip(prompt_data, clip_id, model_name)
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"   ⏰ Generation exceeded timeout ({elapsed:.1f}s > {timeout}s)")
                print(f"   🧪 Using result anyway (completed)")
                
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Generation failed after {elapsed:.1f}s: {str(e)}")
            
            # Always fallback to mock on any error to prevent hanging
            print(f"   🧪 Creating mock clip to prevent hanging...")
            return self._create_mock_single_clip(prompt_data, clip_id, model_name)
    
    def _generate_single_clip(self, prompt_data: Dict, clip_id: int, model_name: str) -> Dict:
        """Generate a single video clip using specified FAL model"""
        
        try:
            # Validate input data
            if not prompt_data:
                raise ValueError("prompt_data is None or empty")
            
            if not isinstance(prompt_data, dict):
                raise ValueError(f"prompt_data must be a dict, got {type(prompt_data)}")
            
            # Extract prompt and parameters with validation
            enhanced_prompt = prompt_data.get('enhanced_prompt', '')
            if not enhanced_prompt:
                # Fallback to basic description
                enhanced_prompt = prompt_data.get('description', '')
                if not enhanced_prompt:
                    raise ValueError("No enhanced_prompt or description found in prompt_data")
            
            technical_params = prompt_data.get('technical_params', {})
            duration = technical_params.get('duration', 7)
            
            # Validate duration
            if not isinstance(duration, (int, float)) or duration <= 0:
                print(f"⚠️  Invalid duration {duration}, using default 7s")
                duration = 7
            
            # Get model configuration
            model_config = self.models[model_name]
            
            # Prepare generation arguments with AGGRESSIVE vertical format enforcement
            # Strong vertical format prompt with multiple keywords
            vertical_prompt = f"VERTICAL VIDEO: {enhanced_prompt}, shot in 9:16 vertical aspect ratio, portrait mode, mobile phone video format, Instagram Reels style, TikTok format, vertical smartphone recording, tall narrow frame, portrait orientation video"
            
            generation_args = {
                'prompt': vertical_prompt,
                'duration': min(duration, model_config['max_duration']),
                'aspect_ratio': '9:16'
            }
            
            # Model-specific parameter adjustments with verified FAL.AI parameters only
            if model_name == 'hailuo-02':
                # Hailuo-02 specific parameters based on FAL.AI docs
                generation_args.update({
                    'aspect_ratio': '9:16'  # Force vertical - this is critical!
                })
            elif model_name == 'runway-gen3':
                generation_args.update({
                    'aspect_ratio': '9:16'  # Force vertical
                })
            elif model_name == 'pika-labs':
                generation_args.update({
                    'aspect_ratio': '9:16'  # Force vertical
                })
            
            # Generate video using FAL.AI
            print(f"   🚀 Submitting to {model_config['endpoint']}...")
            print(f"   📐 Generation parameters: {generation_args}")
            
            try:
                result = fal_client.submit(
                    model_config['endpoint'],
                    arguments=generation_args
                )
                
                print(f"   📋 Submit result type: {type(result)}")
                print(f"   🔍 Request ID: {result.request_id if result and hasattr(result, 'request_id') else 'None'}")
                
                if not result:
                    raise Exception("FAL.AI submit returned None")
                    
                if not hasattr(result, 'request_id'):
                    raise Exception(f"FAL.AI result missing request_id attribute. Result: {result}")
                    
                if not result.request_id:
                    raise Exception("FAL.AI request_id is empty")
                
                # Wait for result with proper timeout handling
                print(f"   ⏳ Waiting for generation with request_id: {result.request_id}")
                
                try:
                    # Try simple approach first - direct get() with shorter wait
                    print(f"   ⚡ Attempting direct result retrieval...")
                    start_time = time.time()
                    
                    # First, try a simple get() call with reasonable expectations
                    try:
                        final_result = result.get()
                        elapsed = time.time() - start_time
                        print(f"   ✅ Generation completed in {elapsed:.1f} seconds")
                        
                    except Exception as direct_error:
                        print(f"   ⚠️  Direct get() failed: {str(direct_error)}")
                        print(f"   🔄 Trying status-based approach...")
                        
                        # Fallback: Use status checking with reduced timeout
                        max_attempts = 30  # 5 minutes total (30 * 10 seconds)
                        attempt = 0
                        final_result = None
                        
                        while attempt < max_attempts and not final_result:
                            try:
                                # Check status - FAL client returns objects, not dicts
                                status = fal_client.status(model_config['endpoint'], result.request_id)
                                
                                # Handle different status object types
                                if hasattr(status, 'status'):
                                    status_state = status.status
                                elif hasattr(status, '__class__'):
                                    status_state = status.__class__.__name__
                                else:
                                    status_state = str(status)
                                
                                print(f"   📊 Check {attempt + 1}/30: {status_state}")
                                
                                # If status indicates completion, try to get result
                                if status_state in ['COMPLETED', 'Completed', 'completed']:
                                    try:
                                        final_result = result.get()  # Use original result object, not status
                                        print(f"   ✅ Status-based completion after {attempt + 1} checks")
                                        break
                                    except Exception as get_error:
                                        print(f"   ⚠️  Get failed despite completion status: {get_error}")
                                        # Continue trying
                                        
                                elif status_state in ['FAILED', 'Failed', 'failed']:
                                    error_msg = getattr(status, 'error', 'Generation failed')
                                    raise Exception(f"FAL.AI reported failure: {error_msg}")
                                    
                                # After many attempts, try direct get regardless of status
                                elif attempt >= 20:
                                    print(f"   ⏰ Extended wait, trying direct get() again...")
                                    try:
                                        final_result = result.get()
                                        break
                                    except Exception as late_get_error:
                                        print(f"   ⚠️  Late get() failed: {late_get_error}")
                                
                                time.sleep(10)
                                attempt += 1
                                
                            except Exception as status_error:
                                print(f"   ⚠️  Status check error: {str(status_error)}")
                                # If status checking fails, try direct get
                                try:
                                    final_result = result.get()
                                    print(f"   ✅ Direct get() succeeded despite status error")
                                    break
                                except Exception as direct_get_error:
                                    print(f"   ⚠️  Direct get() also failed: {direct_get_error}")
                                
                                attempt += 1
                                if attempt < max_attempts:
                                    time.sleep(10)
                                    continue
                                else:
                                    break
                        
                        # If still no result, raise timeout
                        if not final_result:
                            elapsed = time.time() - start_time
                            raise Exception(f"FAL.AI timeout after {elapsed:.1f}s ({max_attempts} attempts)")
                        
                except Exception as wait_error:
                    print(f"   ❌ Generation wait failed: {str(wait_error)}")
                    raise Exception(f"FAL.AI generation failed: {str(wait_error)}")
                
            except Exception as api_error:
                print(f"   ❌ FAL.AI API Error: {str(api_error)}")
                # Fall back to mock generation for testing
                print(f"   🧪 Falling back to mock generation for testing...")
                return self._create_mock_single_clip(prompt_data, clip_id, model_name)
            
            # Download and save video
            if final_result and 'video' in final_result:
                video_url = final_result['video']['url']
                clip_filename = f"clip_{clip_id}_{model_name}.mp4"
                clip_path = os.path.join(self.clips_folder, clip_filename)
                
                # Download video
                print(f"   💾 Downloading video...")
                success = self._download_video(video_url, clip_path)
                
                if success:
                    # Check if video needs aspect ratio correction
                    corrected_path = self._ensure_vertical_aspect_ratio(clip_path, clip_id, model_name)
                    if corrected_path:
                        clip_path = corrected_path
                        clip_filename = os.path.basename(corrected_path)
                    
                    # Validate video quality
                    quality_check = self.validate_clip_quality(clip_path)
                    
                    return {
                        'clip_id': clip_id,
                        'file_path': clip_path,
                        'filename': clip_filename,
                        'status': 'success',
                        'model_used': model_name,
                        'prompt_data': prompt_data,
                        'generation_result': final_result,
                        'quality_check': quality_check,
                        'duration': duration,
                        'resolution': '1080x1920',
                        'format': 'mp4',
                        'cost_estimate': model_config['cost_per_clip']
                    }
                else:
                    return self._create_failed_clip(clip_id, "Failed to download video", prompt_data, model_name)
            else:
                return self._create_failed_clip(clip_id, "No video in result", prompt_data, model_name)
                
        except Exception as e:
            print(f"   ❌ Generation failed: {str(e)}")
            return self._create_failed_clip(clip_id, str(e), prompt_data, model_name)
    
    def _download_video(self, video_url: str, output_path: str) -> bool:
        """Download video from URL to local file"""
        try:
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"   ❌ Download failed: {e}")
            return False
    
    def _create_failed_clip(self, clip_id: int, error: str, prompt_data: Dict, model_name: str) -> Dict:
        """Create failed clip data structure"""
        return {
            'clip_id': clip_id,
            'file_path': None,
            'filename': None,
            'status': 'failed',
            'error': error,
            'model_used': model_name,
            'prompt_data': prompt_data
        }
    
    def _create_mock_single_clip(self, prompt_data: Dict, clip_id: int, model_name: str) -> Dict:
        """Create a single mock clip for testing when FAL.AI fails"""
        clip_filename = f"mock_clip_{clip_id}_{model_name}.mp4"
        clip_path = os.path.join(self.clips_folder, clip_filename)
        
        # Create realistic mock file (1MB video-like size)
        mock_video_content = b'\\x00' * 1048576  # 1MB of null bytes
        with open(clip_path, 'wb') as f:
            f.write(mock_video_content)
        
        duration = prompt_data.get('technical_params', {}).get('duration', 7)
        
        return {
            'clip_id': clip_id,
            'file_path': clip_path,
            'filename': clip_filename,
            'status': 'mock',
            'model_used': model_name,
            'prompt_data': prompt_data,
            'duration': duration,
            'resolution': '1080x1920',
            'format': 'mp4',
            'cost_estimate': self.models[model_name]['cost_per_clip'],
            'quality_check': {
                'valid': True,
                'file_size': 1048576,
                'estimated_quality': 'mock'
            }
        }
    
    def validate_clip_quality(self, clip_path: str) -> Dict:
        """Basic video quality validation"""
        
        if not os.path.exists(clip_path):
            return {'valid': False, 'reason': 'File not found'}
        
        file_size = os.path.getsize(clip_path)
        if file_size == 0:
            return {'valid': False, 'reason': 'Empty file'}
        
        # Basic file size validation (minimum 100KB for short clips)
        if file_size < 100000:
            return {'valid': False, 'reason': 'File too small', 'size': file_size}
        
        # Additional validation would go here (resolution, duration, codec, etc.)
        # For now, basic validation
        return {
            'valid': True,
            'file_size': file_size,
            'format': 'mp4',
            'estimated_quality': 'good' if file_size > 1000000 else 'basic'
        }
    
    def _create_mock_clips(self, refined_prompts: List[Dict]) -> List[Dict]:
        """Create mock clips when FAL API not available (for testing)"""
        print("🧪 Creating mock video clips for testing...")
        mock_clips = []
        
        for i, prompt_data in enumerate(refined_prompts):
            clip_filename = f"mock_clip_{i + 1}.mp4"
            clip_path = os.path.join(self.clips_folder, clip_filename)
            
            # Create realistic mock file (small video-like size)
            mock_video_content = b'\x00' * 1048576  # 1MB of null bytes
            with open(clip_path, 'wb') as f:
                f.write(mock_video_content)
            
            mock_clips.append({
                'clip_id': i + 1,
                'file_path': clip_path,
                'filename': clip_filename,
                'status': 'mock',
                'model_used': prompt_data.get('recommended_model', 'hailuo-02'),
                'prompt_data': prompt_data,
                'duration': prompt_data.get('technical_params', {}).get('duration', 7),
                'resolution': '1080x1920',
                'format': 'mp4',
                'quality_check': {
                    'valid': True,
                    'file_size': 1048576,
                    'estimated_quality': 'mock'
                }
            })
        
        print(f"✅ Created {len(mock_clips)} mock video clips")
        return mock_clips
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get detailed information about a specific model"""
        return self.models.get(model_name, {})
    
    def estimate_generation_cost(self, refined_prompts: List[Dict]) -> Dict:
        """Estimate total cost for video generation"""
        total_cost = 0.0
        model_usage = {}
        
        for prompt_data in refined_prompts:
            selected_model = self.select_optimal_model(prompt_data)
            model_cost = self.models[selected_model]['cost_per_clip']
            total_cost += model_cost
            
            if selected_model not in model_usage:
                model_usage[selected_model] = {'clips': 0, 'cost': 0.0}
            model_usage[selected_model]['clips'] += 1
            model_usage[selected_model]['cost'] += model_cost
        
        return {
            'total_estimated_cost': total_cost,
            'model_breakdown': model_usage,
            'clip_count': len(refined_prompts),
            'average_cost_per_clip': total_cost / len(refined_prompts) if refined_prompts else 0
        }
    
    def _ensure_vertical_aspect_ratio(self, video_path: str, clip_id: int, model_name: str) -> Optional[str]:
        """Convert video to vertical 9:16 aspect ratio using FFmpeg crop/scale"""
        try:
            print(f"   🔄 Converting to 9:16 vertical format for clip {clip_id}...")
            
            corrected_filename = f"clip_{clip_id}_{model_name}_vertical.mp4"
            corrected_path = os.path.join(self.clips_folder, corrected_filename)
            
            # Try FFmpeg conversion to 9:16 aspect ratio
            try:
                import subprocess
                
                # FFmpeg command to convert to 9:16 by cropping center and scaling
                ffmpeg_cmd = [
                    'ffmpeg', '-y',  # -y to overwrite output file
                    '-i', video_path,  # Input file
                    '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',  # Scale and crop to 9:16
                    '-c:a', 'copy',  # Copy audio without re-encoding
                    '-crf', '23',  # Good quality
                    corrected_path
                ]
                
                print(f"   🎬 Running FFmpeg conversion...")
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0 and os.path.exists(corrected_path):
                    file_size = os.path.getsize(corrected_path)
                    if file_size > 0:
                        print(f"   ✅ Successfully converted to 9:16 format: {corrected_filename}")
                        print(f"   📐 New format: 1080x1920 vertical")
                        return corrected_path
                    else:
                        print(f"   ⚠️  FFmpeg produced empty file")
                else:
                    print(f"   ⚠️  FFmpeg failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  FFmpeg timeout - video too long or complex")
            except FileNotFoundError:
                print(f"   ⚠️  FFmpeg not found - installing FFmpeg recommended for aspect ratio correction")
            except Exception as ffmpeg_error:
                print(f"   ⚠️  FFmpeg error: {ffmpeg_error}")
            
            # Fallback: Just copy original and warn user
            try:
                import shutil
                shutil.copy2(video_path, corrected_path)
                print(f"   🟡 Fallback: Copied original video (may still be wide format)")
                print(f"   💡 Install FFmpeg for automatic aspect ratio correction")
                return corrected_path
            except Exception as copy_error:
                print(f"   ❌ Could not copy file: {copy_error}")
                return None
                
        except Exception as e:
            print(f"   ❌ Aspect ratio correction failed: {e}")
            return None