"""
Video generation prompt templates for different content types
"""

VIDEO_PROMPT_TEMPLATES = {
    'fashion': {
        'base_prompt': "High-quality fashion video showcasing {subject} in {setting}",
        'style_modifiers': ["cinematic lighting", "professional photography", "vibrant colors"],
        'technical_specs': "1080x1920 vertical format, 24fps, high definition"
    },
    
    'cooking': {
        'base_prompt': "Professional cooking video showing {process} with {ingredients}",
        'style_modifiers': ["appetizing close-ups", "warm lighting", "detailed textures"],
        'technical_specs': "1080x1920 vertical format, 30fps, food photography style"
    },
    
    'fitness': {
        'base_prompt': "Dynamic fitness video demonstrating {exercise} in {environment}",
        'style_modifiers': ["energetic movement", "motivational atmosphere", "clear instruction"],
        'technical_specs': "1080x1920 vertical format, 30fps, action-focused"
    },
    
    'travel': {
        'base_prompt': "Stunning travel video showcasing {destination} with {activities}",
        'style_modifiers': ["breathtaking scenery", "adventure feeling", "cultural authenticity"],
        'technical_specs': "1080x1920 vertical format, 24fps, travel documentary style"
    },
    
    'education': {
        'base_prompt': "Educational video explaining {concept} with {visual_aids}",
        'style_modifiers': ["clear visualization", "engaging graphics", "professional presentation"],
        'technical_specs': "1080x1920 vertical format, 30fps, educational style"
    },
    
    'business': {
        'base_prompt': "Professional business video presenting {topic} in {context}",
        'style_modifiers': ["corporate aesthetic", "trustworthy appearance", "modern design"],
        'technical_specs': "1080x1920 vertical format, 24fps, business presentation style"
    },
    
    'lifestyle': {
        'base_prompt': "Lifestyle video featuring {activity} in {setting}",
        'style_modifiers': ["natural lighting", "authentic moments", "aspirational quality"],
        'technical_specs': "1080x1920 vertical format, 24fps, lifestyle content style"
    },
    
    'technology': {
        'base_prompt': "Tech video demonstrating {product} with {features}",
        'style_modifiers': ["sleek design", "futuristic elements", "clear demonstrations"],
        'technical_specs': "1080x1920 vertical format, 30fps, tech review style"
    }
}

QUALITY_MODIFIERS = [
    "ultra high quality",
    "professional cinematography", 
    "perfect composition",
    "sharp focus",
    "vibrant colors",
    "excellent lighting",
    "smooth motion",
    "engaging visuals"
]

PLATFORM_OPTIMIZATIONS = {
    'instagram': {
        'aspect_ratio': "1080x1920",
        'duration_preference': "15-30 seconds",
        'style_focus': "visually striking, fast-paced",
        'engagement_elements': ["hook within first 3 seconds", "clear call-to-action"]
    },
    
    'tiktok': {
        'aspect_ratio': "1080x1920", 
        'duration_preference': "15-60 seconds",
        'style_focus': "trending, authentic, entertaining",
        'engagement_elements': ["trending audio", "quick cuts", "viral potential"]
    },
    
    'facebook': {
        'aspect_ratio': "1080x1920",
        'duration_preference': "15-90 seconds", 
        'style_focus': "informative, shareable",
        'engagement_elements': ["clear storytelling", "emotional connection"]
    }
}


def get_video_prompt_template(content_type: str, platform: str = 'instagram') -> dict:
    """Get optimized video prompt template for content type and platform"""
    
    # Get base template or use generic
    template = VIDEO_PROMPT_TEMPLATES.get(content_type.lower(), {
        'base_prompt': f"High-quality {content_type} video with engaging visuals",
        'style_modifiers': ["professional quality", "engaging content"],
        'technical_specs': "1080x1920 vertical format, 30fps"
    })
    
    # Add platform optimizations
    platform_opts = PLATFORM_OPTIMIZATIONS.get(platform.lower(), PLATFORM_OPTIMIZATIONS['instagram'])
    
    return {
        **template,
        'platform_optimization': platform_opts,
        'quality_modifiers': QUALITY_MODIFIERS
    }


def build_enhanced_prompt(base_prompt: str, content_data: dict, platform: str = 'instagram') -> str:
    """Build enhanced video generation prompt"""
    
    # Start with base prompt
    enhanced_prompt = base_prompt
    
    # Add quality modifiers
    quality_additions = ", ".join(QUALITY_MODIFIERS[:4])  # Use top 4 quality modifiers
    enhanced_prompt += f", {quality_additions}"
    
    # Add platform-specific optimizations
    platform_opts = PLATFORM_OPTIMIZATIONS.get(platform.lower(), PLATFORM_OPTIMIZATIONS['instagram'])
    enhanced_prompt += f", {platform_opts['style_focus']}"
    
    # Add technical specifications
    enhanced_prompt += f", {platform_opts['aspect_ratio']} format"
    
    return enhanced_prompt