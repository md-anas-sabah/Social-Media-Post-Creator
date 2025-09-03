"""
Helper functions for reel generation
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, Any


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds"""
    duration_map = {
        '15s': 15,
        '20s': 20,
        '30s': 30,
        '15': 15,
        '20': 20,
        '30': 30
    }
    
    return duration_map.get(duration_str.lower(), 20)


def create_unique_reel_folder(user_prompt: str, platform: str = 'instagram') -> tuple:
    """Create unique folder for reel output"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    prompt_slug = re.sub(r'[^\w\s-]', '', user_prompt.lower())
    prompt_slug = re.sub(r'\s+', '_', prompt_slug)[:20]
    
    folder_name = f"reel_{platform}_{prompt_slug}_{timestamp}"
    reel_folder = os.path.join(os.getcwd(), "reels", folder_name)
    os.makedirs(reel_folder, exist_ok=True)
    
    return reel_folder, timestamp


def save_reel_metadata(reel_folder: str, metadata: Dict[str, Any]) -> str:
    """Save reel generation metadata"""
    metadata_path = os.path.join(reel_folder, 'reel_metadata.json')
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata_path


def create_reel_summary(reel_folder: str, result_data: Dict) -> str:
    """Create human-readable summary"""
    summary_path = os.path.join(reel_folder, 'reel_summary.md')
    
    # Handle different phases
    phase = result_data.get('phase', 1)
    status = result_data.get('status', 'unknown')
    
    summary_content = f"""# Reel Generation Summary

## Generation Details
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **User Prompt**: {result_data.get('user_prompt', 'N/A')}
- **Platform**: {result_data.get('platform', 'N/A')}
- **Duration**: {result_data.get('duration', 'N/A')}s
- **Content Mode**: {result_data.get('content_mode', 'N/A')}
- **Current Phase**: {phase}
- **Status**: {status}

"""
    
    # Add phase-specific content
    if phase >= 2 and result_data.get('content_planning'):
        planning_data = result_data['content_planning']
        
        summary_content += """## Content Planning Results

### Content Analysis
"""
        
        if isinstance(planning_data, dict):
            content_analysis = planning_data.get('content_analysis', {})
            summary_content += f"""- **Category**: {content_analysis.get('category', 'N/A')}
- **Complexity Level**: {content_analysis.get('complexity_level', 'N/A')}
- **Target Audience**: {content_analysis.get('target_audience', 'N/A')}
- **Engagement Type**: {content_analysis.get('engagement_type', 'N/A')}

### Mode Selection
"""
            mode_selection = planning_data.get('mode_selection', {})
            summary_content += f"""- **Recommended Mode**: {mode_selection.get('recommended_mode', 'N/A')}
- **User Requested**: {mode_selection.get('user_requested', 'N/A')}
- **Rationale**: {mode_selection.get('rationale', 'N/A')}

### Storyboard
"""
            storyboard = planning_data.get('storyboard', {})
            summary_content += f"""- **Total Duration**: {storyboard.get('total_duration', 'N/A')}s
- **Scene Count**: {storyboard.get('scene_count', 'N/A')}

#### Scenes
"""
            scenes = storyboard.get('scenes', [])
            for scene in scenes:
                if isinstance(scene, dict):
                    summary_content += f"""
**Scene {scene.get('scene_number', 'N/A')}** ({scene.get('duration', 'N/A')}s)
- Title: {scene.get('title', 'N/A')}
- Description: {scene.get('description', 'N/A')}
- Key Message: {scene.get('key_message', 'N/A')}
- Technical Notes: {scene.get('technical_notes', 'N/A')}
"""

            summary_content += """
### Visual Style Guidelines
"""
            visual_style = planning_data.get('visual_style', {})
            summary_content += f"""- **Color Palette**: {visual_style.get('color_palette', 'N/A')}
- **Aesthetic Mood**: {visual_style.get('aesthetic_mood', 'N/A')}
- **Platform Optimization**: {visual_style.get('platform_optimization', 'N/A')}
- **Engagement Hooks**: {visual_style.get('engagement_hooks', 'N/A')}

### Success Metrics Prediction
"""
            success_metrics = planning_data.get('success_metrics', {})
            summary_content += f"""- **Engagement Prediction**: {success_metrics.get('engagement_prediction', 'N/A')}
- **Target Completion Rate**: {success_metrics.get('target_completion_rate', 'N/A')}
- **Key Performance Indicators**: {success_metrics.get('key_performance_indicators', 'N/A')}
"""
        else:
            summary_content += f"""
Raw planning result: {str(planning_data)[:500]}...
"""
    
    # Add file information
    summary_content += f"""
## Generated Files
- **Final Reel**: {result_data.get('final_reel_path', 'Not yet generated')}
- **Raw Clips**: {len(result_data.get('video_clips', []))} clips generated
- **Audio Files**: {len(result_data.get('audio_files', []))} audio files

## Quality Assessment
- **Overall Score**: {result_data.get('qa_score', 'N/A')}
- **QA Status**: {result_data.get('qa_status', 'N/A')}

## Next Steps
"""
    
    if phase == 2:
        summary_content += """- Phase 3: Claude Prompt Refinement
- Phase 4: Video Generation  
- Phase 5: Audio Generation
- Phase 6: Synchronization & Editing
- Phase 7: QA Testing & Reloop
- Phase 8: Integration & Testing
"""
    else:
        summary_content += f"""Current phase: {phase}
Next phase: {result_data.get('next_phase', 'TBD')}
"""
    
    summary_content += f"""
## Notes
{result_data.get('message', 'No additional notes')}
"""
    
    if result_data.get('error'):
        summary_content += f"""
## Error Information
{result_data.get('error')}
"""
    
    with open(summary_path, 'w') as f:
        f.write(summary_content)
    
    return summary_path


def create_reel_preview_html(reel_folder: str, reel_data: Dict) -> str:
    """Create HTML preview for the reel"""
    preview_path = os.path.join(reel_folder, 'reel_preview.html')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reel Preview - {reel_data.get('user_prompt', 'Generated Reel')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .reel-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .video-preview {{
            text-align: center;
            margin: 20px 0;
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="reel-container">
        <h1>🎬 Reel Preview</h1>
        
        <div class="metadata">
            <h3>Generation Details</h3>
            <p><strong>Prompt:</strong> {reel_data.get('user_prompt', 'N/A')}</p>
            <p><strong>Platform:</strong> {reel_data.get('platform', 'N/A')}</p>
            <p><strong>Duration:</strong> {reel_data.get('duration', 'N/A')}s</p>
            <p><strong>Mode:</strong> {reel_data.get('content_mode', 'N/A')}</p>
        </div>
        
        <div class="video-preview">
            <h3>Video Preview</h3>
            <p><em>Video player would be embedded here</em></p>
            <p>File: {reel_data.get('final_reel_path', 'N/A')}</p>
        </div>
        
        <div class="metadata">
            <h3>Quality Assessment</h3>
            <p><strong>Overall Score:</strong> {reel_data.get('qa_score', 'N/A')}</p>
            <p><strong>Status:</strong> {reel_data.get('qa_status', 'N/A')}</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(preview_path, 'w') as f:
        f.write(html_content)
    
    return preview_path


def analyze_content_category(user_prompt: str) -> str:
    """Analyze content category from user prompt"""
    prompt_lower = user_prompt.lower()
    
    # Educational/Tutorial keywords
    educational_keywords = ['tutorial', 'how to', 'learn', 'guide', 'tips', 'explain', 'teach', 'step', 'process']
    if any(keyword in prompt_lower for keyword in educational_keywords):
        return 'educational'
    
    # Fashion/Lifestyle keywords
    fashion_keywords = ['fashion', 'style', 'outfit', 'look', 'wear', 'trend', 'clothing', 'brand showcase']
    if any(keyword in prompt_lower for keyword in fashion_keywords):
        return 'fashion'
    
    # Food/Cooking keywords
    food_keywords = ['food', 'cooking', 'recipe', 'kitchen', 'meal', 'dish', 'ingredient', 'restaurant']
    if any(keyword in prompt_lower for keyword in food_keywords):
        return 'food'
    
    # Fitness/Health keywords
    fitness_keywords = ['fitness', 'workout', 'exercise', 'health', 'gym', 'training', 'motivation']
    if any(keyword in prompt_lower for keyword in fitness_keywords):
        return 'fitness'
    
    # Business/Professional keywords
    business_keywords = ['business', 'professional', 'corporate', 'startup', 'marketing', 'sales']
    if any(keyword in prompt_lower for keyword in business_keywords):
        return 'business'
    
    return 'lifestyle'


def suggest_content_mode(content_category: str, user_prompt: str) -> tuple:
    """Suggest optimal content mode based on category and complexity"""
    prompt_lower = user_prompt.lower()
    
    # Force narration for educational content
    if content_category == 'educational':
        return 'narration', 'Educational content benefits from clear explanations'
    
    # Visual-focused content works better with music (check before complex keywords)
    visual_keywords = ['showcase', 'display', 'show', 'reveal', 'transformation', 'before/after', 'brand']
    if any(keyword in prompt_lower for keyword in visual_keywords):
        return 'music', 'Visual storytelling is enhanced by background music'
    
    # Complex explanations need narration (excluding visual keywords above)
    complex_keywords = ['explain', 'why', 'how', 'process', 'method', 'technique', 'analysis', 'tutorial']
    if any(keyword in prompt_lower for keyword in complex_keywords):
        return 'narration', 'Complex topics require verbal explanation for clarity'
    
    # Default suggestions by category
    category_modes = {
        'fashion': ('music', 'Fashion content is highly visual and benefits from music'),
        'food': ('music', 'Food visuals are enhanced by atmospheric music'),
        'fitness': ('music', 'Fitness content works well with energetic background music'),
        'business': ('narration', 'Business content often requires clear communication'),
        'lifestyle': ('music', 'Lifestyle content benefits from mood-setting music')
    }
    
    return category_modes.get(content_category, ('music', 'Default visual storytelling approach'))


def calculate_scene_timing(duration: int, scene_count: int = None) -> list:
    """Calculate optimal scene timing based on total duration"""
    if scene_count is None:
        # Auto-determine scene count based on duration
        if duration <= 15:
            scene_count = 2
        else:
            scene_count = 3
    
    if scene_count == 2:
        # Two scenes: slightly longer first scene
        return [int(duration * 0.55), duration - int(duration * 0.55)]
    elif scene_count == 3:
        # Three scenes: more evenly distributed
        base_duration = duration // 3
        remainder = duration % 3
        scenes = [base_duration] * 3
        
        # Distribute remainder: first scene gets extra, then last scene
        if remainder > 0:
            scenes[0] += 1
            remainder -= 1
        if remainder > 0:
            scenes[2] += 1
            
        return scenes
    
    # Fallback for other scene counts
    base_duration = duration // scene_count
    remainder = duration % scene_count
    scenes = [base_duration] * scene_count
    
    # Distribute remainder evenly
    for i in range(remainder):
        scenes[i] += 1
    
    return scenes


def get_platform_specifications(platform: str) -> Dict[str, Any]:
    """Get platform-specific requirements and recommendations"""
    specs = {
        'instagram': {
            'aspect_ratio': '9:16',
            'resolution': '1080x1920',
            'max_duration': 30,
            'optimal_durations': [15, 20, 30],
            'trending_styles': ['fast cuts', 'smooth transitions', 'text overlays'],
            'engagement_hooks': ['strong opening', 'trending audio', 'visual hooks']
        },
        'tiktok': {
            'aspect_ratio': '9:16',
            'resolution': '1080x1920',
            'max_duration': 30,
            'optimal_durations': [15, 20],
            'trending_styles': ['quick cuts', 'trending effects', 'text-heavy'],
            'engagement_hooks': ['immediate action', 'trending sounds', 'challenges']
        },
        'facebook': {
            'aspect_ratio': '9:16',
            'resolution': '1080x1920',
            'max_duration': 30,
            'optimal_durations': [15, 20, 30],
            'trending_styles': ['storytelling', 'lifestyle', 'informational'],
            'engagement_hooks': ['relatable content', 'emotional connection', 'shareable']
        }
    }
    
    return specs.get(platform.lower(), specs['instagram'])


def validate_environment():
    """Check if required dependencies and API keys are configured"""
    from decouple import config
    
    validation_results = {
        'openai_api_key': bool(config('OPENAI_API_KEY', default='')),
        'fal_key': bool(config('FAL_KEY', default='')),
        'claude_api_key': bool(config('CLAUDE_API_KEY', default='')),
        'elevenlabs_api_key': bool(config('ELEVENLABS_API_KEY', default=''))
    }
    
    # Check for required Python packages
    try:
        import moviepy
        validation_results['moviepy'] = True
    except ImportError:
        validation_results['moviepy'] = False
    
    try:
        import fal_client
        validation_results['fal_client'] = True
    except ImportError:
        validation_results['fal_client'] = False
    
    return validation_results