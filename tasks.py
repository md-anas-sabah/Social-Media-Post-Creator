from crewai import Task
from textwrap import dedent


class SocialMediaTasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def ideation_task(self, agent, user_prompt, platform="instagram"):
        return Task(
            description=dedent(
                f"""
            Based on the user's prompt: "{user_prompt}"
            
            Generate exactly 3 creative and engaging social media post ideas for {platform}.
            
            Each idea should include:
            - A compelling hook/opening line
            - Brief description of the post concept
            - Target audience appeal
            - Engagement potential
            
            Format your response as:
            
            **Option 1:**
            Hook: [compelling opening line]
            Concept: [brief description]
            
            **Option 2:**
            Hook: [compelling opening line]  
            Concept: [brief description]
            
            **Option 3:**
            Hook: [compelling opening line]
            Concept: [brief description]
            
            {self.__tip_section()}
            
            Make sure each idea is unique, engaging, and tailored to the platform.
        """
            ),
            expected_output="3 formatted post ideas with hooks and concepts",
            agent=agent,
        )

    def copywriting_task(self, agent, selected_idea, user_prompt, platform="instagram"):
        return Task(
            description=dedent(
                f"""
            Based on the selected idea: "{selected_idea}"
            Original user prompt: "{user_prompt}"
            Platform: {platform}
            
            Create a compelling social media caption that:
            - Starts with an engaging hook
            - Includes a clear call-to-action
            - Is optimized for {platform}
            - Matches the brand voice and tone
            - Is the perfect length for the platform
            - Includes emojis strategically
            
            {self.__tip_section()}
            
            Focus on engagement, conversion, and brand building.
        """
            ),
            expected_output="A polished, platform-optimized social media caption",
            agent=agent,
        )

    def image_generation_task(self, agent, caption_content, user_prompt):
        return Task(
            description=dedent(
                f"""
            Based on the caption content: "{caption_content}"
            Original user prompt: "{user_prompt}"
            
            FIRST, analyze the content to determine if this should be a SINGLE IMAGE or CAROUSEL POST:
            
            CREATE CAROUSEL if content includes:
            - Lists (e.g., "5 ways to...", "10 tips for...", "7 steps to...")
            - Sequential tips or advice
            - Multiple points or strategies
            - Step-by-step guides
            - Numbered or bulleted lists
            
            CREATE SINGLE IMAGE for:
            - General announcements
            - Simple quotes or motivational content
            - Single concept posts
            - Content without clear list structure
            
            CAROUSEL EXTRACTION PROCESS:
            1. Look for list indicators: numbers, bullets, "ways", "tips", "steps", "methods"
            2. Extract each individual point/tip as a separate concept
            3. Count the total number of points to determine carousel size
            4. Create one focused prompt per point (not mentioning other points)
            
            PREMIUM VISUAL STYLE REQUIREMENTS:
            - Clean, modern, minimalist design with premium aesthetics
            - Professional typography and layout suitable for top-tier brands
            - Consistent color palette (choose sophisticated colors like deep blues, elegant grays, warm golds, or modern pastels)
            - High contrast and readability
            - Instagram/LinkedIn professional standard quality
            - Clean white or gradient backgrounds
            - Professional iconography and visual elements
            
            CULTURAL CONSIDERATIONS:
            - If the content is about Father's Day, Christmas, general celebrations, or everyday topics, create images with INDIAN/SOUTH ASIAN cultural context
            - Use Indian clothing (kurta, casual Indian wear), Indian settings, Indian families
            - Only use Arabic/Islamic styling for explicitly religious Islamic content (Eid, Ramadan, Islamic holidays)
            - For general business/lifestyle content, default to Indian cultural representation
            - Include diverse Indian family representations, modern Indian lifestyle, contemporary Indian settings
            
            FOR SINGLE IMAGES:
            Use the generate_image tool with a premium-quality prompt.
            
            FOR CAROUSEL POSTS:
            1. Extract the list items/tips from the content
            2. Create individual premium prompts for each slide
            3. Ensure consistent style across all slides (same color scheme, typography, layout style)
            4. Use the generate_carousel_images tool with the list of prompts
            
            IMPORTANT: Each carousel prompt should create ONE COMPLETE IMAGE focused on ONE specific tip/point.
            DO NOT mention "slide X of Y" or "part of series" - each image should be self-contained.
            
            PREMIUM PROMPT TEMPLATE FOR CAROUSEL:
            "Professional social media post design featuring: [SPECIFIC_TIP_CONTENT]. Modern minimalist layout, premium typography, clean [COLOR_SCHEME] color scheme, high-end brand aesthetic, Instagram-ready design, single focused concept, [CULTURAL_CONTEXT]"
            
            EXAMPLE GOOD PROMPTS FOR "5 Ways to Improve Focus":
            Prompt 1: "Professional social media post design featuring: Eliminate distractions from your workspace. Modern minimalist layout, premium typography, clean navy blue and white color scheme, high-end brand aesthetic, Instagram-ready design, single focused concept"
            Prompt 2: "Professional social media post design featuring: Take regular breaks every 25 minutes. Modern minimalist layout, premium typography, clean navy blue and white color scheme, high-end brand aesthetic, Instagram-ready design, single focused concept"
            Prompt 3: "Professional social media post design featuring: Practice deep breathing exercises. Modern minimalist layout, premium typography, clean navy blue and white color scheme, high-end brand aesthetic, Instagram-ready design, single focused concept"
            
            CRITICAL: Each prompt generates ONE COMPLETE STANDALONE IMAGE. Never reference other slides or use terms like "slide 1 of 5".
            
            The images should:
            - Look like they're created by top-tier design agencies
            - Be visually striking and social media ready
            - Complement the caption perfectly
            - Be culturally appropriate and representative of the target audience
            - Follow current premium design trends
            - Be optimized for social media dimensions
            - Have consistent branding across carousel slides
            
            {self.__tip_section()}
            
            Return the image prompt(s) and generated image URL(s).
        """
            ),
            expected_output="Single image or carousel images with premium quality prompts and URLs",
            agent=agent,
        )

    def hashtag_research_task(self, agent, caption_content, user_prompt, platform="instagram"):
        return Task(
            description=dedent(
                f"""
            Based on the caption: "{caption_content}"
            Original user prompt: "{user_prompt}"
            Platform: {platform}
            
            Generate ACTUAL HASHTAGS (not just strategy advice) that will maximize reach and engagement.
            
            REQUIRED OUTPUT FORMAT:
            HASHTAGS: #hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5 #hashtag6 #hashtag7 #hashtag8
            
            Requirements:
            - Provide exactly 8-12 relevant hashtags
            - Mix of popular (high volume) and niche (targeted) hashtags
            - Include trending hashtags if relevant to the topic
            - Make hashtags specific to the content theme
            - Optimize for {platform} platform
            
            Examples:
            - For Father's Day: #FathersDay #Dad #Family #FatherLove #DadAndMe #FathersDay2024 #FamilyTime #DadStories
            - For Eid: #EidMubarak #Eid2024 #EidCelebration #MuslimFestival #EidJoy #Blessed #Ramadan #EidWithFamily
            
            {self.__tip_section()}
            
            IMPORTANT: Start your response with "HASHTAGS:" followed by the actual hashtags separated by spaces.
        """
            ),
            expected_output="A list of 8-12 relevant hashtags starting with 'HASHTAGS:' prefix",
            agent=agent,
        )

    def timing_optimization_task(self, agent, platform="instagram"):
        return Task(
            description=dedent(
                f"""
            Provide optimal posting time recommendations for {platform}.
            
            Use the get_optimal_posting_time tool to get platform-specific recommendations.
            
            Include:
            - Best posting times for {platform}
            - Day of week recommendations
            - Audience timezone considerations
            - Platform-specific tips
            
            {self.__tip_section()}
            
            Provide actionable timing recommendations.
        """
            ),
            expected_output="Optimal posting times and platform-specific recommendations",
            agent=agent,
        )

    def final_output_task(self, agent, caption, image_url, hashtags, timing, user_prompt):
        return Task(
            description=dedent(
                f"""
            Compile the final social media post output with all components:
            
            Caption: {caption}
            Image URL: {image_url}
            Hashtags: {hashtags}
            Timing: {timing}
            Original prompt: {user_prompt}
            
            Format everything into a clean, professional final output that the user can directly use for their social media post.
            
            {self.__tip_section()}
            
            Make it look polished and ready to post.
        """
            ),
            expected_output="Complete formatted social media post with all components",
            agent=agent,
        )
