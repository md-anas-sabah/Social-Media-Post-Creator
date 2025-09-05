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


class VideoGenerator:
    """Advanced FAL.AI video generation with multi-model support and intelligent fallbacks"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.fal_key = config('FAL_KEY', default='')
        
        # Ensure raw_clips folder exists
        self.clips_folder = os.path.join(output_folder, 'raw_clips')
        os.makedirs(self.clips_folder, exist_ok=True)
        
        # Initialize FAL client
        if self.fal_key:
            fal_client.api_key = self.fal_key
        
        # Model configurations
        self.models = {
            'hailuo-02': {
                'endpoint': 'fal-ai/minimax/hailuo-02',
                'max_duration': 10,
                'cost_per_clip': 0.49,
                'strengths': ['realistic_motion', 'human_activities', 'cost_effective'],
                'best_for': ['lifestyle', 'product_demo', 'tutorial']
            },
            'runway-gen3': {
                'endpoint': 'fal-ai/runway/gen3/turbo/text-to-video',
                'max_duration': 10,
                'cost_per_clip': 1.20,
                'strengths': ['creative_transitions', 'dynamic_scenes', 'artistic'],
                'best_for': ['creative', 'artistic', 'transitions']
            },
            'pika-labs': {
                'endpoint': 'fal-ai/pika/text-to-video',
                'max_duration': 8,
                'cost_per_clip': 0.80,
                'strengths': ['artistic_effects', 'engaging_visuals', 'stylized'],
                'best_for': ['entertainment', 'creative', 'stylized']
            },
            'veo-2': {
                'endpoint': 'fal-ai/veo-2/image-to-video',
                'max_duration': 5,
                'cost_per_clip': 2.50,
                'strengths': ['image_animation', 'product_enhancement', 'quality'],
                'best_for': ['product_showcase', 'image_animation', 'premium']
            }
        }
        
        # Default fallback order
        self.fallback_order = ['hailuo-02', 'runway-gen3', 'pika-labs']
    
    def select_optimal_model(self, prompt_data: Dict) -> str:
        """Intelligent model selection based on prompt characteristics and requirements"""
        
        # Get model recommendation from Claude refinement (Phase 3)
        recommended_model = prompt_data.get('recommended_model', 'hailuo-02')
        
        # Map Claude recommendations to our model names
        model_mapping = {
            'hailuo-02': 'hailuo-02',
            'runway-gen3': 'runway-gen3',
            'pika-labs': 'pika-labs',
            'veo-2': 'veo-2'
        }
        
        selected_model = model_mapping.get(recommended_model, 'hailuo-02')
        
        # Validate model availability and constraints
        if selected_model in self.models:
            # Check duration constraint
            required_duration = prompt_data.get('technical_params', {}).get('duration', 7)
            if required_duration <= self.models[selected_model]['max_duration']:
                return selected_model
        
        # Fallback to default if constraints not met
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
            
            result = fal_client.submit(
                model_config['endpoint'],
                arguments=generation_args,
                with_logs=True
            )
            
            # Wait for result with timeout
            print(f"   ⏳ Waiting for generation (max 300s)...")
            final_result = fal_client.result(result.request_id, timeout=300)
            
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