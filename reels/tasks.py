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
    
    def synchronization_task(self, agent, video_generation_result, audio_generation_result):
        """Professional video stitching and audio synchronization using MoviePy"""
        
        # Extract video clips from Phase 4 results
        if isinstance(video_generation_result, str):
            try:
                import json
                video_data = json.loads(video_generation_result)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"⚠️  Failed to parse video_generation_result JSON: {e}")
                video_data = {"generated_clips": [], "video_clips": []}
        else:
            video_data = video_generation_result
        
        video_clips = video_data.get('generated_clips', video_data.get('video_clips', []))
        
        # Extract audio data from Phase 5 results  
        if isinstance(audio_generation_result, str):
            try:
                import json
                audio_data = json.loads(audio_generation_result)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"⚠️  Failed to parse audio_generation_result JSON: {e}")
                audio_data = {"audio_generation_status": "parse_error", "generated_audio": {}}
        else:
            audio_data = audio_generation_result or {}
        
        return Task(
            description=dedent(f"""
                PHASE 6: PROFESSIONAL VIDEO SYNCHRONIZATION & EDITING MISSION
                Execute professional video synchronization and editing using MoviePy to create a high-quality social media reel.
                
                **INPUT DATA ANALYSIS:**
                - Video clips from Phase 4: {len(video_clips)} clips generated
                - Audio data from Phase 5: {audio_data.get('mode', 'unknown')} mode, {audio_data.get('duration', 0):.1f}s duration
                - Target platform: Instagram/TikTok (1080x1920 resolution)
                - Quality standard: Professional (libx264, CRF 23, 30fps)
                
                **PROCESSING WORKFLOW:**
                
                **STEP 1: VIDEO STITCHING**
                Use the Professional Synchronization Tool with action="stitch_and_sync" to:
                - Load and validate all video clips from Phase 4 generation results
                - Apply professional enhancements (resize to 1080x1920, color correction, stabilization)
                - Stitch clips with seamless transitions (fade in/out, crossfades, cross-dissolve)
                - Optimize quality settings for social media platforms
                
                **STEP 2: AUDIO SYNCHRONIZATION**
                Synchronize audio from Phase 5 with the stitched video:
                - Load audio file and analyze duration vs video duration
                - Apply intelligent duration matching:
                  * For background music: Loop seamlessly to match video duration
                  * For narration: Maintain original timing and pacing
                - Apply audio enhancements (normalization, fade in/out)
                - Achieve frame-accurate audio-video alignment
                
                **STEP 3: FINAL OPTIMIZATION**
                - Apply professional video effects and color grading
                - Ensure platform compliance (Instagram/TikTok specifications)
                - Export with optimal codec settings (libx264, AAC audio, MP4 container)
                - Generate comprehensive processing metadata
                
                **MANDATORY TOOL USAGE:**
                YOU MUST use the "Professional Synchronization Tool" to execute all synchronization operations.
                
                Required Tool Parameters:
                {{
                    "action": "stitch_and_sync",
                    "video_clips": {video_clips},
                    "audio_data": {audio_data},
                    "output_folder": "[auto-detected from context]",
                    "platform": "instagram",
                    "quality": "professional"
                }}
                
                **ERROR HANDLING:**
                - Graceful fallback when MoviePy unavailable (mock processing)
                - Comprehensive logging of all processing steps
                - Partial success scenarios (video-only if audio fails)
                - Quality validation with detailed error reporting
                
                **SUCCESS CRITERIA:**
                - Final reel exported as MP4 with professional quality
                - Perfect audio-video synchronization achieved
                - All transitions and effects applied successfully
                - Processing metadata generated for quality assessment
                - Platform-optimized output ready for Phase 7 QA testing
                
                PHASE 4 VIDEO GENERATION INPUT:
                {video_generation_result}
                
                PHASE 5 AUDIO GENERATION INPUT:
                {audio_generation_result}
            """),
            agent=agent,
            expected_output=dedent("""
                Complete professional reel synchronization results in JSON format:
                
                {{
                    "status": "completed",
                    "final_reel_path": "/path/to/final_reel.mp4",
                    "video_stitching": {{
                        "clips_used": 3,
                        "total_duration": 20.5,
                        "resolution": "1080x1920",
                        "transitions_applied": true,
                        "quality": "professional"
                    }},
                    "audio_synchronization": {{
                        "sync_quality": "perfect",
                        "audio_mode": "narration",
                        "duration_matched": true,
                        "enhancements_applied": true
                    }},
                    "processing_summary": {{
                        "total_processing_steps": 6,
                        "files_created_count": 2,
                        "professional_grade": true
                    }},
                    "metadata_path": "/path/to/synchronization_metadata.json"
                }}
                
                Key deliverables:
                - High-quality MP4 reel file ready for social media platforms
                - Perfect audio-video synchronization with professional transitions
                - Comprehensive processing metadata for quality assessment
                - Platform-optimized output (1080x1920, 30fps, optimal compression)
            """)
        )
    
    def qa_testing_task(self, agent, synchronization_result, context):
        """Comprehensive quality assessment with intelligent reloop system"""
        
        # Extract synchronization data for QA analysis
        if isinstance(synchronization_result, str):
            try:
                import json
                sync_data = json.loads(synchronization_result)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"⚠️  Failed to parse synchronization_result JSON: {e}")
                sync_data = {"status": "parse_error", "error": str(e)}
        else:
            sync_data = synchronization_result or {"status": "unknown"}
        
        return Task(
            description=dedent(f"""
                PHASE 7: COMPREHENSIVE QUALITY ASSESSMENT & INTELLIGENT RELOOP SYSTEM
                Execute advanced multi-dimensional quality assessment and determine strategic reloop requirements for professional social media reels.
                
                **SYNCHRONIZATION INPUT DATA**:
                Phase 6 Results: {sync_data.get('status', 'unknown')} status
                Final Reel: {sync_data.get('final_reel_path', 'unknown')}
                Processing Quality: {sync_data.get('video_stitching', {}).get('quality', 'unknown')}
                Audio Sync: {sync_data.get('audio_synchronization', {}).get('sync_quality', 'unknown')}
                
                **CONTEXT DATA**:
                - Platform: {context.get('platform', 'instagram')}
                - Duration: {context.get('duration', 20)} seconds
                - Content Mode: {context.get('content_mode', 'music')}
                - User Prompt: {context.get('user_prompt', '')}
                
                **COMPREHENSIVE QUALITY ASSESSMENT FRAMEWORK**:
                
                **DIMENSION 1: TECHNICAL QUALITY ANALYSIS** (Weight: 25%, Threshold: ≥0.80)
                - File integrity validation and technical compliance assessment
                - Resolution optimization verification (1080x1920 standard for Instagram/TikTok)
                - Audio-video synchronization accuracy evaluation
                - Compression quality and format compliance validation
                - Platform compatibility and technical requirements verification
                
                **DIMENSION 2: CONTENT QUALITY EVALUATION** (Weight: 25%, Threshold: ≥0.75)
                - Narrative flow and coherence analysis with Claude enhancement when available
                - Visual appeal and professional presentation assessment
                - Content structure and pacing evaluation
                - Creative quality and engagement factor analysis
                - Scene transitions and visual continuity validation
                
                **DIMENSION 3: BRAND ALIGNMENT ASSESSMENT** (Weight: 20%, Threshold: ≥0.85)
                - Brand voice consistency evaluation based on user prompt analysis
                - Messaging alignment with intended brand communication
                - Professional presentation standards enforcement
                - Content appropriateness and brand safety validation
                
                **DIMENSION 4: PLATFORM OPTIMIZATION** (Weight: 15%, Threshold: ≥0.80)
                - Platform-specific requirement compliance (Instagram: 15-30s, TikTok: 9-21s)
                - Format and resolution standards enforcement
                - Audio optimization for platform algorithms
                - Engagement-optimized duration and pacing validation
                
                **DIMENSION 5: ENGAGEMENT POTENTIAL PREDICTION** (Weight: 15%, Threshold: ≥0.70)
                - Social media performance prediction based on content analysis
                - Platform algorithm optimization assessment
                - Audience retention and engagement factor evaluation
                - Virability and shareability potential analysis
                
                **INTELLIGENT RELOOP DECISION SYSTEM**:
                
                **PASS CRITERIA**: Overall weighted score ≥ 0.76 AND no individual dimension below critical thresholds
                
                **RELOOP STRATEGIES** (Executed if quality assessment fails):
                
                1. **Parameter Adjustment Reloop** (Score: 0.65-0.76, Technical Issues):
                   - Focus: File integrity, resolution compliance, sync optimization
                   - Cost: Minimal processing time
                   - Timeline: 5-15 minutes
                   - Success Indicators: Technical score > 0.80, File integrity resolved
                
                2. **Prompt Refinement Reloop** (Score: 0.60-0.76, Content Issues):
                   - Focus: Claude-enhanced prompts, narrative improvement
                   - Cost: +$0.02-0.05 for Claude API calls
                   - Timeline: 10-20 minutes
                   - Success Indicators: Content quality > 0.75, Visual appeal improved
                
                3. **Model Switch Reloop** (Score: 0.55-0.75, Multiple Failures):
                   - Focus: Alternative AI model selection, quality comparison
                   - Cost: Varies by model selection (Runway Gen3, Pika Labs, Veo-2)
                   - Timeline: 20-40 minutes
                   - Success Indicators: Overall score improvement, Multiple criteria passing
                
                4. **Content Restructure Reloop** (Score: 0.50-0.70, Engagement/Structure Issues):
                   - Focus: Storyboard redesign, content flow optimization
                   - Cost: Moderate (partial regeneration)
                   - Timeline: 30-60 minutes
                   - Success Indicators: Engagement > 0.70, Improved narrative structure
                
                5. **Complete Regeneration Reloop** (Score: <0.50, Critical Failure):
                   - Focus: Full pipeline restart with lessons learned
                   - Cost: Full regeneration cost
                   - Timeline: 45-90 minutes
                   - Success Indicators: All quality criteria passing
                
                **MANDATORY TOOL USAGE**:
                YOU MUST use the "Advanced QA Testing Tool" to execute the comprehensive assessment.
                
                Required Tool Parameters:
                {{
                    "action": "comprehensive_assessment",
                    "reel_data": {sync_data},
                    "context": {context},
                    "output_folder": "[auto-detected from context]",
                    "claude_api_key": "[auto-detected from environment]"
                }}
                
                **COST-BENEFIT ANALYSIS REQUIREMENTS**:
                For each reloop recommendation, provide:
                - Projected quality improvement estimation
                - Cost-benefit ratio calculation and recommendation
                - Alternative strategy evaluation and ranking
                - Implementation timeline and resource requirements
                - Success probability and risk assessment
                
                **PROCESSING WORKFLOW**:
                1. Receive complete reel data from Phase 6 synchronization results
                2. Execute comprehensive multi-dimensional quality assessment using QA tool
                3. Analyze each quality dimension against professional thresholds
                4. Calculate weighted overall score and determine pass/fail status
                5. If failed: Analyze failure patterns and determine optimal reloop strategy
                6. Generate specific improvement recommendations with implementation guidance
                7. Provide cost-benefit analysis and projected outcomes
                8. Output final quality verdict or actionable reloop strategy
                
                **SUCCESS METRICS**:
                - Technical Quality ≥ 0.80 (file integrity, resolution, sync)
                - Content Quality ≥ 0.75 (narrative, visual appeal, coherence)
                - Brand Alignment ≥ 0.85 (voice consistency, messaging)
                - Platform Optimization ≥ 0.80 (requirements, duration, format)
                - Engagement Potential ≥ 0.70 (social media performance prediction)
                - Overall Weighted Score ≥ 0.76 (professional grade threshold)
                
                PHASE 6 SYNCHRONIZATION INPUT:
                {synchronization_result}
                
                CONTEXT INPUT:
                {context}
            """),
            agent=agent,
            expected_output=dedent("""
                Comprehensive Quality Assessment and Reloop Strategy Report in JSON format:
                
                {{
                    "quality_assessment": {{
                        "overall_score": 0.823,
                        "pass_status": "pass",
                        "quality_grade": "good",
                        "dimension_scores": {{
                            "technical_quality": 0.87,
                            "content_quality": 0.79,
                            "brand_alignment": 0.85,
                            "platform_optimization": 0.82,
                            "engagement_potential": 0.74
                        }},
                        "failed_criteria": [],
                        "detailed_breakdown": {{
                            "technical_details": {{"file_integrity": {{"score": 0.9}}, "resolution": {{"score": 1.0}}}},
                            "content_details": {{"narrative_flow": {{"score": 0.8}}, "visual_appeal": {{"score": 0.78}}}},
                            "threshold_comparison": {{"all_criteria_passed": true}}
                        }},
                        "processing_time": 2.34,
                        "claude_analysis_available": true
                    }},
                    "reloop_strategy": {{
                        "reloop_needed": false,
                        "strategy": "none",
                        "confidence": 1.0,
                        "reasoning": "Quality assessment passed all professional thresholds"
                    }},
                    "improvement_recommendations": {{
                        "priority_improvements": [],
                        "optional_enhancements": ["Consider adding subtle color grading for visual pop"],
                        "estimated_effort": "low"
                    }},
                    "final_verdict": {{
                        "approved_for_publication": true,
                        "quality_certification": "professional_grade",
                        "platform_readiness": ["instagram", "tiktok", "facebook"],
                        "confidence_score": 0.95
                    }},
                    "qa_report_path": "/path/to/comprehensive_qa_report.json"
                }}
                
                **FOR FAILED ASSESSMENTS** (when overall_score < 0.76):
                {{
                    "quality_assessment": {{
                        "overall_score": 0.658,
                        "pass_status": "fail",
                        "quality_grade": "needs_improvement",
                        "failed_criteria": ["technical_quality", "content_quality"],
                        // ... detailed breakdown
                    }},
                    "reloop_strategy": {{
                        "reloop_needed": true,
                        "strategy": "prompt_refinement",
                        "confidence": 0.85,
                        "focus_areas": ["narrative_flow", "visual_appeal", "content_coherence"],
                        "estimated_cost": "+$0.02-0.05",
                        "cost_benefit_analysis": {{
                            "projected_score": 0.768,
                            "estimated_improvement": 0.10,
                            "cost_benefit_ratio": 2.3,
                            "recommendation": "proceed"
                        }},
                        "implementation_guidance": {{
                            "priority_order": ["content_enhancement", "claude_optimization"],
                            "specific_actions": ["Use Claude to enhance prompts", "Improve narrative flow"],
                            "expected_timeline": "10-20 minutes",
                            "success_indicators": ["Content quality score > 0.75"]
                        }}
                    }},
                    "final_verdict": {{
                        "approved_for_publication": false,
                        "reloop_required": true,
                        "recommended_action": "Execute prompt_refinement reloop strategy"
                    }}
                }}
                
                Key deliverables:
                - Professional-grade quality assessment with detailed scoring
                - Strategic reloop recommendations with cost-benefit analysis
                - Specific improvement guidance and implementation timeline
                - Final publication approval or reloop execution plan
            """)
        )