"""
Reel-specific tasks for video generation workflow
"""

from crewai import Task
from textwrap import dedent


class ReelTasks:
    """Specialized tasks for video reel generation"""
    
    def content_planning_task(self, agent, prompt, mode, duration=20):
        """Analyze content and create storyboard"""
        return Task(
            description=dedent(f"""
                CONTENT PLANNING MISSION:
                Analyze user prompt: "{prompt}"
                Requested mode: "{mode}"
                Target duration: {duration} seconds
                
                STEP 1: CONTENT ANALYSIS
                - Identify content category (educational, entertainment, promotional, lifestyle, tutorial, etc.)
                - Determine complexity level and information density
                - Analyze target audience and engagement expectations
                - Consider platform-specific requirements
                
                STEP 2: INTELLIGENT MODE SELECTION
                - Apply mode selection rules based on content characteristics
                - Override user preference if analysis suggests better alternative
                - Provide clear rationale for mode recommendation
                
                STEP 3: STORYBOARD CREATION
                Create 2-3 scenes based on duration:
                - 15s reels: 2 scenes (8s + 7s)
                - 20s reels: 3 scenes (7s + 6s + 7s)
                - 30s reels: 3 scenes (10s + 10s + 10s)
                
                For each scene include:
                - Scene description and visual elements
                - Key messaging or narrative focus
                - Timing and pacing
                - Technical requirements (camera angles, transitions)
                
                STEP 4: VISUAL STYLE GUIDELINES
                - Color palette recommendations
                - Visual aesthetics and mood
                - Platform-specific optimizations
                - Engagement hooks and retention elements
                
                REQUIRED OUTPUT FORMAT (strict JSON):
                {{
                    "content_analysis": {{
                        "category": "string",
                        "complexity_level": "low|medium|high",
                        "target_audience": "string",
                        "engagement_type": "string"
                    }},
                    "mode_selection": {{
                        "recommended_mode": "music|narration",
                        "user_requested": "{mode}",
                        "override_reason": "string or null",
                        "rationale": "string"
                    }},
                    "storyboard": {{
                        "total_duration": {duration},
                        "scene_count": "int",
                        "scenes": [
                            {{
                                "scene_number": 1,
                                "duration": "int",
                                "title": "string",
                                "description": "string",
                                "visual_elements": "string",
                                "key_message": "string",
                                "technical_notes": "string"
                            }}
                        ]
                    }},
                    "visual_style": {{
                        "color_palette": "string",
                        "aesthetic_mood": "string",
                        "platform_optimization": "string",
                        "engagement_hooks": "string"
                    }},
                    "success_metrics": {{
                        "engagement_prediction": "high|medium|low",
                        "target_completion_rate": "percentage",
                        "key_performance_indicators": "string"
                    }}
                }}
            """),
            agent=agent,
            expected_output="Complete content planning JSON with analysis, mode selection, storyboard, and visual guidelines"
        )
    
    def prompt_refinement_task(self, agent, storyboard):
        """Claude-enhanced prompt optimization"""
        return Task(
            description=dedent("""
                Using the storyboard provided, refine and optimize video generation prompts.
                
                For each scene in the storyboard:
                1. Transform basic descriptions into professional video prompts
                2. Add technical specifications (resolution, style, etc.)
                3. Include quality indicators and success predictors
                4. Optimize for the target AI video models
                
                Output format: Enhanced prompts with quality scores
            """),
            agent=agent,
            expected_output="Refined video generation prompts with quality predictions"
        )
    
    def video_generation_task(self, agent, refined_prompts):
        """Generate video clips using FAL.AI models"""
        return Task(
            description=dedent("""
                Generate video clips using the refined prompts provided.
                
                For each prompt:
                1. Generate video clip using FAL.AI models
                2. Implement fallback strategies if primary model fails
                3. Validate video quality and technical specifications
                4. Save clips to designated output folder
                
                Output format: List of generated video file paths with metadata
            """),
            agent=agent,
            expected_output="Generated video clips saved to output folder with metadata"
        )
    
    def audio_generation_task(self, agent, content_mode):
        """Create narration or background music"""
        return Task(
            description=dedent(f"""
                Create audio content for {content_mode} mode.
                
                If narration mode:
                1. Generate TTS narration script
                2. Create high-quality voice narration
                3. Optimize timing for video content
                
                If music mode:
                1. Generate appropriate background music
                2. Ensure music matches video theme and pace
                3. Optimize volume and timing
                
                Output format: Audio file paths with timing metadata
            """),
            agent=agent,
            expected_output="Audio files with timing and synchronization metadata"
        )
    
    def synchronization_task(self, agent, video_clips, audio):
        """Stitch videos and sync audio"""
        return Task(
            description=dedent("""
                Combine video clips and audio into final reel.
                
                Process:
                1. Stitch video clips with professional transitions
                2. Synchronize audio with video timeline
                3. Apply final quality optimizations
                4. Export final reel in appropriate format
                
                Output format: Final reel file path with complete metadata
            """),
            agent=agent,
            expected_output="Final synchronized reel with professional quality"
        )
    
    def qa_testing_task(self, agent, final_reel):
        """Quality assessment with reloop capability"""
        return Task(
            description=dedent("""
                Perform comprehensive quality assessment of the final reel.
                
                Assessment areas:
                1. Technical quality (resolution, sync, compression)
                2. Content quality (narrative flow, visual appeal)
                3. Brand alignment and platform optimization
                4. Engagement potential prediction
                
                If quality thresholds not met, recommend reloop strategy.
                
                Output format: QA report with scores and improvement recommendations
            """),
            agent=agent,
            expected_output="Quality assessment report with pass/fail status and improvement recommendations"
        )