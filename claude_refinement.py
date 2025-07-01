from anthropic import Anthropic
from decouple import config
import json
from typing import Dict, Any, List


class ClaudeRefinementService:
    def __init__(self):
        self.client = Anthropic(api_key=config('CLAUDE_API_KEY'))
    
    def refine_image_prompt(self, original_prompt: str, content_context: str = "", platform: str = "instagram") -> str:
        """
        Refine image generation prompts using Claude to create world-class prompts for FAL.ai
        """
        system_prompt = """You are an elite Ideogram V2A prompt engineer specializing in creating viral social media visuals. Your expertise lies in crafting prompts that produce stunning, share-worthy images that social media users absolutely love.

CRITICAL REQUIREMENT: You must preserve the EXACT spelling and text from the original prompt. Never change, alter, or "improve" the text content - only enhance the visual description around it.

IDEOGRAM V2A MASTERY RULES:
1. Ideogram V2A excels at high-quality imagery with perfect text rendering
2. Use specific visual descriptors that trigger maximum quality outputs
3. Focus on composition, lighting, and aesthetic trends that go viral
4. Specify clear text placement for perfect typography rendering
5. Match the requested art style while maximizing quality
6. Create Instagram/TikTok-worthy visual appeal

STYLE DETECTION & OPTIMIZATION:
- ANIME/MANGA: "High-quality anime style, studio-grade animation quality, detailed character design, vibrant colors, sharp lineart, professional anime illustration"
- PHOTOREALISTIC: "Photorealistic, natural features, perfect anatomy, professional photography quality"
- CARTOON/STYLIZED: "High-quality cartoon style, professional illustration, clean vector art, vibrant colors"
- LOGO/BRAND: "Professional logo design, crisp graphics, brand-quality imagery"

PERFECT TEXT RENDERING FORMULA (CRITICAL):
- ALWAYS use "bold, crystal-clear text" and "perfect typography"
- ALWAYS specify "perfect spelling, no text errors, crisp lettering"
- Specify exact placement: "centered overlay", "bottom third", "top banner"
- ALWAYS include "high contrast for readability"
- Use "professional font rendering, no blurred text"

VIRAL SOCIAL MEDIA AESTHETICS:
- Dramatic cinematic lighting or studio-quality illumination
- Trending color palettes that pop on social feeds
- Eye-catching compositions using rule of thirds
- High contrast and saturation for mobile viewing
- Clean backgrounds that make text and subjects stand out
- Instagram/TikTok trending visual styles

MAXIMUM QUALITY SPECIFICATIONS:
- ALWAYS include "8K resolution, ultra-detailed, crisp and sharp"
- "Professional grade quality, no artifacts, no distortions"
- "Trending on social media, viral aesthetic appeal"
- "High contrast, vibrant colors, perfect clarity"
- "Studio-quality rendering, masterpiece-level detail"

IDEOGRAM V2A OPTIMIZATION TEMPLATES:

FOR ANIME/STYLIZED:
"High-quality anime style illustration, [detailed scene], studio-grade animation quality, vibrant colors, sharp detailed lineart, featuring bold crystal-clear text '[EXACT TEXT]' with perfect spelling and typography, [text placement], cinematic lighting, 8K resolution, ultra-detailed, trending anime aesthetic, no artifacts, masterpiece quality"

FOR PHOTOREALISTIC:
"Photorealistic [image type], [detailed scene], professional photography, studio lighting, featuring bold crystal-clear text '[EXACT TEXT]' with perfect spelling, [text placement], shot with professional camera, 8K resolution, ultra-detailed, viral social media aesthetic, no artifacts, perfect clarity"

CRITICAL RULES:
- NEVER change spelling of any text in the image
- ALWAYS specify "perfect spelling, no text errors" for text
- Match the requested art style while maximizing quality
- ALWAYS include 8K resolution and ultra-detailed specifications
- Focus on viral, trending visual aesthetics
- Ensure maximum text clarity and contrast"""

        user_prompt = f"""Create a viral-worthy Ideogram V2A prompt that will generate stunning, high-quality social media content:

Original prompt: {original_prompt}
Content context: {content_context}
Platform: {platform}

CRITICAL REQUIREMENTS:
1. Preserve EXACT spelling of any text that appears in the image
2. Detect the art style (anime, photorealistic, cartoon, etc.) and optimize accordingly
3. ALWAYS specify "8K resolution, ultra-detailed, crisp and sharp, no artifacts"
4. ALWAYS include "bold crystal-clear text, perfect spelling, no text errors"
5. ALWAYS specify "high contrast for text readability, professional typography"
6. Include viral social media aesthetics for maximum engagement
7. Use appropriate quality keywords for the detected style

STYLE-SPECIFIC OPTIMIZATION:
- If ANIME/MANGA requested: Use "studio-grade animation quality, detailed character design, sharp lineart, professional anime illustration"
- If PHOTOREALISTIC requested: Use "photorealistic, natural features, professional photography quality"
- If CARTOON/STYLIZED requested: Use "high-quality cartoon style, professional illustration, clean vector art"

Transform this into an Ideogram V2A masterpiece prompt that will generate world-class images with perfect text rendering and maximum viral appeal. Focus on achieving the highest possible quality within the requested style."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            refined_prompt = response.content[0].text.strip()
            return refined_prompt
            
        except Exception as e:
            print(f"Error refining image prompt with Claude: {str(e)}")
            return original_prompt
    
    def refine_caption(self, original_caption: str, content_context: str = "", platform: str = "instagram") -> str:
        """
        Refine social media captions using Claude for maximum engagement
        """
        system_prompt = """You are an expert social media copywriter with a proven track record of creating viral, engaging content. Your captions consistently drive high engagement, conversions, and brand awareness.

Your refined captions should be:
1. Hook-driven (start with attention-grabbing first line)
2. Emotionally engaging and relatable
3. Platform-optimized for maximum reach
4. Include strategic call-to-actions
5. Use storytelling techniques
6. Be conversational and authentic
7. Include strategic line breaks for readability
8. Consider trending topics and current events

Platform-specific optimization:
- Instagram: Visual storytelling, emojis, engaging questions
- Facebook: Community-focused, shareable content
- LinkedIn: Professional insights, thought leadership
- Twitter: Concise, witty, trending topics

Always maintain the brand voice while maximizing engagement potential."""

        user_prompt = f"""Please refine this social media caption to be world-class and highly engaging:

Original caption: {original_caption}
Content context: {content_context}
Platform: {platform}

Transform this into a caption that will maximize engagement, shares, and conversions. Make it compelling, authentic, and optimized for the platform."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.8,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            refined_caption = response.content[0].text.strip()
            return refined_caption
            
        except Exception as e:
            print(f"Error refining caption with Claude: {str(e)}")
            return original_caption
    
    def refine_hashtags(self, original_hashtags: List[str], content_context: str = "", platform: str = "instagram") -> List[str]:
        """
        Refine hashtag strategy using Claude for maximum reach and engagement
        """
        system_prompt = """You are a social media growth expert specializing in hashtag strategy and viral content optimization. You understand algorithm behaviors, trending topics, and hashtag performance across platforms.

Your hashtag strategy should include:
1. Mix of trending and niche hashtags
2. Platform-specific optimization
3. Audience-targeted hashtags
4. Brand-relevant hashtags
5. Strategic hashtag volume (optimal for each platform)
6. Community hashtags for engagement
7. Location-based hashtags when relevant

Platform guidelines:
- Instagram: 8-15 hashtags, mix of broad and niche
- LinkedIn: 3-5 professional hashtags
- Twitter: 1-3 relevant hashtags
- Facebook: 1-3 hashtags maximum

Focus on hashtags that will:
- Increase discoverability
- Attract target audience
- Drive engagement
- Build community
- Support brand positioning"""

        hashtags_str = ", ".join(original_hashtags) if original_hashtags else "No hashtags provided"
        
        user_prompt = f"""Please refine this hashtag strategy to maximize reach and engagement:

Original hashtags: {hashtags_str}
Content context: {content_context}
Platform: {platform}

Provide an optimized list of hashtags that will maximize visibility and attract the right audience. Return only the hashtags, one per line, with the # symbol."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.6,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            refined_hashtags_text = response.content[0].text.strip()
            # Extract hashtags from the response
            refined_hashtags = [tag.strip() for tag in refined_hashtags_text.split('\n') if tag.strip().startswith('#')]
            
            return refined_hashtags if refined_hashtags else original_hashtags
            
        except Exception as e:
            print(f"Error refining hashtags with Claude: {str(e)}")
            return original_hashtags
    
    def refine_all_content(self, content_data: Dict[str, Any], platform: str = "instagram") -> Dict[str, Any]:
        """
        Refine all content elements (prompt, caption, hashtags) in one go
        """
        refined_content = content_data.copy()
        
        # Extract context for better refinement
        context = f"Platform: {platform}, Content type: {content_data.get('content_type', 'social media post')}"
        
        # Refine image prompt if present
        if 'image_prompt' in content_data:
            refined_content['image_prompt'] = self.refine_image_prompt(
                content_data['image_prompt'], 
                context, 
                platform
            )
            refined_content['original_image_prompt'] = content_data['image_prompt']
        
        # Refine caption if present
        if 'caption' in content_data:
            refined_content['caption'] = self.refine_caption(
                content_data['caption'], 
                context, 
                platform
            )
            refined_content['original_caption'] = content_data['caption']
        
        # Refine hashtags if present
        if 'hashtags' in content_data:
            refined_content['hashtags'] = self.refine_hashtags(
                content_data['hashtags'], 
                context, 
                platform
            )
            refined_content['original_hashtags'] = content_data['hashtags']
        
        refined_content['claude_refined'] = True
        refined_content['refinement_timestamp'] = str(json.dumps({"timestamp": "now"}))
        
        return refined_content