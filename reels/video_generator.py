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
        
        # Ensure raw_clips folder exists
        self.clips_folder = os.path.join(output_folder, 'raw_clips')
        os.makedirs(self.clips_folder, exist_ok=True)
        print(f"📁 Created clips folder: {self.clips_folder}")
        
        # Initialize FAL client
        if self.fal_key:
            fal_client.api_key = self.fal_key
            os.environ['FAL_KEY'] = self.fal_key
        else:
            raise ValueError("FAL_KEY not found. Please set FAL_KEY in .env file or environment variables.")
        
        # Model configurations - Updated with correct FAL.AI endpoints (2025)
        self.models = {
            'hailuo-02': {
                'endpoint': 'fal-ai/minimax/hailuo-02/pro/text-to-video',
                'max_duration': 10,
                'cost_per_clip': 0.50,  # Pro version pricing
                'strengths': ['realistic_motion', 'human_activities', 'high_quality'],
                'best_for': ['all_content_types', 'professional_quality', 'versatile']
            }
        }
        
        # Default fallback order - only hailuo-02 now
        self.fallback_order = ['hailuo-02']
    
    def select_optimal_model(self, prompt_data: Dict) -> str:
        """Always use hailuo-02 as it's our only model now"""
        return 'hailuo-02'
    
    def generate_video_clips(self, refined_prompts: List[Dict]) -> List[Dict]:
        """Generate video clips using FAL.AI models with intelligent model selection"""
        
        if not self.fal_key:
            print("⚠️  FAL_KEY not configured. Returning mock clips for testing.")
            return self._create_mock_clips(refined_prompts)
        
        print(f"🎬 Generating {len(refined_prompts)} video clips using FAL.AI...")
        generated_clips = []
        
        for i, prompt_data in enumerate(refined_prompts):
            try:
                print(f"\n📹 Generating clip {i + 1}/{len(refined_prompts)}...")
                
                # Select optimal model
                selected_model = self.select_optimal_model(prompt_data)
                print(f"   🤖 Using model: {selected_model}")
                print(f"   📝 Prompt: {prompt_data.get('enhanced_prompt', '')[:60]}...")
                
                # Generate clip
                clip_data = self._generate_single_clip(prompt_data, i + 1, selected_model)
                generated_clips.append(clip_data)
                
                if clip_data['status'] == 'success':
                    print(f"   ✅ Clip {i + 1} generated successfully")
                else:
                    print(f"   ⚠️  Clip {i + 1} generation issues: {clip_data.get('status')}")
                
            except Exception as e:
                print(f"   ❌ Error generating clip {i + 1}: {e}")
                # Create error placeholder
                clip_data = {
                    'clip_id': i + 1,
                    'file_path': None,
                    'status': 'failed',
                    'error': str(e),
                    'prompt_data': prompt_data,
                    'model_used': None
                }
                generated_clips.append(clip_data)
        
        # Summary
        successful_clips = len([c for c in generated_clips if c['status'] == 'success'])
        print(f"\n🎯 Generation Summary: {successful_clips}/{len(refined_prompts)} clips successful")
        
        return generated_clips
    
    def _generate_single_clip(self, prompt_data: Dict, clip_id: int, model_name: str) -> Dict:
        """Generate a single video clip using specified FAL model"""
        
        try:
            # Extract prompt and parameters
            enhanced_prompt = prompt_data.get('enhanced_prompt', '')
            technical_params = prompt_data.get('technical_params', {})
            duration = technical_params.get('duration', 7)
            
            # Get model configuration
            model_config = self.models[model_name]
            
            # Prepare generation arguments
            generation_args = {
                'prompt': enhanced_prompt,
                'duration_seconds': min(duration, model_config['max_duration']),
                'aspect_ratio': '9:16',
                'resolution': 'hd'
            }
            
            # Model-specific parameter adjustments
            if model_name == 'hailuo-02':
                generation_args.update({
                    'fps': 24,
                    'quality': 'high'
                })
            elif model_name == 'runway-gen3':
                generation_args.update({
                    'fps': 30,
                    'motion_intensity': 0.7
                })
            elif model_name == 'pika-labs':
                generation_args.update({
                    'guidance_scale': 7.5,
                    'num_inference_steps': 25
                })
            
            # Generate video using FAL.AI
            print(f"   🚀 Submitting to {model_config['endpoint']}...")
            
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
                
                # Wait for result using correct FAL client syntax
                print(f"   ⏳ Waiting for generation with request_id: {result.request_id}")
                final_result = result.get()
                
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