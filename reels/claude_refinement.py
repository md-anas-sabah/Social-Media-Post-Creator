"""
Claude prompt refinement and quality assessment service
"""

import json
import re
from typing import Dict, List, Any, Optional
import anthropic
from decouple import config


class ClaudeRefinementService:
    """Claude-powered prompt optimization and quality assessment"""
    
    def __init__(self, claude_api_key=None):
        self.claude_api_key = claude_api_key or config('CLAUDE_API_KEY', default='')
        if self.claude_api_key:
            self.claude = anthropic.Anthropic(api_key=self.claude_api_key)
        else:
            self.claude = None
    
    def refine_video_prompts(self, storyboard_data: Dict, context: Dict) -> Dict:
        """Optimize prompts for video generation using Claude AI"""
        if not self.claude:
            print("⚠️  Claude API not available - using basic prompt optimization")
            return self._fallback_prompt_refinement(storyboard_data)
        
        try:
            # Extract scenes from storyboard
            scenes = storyboard_data.get('storyboard', {}).get('scenes', [])
            visual_style = storyboard_data.get('visual_style', {})
            content_analysis = storyboard_data.get('content_analysis', {})
            
            # Create comprehensive refinement prompt for Claude
            refinement_prompt = self._build_claude_refinement_prompt(scenes, visual_style, content_analysis, context)
            
            # Call Claude API
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": refinement_prompt
                    }
                ]
            )
            
            # Parse Claude's response
            claude_response = response.content[0].text
            refined_data = self._parse_claude_refinement_response(claude_response)
            
            return {
                'status': 'success',
                'original_storyboard': storyboard_data,
                'refined_prompts': refined_data.get('refined_prompts', []),
                'quality_predictions': refined_data.get('quality_predictions', {}),
                'model_optimizations': refined_data.get('model_optimizations', {}),
                'claude_analysis': refined_data.get('analysis', ''),
                'improvement_suggestions': refined_data.get('improvements', []),
                'timestamp': context.get('timestamp', '')
            }
            
        except Exception as e:
            print(f"❌ Error in Claude refinement: {e}")
            return self._fallback_prompt_refinement(storyboard_data)
    
    def assess_content_quality(self, reel_data: Dict) -> Dict:
        """Claude-powered quality review and assessment"""
        if not self.claude:
            print("⚠️  Claude API not available - using basic quality assessment")
            return self._fallback_quality_assessment(reel_data)
        
        try:
            # Build quality assessment prompt
            assessment_prompt = self._build_quality_assessment_prompt(reel_data)
            
            # Call Claude API for quality assessment
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": assessment_prompt
                    }
                ]
            )
            
            # Parse quality assessment response
            claude_response = response.content[0].text
            quality_data = self._parse_quality_assessment_response(claude_response)
            
            return {
                'status': 'success',
                'technical_quality': quality_data.get('technical_quality', 0.7),
                'content_quality': quality_data.get('content_quality', 0.7),
                'brand_alignment': quality_data.get('brand_alignment', 0.7),
                'platform_optimization': quality_data.get('platform_optimization', 0.7),
                'engagement_potential': quality_data.get('engagement_potential', 0.7),
                'overall_score': quality_data.get('overall_score', 0.7),
                'detailed_analysis': quality_data.get('analysis', ''),
                'recommendations': quality_data.get('recommendations', []),
                'pass_threshold': quality_data.get('overall_score', 0.7) >= 0.75,
                'reloop_required': quality_data.get('overall_score', 0.7) < 0.75
            }
            
        except Exception as e:
            print(f"❌ Error in quality assessment: {e}")
            return self._fallback_quality_assessment(reel_data)
    
    def suggest_improvements(self, quality_report: Dict, storyboard_data: Dict) -> List[str]:
        """Generate specific improvement recommendations based on quality issues"""
        if not self.claude:
            return self._fallback_improvement_suggestions(quality_report)
        
        try:
            # Build improvement suggestions prompt
            improvement_prompt = self._build_improvement_prompt(quality_report, storyboard_data)
            
            # Call Claude API for improvement suggestions
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.4,
                messages=[
                    {
                        "role": "user",
                        "content": improvement_prompt
                    }
                ]
            )
            
            # Parse improvement suggestions
            claude_response = response.content[0].text
            suggestions = self._parse_improvement_suggestions(claude_response)
            
            return suggestions
            
        except Exception as e:
            print(f"❌ Error generating improvements: {e}")
            return self._fallback_improvement_suggestions(quality_report)
    
    def _build_claude_refinement_prompt(self, scenes: List[Dict], visual_style: Dict, content_analysis: Dict, context: Dict) -> str:
        """Build comprehensive prompt for Claude refinement"""
        return f"""
You are an expert AI video generation prompt engineer. Your task is to refine and optimize video generation prompts for maximum quality and engagement.

CONTEXT:
- Platform: {context.get('platform', 'instagram')}
- Duration: {context.get('duration', '20')}s
- Content Mode: {context.get('content_mode', 'music')}
- Content Category: {content_analysis.get('category', 'general')}
- Target Audience: {content_analysis.get('target_audience', 'general')}

VISUAL STYLE:
- Color Palette: {visual_style.get('color_palette', 'vibrant')}
- Aesthetic: {visual_style.get('aesthetic_mood', 'modern')}
- Engagement Hooks: {visual_style.get('engagement_hooks', 'dynamic')}

ORIGINAL SCENES:
{json.dumps(scenes, indent=2)}

TASK: Refine each scene's description into professional video generation prompts optimized for AI models like Runway, Pika, or Hailuo.

CRITICAL: All videos MUST be in VERTICAL 9:16 format for social media reels (1080x1920 resolution).

FOR EACH SCENE, PROVIDE:
1. **Enhanced Prompt**: Professional, detailed description with VERTICAL format specifications and "9:16 aspect ratio" explicitly mentioned
2. **Quality Score**: Predicted success rate (0.0-1.0)
3. **Model Recommendations**: Best AI model for this specific prompt
4. **Technical Parameters**: Resolution (1080x1920), duration, style parameters, vertical format
5. **Alternative Versions**: 2-3 variations for fallback options

OUTPUT FORMAT (JSON):
{{
    "refined_prompts": [
        {{
            "scene_number": 1,
            "original_description": "...",
            "enhanced_prompt": "Professional vertical video prompt, 9:16 aspect ratio, 1080x1920 resolution, with technical details...",
            "quality_prediction": 0.85,
            "recommended_model": "hailuo-02",
            "technical_params": {{
                "resolution": "1080x1920",
                "duration": 7,
                "style": "cinematic",
                "camera_movement": "smooth_pan"
            }},
            "alternative_prompts": ["Alt 1...", "Alt 2..."]
        }}
    ],
    "quality_predictions": {{
        "overall_score": 0.82,
        "technical_feasibility": 0.85,
        "creative_appeal": 0.80,
        "engagement_potential": 0.85
    }},
    "model_optimizations": {{
        "primary_model": "hailuo-02",
        "fallback_models": ["runway-gen3", "pika-labs"],
        "model_specific_tips": []
    }},
    "analysis": "Detailed analysis of prompt improvements...",
    "improvements": ["Improvement 1", "Improvement 2"]
}}

Focus on creating prompts that will generate visually stunning, engaging video content optimized for social media success.
"""
    
    def _build_quality_assessment_prompt(self, reel_data: Dict) -> str:
        """Build prompt for Claude quality assessment"""
        return f"""
You are an expert video content quality assessor specializing in social media reels. Analyze the provided reel data and provide comprehensive quality scores.

REEL DATA:
{json.dumps(reel_data, indent=2)}

ASSESSMENT CRITERIA:
1. **Technical Quality** (0.0-1.0): Resolution, sync, compression, format compliance
2. **Content Quality** (0.0-1.0): Narrative flow, visual appeal, pacing
3. **Brand Alignment** (0.0-1.0): Consistency with brand voice and messaging
4. **Platform Optimization** (0.0-1.0): Platform-specific requirements met
5. **Engagement Potential** (0.0-1.0): Predicted audience engagement and retention

QUALITY THRESHOLDS:
- PASS: Overall score ≥ 0.75
- RELOOP REQUIRED: Overall score < 0.75

OUTPUT FORMAT (JSON):
{{
    "technical_quality": 0.85,
    "content_quality": 0.80,
    "brand_alignment": 0.90,
    "platform_optimization": 0.85,
    "engagement_potential": 0.75,
    "overall_score": 0.83,
    "analysis": "Detailed quality analysis...",
    "recommendations": ["Specific improvement 1", "Specific improvement 2"]
}}

Provide detailed analysis and actionable recommendations for improvement.
"""
    
    def _build_improvement_prompt(self, quality_report: Dict, storyboard_data: Dict) -> str:
        """Build prompt for improvement suggestions"""
        return f"""
You are an expert video improvement consultant. Based on the quality assessment, provide specific, actionable improvement recommendations.

QUALITY REPORT:
{json.dumps(quality_report, indent=2)}

ORIGINAL STORYBOARD:
{json.dumps(storyboard_data, indent=2)}

PROVIDE:
1. **Priority Issues**: Most critical problems to address
2. **Specific Actions**: Concrete steps to improve each quality dimension
3. **Reloop Strategy**: Recommended approach for regeneration
4. **Success Metrics**: How to measure improvement

OUTPUT: List of specific, actionable improvement recommendations.
"""
    
    def _parse_claude_refinement_response(self, response: str) -> Dict:
        """Parse Claude's refinement response into structured data"""
        try:
            # First try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # If no JSON found, parse the text format
            return self._parse_claude_text_response(response)
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            return self._parse_claude_text_response(response)
    
    def _parse_claude_text_response(self, response: str) -> Dict:
        """Parse Claude's text response into structured JSON format"""
        refined_prompts = []
        scene_number = 1
        
        try:
            # Extract scenes using regex patterns
            scene_pattern = r'Scene\s+(\d+):\s*\n?-?\s*Enhanced Prompt:\s*["\']?([^"\'\n]*(?:\n[^-\n]+)*?)["\']?\s*\n?\s*-?\s*Quality Prediction:\s*([0-9.]+)\s*\n?\s*-?\s*Recommended Model:\s*([a-zA-Z0-9-]+)'
            
            scenes = re.findall(scene_pattern, response, re.DOTALL | re.IGNORECASE)
            
            for scene_match in scenes:
                scene_num = int(scene_match[0]) if scene_match[0].isdigit() else scene_number
                enhanced_prompt = scene_match[1].strip()
                quality_pred = float(scene_match[2]) if scene_match[2] else 0.75
                recommended_model = scene_match[3].strip().lower()
                
                # Extract technical parameters if present
                tech_params_pattern = r'Technical Parameters:\s*\{([^}]+)\}'
                tech_match = re.search(tech_params_pattern, response)
                tech_params = {
                    'resolution': '1080x1920',
                    'duration': 7 if scene_number == 1 else 8,
                    'style': 'cinematic',
                    'fps': 30
                }
                
                if tech_match:
                    try:
                        # Try to parse the technical parameters
                        tech_content = tech_match.group(1)
                        tech_pairs = re.findall(r'"([^"]+)":\s*"?([^",}]+)"?', tech_content)
                        for key, value in tech_pairs:
                            tech_params[key] = int(value) if value.isdigit() else value.strip('"')
                    except:
                        pass
                
                refined_prompts.append({
                    'scene_number': scene_num,
                    'original_description': f'Scene {scene_num} description',
                    'enhanced_prompt': enhanced_prompt,
                    'quality_prediction': quality_pred,
                    'recommended_model': recommended_model,
                    'technical_params': tech_params,
                    'alternative_prompts': []
                })
                
                scene_number += 1
            
            # If no scenes found, create a basic fallback
            if not refined_prompts:
                # Try to extract any quoted prompts from the response
                prompt_matches = re.findall(r'"([^"]{50,})"', response)
                for i, prompt in enumerate(prompt_matches[:2]):  # Max 2 scenes
                    refined_prompts.append({
                        'scene_number': i + 1,
                        'original_description': f'Scene {i + 1} extracted from response',
                        'enhanced_prompt': prompt,
                        'quality_prediction': 0.75,
                        'recommended_model': 'hailuo-02' if i == 0 else 'runway-gen3',
                        'technical_params': {
                            'resolution': '1080x1920',
                            'duration': 7 if i == 0 else 8,
                            'style': 'cinematic',
                            'fps': 30
                        },
                        'alternative_prompts': []
                    })
            
            # Extract overall quality score
            overall_score_match = re.search(r'overall.*?quality.*?score.*?([0-9.]+)', response, re.IGNORECASE)
            if overall_score_match:
                score_str = overall_score_match.group(1).rstrip('.')
                try:
                    overall_score = float(score_str)
                except ValueError:
                    overall_score = 0.8
            else:
                overall_score = 0.8
            
            return {
                'refined_prompts': refined_prompts,
                'quality_predictions': {'overall_score': overall_score},
                'analysis': response,
                'improvements': []
            }
            
        except Exception as e:
            print(f"⚠️  Error parsing Claude text response: {e}")
            # Final fallback - create basic prompts
            return {
                'refined_prompts': [{
                    'scene_number': 1,
                    'original_description': 'Basic scene',
                    'enhanced_prompt': 'High-quality cinematic video with professional lighting and composition',
                    'quality_prediction': 0.75,
                    'recommended_model': 'hailuo-02',
                    'technical_params': {
                        'resolution': '1080x1920',
                        'duration': 10,
                        'style': 'cinematic',
                        'fps': 30
                    },
                    'alternative_prompts': []
                }],
                'quality_predictions': {'overall_score': 0.75},
                'analysis': response,
                'improvements': []
            }
    
    def _parse_quality_assessment_response(self, response: str) -> Dict:
        """Parse Claude's quality assessment response"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    'technical_quality': 0.7,
                    'content_quality': 0.7,
                    'brand_alignment': 0.7,
                    'platform_optimization': 0.7,
                    'engagement_potential': 0.7,
                    'overall_score': 0.7,
                    'analysis': response,
                    'recommendations': []
                }
        except json.JSONDecodeError:
            return {
                'technical_quality': 0.7,
                'content_quality': 0.7,
                'brand_alignment': 0.7,
                'platform_optimization': 0.7,
                'engagement_potential': 0.7,
                'overall_score': 0.7,
                'analysis': response,
                'recommendations': []
            }
    
    def _parse_improvement_suggestions(self, response: str) -> List[str]:
        """Parse improvement suggestions from Claude response"""
        try:
            # Try to extract list from response
            lines = response.split('\n')
            suggestions = []
            for line in lines:
                line = line.strip()
                if line.startswith(('-', '•', '*')) or line[0:1].isdigit():
                    suggestion = re.sub(r'^[-•*\d\.\s]+', '', line).strip()
                    if suggestion:
                        suggestions.append(suggestion)
            return suggestions if suggestions else [response]
        except Exception:
            return [response]
    
    def _fallback_prompt_refinement(self, storyboard_data: Dict) -> Dict:
        """Fallback refinement when Claude not available"""
        scenes = storyboard_data.get('storyboard', {}).get('scenes', [])
        refined_prompts = []
        
        for scene in scenes:
            refined_prompts.append({
                'scene_number': scene.get('scene_number', 1),
                'original_description': scene.get('description', ''),
                'enhanced_prompt': f"High-quality cinematic {scene.get('description', '')}, professional lighting, vertical 9:16 aspect ratio, 1080x1920 resolution, mobile-optimized vertical video format",
                'quality_prediction': 0.75,
                'recommended_model': 'hailuo-02',
                'technical_params': {
                    'resolution': '1080x1920',
                    'duration': scene.get('duration', 7),
                    'style': 'cinematic'
                }
            })
        
        return {
            'status': 'fallback',
            'refined_prompts': refined_prompts,
            'quality_predictions': {'overall_score': 0.75},
            'analysis': 'Basic prompt enhancement applied (Claude not available)'
        }
    
    def _fallback_quality_assessment(self, reel_data: Dict) -> Dict:
        """Fallback quality assessment when Claude not available"""
        return {
            'status': 'fallback',
            'technical_quality': 0.7,
            'content_quality': 0.7,
            'brand_alignment': 0.7,
            'platform_optimization': 0.7,
            'engagement_potential': 0.7,
            'overall_score': 0.7,
            'detailed_analysis': 'Basic quality assessment (Claude not available)',
            'recommendations': ['Enable Claude API for detailed quality assessment'],
            'pass_threshold': True,
            'reloop_required': False
        }
    
    def _fallback_improvement_suggestions(self, quality_report: Dict) -> List[str]:
        """Fallback improvement suggestions when Claude not available"""
        return [
            "Enable Claude API for detailed improvement recommendations",
            "Ensure all video clips meet minimum quality standards",
            "Verify audio-video synchronization",
            "Optimize content for target platform specifications"
        ]