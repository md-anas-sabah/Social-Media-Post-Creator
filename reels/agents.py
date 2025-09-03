"""
Reel-specific agents for video generation workflow
"""

from crewai import Agent
from textwrap import dedent


class ReelAgents:
    """Specialized agents for video reel generation"""
    
    def content_planning_agent(self):
        """Smart content analysis and mode selection"""
        return Agent(
            role='Content Planning Specialist',
            goal='Analyze user prompts and create intelligent storyboards for video reels',
            backstory=dedent("""
                You are an expert content strategist specializing in social media video content.
                You understand how to break down concepts into engaging visual sequences
                and determine the optimal content mode (music vs narration) based on content type.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def claude_refinement_agent(self):
        """Claude-powered prompt optimization"""
        return Agent(
            role='Prompt Refinement Expert',
            goal='Optimize video generation prompts for maximum quality using Claude AI',
            backstory=dedent("""
                You are a prompt engineering specialist with deep knowledge of AI video generation.
                You excel at transforming basic prompts into professional specifications
                that produce high-quality, engaging video content.
            """),
            verbose=True,
            allow_delegation=False
        )
    
    def video_generation_agent(self, output_folder):
        """Multi-model video generation with fallbacks"""
        return Agent(
            role='Video Generation Specialist',
            goal='Generate high-quality video clips using FAL.AI models',
            backstory=dedent(f"""
                You are an expert in AI video generation with access to multiple models.
                You generate professional video clips and save them to {output_folder}.
                You handle fallback strategies when primary models fail.
            """),
            verbose=True,
            allow_delegation=False
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