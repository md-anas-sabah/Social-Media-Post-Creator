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
        system_prompt = """You are a master prompt engineer specializing in creating world-class image generation prompts for social media content. Your expertise lies in transforming basic prompts into detailed, professional prompts that produce stunning visuals.

CRITICAL REQUIREMENT: You must preserve the EXACT spelling and text from the original prompt. Never change, alter, or "improve" the text content - only enhance the visual description around it.

Your task is to refine image generation prompts to be:
1. Highly detailed and specific
2. Visually compelling and professional
3. Optimized for social media platforms
4. Culturally appropriate (default to modern Indian/South Asian representation)
5. Technical specifications for best results
6. EXACT text preservation - never alter spelling or wording of text content

Always use this professional template structure:
"High-resolution [type], showing [detailed subject description] in [specific setting], in the style of professional social media photography, captured with [camera specifications], using [specific lighting], with clean and centered text saying '[EXACT ORIGINAL TEXT]' in elegant, bold typography. [Additional visual details]. No distortions, no artifacts, realistic proportions, highly detailed, ultra sharp, suitable for print and digital use."

CRITICAL RULES:
- NEVER change the spelling of any text that will appear in the image
- NEVER alter or "correct" text content from the original prompt
- ONLY enhance the visual, lighting, composition, and technical aspects
- Preserve exact capitalization, spacing, and spelling of all text
- If the original says "International Job Day", use EXACTLY "International Job Day"
- If the original says "Happy Birthday", use EXACTLY "Happy Birthday"

Focus on:
- Professional photography quality
- EXACT text preservation (no spelling changes)
- Realistic proportions and anatomy
- Appropriate lighting and composition
- Platform-specific optimization
- Cultural sensitivity and modern representation"""

        user_prompt = f"""Please refine this image generation prompt to be world-class:

Original prompt: {original_prompt}
Content context: {content_context}
Platform: {platform}

IMPORTANT: Preserve the EXACT spelling and text content from the original prompt. Do not change any words that will appear as text in the image.

Transform this into a detailed, professional prompt that will generate stunning social media visuals. Enhance the visual description, lighting, composition, and technical aspects while keeping all text content exactly as provided in the original prompt."""

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