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
    
    summary_content = f"""# Reel Generation Summary

## Generation Details
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **User Prompt**: {result_data.get('user_prompt', 'N/A')}
- **Platform**: {result_data.get('platform', 'N/A')}
- **Duration**: {result_data.get('duration', 'N/A')}s
- **Content Mode**: {result_data.get('content_mode', 'N/A')}

## Generated Files
- **Final Reel**: {result_data.get('final_reel_path', 'N/A')}
- **Raw Clips**: {len(result_data.get('video_clips', []))} clips generated
- **Audio Files**: {len(result_data.get('audio_files', []))} audio files

## Quality Assessment
- **Overall Score**: {result_data.get('qa_score', 'N/A')}
- **Status**: {result_data.get('qa_status', 'N/A')}

## Notes
{result_data.get('notes', 'No additional notes')}
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