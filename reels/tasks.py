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
    
    def prompt_refinement_task(self, agent, storyboard_result, context):
        """Claude-enhanced prompt optimization"""
        return Task(
            description=dedent(f"""
                CLAUDE PROMPT REFINEMENT MISSION:
                Transform the storyboard data into professional video generation prompts using Claude AI optimization.
                
                STORYBOARD INPUT:
                {storyboard_result}
                
                CONTEXT DATA:
                - Platform: {context.get('platform', 'instagram')}
                - Duration: {context.get('duration', 20)} seconds
                - Content Mode: {context.get('content_mode', 'music')}
                - User Prompt: {context.get('user_prompt', '')}
                
                STEP 1: USE CLAUDE PROMPT REFINEMENT TOOL
                You have access to the "Claude Prompt Refinement Tool" which integrates Claude AI for prompt optimization.
                
                Use the tool to:
                1. Extract scenes from storyboard data
                2. Analyze visual style and content requirements  
                3. Send comprehensive refinement request to Claude API
                4. Parse enhanced prompts with quality predictions
                
                STEP 2: PROFESSIONAL OPTIMIZATION
                For each scene, Claude should provide:
                - Enhanced video generation prompt with technical specifications
                - Quality prediction score (0.0-1.0)
                - Recommended AI model (hailuo-02, runway-gen3, pika-labs, etc.)
                - Technical parameters (resolution, duration, style, camera movement)
                - Alternative prompt variations for fallback
                
                STEP 3: MODEL-SPECIFIC ADAPTATION
                Optimize prompts for specific AI video models:
                - Hailuo-02: Cinematic style, smooth camera movements
                - Runway Gen-3: Creative transitions, dynamic scenes
                - Pika Labs: Artistic effects, engaging visuals
                
                STEP 4: QUALITY ASSURANCE
                Ensure all enhanced prompts include:
                - Professional video terminology
                - Technical specifications (1080x1920, fps, duration)
                - Style parameters (lighting, composition, mood)
                - Platform optimization for social media engagement
                
                TOOL USAGE:
                Use the "Claude Prompt Refinement Tool" with the storyboard data and context.
                The tool will handle Claude API integration and return enhanced prompts with quality predictions.
                
                EXPECTED OUTPUT STRUCTURE:
                {{
                    "status": "success|fallback",
                    "original_storyboard": "original storyboard data",
                    "refined_prompts": [
                        {{
                            "scene_number": 1,
                            "original_description": "basic scene description",
                            "enhanced_prompt": "professional video prompt with technical specs",
                            "quality_prediction": 0.85,
                            "recommended_model": "hailuo-02",
                            "technical_params": {{
                                "resolution": "1080x1920",
                                "duration": 7,
                                "style": "cinematic",
                                "camera_movement": "smooth_pan"
                            }},
                            "alternative_prompts": ["variation 1", "variation 2"]
                        }}
                    ],
                    "quality_predictions": {{
                        "overall_score": 0.82,
                        "technical_feasibility": 0.85,
                        "creative_appeal": 0.80,
                        "engagement_potential": 0.85
                    }},
                    "model_optimizations": {{
                        "primary_model": "hailuo-02",
                        "fallback_models": ["runway-gen3", "pika-labs"],
                        "model_specific_tips": []
                    }},
                    "claude_analysis": "detailed analysis from Claude",
                    "improvement_suggestions": ["suggestion 1", "suggestion 2"]
                }}
                
                CRITICAL REQUIREMENTS:
                1. All prompts must be enhanced beyond basic descriptions
                2. Quality predictions must be realistic and based on Claude's analysis
                3. Technical parameters must be complete and accurate
                4. Fallback system must work when Claude API unavailable
                5. Output must be ready for video generation models
                
                SUCCESS METRICS:
                - Enhanced prompts have quality scores ≥ 0.75
                - Technical specifications are complete
                - Model recommendations are appropriate
                - Alternative variations provided for robustness
            """),
            agent=agent,
            expected_output="Claude-enhanced video generation prompts with quality predictions, model recommendations, and technical specifications ready for Phase 4 video generation"
        )
    
    def video_generation_task(self, agent, claude_refinement_result, context):
        """Generate professional video clips using enhanced prompts from Phase 3"""
        return Task(
            description=dedent(f"""
                PHASE 4: ADVANCED VIDEO GENERATION MISSION
                Transform Claude-enhanced prompts into professional video clips using multi-model FAL.AI integration.
                
                PHASE 3 INPUT (CLAUDE REFINEMENT RESULT):
                {claude_refinement_result}
                
                CONTEXT DATA:
                - Platform: {context.get('platform', 'instagram')}
                - Duration: {context.get('duration', 20)} seconds total
                - Content Mode: {context.get('content_mode', 'music')}
                - User Prompt: {context.get('user_prompt', '')}
                - Output Folder: Available in agent configuration
                
                STEP 1: EXTRACT REFINED PROMPTS
                Extract the refined_prompts array from Claude refinement result:
                - Parse Claude enhancement data structure
                - Validate prompt quality and technical parameters
                - Confirm model recommendations and fallback options
                
                STEP 2: INTELLIGENT MODEL SELECTION
                For each refined prompt:
                - Use Claude's model recommendation as primary choice
                - Validate model capabilities vs requirements (duration, style, etc.)
                - Apply intelligent fallback if constraints not met
                - Consider cost-quality optimization
                
                STEP 3: PROFESSIONAL VIDEO GENERATION
                Execute video generation using the Advanced Video Generation Tool:
                
                SIMPLIFIED USAGE: The tool now auto-detects the output folder and has smart defaults.
                You only need to provide the refined_prompts_data parameter as a JSON string.
                
                REQUIRED PARAMETER:
                - refined_prompts_data: Convert claude_refinement_result to JSON string
                
                OPTIONAL PARAMETERS (auto-detected if not provided):
                - output_folder: Will auto-detect current reel folder and use raw_clips/ subdirectory
                - context: Will use smart defaults for platform, duration, content_mode
                
                MANDATORY TOOL USAGE:
                YOU MUST use the "Advanced Video Generation Tool" to generate the video clips. 
                Call the tool with the refined prompts data as a JSON string parameter.
                
                Example tool usage:
                Use the Advanced Video Generation Tool with:
                - refined_prompts_data: The complete claude_refinement_result as a JSON string
                
                STEP 4: MULTI-MODEL VIDEO GENERATION
                For each clip, execute:
                - Model Selection: Use optimal model based on Claude recommendations
                - Parameter Configuration: Apply model-specific settings for maximum quality
                - Generation Execution: Submit to FAL.AI with proper error handling
                - Quality Validation: Validate generated video meets technical standards
                - File Management: Download and save with organized naming
                
                MODEL-SPECIFIC OPTIMIZATIONS:
                - **Hailuo 02**: 24fps, high quality, realistic motion optimization
                - **Runway Gen3**: 30fps, motion intensity 0.7, creative transitions
                - **Pika Labs**: Guidance scale 7.5, artistic visual effects
                - **Veo 2**: Premium quality, image animation enhancement
                
                STEP 5: QUALITY ASSURANCE
                For each generated clip:
                - File Integrity: Verify successful download and proper file size
                - Technical Validation: Check resolution, duration, format compliance
                - Visual Quality: Basic quality assessment and scoring
                - Metadata Recording: Complete generation data and model information
                
                STEP 6: COMPREHENSIVE REPORTING
                Generate detailed generation report including:
                - Success/failure status for each clip
                - Model usage breakdown and performance analysis
                - Quality assessment scores and validation results
                - Cost analysis with per-clip and total estimates
                - File organization with complete paths and metadata
                
                REQUIRED OUTPUT STRUCTURE:
                {{
                    "video_generation_status": "success|partial|failed",
                    "generated_clips": [
                        {{
                            "clip_id": 1,
                            "file_path": "/path/to/clip_1_hailuo-02.mp4",
                            "filename": "clip_1_hailuo-02.mp4",
                            "status": "success|mock|failed",
                            "model_used": "hailuo-02",
                            "duration": 7,
                            "resolution": "1080x1920",
                            "quality_check": {{
                                "valid": true,
                                "file_size": 1048576,
                                "estimated_quality": "good"
                            }},
                            "cost_estimate": 0.49,
                            "prompt_data": "original refined prompt data"
                        }}
                    ],
                    "generation_summary": {{
                        "total_clips": 3,
                        "successful_clips": 3,
                        "failed_clips": 0,
                        "total_cost": 1.47,
                        "average_cost_per_clip": 0.49,
                        "model_usage": {{
                            "hailuo-02": {{"clips": 2, "cost": 0.98}},
                            "runway-gen3": {{"clips": 1, "cost": 1.20}}
                        }}
                    }},
                    "quality_assessment": {{
                        "overall_quality_score": 0.85,
                        "technical_compliance": true,
                        "all_clips_valid": true,
                        "ready_for_synchronization": true
                    }},
                    "next_phase_data": {{
                        "clips_folder": "/path/to/raw_clips/",
                        "clip_files": ["clip_1.mp4", "clip_2.mp4", "clip_3.mp4"],
                        "total_duration": 20,
                        "ready_for_phase_5": true
                    }}
                }}
                
                CRITICAL REQUIREMENTS:
                1. All video clips must be successfully generated or have proper fallbacks
                2. Quality validation must pass for all clips
                3. Complete metadata must be preserved for Phase 5 synchronization
                4. Cost tracking must be accurate and comprehensive
                5. File organization must be systematic and accessible
                
                SUCCESS METRICS:
                - Video generation success rate ≥ 90%
                - All clips meet minimum quality thresholds
                - Total generation time < 15 minutes for standard 3-clip reel
                - Cost estimates accurate within 10% margin
                - Files properly organized and metadata complete
                
                ERROR HANDLING:
                - Implement intelligent fallback to alternative models
                - Provide clear error messages and recovery suggestions
                - Maintain partial success capability (generate available clips)
                - Ensure no data loss during generation failures
            """),
            agent=agent,
            expected_output="Professional video clips generated with complete quality validation, cost analysis, and metadata ready for Phase 5 synchronization"
        )
    
    def audio_generation_task(self, agent, video_generation_result, context):
        """Generate professional audio using FAL AI F5 TTS for narration or background music for music mode"""
        return Task(
            description=dedent(f"""
                PHASE 5: ADVANCED AUDIO GENERATION MISSION
                Transform video content into synchronized audio using FAL AI F5 TTS for narration or generate matching background music.
                
                PHASE 4 INPUT (VIDEO GENERATION RESULT):
                {video_generation_result}
                
                CONTEXT DATA:
                - Platform: {context.get('platform', 'instagram')}
                - Duration: {context.get('duration', 20)} seconds total
                - Content Mode: {context.get('content_mode', 'music')}
                - User Prompt: {context.get('user_prompt', '')}
                - Timestamp: Available in context
                
                STEP 1: ANALYZE VIDEO GENERATION RESULTS
                Extract key information from Phase 4:
                - Video clips generated and their durations
                - Total reel duration and timing breakdown
                - Output folder location for audio placement
                - Quality status of video generation
                - Content themes and visual elements for audio matching
                
                STEP 2: DETERMINE AUDIO GENERATION APPROACH
                Based on content_mode:
                
                **NARRATION MODE** (Educational/Tutorial Content):
                - Analyze user prompt and video content to create educational script
                - Generate professional narration using FAL AI F5 TTS
                - Optimize speech speed and timing for video duration
                - Create natural, engaging voice-over that enhances video content
                - Cost: ~$0.05 per 1000 characters
                
                **MUSIC MODE** (Entertainment/Promotional Content):
                - Generate appropriate background music matching video theme and mood
                - Ensure music complements visual pacing and energy
                - Select genre and style based on platform and audience
                - Optimize for social media engagement and retention
                - Cost: Free (mock generation) for development phase
                
                STEP 3: EXECUTE AUDIO GENERATION
                Use the "Advanced Audio Generation Tool" with the following parameters:
                
                MANDATORY TOOL USAGE:
                YOU MUST use the "Advanced Audio Generation Tool" to generate the audio content.
                
                Required Parameters:
                - video_generation_result: The complete Phase 4 result data as JSON string
                - content_mode: Either "narration" or "music" based on context
                - audio_theme: Determine from user prompt (e.g., "professional", "upbeat", "cinematic")
                - context: Pass complete context information as JSON string
                
                Optional Parameters (tool will auto-determine if not provided):
                - script_content: For narration mode, let tool create intelligent script from context
                
                STEP 4: AUDIO PROCESSING AND OPTIMIZATION
                The tool will automatically:
                - Process generated audio for optimal quality
                - Match duration precisely with video content
                - Optimize format and compression for social media
                - Prepare synchronization metadata for Phase 6
                - Validate audio quality and technical compliance
                
                STEP 5: QUALITY ASSURANCE AND VALIDATION
                - Verify audio generation success and quality scores
                - Ensure proper duration matching with video clips
                - Validate file format compliance and technical specifications
                - Confirm readiness for Phase 6 synchronization
                - Generate comprehensive cost analysis and quality reports
                
                EXPECTED OUTPUT FORMAT (strict JSON):
                {{
                    "audio_generation_status": "success|mock|failed",
                    "content_mode": "narration|music",
                    "generated_audio": {{
                        "file_path": "path/to/audio/file",
                        "filename": "audio_filename",
                        "duration": 20,
                        "type": "narration|background_music",
                        "status": "success|mock|failed",
                        "format": "wav|mp3",
                        "cost_estimate": 0.05
                    }},
                    "generation_summary": {{
                        "audio_type": "narration|music",
                        "duration": 20,
                        "theme": "audio_theme",
                        "cost": 0.05,
                        "status": "success"
                    }},
                    "quality_assessment": {{
                        "audio_quality_score": 0.9,
                        "sync_ready": true,
                        "format_compliance": true,
                        "ready_for_synchronization": true
                    }},
                    "next_phase_data": {{
                        "audio_folder": "path/to/audio/folder",
                        "final_audio_file": "final_audio_filename",
                        "audio_duration": 20,
                        "video_clips": 3,
                        "ready_for_phase_6": true
                    }},
                    "script_content": "generated_script_for_narration"
                }}
                
                CRITICAL REQUIREMENTS:
                1. Audio must be precisely timed to match video duration
                2. Quality standards must meet social media platform requirements
                3. Cost estimates must be accurate and transparent
                4. File organization must be systematic and accessible
                5. All metadata must be preserved for Phase 6 synchronization
                
                SUCCESS METRICS:
                - Audio generation success rate ≥ 95%
                - Perfect duration matching with video content
                - Professional audio quality (≥ 44.1kHz for narration)
                - Cost efficiency within estimated budgets
                - Ready for seamless Phase 6 integration
                
                ERROR HANDLING:
                - Intelligent fallback to mock audio for testing scenarios
                - Clear error reporting with specific failure reasons
                - Maintain partial success capability when possible
                - Preserve all generation attempts and metadata for debugging
            """),
            agent=agent,
            expected_output="Professional audio content with FAL AI F5 TTS narration or background music, perfectly synchronized and ready for Phase 6 video integration"
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