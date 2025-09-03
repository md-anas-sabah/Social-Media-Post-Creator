"""
Audio generation prompt templates for narration and music
"""

NARRATION_TEMPLATES = {
    'educational': {
        'voice_style': "clear, professional, engaging teacher voice",
        'pacing': "moderate, with natural pauses for emphasis",
        'tone': "informative yet friendly, encouraging learning"
    },
    
    'tutorial': {
        'voice_style': "helpful, step-by-step instruction voice",
        'pacing': "slow to moderate, allowing time to follow along", 
        'tone': "patient, supportive, encouraging"
    },
    
    'promotional': {
        'voice_style': "confident, persuasive sales voice",
        'pacing': "energetic, with strategic emphasis",
        'tone': "exciting, trustworthy, compelling"
    },
    
    'storytelling': {
        'voice_style': "engaging narrator voice with emotional range",
        'pacing': "varied pace to match story rhythm",
        'tone': "captivating, expressive, immersive"
    },
    
    'documentary': {
        'voice_style': "authoritative documentary narrator voice",
        'pacing': "steady, professional cadence",
        'tone': "informative, trustworthy, neutral"
    }
}

MUSIC_TEMPLATES = {
    'upbeat': {
        'genre': "energetic pop or electronic music",
        'mood': "positive, motivating, uplifting",
        'tempo': "120-140 BPM, driving rhythm",
        'instruments': "synthesizers, drums, bass, upbeat melodies"
    },
    
    'chill': {
        'genre': "ambient, lo-fi, or chill electronic",
        'mood': "relaxed, peaceful, contemplative", 
        'tempo': "70-90 BPM, laid-back groove",
        'instruments': "soft synths, gentle percussion, atmospheric pads"
    },
    
    'dramatic': {
        'genre': "cinematic orchestral or electronic",
        'mood': "intense, emotional, powerful",
        'tempo': "90-120 BPM, building intensity", 
        'instruments': "strings, brass, powerful drums, epic melodies"
    },
    
    'corporate': {
        'genre': "professional, inspiring background music",
        'mood': "confident, trustworthy, modern",
        'tempo': "100-120 BPM, steady progression",
        'instruments': "piano, strings, light percussion, corporate feel"
    },
    
    'trendy': {
        'genre': "current popular music style",
        'mood': "fashionable, contemporary, catchy",
        'tempo': "100-130 BPM, social media friendly",
        'instruments': "modern production, trending sounds, viral-ready"
    }
}

TTS_VOICE_OPTIONS = {
    'professional_female': {
        'description': "Professional female voice, clear and authoritative",
        'use_cases': ["business", "educational", "tutorial"]
    },
    
    'professional_male': {
        'description': "Professional male voice, confident and trustworthy", 
        'use_cases': ["documentary", "corporate", "informational"]
    },
    
    'friendly_female': {
        'description': "Warm, approachable female voice",
        'use_cases': ["lifestyle", "tutorial", "conversational"]
    },
    
    'friendly_male': {
        'description': "Casual, relatable male voice",
        'use_cases': ["storytelling", "casual tutorials", "personal content"]
    },
    
    'energetic_female': {
        'description': "Upbeat, enthusiastic female voice",
        'use_cases': ["fitness", "motivational", "promotional"]
    },
    
    'energetic_male': {
        'description': "Dynamic, motivating male voice", 
        'use_cases': ["sports", "fitness", "high-energy content"]
    }
}


def get_narration_script_template(content_type: str, key_points: list, duration: int) -> str:
    """Generate narration script template based on content"""
    
    # Calculate words per minute (average 150 WPM for narration)
    target_words = int((duration / 60) * 150)
    
    script_template = f"""
NARRATION SCRIPT - {content_type.upper()}
Target Duration: {duration} seconds
Target Words: ~{target_words} words

OPENING HOOK (3-5 seconds):
[Attention-grabbing opening statement]

MAIN CONTENT ({duration-8} seconds):
"""
    
    # Add key points structure
    for i, point in enumerate(key_points[:3]):  # Limit to 3 main points
        script_template += f"\nPOINT {i+1}: {point}\n[Detailed explanation - ~{target_words//len(key_points[:3])} words]\n"
    
    script_template += f"""
CLOSING/CTA (3-5 seconds):
[Strong closing statement or call-to-action]

VOICE DIRECTION:
- Tone: {NARRATION_TEMPLATES.get(content_type, NARRATION_TEMPLATES['educational'])['tone']}
- Pacing: {NARRATION_TEMPLATES.get(content_type, NARRATION_TEMPLATES['educational'])['pacing']} 
- Style: {NARRATION_TEMPLATES.get(content_type, NARRATION_TEMPLATES['educational'])['voice_style']}
"""
    
    return script_template


def get_music_prompt(content_theme: str, duration: int, platform: str = 'instagram') -> str:
    """Generate music generation prompt"""
    
    # Determine music style based on content theme
    if any(word in content_theme.lower() for word in ['fitness', 'workout', 'energy', 'motivation']):
        music_style = 'upbeat'
    elif any(word in content_theme.lower() for word in ['business', 'corporate', 'professional']):
        music_style = 'corporate'  
    elif any(word in content_theme.lower() for word in ['fashion', 'lifestyle', 'trendy']):
        music_style = 'trendy'
    elif any(word in content_theme.lower() for word in ['dramatic', 'story', 'emotional']):
        music_style = 'dramatic'
    else:
        music_style = 'chill'
    
    template = MUSIC_TEMPLATES[music_style]
    
    music_prompt = f"""
Generate {duration}-second background music track:

STYLE: {template['genre']}
MOOD: {template['mood']}
TEMPO: {template['tempo']}
INSTRUMENTS: {template['instruments']}

PLATFORM OPTIMIZATION: {platform}
- Suitable for social media consumption
- Clear audio quality for mobile speakers
- Engaging but not overpowering visuals
- Trending audio potential

TECHNICAL REQUIREMENTS:
- Duration: exactly {duration} seconds
- Format: MP3, high quality
- Volume: Balanced for background use
- Loop capability: Seamless if needed
"""
    
    return music_prompt


def determine_content_mode(user_prompt: str) -> str:
    """Analyze prompt to determine if narration or music mode is better"""
    
    # Keywords that suggest narration mode
    narration_keywords = [
        'tutorial', 'how to', 'explain', 'teach', 'learn', 'guide', 
        'instruction', 'tips', 'advice', 'review', 'documentary',
        'educational', 'informational', 'demonstrate'
    ]
    
    # Keywords that suggest music mode  
    music_keywords = [
        'showcase', 'fashion', 'lifestyle', 'aesthetic', 'visual',
        'montage', 'compilation', 'artistic', 'cinematic', 'mood',
        'atmosphere', 'vibe', 'style', 'beauty', 'travel'
    ]
    
    prompt_lower = user_prompt.lower()
    
    narration_score = sum(1 for keyword in narration_keywords if keyword in prompt_lower)
    music_score = sum(1 for keyword in music_keywords if keyword in prompt_lower)
    
    if narration_score > music_score:
        return 'narration'
    elif music_score > narration_score:
        return 'music'
    else:
        # Default to music for social media content
        return 'music'


def get_recommended_voice(content_type: str, gender_preference: str = 'auto') -> dict:
    """Get recommended TTS voice based on content type"""
    
    voice_recommendations = {
        'educational': ['professional_female', 'professional_male'],
        'tutorial': ['friendly_female', 'friendly_male'],
        'business': ['professional_male', 'professional_female'],
        'fitness': ['energetic_female', 'energetic_male'],
        'lifestyle': ['friendly_female', 'friendly_male'],
        'documentary': ['professional_male', 'professional_female']
    }
    
    recommended_voices = voice_recommendations.get(content_type, ['friendly_female', 'friendly_male'])
    
    if gender_preference == 'female':
        recommended_voices = [v for v in recommended_voices if 'female' in v]
    elif gender_preference == 'male':
        recommended_voices = [v for v in recommended_voices if 'male' in v]
    
    primary_voice = recommended_voices[0] if recommended_voices else 'friendly_female'
    
    return TTS_VOICE_OPTIONS[primary_voice]