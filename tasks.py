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
            - Realistic, high-quality photographic style or clean modern design
            - Professional, polished appearance that looks authentic
            - High-resolution, crisp imagery suitable for social media
            - Natural lighting and realistic textures when using photographic elements
            - Clean images WITHOUT any text or typography overlays
            - Vibrant, engaging colors that perform well on social platforms
            - Premium aesthetic that attracts social media users - let the visuals speak for themselves
            
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
            2. Create individual clean image prompts for each slide that visually represent the concept
            3. Ensure consistent photographic style across all slides (same lighting, color tone, quality)
            4. Use the generate_carousel_images tool with the list of prompts
            
            IMPORTANT: Create clean, text-free images that visually represent each tip/concept.
            The numbering and text content will be handled in the caption, not on the image itself.
            Focus on creating visually compelling images that support each tip conceptually.
            
            CAROUSEL PROMPT TEMPLATE:
            "Clean, high-quality photograph representing: [SPECIFIC_TIP_CONTENT]. Realistic, professional photography style. No text or typography on the image. Vibrant colors, natural lighting, Instagram-ready format. Focus on visual storytelling that conceptually represents the tip."
            
            EXAMPLE PROMPTS FOR "5 Ways to Improve Focus":
            Prompt 1: "Clean, high-quality photograph of an organized, minimalist workspace with no distractions. Realistic, professional photography style. No text on the image. Vibrant colors, natural lighting, Instagram-ready format."
            Prompt 2: "Clean, high-quality photograph of a person taking a peaceful break in a modern office or home setting. Realistic, professional photography style. No text on the image. Vibrant colors, natural lighting, Instagram-ready format."
            Prompt 3: "Clean, high-quality photograph of a person in a calm, meditative pose doing breathing exercises. Realistic, professional photography style. No text on the image. Vibrant colors, natural lighting, Instagram-ready format."
            
            CRITICAL: Never include any text, numbers, or typography on the images. Keep them clean and purely visual.
            
            The images should:
            - Look realistic and professional, like high-quality photography
            - Feature real-looking people, objects, and environments when relevant
            - Be completely clean with NO text, numbers, or typography whatsoever
            - Use natural lighting and authentic-looking settings
            - Have consistent photographic quality and styling across all carousel slides
            - Visually represent the concept/tip through imagery alone
            - Look engaging and authentic to attract social media users
            - Let the visual tell the story - text will be in the caption
            
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

    def story_generation_task(self, agent, caption_content, user_prompt):
        return Task(
            description=dedent(
                f"""
            Based on the caption content: "{caption_content}"
            Original user prompt: "{user_prompt}"
            
            Create STORY TEMPLATE content optimized for Instagram, Facebook, and LinkedIn Stories.
            
            STORY SPECIFICATIONS:
            - Dimensions: 1080 × 1920 pixels (9:16 aspect ratio)
            - Safe Zone: Keep important elements within 1080 × 1420 px (centered vertically)
            - Premium vertical design optimized for mobile viewing
            
            STORY CONTENT ANALYSIS:
            Determine the best Story format based on content:
            
            CREATE SINGLE STORY for:
            - Simple announcements
            - Motivational quotes
            - Behind-the-scenes content
            - Quick tips or facts
            - Product highlights
            
            CREATE STORY SERIES (2-5 stories) for:
            - Step-by-step tutorials
            - Multiple tips or insights
            - Product showcases with different angles
            - Story-driven content with progression
            - Educational content with multiple points
            
            PREMIUM STORY VISUAL REQUIREMENTS:
            - Vertical 9:16 format (1080×1920px)
            - Text-safe zone awareness (avoid top/bottom 250px for key content)
            - High-quality, engaging visuals that work on mobile
            - Clean, modern aesthetic suitable for Stories
            - Vibrant colors that perform well in Story format
            - Professional photography style or clean graphics
            - NO text overlays on images (text will be added separately)
            
            CULTURAL CONSIDERATIONS:
            - For general content: Use INDIAN/SOUTH ASIAN cultural context
            - Indian clothing, settings, families, and lifestyle
            - Only use Arabic/Islamic styling for explicitly religious content
            - Modern Indian urban/lifestyle representation
            
            FOR SINGLE STORY:
            Use the generate_story_image tool with a premium vertical prompt.
            
            FOR STORY SERIES:
            1. Break content into logical story segments (2-5 stories max)
            2. Create individual story prompts that flow together
            3. Ensure visual consistency across the series
            4. Use the generate_story_series tool with the list of prompts
            
            STORY PROMPT TEMPLATE:
            "Vertical story format (9:16, 1080x1920px): [SPECIFIC_STORY_CONTENT]. High-quality mobile-optimized photography. Clean, modern aesthetic. No text overlays. Professional lighting, engaging composition. Instagram Story ready format. Focus on [MAIN_SUBJECT/THEME]."
            
            EXAMPLE STORY PROMPTS:
            Single Story: "Vertical story format (9:16, 1080x1920px): Professional woman in modern Indian casual wear holding coffee, smiling in bright modern office space. High-quality mobile photography, clean aesthetic, no text overlays, natural lighting, Instagram Story ready."
            
            Story Series Example (3-part productivity tips):
            Story 1: "Vertical story format: Clean, organized desk setup with laptop and notebook in modern Indian home office. Mobile-optimized photography, no text, natural lighting."
            Story 2: "Vertical story format: Person in comfortable Indian casual wear taking a mindful break, sitting by window with plants. Clean aesthetic, professional mobile photography."
            Story 3: "Vertical story format: Hands holding smartphone with productivity app, modern Indian lifestyle setting. High-quality vertical photography, Instagram Story ready."
            
            CRITICAL REQUIREMENTS:
            - Always use 9:16 vertical format
            - Keep text-safe zones in mind
            - No text or typography on images
            - High mobile engagement potential
            - Professional story-appropriate quality
            - Consistent visual style if creating series
            
            {self.__tip_section()}
            
            Return the story image prompt(s) and generated Story URL(s).
        """
            ),
            expected_output="Single Story image or Story series with premium quality vertical prompts and URLs",
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

    def content_calendar_planning_task(self, agent, user_prompt, platforms=None, duration_weeks=4):
        return Task(
            description=dedent(
                f"""
            Based on the user's request: "{user_prompt}"
            Target platforms: {platforms if platforms else "Instagram, Facebook, Twitter, LinkedIn"}
            Calendar duration: {duration_weeks} weeks
            
            Create a COMPREHENSIVE and ACTIONABLE content calendar plan that includes:
            
            CALENDAR STRUCTURE REQUIREMENTS:
            - Complete daily scheduling for ALL {duration_weeks} weeks (no shortcuts like "Continue pattern")
            - Platform-specific content distribution across all days
            - Content type variety (posts, stories, carousels, reels, live videos, polls)
            - Strategic theme alignment with seasonal/trending topics
            - Optimal posting times for each platform based on audience behavior
            
            CONTENT ELEMENTS FOR EACH ENTRY (REQUIRED):
            1. Date/Time: Specific posting schedule with exact dates
            2. Platform: Target social media platform
            3. Content Type: Post format (single post, carousel, story, reel, live video, poll, etc.)
            4. Topic/Theme: Detailed content subject and focus
            5. Caption/Copy: FULL caption text or detailed description (not just brief)
            6. Media: Specific image/video description with visual requirements
            7. Hashtags/Tags: 8-12 strategic hashtags relevant to the content
            8. Call-to-Action: Specific action for audience engagement
            9. Status: Draft/Scheduled/Published tracking
            10. Performance Goal: Expected engagement/reach target
            
            ADVANCED STRATEGIC CONSIDERATIONS:
            - Content variety: 40% promotional, 30% educational, 20% behind-the-scenes, 10% user-generated
            - Platform-specific best practices and algorithm optimization
            - Audience engagement patterns and peak activity times
            - Brand consistency across all touchpoints
            - Seasonal relevance, holidays, and trending topics integration
            - Cross-platform content adaptation and repurposing
            - Campaign alignment with business objectives
            - Competitor analysis integration
            - Influencer collaboration opportunities
            - Community building and user-generated content strategies
            
            CONTENT CALENDAR FORMAT (COMPLETE ALL WEEKS):
            
            ## CONTENT CALENDAR - {duration_weeks} Week Strategy
            
            ### Week 1 (Dates: [Specific Start Date] - [Specific End Date])
            
            **Monday, [Exact Date]**
            - Platform: [Platform]
            - Time: [Optimal Time with timezone]
            - Content Type: [Specific type]
            - Topic/Theme: [Detailed theme]
            - Caption: [Full caption text or comprehensive description]
            - Media: [Detailed visual requirements]
            - Hashtags: [8-12 strategic hashtags]
            - Call-to-Action: [Specific CTA]
            - Performance Goal: [Expected metrics]
            - Status: Draft
            
            **Tuesday, [Exact Date]**
            [Complete entry with all fields]
            
            **Wednesday, [Exact Date]**
            [Complete entry with all fields]
            
            **Thursday, [Exact Date]**
            [Complete entry with all fields]
            
            **Friday, [Exact Date]**
            [Complete entry with all fields]
            
            **Saturday, [Exact Date]**
            [Complete entry with all fields]
            
            **Sunday, [Exact Date]**
            [Complete entry with all fields]
            
            ### Week 2 (Dates: [Specific Start Date] - [Specific End Date])
            [Complete daily entries for all 7 days]
            
            ### Week 3 (Dates: [Specific Start Date] - [Specific End Date])
            [Complete daily entries for all 7 days]
            
            ### Week 4 (Dates: [Specific Start Date] - [Specific End Date])
            [Complete daily entries for all 7 days]
            
            [Continue for additional weeks if duration_weeks > 4]
            
            ## CONTENT THEMES & WEEKLY OBJECTIVES
            **Week 1 Theme:** [Specific theme with objectives]
            **Week 2 Theme:** [Specific theme with objectives]
            **Week 3 Theme:** [Specific theme with objectives]
            **Week 4 Theme:** [Specific theme with objectives]
            
            ## PLATFORM-SPECIFIC STRATEGY
            **Instagram:**
            - Posting frequency: [Specific schedule]
            - Content mix: [Percentage breakdown]
            - Optimal times: [Specific times]
            - Engagement tactics: [Specific strategies]
            
            **Facebook:**
            - Posting frequency: [Specific schedule]
            - Content mix: [Percentage breakdown]
            - Optimal times: [Specific times]
            - Engagement tactics: [Specific strategies]
            
            **Twitter:**
            - Posting frequency: [Specific schedule]
            - Content mix: [Percentage breakdown]
            - Optimal times: [Specific times]
            - Engagement tactics: [Specific strategies]
            
            **LinkedIn:**
            - Posting frequency: [Specific schedule]
            - Content mix: [Percentage breakdown]
            - Optimal times: [Specific times]
            - Engagement tactics: [Specific strategies]
            
            ## HASHTAG STRATEGY
            - Brand hashtags: [Branded hashtags]
            - Industry hashtags: [Industry-specific tags]
            - Trending hashtags: [Current trending tags]
            - Niche hashtags: [Targeted niche tags]
            - Weekly rotating hashtags: [Weekly themes]
            
            ## CONTENT CREATION REQUIREMENTS
            - Visual assets needed: [Detailed list]
            - Video content requirements: [Specific needs]
            - Graphic design needs: [Template requirements]
            - Photography sessions: [Planned shoots]
            - Content writing: [Copy requirements]
            
            ## ENGAGEMENT & COMMUNITY MANAGEMENT
            - Response time targets: [Specific timeframes]
            - Community engagement hours: [Daily schedules]
            - User-generated content campaigns: [Specific campaigns]
            - Influencer collaboration schedule: [Partnership timing]
            - Contest and giveaway calendar: [Promotional events]
            
            ## PERFORMANCE TRACKING & KPIs
            - Weekly engagement targets: [Specific metrics]
            - Follower growth goals: [Growth targets]
            - Reach and impression goals: [Visibility targets]
            - Conversion tracking: [Business objectives]
            - Monthly performance reviews: [Review schedule]
            
            ## CONTENT REPURPOSING STRATEGY
            - Cross-platform adaptation guide: [Repurposing rules]
            - Long-form to short-form content: [Adaptation strategies]
            - Video to image conversions: [Visual strategies]
            - Blog to social content: [Content breakdown]
            
            CRITICAL REQUIREMENTS:
            1. Provide COMPLETE daily entries for ALL {duration_weeks} weeks
            2. Include FULL captions or detailed descriptions (not brief summaries)
            3. Provide 8-12 specific hashtags for each entry
            4. Include specific call-to-actions for each post
            5. Set performance goals for each content piece
            6. Ensure content variety and platform optimization
            7. Make the calendar immediately actionable for the user
            
            {self.__tip_section()}
            
            Create a detailed, comprehensive, immediately actionable content calendar that serves as a complete social media strategy blueprint.
        """
            ),
            expected_output="Comprehensive, detailed content calendar with complete daily scheduling, full captions, strategic hashtags, and actionable recommendations for all weeks",
            agent=agent,
        )
