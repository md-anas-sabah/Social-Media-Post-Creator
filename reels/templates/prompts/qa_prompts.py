"""
Quality assessment prompt templates for reel evaluation
"""

QA_ASSESSMENT_PROMPTS = {
    'technical_quality': """
Assess the technical quality of this video reel:

EVALUATION CRITERIA:
1. Resolution and Visual Clarity (0-100)
   - Is the video sharp and clear?
   - Appropriate resolution for platform?
   - No pixelation or compression artifacts?

2. Audio-Video Synchronization (0-100) 
   - Is audio perfectly synced with video?
   - No delays or timing issues?
   - Audio quality consistent throughout?

3. Compression and File Quality (0-100)
   - Appropriate file size for quality?
   - No compression artifacts?
   - Smooth playback?

4. Technical Specifications (0-100)
   - Correct aspect ratio (1080x1920)?
   - Appropriate frame rate?
   - Platform-optimized format?

Provide scores for each criterion and overall technical score (0-100).
""",

    'content_quality': """
Evaluate the content quality and engagement potential:

EVALUATION CRITERIA:
1. Visual Appeal (0-100)
   - Aesthetically pleasing composition?
   - Good use of colors and lighting?
   - Professional visual quality?

2. Narrative Flow (0-100)
   - Clear beginning, middle, end?
   - Smooth transitions between scenes?
   - Logical progression of content?

3. Engagement Hooks (0-100)
   - Strong opening within first 3 seconds?
   - Maintains viewer interest throughout?
   - Compelling call-to-action or conclusion?

4. Content Relevance (0-100)
   - Matches user's original prompt?
   - Appropriate for target audience?
   - Valuable or entertaining content?

Provide scores and overall content quality assessment (0-100).
""",

    'brand_alignment': """
Assess brand alignment and messaging consistency:

EVALUATION CRITERIA:
1. Brand Voice Consistency (0-100)
   - Matches intended brand personality?
   - Appropriate tone and style?
   - Professional representation?

2. Visual Brand Elements (0-100)
   - Consistent with brand aesthetics?
   - Appropriate color schemes?
   - Professional visual standards?

3. Messaging Clarity (0-100)
   - Clear and coherent message?
   - Aligns with brand values?
   - Appropriate messaging for platform?

4. Target Audience Fit (0-100)
   - Appeals to intended audience?
   - Age-appropriate content?
   - Cultural sensitivity maintained?

Provide brand alignment score (0-100) and specific feedback.
""",

    'platform_optimization': """
Evaluate platform-specific optimization:

PLATFORM-SPECIFIC CRITERIA:
1. Format Optimization (0-100)
   - Correct aspect ratio for platform?
   - Appropriate duration for platform?
   - Mobile-friendly viewing experience?

2. Algorithm Friendliness (0-100)
   - Uses platform-preferred features?
   - Optimized for discovery?
   - Follows platform best practices?

3. Engagement Optimization (0-100)
   - Designed to encourage interaction?
   - Shareable content structure?
   - Clear call-to-action appropriate for platform?

4. Trend Alignment (0-100)
   - Uses current platform trends appropriately?
   - Contemporary style and approach?
   - Viral potential indicators?

Provide platform optimization score (0-100) and recommendations.
""",

    'engagement_potential': """
Predict social media engagement potential:

ENGAGEMENT FACTORS:
1. Hook Effectiveness (0-100)
   - Grabs attention in first 3 seconds?
   - Creates curiosity or emotional response?
   - Encourages continued viewing?

2. Shareability Factor (0-100)
   - Contains shareable moments?
   - Emotionally compelling content?
   - Memorable or quotable elements?

3. Comment Generation (0-100)
   - Likely to spark discussion?
   - Contains conversation starters?
   - Encourages user interaction?

4. Retention Likelihood (0-100)
   - Maintains interest throughout?
   - Satisfying conclusion?
   - Encourages rewatching?

5. Viral Potential (0-100)
   - Unique or surprising elements?
   - Trendy or timely content?
   - High entertainment or educational value?

Provide engagement prediction score (0-100) and key engagement drivers.
"""
}

RELOOP_STRATEGY_PROMPTS = {
    'prompt_refinement': """
Analyze the failed quality assessment and suggest prompt refinements:

CURRENT ISSUES: {failed_criteria}
QUALITY SCORES: {quality_scores}

REFINEMENT RECOMMENDATIONS:
1. Identify specific prompt weaknesses
2. Suggest enhanced descriptions
3. Recommend additional quality modifiers
4. Propose technical specification improvements
5. Suggest style or mood adjustments

Provide specific, actionable prompt refinements that address the quality issues.
Cost impact: +$0.02-0.05 per refinement iteration.
""",

    'model_switch': """
Recommend alternative AI model based on quality failures:

FAILED CRITERIA: {failed_criteria}
CURRENT MODEL PERFORMANCE: {current_scores}

MODEL RECOMMENDATIONS:
1. Analyze which model aspects failed
2. Suggest alternative models with strengths in failed areas
3. Predict improvement potential with model switch
4. Estimate cost impact of model change
5. Recommend fallback options

Provide model switch strategy with expected improvements.
""",

    'parameter_adjustment': """
Suggest technical parameter adjustments to improve quality:

QUALITY ISSUES: {technical_issues}
CURRENT PARAMETERS: {current_parameters}

ADJUSTMENT RECOMMENDATIONS:
1. Resolution or format changes
2. Frame rate optimizations  
3. Compression setting adjustments
4. Audio quality improvements
5. Synchronization timing fixes

Provide specific parameter changes with minimal cost impact.
""",

    'content_restructure': """
Recommend content structure changes for major quality improvements:

MAJOR QUALITY FAILURES: {quality_report}
CONTENT ANALYSIS: {content_analysis}

RESTRUCTURE RECOMMENDATIONS:
1. Storyboard revision suggestions
2. Scene reordering or replacement
3. Pacing and timing adjustments
4. Content focus refinements
5. Narrative structure improvements

Provide comprehensive restructure plan for significant quality gains.
Cost impact: Moderate (new content generation required).
"""
}

IMPROVEMENT_SUGGESTION_PROMPTS = {
    'visual_improvements': """
Suggest specific visual improvements based on quality assessment:

VISUAL ISSUES IDENTIFIED: {visual_problems}

IMPROVEMENT SUGGESTIONS:
- Lighting and color adjustments
- Composition and framing enhancements
- Visual effects or filters recommendations
- Transition improvements
- Overall aesthetic refinements

Provide actionable visual improvement recommendations.
""",

    'audio_improvements': """
Recommend audio enhancements for better quality:

AUDIO ISSUES: {audio_problems}

ENHANCEMENT RECOMMENDATIONS:
- Volume level adjustments
- Audio quality improvements
- Synchronization fixes
- Sound design enhancements
- Music or narration refinements

Provide specific audio improvement strategies.
""",

    'engagement_improvements': """
Suggest ways to improve engagement potential:

ENGAGEMENT WEAKNESSES: {engagement_issues}

IMPROVEMENT STRATEGIES:
- Hook strengthening techniques
- Pacing optimization
- Call-to-action enhancements
- Shareability factor improvements
- Viral potential boosters

Provide engagement optimization recommendations.
""",

    'platform_improvements': """
Recommend platform-specific optimizations:

PLATFORM: {platform}
OPTIMIZATION GAPS: {platform_issues}

PLATFORM-SPECIFIC IMPROVEMENTS:
- Format and technical optimizations
- Algorithm-friendly adjustments
- Trend alignment improvements
- Engagement feature utilization
- Discovery optimization

Provide platform-optimized improvement suggestions.
"""
}


def get_qa_prompt(assessment_type: str, context_data: dict = None) -> str:
    """Get quality assessment prompt for specific evaluation type"""
    
    base_prompt = QA_ASSESSMENT_PROMPTS.get(assessment_type, "")
    
    if context_data:
        # Format prompt with context data
        try:
            base_prompt = base_prompt.format(**context_data)
        except KeyError:
            # If formatting fails, return base prompt
            pass
    
    return base_prompt


def get_reloop_prompt(strategy: str, failure_data: dict) -> str:
    """Get reloop strategy prompt with failure context"""
    
    base_prompt = RELOOP_STRATEGY_PROMPTS.get(strategy, "")
    
    try:
        formatted_prompt = base_prompt.format(**failure_data)
        return formatted_prompt
    except (KeyError, ValueError):
        return base_prompt


def get_improvement_prompt(improvement_type: str, issue_data: dict) -> str:
    """Get improvement suggestion prompt with issue context"""
    
    base_prompt = IMPROVEMENT_SUGGESTION_PROMPTS.get(improvement_type, "")
    
    try:
        formatted_prompt = base_prompt.format(**issue_data)
        return formatted_prompt
    except (KeyError, ValueError):
        return base_prompt


def generate_comprehensive_qa_prompt(reel_data: dict, platform: str = 'instagram') -> str:
    """Generate comprehensive quality assessment prompt"""
    
    comprehensive_prompt = f"""
COMPREHENSIVE REEL QUALITY ASSESSMENT

REEL DETAILS:
- Platform: {platform}
- Duration: {reel_data.get('duration', 'N/A')} seconds
- Content Type: {reel_data.get('content_type', 'N/A')}
- Mode: {reel_data.get('content_mode', 'N/A')}

ASSESSMENT REQUIREMENTS:
1. Technical Quality Analysis (25% weight)
2. Content Quality Evaluation (25% weight) 
3. Brand Alignment Assessment (20% weight)
4. Platform Optimization Review (15% weight)
5. Engagement Potential Prediction (15% weight)

For each category, provide:
- Individual scores (0-100)
- Specific feedback and observations
- Improvement recommendations if below threshold
- Overall category assessment

FINAL OUTPUT:
- Overall Quality Score (weighted average)
- Pass/Fail determination (>76 = Pass)
- Priority improvement areas
- Reloop strategy recommendation if failed
- Estimated improvement timeline and cost

Provide detailed, actionable assessment with specific recommendations.
"""
    
    return comprehensive_prompt