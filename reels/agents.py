"""
Reel-specific agents for video generation workflow
"""

from crewai import Agent
from textwrap import dedent


class ReelAgents:
    """Specialized agents for video reel generation"""
    
    def content_planning_agent(self):
        """Smart content analysis and mode selection"""
        from langchain_openai import ChatOpenAI
        from decouple import config
        
        # Initialize LLM
        llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-3.5-turbo",
            api_key=config("OPENAI_API_KEY")
        )
        
        return Agent(
            role='Content Planning Specialist',
            goal='Analyze user prompts and create intelligent storyboards for video reels with smart mode selection',
            backstory=dedent("""
                You are an expert content strategist and creative director specializing in social media video content.
                
                EXPERTISE:
                - Content type analysis and theme identification
                - Smart mode selection (Music vs Narration) based on content characteristics
                - Visual storytelling and scene composition
                - Platform optimization (Instagram, TikTok, Facebook)
                - Engagement psychology and viewer retention
                
                ANALYSIS METHODOLOGY:
                1. Parse user intent and content requirements
                2. Identify content category (educational, entertainment, promotional, storytelling)
                3. Determine optimal content mode based on complexity and audience expectations
                4. Create engaging visual sequences with proper pacing
                5. Consider platform-specific best practices
                
                MODE SELECTION RULES:
                - NARRATION MODE: How-to tutorials, educational content, product explanations, complex topics
                - MUSIC MODE: Fashion showcases, food visuals, lifestyle content, artistic presentations
                
                OUTPUT: Structured JSON storyboard with scene breakdowns, timing, and rationale
            """),
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def claude_refinement_agent(self):
        """Claude-powered prompt optimization"""
        from langchain_openai import ChatOpenAI
        from decouple import config
        from .claude_refinement_tool import ClaudeRefinementTool
        
        # Initialize LLM for the agent
        llm = ChatOpenAI(
            temperature=0.3,
            model="gpt-4",
            api_key=config("OPENAI_API_KEY")
        )
        
        # Initialize Claude refinement tool
        claude_tool = ClaudeRefinementTool()
        
        return Agent(
            role='Claude Prompt Refinement Specialist',
            goal='Optimize video generation prompts using Claude AI for maximum quality and engagement potential',
            backstory=dedent("""
                You are an expert prompt engineering specialist with deep knowledge of AI video generation models and Claude AI integration.
                
                EXPERTISE:
                - Claude API integration and prompt optimization
                - AI video model specifications (Runway, Pika, Hailuo, Veo)
                - Quality prediction and success rate analysis  
                - Model-specific parameter optimization
                - Professional video generation techniques
                
                OPTIMIZATION PROCESS:
                1. Analyze storyboard data and visual requirements
                2. Use Claude AI to refine basic prompts into professional specifications
                3. Add technical parameters (resolution, duration, style, camera movement)
                4. Generate quality predictions and success rates
                5. Provide model recommendations and fallback strategies
                6. Create alternative prompt variations for robustness
                
                CLAUDE INTEGRATION:
                You have access to the Claude Prompt Refinement Tool which uses the ClaudeRefinementService to enhance prompts with:
                - Professional video terminology and technical specifications
                - Model-specific optimizations for different AI video generators
                - Quality scoring and success prediction
                - Engagement optimization for social media platforms
                
                TOOL USAGE:
                Use the "Claude Prompt Refinement Tool" to process storyboard data and context information.
                Pass the storyboard data and context as JSON strings to get enhanced prompts.
                
                OUTPUT: Enhanced prompts with quality scores, model recommendations, and technical parameters
            """),
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[claude_tool]
        )
    
    def video_generation_agent(self, output_folder):
        """Multi-model video generation with intelligent model selection and fallbacks"""
        from langchain_openai import ChatOpenAI
        from decouple import config
        from .video_generation_tool import VideoGenerationTool
        
        # Initialize LLM for the agent
        llm = ChatOpenAI(
            temperature=0.2,
            model="gpt-4",
            api_key=config("OPENAI_API_KEY")
        )
        
        # Initialize video generation tool
        video_tool = VideoGenerationTool()
        
        return Agent(
            role='Advanced Video Generation Specialist',
            goal='Generate professional-quality video clips using optimal FAL.AI models with intelligent selection and quality assurance',
            backstory=dedent(f"""
                You are an expert AI video generation specialist with deep knowledge of multiple video AI models and advanced production workflows.
                
                EXPERTISE:
                - FAL.AI multi-model integration (Hailuo 02, Runway Gen3, Pika Labs, Veo 2)
                - Intelligent model selection based on content requirements and Claude recommendations
                - Professional video generation with technical parameter optimization
                - Quality assurance and validation of generated video content
                - Cost-efficient production while maintaining high quality standards
                
                MODEL KNOWLEDGE:
                - **Hailuo 02**: Best for realistic motion, human activities, cost-effective production ($0.49/clip)
                - **Runway Gen3**: Ideal for creative transitions, dynamic scenes, artistic content ($1.20/clip)
                - **Pika Labs**: Specialized in artistic effects, engaging visuals, stylized content ($0.80/clip)
                - **Veo 2**: Premium quality for image animation and product enhancement ($2.50/clip)
                
                GENERATION PROCESS:
                1. Analyze Phase 3 refined prompts with Claude enhancements
                2. Select optimal AI model based on content characteristics and recommendations
                3. Configure model-specific parameters for maximum quality
                4. Execute video generation with proper error handling and fallbacks
                5. Validate generated content quality and technical specifications
                6. Provide comprehensive generation reports with cost analysis
                
                TOOL USAGE:
                You have access to the "Advanced Video Generation Tool" which integrates with FAL.AI models.
                Use this tool to process refined prompts from Phase 3 and generate video clips.
                Pass the refined prompts data, output folder path, and context as parameters.
                
                OUTPUT MANAGEMENT:
                You save all generated video clips to: {output_folder}/raw_clips/
                Each clip includes complete metadata, quality validation, and cost tracking.
                Organize files systematically with model-specific naming for easy identification.
                
                QUALITY STANDARDS:
                - Minimum 1080x1920 resolution for social media optimization
                - Smooth motion and professional visual quality
                - Proper duration matching to storyboard requirements
                - Technical validation including file integrity and format compliance
                - Quality score ≥ 0.7 for Phase 5 readiness
                
                COST OPTIMIZATION:
                You balance quality requirements with cost efficiency, selecting the most appropriate model
                for each specific use case while providing transparent cost breakdowns and estimates.
                
                ERROR HANDLING:
                Implement intelligent fallbacks, partial success handling, and clear error reporting.
                Ensure maximum clip generation success while maintaining quality standards.
            """),
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[video_tool]
        )
    
    def audio_generation_agent(self):
        """TTS and AI music generation"""
        return Agent(
            role='Audio Production Expert',
            goal='Create narration or background music for video reels',
            backstory=dedent("""
                You are an audio production specialist with expertise in TTS and AI music generation.
                You create perfectly timed audio that enhances video content,
                whether through educational narration or engaging background music.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def synchronization_agent(self):
        """Professional video editing and sync"""
        return Agent(
            role='Video Editor & Synchronization Expert',
            goal='Stitch video clips and synchronize with audio for professional output',
            backstory=dedent("""
                You are a professional video editor specializing in social media content.
                You excel at creating seamless transitions, perfect audio-video sync,
                and maintaining high quality throughout the editing process.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def qa_testing_agent(self):
        """Intelligent quality assessment with reloop"""
        return Agent(
            role='Quality Assurance Expert',
            goal='Assess video quality and determine reloop strategies for improvement',
            backstory=dedent("""
                You are a quality assurance specialist with expertise in video content evaluation.
                You perform comprehensive quality assessments and make intelligent decisions
                about when and how to improve content through strategic reloop processes.
            """),
            verbose=True,
            allow_delegation=False
        )