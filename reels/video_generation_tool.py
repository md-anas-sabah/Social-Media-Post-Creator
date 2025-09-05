"""
Custom CrewAI tool for video generation using FAL.AI
"""

from crewai.tools.base_tool import BaseTool
from typing import Type, Dict, List, Any
from pydantic import BaseModel, Field
import json
import re
from .video_generator import VideoGenerator


class VideoGenerationInput(BaseModel):
    """Input schema for video generation tool"""
    refined_prompts_data: str = Field(
        description="JSON string containing refined prompts from Phase 3 Claude enhancement"
    )
    output_folder: str = Field(
        description="Output folder path where video clips should be saved",
        default=""
    )
    context: str = Field(
        description="Context data (JSON string) with platform, duration, content_mode info",
        default=""
    )


class VideoGenerationTool(BaseTool):
    name: str = "Advanced Video Generation Tool"
    description: str = (
        "Generates professional video clips using FAL.AI multi-model system. "
        "Takes Claude-enhanced prompts and produces high-quality video content with intelligent model selection, "
        "quality validation, and comprehensive cost analysis."
    )
    args_schema: Type[BaseModel] = VideoGenerationInput

    def _run(self, refined_prompts_data: str, output_folder: str = "", context: str = "") -> str:
        """Execute video generation using FAL.AI models"""
        try:
            # Parse context first to get folder info if needed
            try:
                context_dict = json.loads(context) if isinstance(context, str) and context else {}
            except json.JSONDecodeError:
                context_dict = {}
            
            # Set default context values
            context_dict.setdefault('platform', 'instagram')
            context_dict.setdefault('duration', 20)
            context_dict.setdefault('content_mode', 'music')
            
            # Auto-determine output folder if not provided
            if not output_folder:
                # Try to find current reel folder
                import os
                reel_folders = [d for d in os.listdir('reels') if d.startswith('reel_') and os.path.isdir(os.path.join('reels', d))]
                if reel_folders:
                    # Get the most recent reel folder
                    latest_folder = max(reel_folders, key=lambda x: os.path.getctime(os.path.join('reels', x)))
                    output_folder = os.path.join('reels', latest_folder, 'raw_clips')
                    # Ensure the raw_clips directory exists
                    os.makedirs(output_folder, exist_ok=True)
                else:
                    return json.dumps({
                        'video_generation_status': 'failed',
                        'error': 'No output folder specified and could not auto-detect reel folder'
                    })
            
            # Parse refined prompts data with robust handling
            refined_prompts = []
            try:
                refined_data = self._parse_refined_prompts_data(refined_prompts_data)
                
                # Extract refined prompts from parsed data
                if isinstance(refined_data, dict) and 'refined_prompts' in refined_data:
                    refined_prompts = refined_data['refined_prompts']
                elif isinstance(refined_data, list):
                    refined_prompts = refined_data
                elif isinstance(refined_data, dict):
                    # Check for alternative formats
                    if 'raw_result' in refined_data:
                        # Handle text format with parsing
                        refined_prompts = self._parse_text_prompts(refined_data['raw_result'])
                    else:
                        # Try to create prompts from dict structure
                        refined_prompts = self._dict_to_prompts(refined_data)
                else:
                    refined_prompts = []
                
                # Ensure we have at least one prompt
                if not refined_prompts:
                    refined_prompts = self._create_fallback_prompts(context_dict)
                    
            except Exception as e:
                print(f"⚠️  Error parsing refined prompts: {e}")
                # Create fallback prompts
                refined_prompts = self._create_fallback_prompts(context_dict)
            
            print(f"\n🎬 PHASE 4: Video Generation Starting")
            print(f"   📋 Processing {len(refined_prompts)} refined prompts")
            print(f"   📁 Output folder: {output_folder}")
            print(f"   🎯 Platform: {context_dict.get('platform', 'instagram')}")
            
            # Initialize video generator
            video_gen = VideoGenerator(output_folder)
            
            # Estimate costs before generation
            cost_estimate = video_gen.estimate_generation_cost(refined_prompts)
            print(f"   💰 Estimated cost: ${cost_estimate['total_estimated_cost']:.2f}")
            
            # Generate video clips
            generated_clips = video_gen.generate_video_clips(refined_prompts)
            
            # Analyze results
            successful_clips = [c for c in generated_clips if c['status'] in ['success', 'mock']]
            failed_clips = [c for c in generated_clips if c['status'] == 'failed']
            
            # Calculate actual costs
            total_cost = sum(c.get('cost_estimate', 0) for c in generated_clips)
            
            # Determine overall status
            if len(successful_clips) == len(generated_clips):
                overall_status = 'success'
            elif len(successful_clips) > 0:
                overall_status = 'partial'
            else:
                overall_status = 'failed'
            
            # Quality assessment
            valid_clips = [c for c in successful_clips if c.get('quality_check', {}).get('valid', False)]
            overall_quality_score = len(valid_clips) / len(generated_clips) if generated_clips else 0
            
            # Build comprehensive result
            result = {
                'video_generation_status': overall_status,
                'generated_clips': generated_clips,
                'generation_summary': {
                    'total_clips': len(generated_clips),
                    'successful_clips': len(successful_clips),
                    'failed_clips': len(failed_clips),
                    'total_cost': total_cost,
                    'average_cost_per_clip': total_cost / len(generated_clips) if generated_clips else 0,
                    'model_usage': cost_estimate['model_breakdown']
                },
                'quality_assessment': {
                    'overall_quality_score': overall_quality_score,
                    'technical_compliance': overall_quality_score > 0.8,
                    'all_clips_valid': len(valid_clips) == len(generated_clips),
                    'ready_for_synchronization': overall_status in ['success', 'partial'] and overall_quality_score > 0.7
                },
                'next_phase_data': {
                    'clips_folder': video_gen.clips_folder,
                    'clip_files': [c['filename'] for c in successful_clips if c.get('filename')],
                    'total_duration': context_dict.get('duration', 20),
                    'ready_for_phase_5': overall_status in ['success', 'partial']
                }
            }
            
            # Print summary
            print(f"\n🎯 VIDEO GENERATION COMPLETE!")
            print(f"   ✅ Success: {len(successful_clips)}/{len(generated_clips)} clips")
            print(f"   💰 Total cost: ${total_cost:.2f}")
            print(f"   📊 Quality score: {overall_quality_score:.2f}")
            print(f"   🚀 Ready for Phase 5: {result['quality_assessment']['ready_for_synchronization']}")
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                'video_generation_status': 'failed',
                'error': str(e),
                'message': f'Video generation failed: {str(e)}'
            }
            print(f"❌ Video generation error: {str(e)}")
            return json.dumps(error_result, indent=2)
    
    def _parse_refined_prompts_data(self, data: str) -> Any:
        """Parse refined prompts data with multiple format support"""
        if isinstance(data, str):
            # Try JSON parsing first
            try:
                json_match = re.search(r'\[.*\]|\{.*\}', data, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
            
            # Try Python dict format
            try:
                # Convert single quotes to double quotes for JSON compatibility
                json_str = re.sub(r"'([^']*)':", r'"\1":', data)
                json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
                return json.loads(json_str)
            except:
                pass
            
            # Return as text for further parsing
            return {'raw_result': data}
        else:
            return data
    
    def _parse_text_prompts(self, text: str) -> List[Dict]:
        """Extract prompts from text format"""
        prompts = []
        
        try:
            # Look for quoted prompts in the text
            prompt_matches = re.findall(r'"([^"]{20,})"', text)
            
            for i, prompt in enumerate(prompt_matches[:2]):  # Max 2 clips for demo
                # Extract quality prediction if present
                quality_pattern = rf'{re.escape(prompt)}.*?Quality Prediction:\s*([0-9.]+)'
                quality_match = re.search(quality_pattern, text, re.DOTALL)
                quality = float(quality_match.group(1)) if quality_match else 0.75
                
                # Extract model recommendation if present  
                model_pattern = rf'{re.escape(prompt)}.*?Recommended Model:\s*([a-zA-Z0-9-]+)'
                model_match = re.search(model_pattern, text, re.DOTALL)
                model = model_match.group(1).strip() if model_match else ('hailuo-02' if i == 0 else 'runway-gen3')
                
                prompts.append({
                    'scene_number': i + 1,
                    'enhanced_prompt': prompt,
                    'quality_prediction': quality,
                    'recommended_model': model,
                    'technical_params': {
                        'resolution': '1080x1920',
                        'duration': 7 if i == 0 else 8,
                        'style': 'cinematic'
                    }
                })
        except Exception as e:
            print(f"⚠️  Error parsing text prompts: {e}")
        
        return prompts
    
    def _dict_to_prompts(self, data: Dict) -> List[Dict]:
        """Convert various dict formats to prompts list"""
        prompts = []
        
        try:
            # Check for scene1, scene2 format
            scene_keys = [k for k in data.keys() if k.startswith('scene')]
            for scene_key in sorted(scene_keys):
                scene_data = data[scene_key]
                if isinstance(scene_data, dict):
                    prompts.append({
                        'scene_number': len(prompts) + 1,
                        'enhanced_prompt': scene_data.get('enhanced_prompt', 'Default prompt'),
                        'quality_prediction': scene_data.get('quality_prediction', 0.75),
                        'recommended_model': scene_data.get('recommended_model', 'hailuo-02'),
                        'technical_params': scene_data.get('technical_parameters', {
                            'resolution': '1080x1920',
                            'duration': 8,
                            'style': 'cinematic'
                        })
                    })
        except Exception as e:
            print(f"⚠️  Error converting dict to prompts: {e}")
        
        return prompts
    
    def _create_fallback_prompts(self, context: Dict) -> List[Dict]:
        """Create basic fallback prompts when parsing fails"""
        user_prompt = context.get('user_prompt', 'video content')
        
        return [
            {
                'scene_number': 1,
                'enhanced_prompt': f'High-quality cinematic {user_prompt}, professional lighting, smooth camera movement, 1080x1920 resolution',
                'quality_prediction': 0.75,
                'recommended_model': 'hailuo-02',
                'technical_params': {
                    'resolution': '1080x1920',
                    'duration': 10,
                    'style': 'cinematic'
                }
            }
        ]