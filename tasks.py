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
            
            Create a detailed, creative prompt for AI image generation that will result in a stunning visual for this social media post.
            
            Then generate the image using the generate_image tool.
            
            The image should:
            - Be visually striking and social media ready
            - Complement the caption perfectly
            - Be appropriate for the brand/topic
            - Follow current design trends
            - Be optimized for social media dimensions
            
            {self.__tip_section()}
            
            Return both the image prompt you created and the generated image URL.
        """
            ),
            expected_output="Image generation prompt and the generated image URL",
            agent=agent,
        )

    def hashtag_research_task(self, agent, caption_content, user_prompt, platform="instagram"):
        return Task(
            description=dedent(
                f"""
            Based on the caption: "{caption_content}"
            Original user prompt: "{user_prompt}"
            Platform: {platform}
            
            Research and provide relevant hashtags that will maximize reach and engagement.
            
            Provide:
            - 5-10 highly relevant hashtags
            - Mix of popular and niche hashtags
            - Platform-appropriate hashtag strategy
            - Trending hashtags if relevant
            
            {self.__tip_section()}
            
            Focus on hashtags that will drive real engagement and reach.
        """
            ),
            expected_output="A strategic list of relevant hashtags for the post",
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
