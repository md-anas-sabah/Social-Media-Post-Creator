"""
Custom CrewAI tool for Claude prompt refinement
"""

from crewai.tools.base_tool import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import json
import re
from .claude_refinement import ClaudeRefinementService


class ClaudeRefinementInput(BaseModel):
    """Input schema for Claude refinement tool"""
    storyboard_data: Dict = Field(
        description="Storyboard data (dict) from content planning phase"
    )
    context: Dict = Field(
        description="Context data (dict) with platform, duration, content_mode, user_prompt"
    )


class ClaudeRefinementTool(BaseTool):
    name: str = "Claude Prompt Refinement Tool"
    description: str = (
        "Uses Claude AI to refine and optimize video generation prompts from storyboard data. "
        "Provides enhanced prompts with quality predictions, model recommendations, and technical parameters."
    )
    args_schema: Type[BaseModel] = ClaudeRefinementInput

    def _run(self, storyboard_data: Dict, context: Dict) -> str:
        """Execute Claude prompt refinement"""
        try:
            # Input is already dict format, no need to parse JSON
            storyboard_dict = storyboard_data
            context_dict = context
            
            # Ensure context has required fields
            if not isinstance(context_dict, dict):
                context_dict = {
                    'platform': 'instagram',
                    'duration': 20,
                    'content_mode': 'music',
                    'user_prompt': 'video reel'
                }
            
            # Initialize Claude refinement service
            claude_service = ClaudeRefinementService()
            
            # Refine prompts using Claude AI
            refined_result = claude_service.refine_video_prompts(
                storyboard_data=storyboard_dict,
                context=context_dict
            )
            
            # Return JSON string result
            return json.dumps(refined_result, indent=2)
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'message': 'Claude refinement failed, using fallback enhancement'
            }
            return json.dumps(error_result, indent=2)