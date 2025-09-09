"""
Intelligent Reloop Execution System
Implements strategic reloop operations based on QA assessment results
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime


class ReloopExecutionManager:
    """Manages the execution of intelligent reloop strategies"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.reloop_history = []
        self.reloop_log_path = os.path.join(output_folder, 'reloop_execution_log.json')
    
    def execute_reloop_strategy(self, qa_report: Dict, reloop_strategy: Dict, context: Dict) -> Dict[str, Any]:
        """Execute the recommended reloop strategy"""
        strategy_name = reloop_strategy.get('strategy', 'unknown')
        
        self._log_reloop_start(strategy_name, qa_report, reloop_strategy)
        
        if not reloop_strategy.get('reloop_needed', False):
            return {
                'status': 'no_reloop_needed',
                'message': 'Quality assessment passed - no reloop required',
                'original_score': qa_report.get('overall_score', 0)
            }
        
        # Execute specific strategy
        if strategy_name == 'parameter_adjustment':
            return self._execute_parameter_adjustment(qa_report, reloop_strategy, context)
        elif strategy_name == 'prompt_refinement':
            return self._execute_prompt_refinement(qa_report, reloop_strategy, context)
        elif strategy_name == 'model_switch':
            return self._execute_model_switch(qa_report, reloop_strategy, context)
        elif strategy_name == 'content_restructure':
            return self._execute_content_restructure(qa_report, reloop_strategy, context)
        elif strategy_name == 'complete_regeneration':
            return self._execute_complete_regeneration(qa_report, reloop_strategy, context)
        else:
            return {
                'status': 'error',
                'message': f'Unknown reloop strategy: {strategy_name}',
                'strategy': strategy_name
            }
    
    def _execute_parameter_adjustment(self, qa_report: Dict, strategy: Dict, context: Dict) -> Dict[str, Any]:
        """Execute parameter adjustment reloop strategy"""
        self._log("Executing parameter adjustment reloop")
        
        # Identify specific technical issues to fix
        technical_details = qa_report.get('technical_details', {})
        failed_criteria = qa_report.get('failed_criteria', [])
        
        adjustments_made = []
        
        # File integrity fixes
        if 'technical_quality' in failed_criteria:
            file_issues = technical_details.get('details', {}).get('file_integrity', {}).get('issues', [])
            
            if 'file_too_small' in file_issues:
                adjustments_made.append('Increase video compression quality settings')
            if 'file_too_large' in file_issues:
                adjustments_made.append('Optimize compression for file size')
            if 'sync_quality_low' in file_issues:
                adjustments_made.append('Improve audio-video synchronization timing')
        
        # Resolution fixes
        resolution_issues = technical_details.get('details', {}).get('resolution_compliance', {}).get('issues', [])
        if 'resolution_suboptimal' in resolution_issues:
            adjustments_made.append('Adjust output resolution to 1080x1920')
        
        # Simulate parameter adjustment execution
        execution_result = {
            'status': 'completed',
            'strategy': 'parameter_adjustment',
            'adjustments_made': adjustments_made,
            'estimated_improvement': strategy.get('cost_benefit_analysis', {}).get('estimated_improvement', 0.05),
            'processing_time': '5-15 minutes',
            'cost': 'minimal',
            'next_steps': 'Re-run video synchronization with adjusted parameters'
        }
        
        self._log(f"Parameter adjustment completed: {len(adjustments_made)} adjustments made")
        return execution_result
    
    def _execute_prompt_refinement(self, qa_report: Dict, strategy: Dict, context: Dict) -> Dict[str, Any]:
        """Execute prompt refinement reloop strategy"""
        self._log("Executing prompt refinement reloop")
        
        # Identify content issues to address
        content_details = qa_report.get('content_details', {})
        failed_criteria = qa_report.get('failed_criteria', [])
        
        refinements_made = []
        
        # Content quality improvements
        if 'content_quality' in failed_criteria:
            content_issues = content_details.get('issues', [])
            
            if 'no_claude_analysis' in content_issues:
                refinements_made.append('Enable Claude API for enhanced content analysis')
            if 'narrative_flow_poor' in content_issues:
                refinements_made.append('Enhance narrative structure and scene flow')
            if 'visual_appeal_low' in content_issues:
                refinements_made.append('Improve visual descriptions and creative elements')
        
        # Generate enhanced prompts using Claude
        original_prompts = self._extract_original_prompts(context)
        enhanced_prompts = self._enhance_prompts_with_claude(original_prompts, qa_report)
        
        execution_result = {
            'status': 'completed',
            'strategy': 'prompt_refinement',
            'refinements_made': refinements_made,
            'original_prompts': original_prompts,
            'enhanced_prompts': enhanced_prompts,
            'estimated_improvement': strategy.get('cost_benefit_analysis', {}).get('estimated_improvement', 0.10),
            'processing_time': '10-20 minutes',
            'cost': '+$0.02-0.05',
            'next_steps': 'Re-run video generation with enhanced prompts'
        }
        
        self._log(f"Prompt refinement completed: {len(refinements_made)} improvements made")
        return execution_result
    
    def _execute_model_switch(self, qa_report: Dict, strategy: Dict, context: Dict) -> Dict[str, Any]:
        """Execute model switch reloop strategy"""
        self._log("Executing model switch reloop")
        
        # Analyze current model performance and suggest alternatives
        current_model = self._identify_current_model(context)
        failed_criteria = qa_report.get('failed_criteria', [])
        
        # Model recommendation logic
        model_recommendations = []
        
        if 'technical_quality' in failed_criteria:
            model_recommendations.append({
                'model': 'runway-gen3',
                'reason': 'Better technical quality and resolution handling',
                'cost_per_clip': '$1.20'
            })
        
        if 'content_quality' in failed_criteria:
            model_recommendations.append({
                'model': 'veo-2',
                'reason': 'Superior content quality and visual appeal',
                'cost_per_clip': '$2.50'
            })
        
        if 'engagement_potential' in failed_criteria:
            model_recommendations.append({
                'model': 'pika-labs',
                'reason': 'Optimized for social media engagement',
                'cost_per_clip': '$0.80'
            })
        
        # Default fallback
        if not model_recommendations:
            model_recommendations.append({
                'model': 'runway-gen3',
                'reason': 'General quality improvement',
                'cost_per_clip': '$1.20'
            })
        
        recommended_model = model_recommendations[0]  # Select top recommendation
        
        execution_result = {
            'status': 'completed',
            'strategy': 'model_switch',
            'current_model': current_model,
            'recommended_model': recommended_model['model'],
            'switch_reason': recommended_model['reason'],
            'all_recommendations': model_recommendations,
            'estimated_improvement': strategy.get('cost_benefit_analysis', {}).get('estimated_improvement', 0.08),
            'processing_time': '20-40 minutes',
            'cost': recommended_model['cost_per_clip'],
            'next_steps': f'Re-run video generation with {recommended_model["model"]} model'
        }
        
        self._log(f"Model switch completed: {current_model} → {recommended_model['model']}")
        return execution_result
    
    def _execute_content_restructure(self, qa_report: Dict, strategy: Dict, context: Dict) -> Dict[str, Any]:
        """Execute content restructure reloop strategy"""
        self._log("Executing content restructure reloop")
        
        # Analyze structural issues
        failed_criteria = qa_report.get('failed_criteria', [])
        
        restructure_actions = []
        
        if 'engagement_potential' in failed_criteria:
            engagement_details = qa_report.get('engagement_details', {})
            factors = engagement_details.get('factors', [])
            
            if 'too_long' in factors:
                restructure_actions.append('Reduce total duration for better engagement')
            elif 'too_short' in factors:
                restructure_actions.append('Extend content with additional scenes')
            
            if 'no_audio' in factors:
                restructure_actions.append('Add compelling audio track or narration')
        
        if 'content_quality' in failed_criteria:
            restructure_actions.append('Redesign storyboard with improved narrative flow')
            restructure_actions.append('Enhance scene transitions and pacing')
        
        if 'platform_optimization' in failed_criteria:
            platform = context.get('platform', 'instagram')
            restructure_actions.append(f'Optimize content structure for {platform} algorithm')
        
        # Generate new content structure
        original_structure = self._extract_content_structure(context)
        improved_structure = self._design_improved_structure(original_structure, qa_report, context)
        
        execution_result = {
            'status': 'completed',
            'strategy': 'content_restructure',
            'restructure_actions': restructure_actions,
            'original_structure': original_structure,
            'improved_structure': improved_structure,
            'estimated_improvement': strategy.get('cost_benefit_analysis', {}).get('estimated_improvement', 0.15),
            'processing_time': '30-60 minutes',
            'cost': 'moderate',
            'next_steps': 'Re-run complete content planning with new structure'
        }
        
        self._log(f"Content restructure completed: {len(restructure_actions)} structural changes")
        return execution_result
    
    def _execute_complete_regeneration(self, qa_report: Dict, strategy: Dict, context: Dict) -> Dict[str, Any]:
        """Execute complete regeneration reloop strategy"""
        self._log("Executing complete regeneration reloop")
        
        # Analyze all failure points for complete restart
        overall_score = qa_report.get('overall_score', 0)
        failed_criteria = qa_report.get('failed_criteria', [])
        
        regeneration_focus = []
        
        # Comprehensive analysis of all failures
        if 'technical_quality' in failed_criteria:
            regeneration_focus.append('Improved technical settings and validation')
        if 'content_quality' in failed_criteria:
            regeneration_focus.append('Enhanced content creation and Claude integration')
        if 'brand_alignment' in failed_criteria:
            regeneration_focus.append('Better brand voice and messaging alignment')
        if 'platform_optimization' in failed_criteria:
            regeneration_focus.append('Platform-specific optimization from start')
        if 'engagement_potential' in failed_criteria:
            regeneration_focus.append('Engagement-first content design approach')
        
        # Lessons learned compilation
        lessons_learned = self._compile_lessons_learned(qa_report, context)
        
        execution_result = {
            'status': 'completed',
            'strategy': 'complete_regeneration',
            'failure_analysis': {
                'original_score': overall_score,
                'critical_failures': len(failed_criteria),
                'failure_reasons': failed_criteria
            },
            'regeneration_focus': regeneration_focus,
            'lessons_learned': lessons_learned,
            'estimated_improvement': strategy.get('cost_benefit_analysis', {}).get('estimated_improvement', 0.25),
            'processing_time': '45-90 minutes',
            'cost': 'full regeneration cost',
            'next_steps': 'Restart complete reel generation pipeline with improvements'
        }
        
        self._log(f"Complete regeneration planned: {len(regeneration_focus)} focus areas identified")
        return execution_result
    
    def _extract_original_prompts(self, context: Dict) -> List[str]:
        """Extract original prompts for refinement"""
        # This would typically extract from previous phase results
        return [
            context.get('user_prompt', 'Create engaging social media content'),
            "Scene 1: Opening hook and brand introduction",
            "Scene 2: Main content demonstration or story",
            "Scene 3: Call to action and conclusion"
        ]
    
    def _enhance_prompts_with_claude(self, prompts: List[str], qa_report: Dict) -> List[str]:
        """Enhance prompts using Claude API (simulated for now)"""
        enhanced = []
        for prompt in prompts:
            # Simulate Claude enhancement
            enhanced_prompt = f"Enhanced: {prompt} [Optimized for visual appeal, narrative flow, and engagement]"
            enhanced.append(enhanced_prompt)
        return enhanced
    
    def _identify_current_model(self, context: Dict) -> str:
        """Identify currently used AI model"""
        # This would extract from video generation results
        return context.get('video_model', 'hailuo-02')
    
    def _extract_content_structure(self, context: Dict) -> Dict[str, Any]:
        """Extract current content structure"""
        return {
            'total_duration': context.get('duration', 20),
            'scene_count': 3,
            'content_mode': context.get('content_mode', 'music'),
            'platform': context.get('platform', 'instagram')
        }
    
    def _design_improved_structure(self, original: Dict, qa_report: Dict, context: Dict) -> Dict[str, Any]:
        """Design improved content structure based on QA feedback"""
        improved = original.copy()
        
        # Apply improvements based on failed criteria
        failed_criteria = qa_report.get('failed_criteria', [])
        
        if 'engagement_potential' in failed_criteria:
            # Optimize for engagement
            platform = context.get('platform', 'instagram')
            if platform == 'tiktok':
                improved['total_duration'] = min(improved['total_duration'], 15)
                improved['pacing'] = 'fast'
            elif platform == 'instagram':
                improved['total_duration'] = max(15, min(improved['total_duration'], 30))
                improved['pacing'] = 'dynamic'
        
        if 'content_quality' in failed_criteria:
            improved['scene_count'] = max(2, min(improved['scene_count'], 4))
            improved['transitions'] = 'enhanced'
            improved['narrative_flow'] = 'optimized'
        
        return improved
    
    def _compile_lessons_learned(self, qa_report: Dict, context: Dict) -> List[str]:
        """Compile lessons learned from current attempt"""
        lessons = []
        
        failed_criteria = qa_report.get('failed_criteria', [])
        
        for criterion in failed_criteria:
            if criterion == 'technical_quality':
                lessons.append('Focus on technical validation throughout pipeline')
            elif criterion == 'content_quality':
                lessons.append('Use Claude enhancement from Phase 3 onwards')
            elif criterion == 'brand_alignment':
                lessons.append('Strengthen brand voice consistency checks')
            elif criterion == 'platform_optimization':
                lessons.append('Apply platform-specific requirements from planning phase')
            elif criterion == 'engagement_potential':
                lessons.append('Prioritize engagement optimization in content design')
        
        # Add general lessons
        lessons.append('Implement continuous quality monitoring throughout pipeline')
        lessons.append('Use higher quality thresholds for earlier intervention')
        
        return lessons
    
    def _log_reloop_start(self, strategy: str, qa_report: Dict, reloop_strategy: Dict):
        """Log the start of reloop execution"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'strategy': strategy,
            'original_score': qa_report.get('overall_score', 0),
            'confidence': reloop_strategy.get('confidence', 0),
            'estimated_improvement': reloop_strategy.get('cost_benefit_analysis', {}).get('estimated_improvement', 0)
        }
        
        self.reloop_history.append(log_entry)
        self._save_reloop_log()
        self._log(f"Starting {strategy} reloop execution")
    
    def _save_reloop_log(self):
        """Save reloop execution log"""
        try:
            with open(self.reloop_log_path, 'w') as f:
                json.dump({
                    'reloop_history': self.reloop_history,
                    'total_reloops': len(self.reloop_history),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            self._log(f"Error saving reloop log: {str(e)}")
    
    def _log(self, message: str):
        """Add message to processing log"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"🔄 Reloop System: {message}")


class ReloopCoordinator:
    """Coordinates reloop execution with the main pipeline"""
    
    def __init__(self):
        self.execution_manager = None
    
    def coordinate_reloop(self, qa_report: Dict, output_folder: str, context: Dict) -> Dict[str, Any]:
        """Coordinate the complete reloop process"""
        self.execution_manager = ReloopExecutionManager(output_folder)
        
        # Extract reloop strategy from QA report
        reloop_strategy = qa_report.get('reloop_strategy', {})
        
        if not reloop_strategy.get('reloop_needed', False):
            return {
                'status': 'no_reloop_needed',
                'message': 'Quality passed - no reloop required',
                'qa_score': qa_report.get('quality_assessment', {}).get('overall_score', 0)
            }
        
        # Execute the reloop strategy
        execution_result = self.execution_manager.execute_reloop_strategy(
            qa_report.get('quality_assessment', {}),
            reloop_strategy,
            context
        )
        
        # Prepare coordination result
        coordination_result = {
            'reloop_executed': True,
            'strategy': reloop_strategy.get('strategy', 'unknown'),
            'execution_result': execution_result,
            'next_phase_to_execute': self._determine_next_phase(reloop_strategy),
            'coordination_timestamp': datetime.now().isoformat()
        }
        
        return coordination_result
    
    def _determine_next_phase(self, reloop_strategy: Dict) -> str:
        """Determine which phase to restart from based on strategy"""
        strategy = reloop_strategy.get('strategy', 'unknown')
        
        phase_mapping = {
            'parameter_adjustment': 'phase_6_synchronization',
            'prompt_refinement': 'phase_3_prompt_refinement',
            'model_switch': 'phase_4_video_generation',
            'content_restructure': 'phase_2_content_planning',
            'complete_regeneration': 'phase_1_foundation'
        }
        
        return phase_mapping.get(strategy, 'phase_6_synchronization')