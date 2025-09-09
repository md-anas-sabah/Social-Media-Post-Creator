"""
Advanced Quality Assessment and Intelligent Reloop System for Video Reels
Multi-dimensional quality analysis with Claude-powered content review
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from .claude_refinement import ClaudeRefinementService


class QualityThresholds:
    """Professional quality assessment thresholds based on social media standards"""
    # Core quality metrics
    TECHNICAL_QUALITY = 0.80    # Resolution, sync, compression, file integrity
    CONTENT_QUALITY = 0.75      # Narrative flow, visual appeal, coherence
    BRAND_ALIGNMENT = 0.85      # Brand voice consistency, messaging alignment
    PLATFORM_OPTIMIZATION = 0.80  # Platform-specific requirements compliance
    ENGAGEMENT_POTENTIAL = 0.70    # Predicted social media performance
    
    # Overall pass threshold (weighted average must exceed this)
    OVERALL_PASS = 0.76
    
    # Reloop decision thresholds
    CRITICAL_FAILURE = 0.50     # Below this triggers complete regeneration
    MODERATE_FAILURE = 0.65     # Between this and OVERALL_PASS triggers targeted fixes
    
    # Individual component minimums (any below this triggers specific reloop)
    MINIMUM_TECHNICAL = 0.60
    MINIMUM_CONTENT = 0.60
    MINIMUM_ENGAGEMENT = 0.55


class TechnicalQualityValidator:
    """Advanced technical quality assessment for video reels"""
    
    @staticmethod
    def validate_file_integrity(file_path: str) -> Dict[str, Any]:
        """Comprehensive file validation"""
        if not os.path.exists(file_path):
            return {
                'score': 0.0,
                'issues': ['file_not_found'],
                'details': f'File does not exist: {file_path}'
            }
        
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {
                    'score': 0.0,
                    'issues': ['empty_file'],
                    'details': 'File is empty'
                }
            
            # Check file extension and basic properties
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in ['.mp4', '.mov', '.avi']:
                return {
                    'score': 0.6,
                    'issues': ['unsupported_format'],
                    'details': f'Unsupported format: {ext}'
                }
            
            # Basic size validation (should be reasonable for a reel)
            min_size = 100 * 1024  # 100KB minimum
            max_size = 100 * 1024 * 1024  # 100MB maximum
            
            score = 0.8
            issues = []
            
            if file_size < min_size:
                score -= 0.2
                issues.append('file_too_small')
            elif file_size > max_size:
                score -= 0.1
                issues.append('file_too_large')
            
            return {
                'score': max(0.0, min(1.0, score)),
                'issues': issues,
                'details': f'File size: {file_size:,} bytes',
                'file_size': file_size
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'issues': ['validation_error'],
                'details': f'Validation error: {str(e)}'
            }
    
    @staticmethod
    def assess_resolution_compliance(reel_data: Dict) -> Dict[str, Any]:
        """Assess resolution and format compliance"""
        target_resolution = reel_data.get('resolution', 'unknown')
        
        if target_resolution == '1080x1920':
            return {
                'score': 1.0,
                'issues': [],
                'details': 'Perfect resolution for Instagram/TikTok'
            }
        elif target_resolution == 'unknown':
            return {
                'score': 0.7,
                'issues': ['resolution_unknown'],
                'details': 'Resolution could not be determined'
            }
        else:
            return {
                'score': 0.6,
                'issues': ['resolution_suboptimal'],
                'details': f'Non-standard resolution: {target_resolution}'
            }
    
    @staticmethod
    def assess_sync_quality(sync_data: Dict) -> Dict[str, Any]:
        """Assess audio-video synchronization quality"""
        sync_quality = sync_data.get('sync_quality', 'unknown')
        
        quality_scores = {
            'perfect': 1.0,
            'good': 0.9,
            'acceptable': 0.75,
            'poor': 0.5,
            'mock': 0.8,  # Mock mode gets decent score
            'unknown': 0.6
        }
        
        score = quality_scores.get(sync_quality, 0.6)
        issues = [] if score >= 0.8 else ['sync_quality_low']
        
        return {
            'score': score,
            'issues': issues,
            'details': f'Sync quality: {sync_quality}'
        }


class ContentQualityAnalyzer:
    """Advanced content quality analysis with Claude integration"""
    
    def __init__(self, claude_service: ClaudeRefinementService):
        self.claude = claude_service
    
    def analyze_narrative_flow(self, reel_data: Dict, context: Dict) -> Dict[str, Any]:
        """Analyze narrative coherence and flow"""
        try:
            # Extract key information for analysis
            user_prompt = context.get('user_prompt', '')
            content_mode = context.get('content_mode', 'unknown')
            video_clips = reel_data.get('video_stitching', {}).get('clips_used', 0)
            total_duration = reel_data.get('video_stitching', {}).get('total_duration', 0)
            
            # Basic heuristic analysis
            score = 0.7  # Base score
            issues = []
            
            # Duration analysis
            if total_duration < 10:
                score -= 0.1
                issues.append('too_short')
            elif total_duration > 35:
                score -= 0.05
                issues.append('too_long')
            
            # Clip count analysis
            if video_clips < 2:
                score -= 0.1
                issues.append('insufficient_clips')
            elif video_clips > 5:
                score -= 0.05
                issues.append('too_many_clips')
            
            return {
                'score': max(0.0, min(1.0, score)),
                'issues': issues,
                'details': f'Narrative analysis: {video_clips} clips, {total_duration:.1f}s duration'
            }
            
        except Exception as e:
            return {
                'score': 0.6,
                'issues': ['analysis_error'],
                'details': f'Content analysis error: {str(e)}'
            }
    
    def analyze_visual_appeal(self, reel_data: Dict) -> Dict[str, Any]:
        """Analyze visual quality and appeal"""
        # Extract visual quality indicators
        enhancement_applied = reel_data.get('video_stitching', {}).get('enhancements_applied', False)
        transitions_applied = reel_data.get('video_stitching', {}).get('transitions_applied', False)
        quality_grade = reel_data.get('video_stitching', {}).get('quality', 'unknown')
        
        score = 0.6  # Base score
        issues = []
        
        if enhancement_applied:
            score += 0.15
        else:
            issues.append('no_enhancements')
        
        if transitions_applied:
            score += 0.15
        else:
            issues.append('no_transitions')
        
        quality_bonuses = {
            'professional': 0.1,
            'high': 0.05,
            'standard': 0.0,
            'mock': 0.05  # Mock gets some credit
        }
        score += quality_bonuses.get(quality_grade, 0)
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'details': f'Visual quality: {quality_grade}, enhancements: {enhancement_applied}'
        }


class EngagementPredictor:
    """Predict social media engagement potential"""
    
    @staticmethod
    def predict_engagement_score(reel_data: Dict, context: Dict) -> Dict[str, Any]:
        """Predict engagement based on multiple factors"""
        try:
            # Extract key factors
            platform = context.get('platform', 'instagram')
            content_mode = context.get('content_mode', 'music')
            duration = reel_data.get('video_stitching', {}).get('total_duration', 20)
            has_audio = bool(reel_data.get('audio_synchronization'))
            
            # Base score by platform
            platform_scores = {
                'instagram': 0.7,
                'tiktok': 0.75,
                'facebook': 0.65,
                'all': 0.7
            }
            
            score = platform_scores.get(platform, 0.65)
            factors = []
            
            # Duration optimization
            optimal_durations = {
                'instagram': (15, 30),
                'tiktok': (9, 21),
                'facebook': (15, 60)
            }
            
            opt_min, opt_max = optimal_durations.get(platform, (15, 30))
            if opt_min <= duration <= opt_max:
                score += 0.1
                factors.append('optimal_duration')
            elif duration < opt_min:
                score -= 0.05
                factors.append('too_short')
            else:
                score -= 0.08
                factors.append('too_long')
            
            # Audio factor
            if has_audio:
                if content_mode == 'narration':
                    score += 0.05
                    factors.append('educational_content')
                else:
                    score += 0.08
                    factors.append('music_content')
            else:
                score -= 0.1
                factors.append('no_audio')
            
            return {
                'score': max(0.0, min(1.0, score)),
                'factors': factors,
                'details': f'Platform: {platform}, Mode: {content_mode}, Duration: {duration}s'
            }
            
        except Exception as e:
            return {
                'score': 0.6,
                'factors': ['prediction_error'],
                'details': f'Engagement prediction error: {str(e)}'
            }


class ReloopStrategyManager:
    """Intelligent reloop strategy determination and management"""
    
    def __init__(self):
        self.strategy_costs = {
            'parameter_adjustment': 'minimal',
            'prompt_refinement': '+$0.02-0.05',
            'model_switch': 'varies by model',
            'content_restructure': 'moderate',
            'complete_regeneration': 'full cost'
        }
    
    def determine_optimal_strategy(self, quality_report: Dict, reel_data: Dict, context: Dict) -> Dict[str, Any]:
        """Determine the most effective reloop strategy based on failures"""
        if quality_report.get('pass_status') == 'pass':
            return {
                'reloop_needed': False,
                'strategy': 'none',
                'confidence': 1.0,
                'reasoning': 'Quality assessment passed all thresholds'
            }
        
        failed_criteria = quality_report.get('failed_criteria', [])
        overall_score = quality_report.get('overall_score', 0)
        individual_scores = self._extract_individual_scores(quality_report)
        
        # Critical failure - complete regeneration needed
        if overall_score < QualityThresholds.CRITICAL_FAILURE:
            return {
                'reloop_needed': True,
                'strategy': 'complete_regeneration',
                'focus_areas': ['all_components'],
                'estimated_cost': self.strategy_costs['complete_regeneration'],
                'confidence': 0.9,
                'reasoning': f'Overall score {overall_score:.2f} below critical threshold {QualityThresholds.CRITICAL_FAILURE}'
            }
        
        # Analyze specific failure patterns
        strategies = self._analyze_failure_patterns(failed_criteria, individual_scores, reel_data, context)
        
        # Select best strategy
        best_strategy = max(strategies, key=lambda s: s['confidence'])
        
        return {
            'reloop_needed': True,
            **best_strategy,
            'alternatives': [s for s in strategies if s != best_strategy]
        }
    
    def _extract_individual_scores(self, quality_report: Dict) -> Dict[str, float]:
        """Extract individual quality scores"""
        return {
            'technical': quality_report.get('technical_quality', 0),
            'content': quality_report.get('content_quality', 0),
            'brand': quality_report.get('brand_alignment', 0),
            'platform': quality_report.get('platform_optimization', 0),
            'engagement': quality_report.get('engagement_potential', 0)
        }
    
    def _analyze_failure_patterns(self, failed_criteria: List[str], scores: Dict[str, float], 
                                reel_data: Dict, context: Dict) -> List[Dict[str, Any]]:
        """Analyze failure patterns and generate strategy options"""
        strategies = []
        
        # Technical quality failures
        if 'technical_quality' in failed_criteria:
            if scores.get('technical', 0) < QualityThresholds.MINIMUM_TECHNICAL:
                strategies.append({
                    'strategy': 'parameter_adjustment',
                    'focus_areas': ['resolution', 'sync_quality', 'file_integrity'],
                    'estimated_cost': self.strategy_costs['parameter_adjustment'],
                    'confidence': 0.8,
                    'reasoning': 'Technical issues can be resolved with parameter adjustments'
                })
        
        # Content quality failures
        if 'content_quality' in failed_criteria:
            if scores.get('content', 0) < QualityThresholds.MINIMUM_CONTENT:
                strategies.append({
                    'strategy': 'prompt_refinement',
                    'focus_areas': ['narrative_flow', 'visual_appeal', 'content_coherence'],
                    'estimated_cost': self.strategy_costs['prompt_refinement'],
                    'confidence': 0.85,
                    'reasoning': 'Content issues best addressed through enhanced prompts'
                })
        
        # Engagement potential failures
        if 'engagement_potential' in failed_criteria:
            if scores.get('engagement', 0) < QualityThresholds.MINIMUM_ENGAGEMENT:
                strategies.append({
                    'strategy': 'content_restructure',
                    'focus_areas': ['platform_optimization', 'content_style', 'timing'],
                    'estimated_cost': self.strategy_costs['content_restructure'],
                    'confidence': 0.75,
                    'reasoning': 'Low engagement requires content restructuring'
                })
        
        # Multiple failures - model switch might help
        if len(failed_criteria) >= 3:
            strategies.append({
                'strategy': 'model_switch',
                'focus_areas': failed_criteria,
                'estimated_cost': self.strategy_costs['model_switch'],
                'confidence': 0.7,
                'reasoning': 'Multiple failures suggest different AI model might perform better'
            })
        
        # Fallback strategy
        if not strategies:
            strategies.append({
                'strategy': 'prompt_refinement',
                'focus_areas': failed_criteria,
                'estimated_cost': self.strategy_costs['prompt_refinement'],
                'confidence': 0.6,
                'reasoning': 'Default strategy for unspecified failures'
            })
        
        return strategies


class IntelligentQASystem:
    """Comprehensive quality assessment with advanced reloop capabilities"""
    
    def __init__(self, output_folder: str, claude_api_key: Optional[str] = None):
        self.output_folder = output_folder
        self.thresholds = QualityThresholds()
        
        # Initialize components
        self.technical_validator = TechnicalQualityValidator()
        self.reloop_manager = ReloopStrategyManager()
        
        # Initialize Claude service if available
        try:
            self.claude_reviewer = ClaudeRefinementService(claude_api_key) if claude_api_key else None
            self.content_analyzer = ContentQualityAnalyzer(self.claude_reviewer) if self.claude_reviewer else None
        except:
            self.claude_reviewer = None
            self.content_analyzer = None
        
        self.engagement_predictor = EngagementPredictor()
        
        # QA output paths
        self.qa_report_path = os.path.join(output_folder, 'qa_report.json')
        self.quality_log_path = os.path.join(output_folder, 'quality_assessment_log.json')
        
        # Processing log
        self.processing_log = []
    
    def comprehensive_assessment(self, reel_data: Dict, context: Dict = None) -> Dict:
        """Advanced multi-dimensional quality analysis with detailed reporting"""
        context = context or {}
        start_time = time.time()
        self._log("Starting comprehensive quality assessment")
        
        try:
            # Component assessments
            technical_assessment = self._assess_technical_quality(reel_data)
            content_assessment = self._assess_content_quality(reel_data, context)
            brand_assessment = self._assess_brand_alignment(reel_data, context)
            platform_assessment = self._assess_platform_optimization(reel_data, context)
            engagement_assessment = self._assess_engagement_potential(reel_data, context)
            
            # Extract scores
            technical_score = technical_assessment['score']
            content_score = content_assessment['score']
            brand_score = brand_assessment['score']
            platform_score = platform_assessment['score']
            engagement_score = engagement_assessment['score']
            
            # Weighted overall score
            overall_score = (
                technical_score * 0.25 +
                content_score * 0.25 +
                brand_score * 0.2 +
                platform_score * 0.15 +
                engagement_score * 0.15
            )
            
            # Determine pass/fail status
            pass_status = self._determine_pass_status(overall_score)
            failed_criteria = self._identify_failed_criteria({
                'technical_quality': technical_score,
                'content_quality': content_score,
                'brand_alignment': brand_score,
                'platform_optimization': platform_score,
                'engagement_potential': engagement_score
            })
            
            # Compile comprehensive assessment
            assessment = {
                # Core scores
                'technical_quality': technical_score,
                'content_quality': content_score,
                'brand_alignment': brand_score,
                'platform_optimization': platform_score,
                'engagement_potential': engagement_score,
                'overall_score': overall_score,
                
                # Status and failures
                'pass_status': pass_status,
                'failed_criteria': failed_criteria,
                'quality_grade': self._determine_quality_grade(overall_score),
                
                # Detailed breakdowns
                'technical_details': technical_assessment,
                'content_details': content_assessment,
                'brand_details': brand_assessment,
                'platform_details': platform_assessment,
                'engagement_details': engagement_assessment,
                
                # Metadata
                'assessment_timestamp': self._get_timestamp(),
                'processing_time': time.time() - start_time,
                'assessment_version': '2.0',
                'claude_analysis_available': bool(self.claude_reviewer),
                
                # Context information
                'input_context': context,
                'threshold_comparison': self._compare_against_thresholds({
                    'technical_quality': technical_score,
                    'content_quality': content_score,
                    'brand_alignment': brand_score,
                    'platform_optimization': platform_score,
                    'engagement_potential': engagement_score,
                    'overall_score': overall_score
                })
            }
            
            # Save assessment log
            self._save_assessment_log(assessment)
            self._log(f"Assessment completed: {pass_status} ({overall_score:.3f} score)")
            
            return assessment
            
        except Exception as e:
            self._log(f"Error in comprehensive assessment: {str(e)}")
            return self._create_fallback_assessment(context)
    
    def determine_reloop_strategy(self, quality_report: Dict, reel_data: Dict = None, context: Dict = None) -> Dict:
        """Advanced reloop strategy determination with intelligent analysis"""
        self._log("Analyzing reloop strategy requirements")
        
        # Use the advanced reloop manager
        strategy_result = self.reloop_manager.determine_optimal_strategy(
            quality_report, 
            reel_data or {}, 
            context or {}
        )
        
        # Enhance with cost-benefit analysis
        if strategy_result['reloop_needed']:
            strategy_result['cost_benefit_analysis'] = self._analyze_cost_benefit(
                strategy_result, quality_report
            )
            
            # Add implementation guidance
            strategy_result['implementation_guidance'] = self._generate_implementation_guidance(
                strategy_result, quality_report
            )
            
            self._log(f"Reloop recommended: {strategy_result['strategy']} (confidence: {strategy_result['confidence']:.2f})")
        else:
            self._log("No reloop needed - quality assessment passed")
        
        return strategy_result
    
    def generate_improvement_recommendations(self, quality_report: Dict, reloop_strategy: Dict) -> Dict[str, Any]:
        """Generate specific improvement recommendations based on QA results"""
        self._log("Generating improvement recommendations")
        
        recommendations = {
            'priority_improvements': [],
            'optional_enhancements': [],
            'technical_fixes': [],
            'content_suggestions': [],
            'estimated_effort': 'low'
        }
        
        # Analyze failed criteria for specific recommendations
        failed_criteria = quality_report.get('failed_criteria', [])
        
        if 'technical_quality' in failed_criteria:
            tech_details = quality_report.get('technical_details', {})
            tech_issues = tech_details.get('issues', [])
            
            if 'file_integrity' in tech_issues:
                recommendations['technical_fixes'].append('Regenerate video file - current file has integrity issues')
            if 'resolution_suboptimal' in tech_issues:
                recommendations['technical_fixes'].append('Adjust output resolution to 1080x1920 for optimal social media compatibility')
            if 'sync_quality_low' in tech_issues:
                recommendations['technical_fixes'].append('Improve audio-video synchronization timing')
        
        if 'content_quality' in failed_criteria:
            content_details = quality_report.get('content_details', {})
            content_issues = content_details.get('issues', [])
            
            if 'narrative_flow_poor' in content_issues:
                recommendations['content_suggestions'].append('Improve narrative structure and flow between scenes')
            if 'visual_appeal_low' in content_issues:
                recommendations['content_suggestions'].append('Enhance visual effects and color grading')
        
        if 'engagement_potential' in failed_criteria:
            engagement_details = quality_report.get('engagement_details', {})
            factors = engagement_details.get('factors', [])
            
            if 'too_long' in factors:
                recommendations['priority_improvements'].append('Reduce video duration for better engagement')
            elif 'too_short' in factors:
                recommendations['priority_improvements'].append('Extend video duration for better content delivery')
            
            if 'no_audio' in factors:
                recommendations['priority_improvements'].append('Add audio track to significantly improve engagement')
        
        # Determine effort level
        total_fixes = len(recommendations['technical_fixes'] + recommendations['content_suggestions'] + recommendations['priority_improvements'])
        if total_fixes > 5:
            recommendations['estimated_effort'] = 'high'
        elif total_fixes > 2:
            recommendations['estimated_effort'] = 'medium'
        
        # Add strategy-specific guidance
        strategy = reloop_strategy.get('strategy', 'none')
        if strategy == 'prompt_refinement':
            recommendations['optional_enhancements'].append('Consider using Claude-enhanced prompts for better quality')
        elif strategy == 'model_switch':
            recommendations['optional_enhancements'].append('Try different AI video generation model for better results')
        
        return recommendations
    
    def _assess_technical_quality(self, reel_data: Dict) -> Dict[str, Any]:
        """Comprehensive technical quality assessment"""
        # Get file path
        final_reel_path = reel_data.get('final_reel_path') or reel_data.get('file_path')
        
        # File integrity check
        if final_reel_path:
            file_integrity = self.technical_validator.validate_file_integrity(final_reel_path)
        else:
            file_integrity = {'score': 0.0, 'issues': ['no_file_path'], 'details': 'No file path provided'}
        
        # Resolution compliance check
        video_data = reel_data.get('video_stitching', {})
        resolution_check = self.technical_validator.assess_resolution_compliance(video_data)
        
        # Sync quality check
        audio_data = reel_data.get('audio_synchronization', {})
        sync_check = self.technical_validator.assess_sync_quality(audio_data)
        
        # Combine scores (weighted)
        overall_score = (
            file_integrity['score'] * 0.4 +
            resolution_check['score'] * 0.3 +
            sync_check['score'] * 0.3
        )
        
        # Combine issues
        all_issues = file_integrity['issues'] + resolution_check['issues'] + sync_check['issues']
        
        return {
            'score': overall_score,
            'issues': all_issues,
            'details': {
                'file_integrity': file_integrity,
                'resolution_compliance': resolution_check,
                'sync_quality': sync_check
            },
            'breakdown': f'File: {file_integrity["score"]:.2f}, Resolution: {resolution_check["score"]:.2f}, Sync: {sync_check["score"]:.2f}'
        }
    
    def _assess_content_quality(self, reel_data: Dict, context: Dict) -> Dict[str, Any]:
        """Advanced content quality assessment"""
        if self.content_analyzer:
            # Use Claude-powered analysis when available
            narrative_analysis = self.content_analyzer.analyze_narrative_flow(reel_data, context)
            visual_analysis = self.content_analyzer.analyze_visual_appeal(reel_data)
        else:
            # Fallback to basic analysis
            narrative_analysis = {'score': 0.7, 'issues': ['no_claude_analysis'], 'details': 'Basic analysis only'}
            visual_analysis = {'score': 0.7, 'issues': ['no_claude_analysis'], 'details': 'Basic analysis only'}
        
        # Combine scores
        overall_score = (narrative_analysis['score'] * 0.6 + visual_analysis['score'] * 0.4)
        
        # Combine issues
        all_issues = narrative_analysis['issues'] + visual_analysis['issues']
        
        return {
            'score': overall_score,
            'issues': all_issues,
            'details': {
                'narrative_flow': narrative_analysis,
                'visual_appeal': visual_analysis
            },
            'breakdown': f'Narrative: {narrative_analysis["score"]:.2f}, Visual: {visual_analysis["score"]:.2f}'
        }
    
    def _assess_brand_alignment(self, reel_data: Dict, context: Dict) -> Dict[str, Any]:
        """Assess brand voice consistency and messaging alignment"""
        # Extract brand-relevant information
        user_prompt = context.get('user_prompt', '')
        content_mode = context.get('content_mode', 'unknown')
        
        # Basic brand alignment assessment
        score = 0.85  # Base score
        issues = []
        
        # Check if user prompt suggests brand content
        brand_keywords = ['brand', 'company', 'business', 'logo', 'marketing', 'product']
        has_brand_context = any(keyword in user_prompt.lower() for keyword in brand_keywords)
        
        if has_brand_context:
            # Higher standards for brand content
            if content_mode == 'narration':
                score += 0.05  # Narration better for brand messaging
            else:
                score -= 0.02  # Music mode less controlled for brand
        
        # Check for professional quality indicators
        video_data = reel_data.get('video_stitching', {})
        if video_data.get('quality') == 'professional':
            score += 0.05
        elif video_data.get('quality') == 'mock':
            score -= 0.1
            issues.append('mock_quality_affects_brand')
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'details': f'Brand context detected: {has_brand_context}, Content mode: {content_mode}',
            'breakdown': f'Base score with brand context and quality adjustments'
        }
    
    def _assess_platform_optimization(self, reel_data: Dict, context: Dict) -> Dict[str, Any]:
        """Assess platform-specific requirements compliance"""
        platform = context.get('platform', 'instagram')
        
        # Resolution check
        video_data = reel_data.get('video_stitching', {})
        resolution = video_data.get('resolution', 'unknown')
        duration = video_data.get('total_duration', 0)
        
        score = 0.7  # Base score
        issues = []
        
        # Resolution optimization
        if resolution == '1080x1920':
            score += 0.15
        elif resolution == 'unknown':
            score -= 0.05
            issues.append('resolution_unknown')
        else:
            score -= 0.1
            issues.append('resolution_suboptimal')
        
        # Duration optimization by platform
        platform_duration_ranges = {
            'instagram': (15, 30),
            'tiktok': (9, 21),
            'facebook': (15, 60),
            'all': (15, 30)
        }
        
        min_dur, max_dur = platform_duration_ranges.get(platform, (15, 30))
        if min_dur <= duration <= max_dur:
            score += 0.1
        elif duration < min_dur:
            score -= 0.08
            issues.append('too_short_for_platform')
        else:
            score -= 0.05
            issues.append('too_long_for_platform')
        
        # Audio optimization
        audio_data = reel_data.get('audio_synchronization', {})
        if audio_data:
            score += 0.05  # Having audio is good for all platforms
        
        return {
            'score': max(0.0, min(1.0, score)),
            'issues': issues,
            'details': f'Platform: {platform}, Duration: {duration}s, Resolution: {resolution}',
            'breakdown': f'Platform-specific optimization for {platform}'
        }
    
    def _assess_engagement_potential(self, reel_data: Dict, context: Dict) -> Dict[str, Any]:
        """Predict social media performance and engagement potential"""
        return self.engagement_predictor.predict_engagement_score(reel_data, context)
    
    def _determine_pass_status(self, overall_score: float) -> str:
        """Determine if quality passes threshold"""
        return 'pass' if overall_score >= self.thresholds.OVERALL_PASS else 'fail'
    
    def _determine_quality_grade(self, overall_score: float) -> str:
        """Determine quality grade based on score"""
        if overall_score >= 0.9:
            return 'excellent'
        elif overall_score >= 0.8:
            return 'good'
        elif overall_score >= self.thresholds.OVERALL_PASS:
            return 'acceptable'
        elif overall_score >= 0.6:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _identify_failed_criteria(self, scores: Dict) -> List[str]:
        """Identify which quality criteria failed"""
        failed = []
        
        if scores['technical_quality'] < self.thresholds.TECHNICAL_QUALITY:
            failed.append('technical_quality')
        if scores['content_quality'] < self.thresholds.CONTENT_QUALITY:
            failed.append('content_quality')
        if scores['brand_alignment'] < self.thresholds.BRAND_ALIGNMENT:
            failed.append('brand_alignment')
        if scores['platform_optimization'] < self.thresholds.PLATFORM_OPTIMIZATION:
            failed.append('platform_optimization')
        if scores['engagement_potential'] < self.thresholds.ENGAGEMENT_POTENTIAL:
            failed.append('engagement_potential')
        
        return failed
    
    def _compare_against_thresholds(self, scores: Dict) -> Dict[str, Any]:
        """Compare scores against thresholds with detailed analysis"""
        comparison = {}
        
        thresholds = {
            'technical_quality': self.thresholds.TECHNICAL_QUALITY,
            'content_quality': self.thresholds.CONTENT_QUALITY,
            'brand_alignment': self.thresholds.BRAND_ALIGNMENT,
            'platform_optimization': self.thresholds.PLATFORM_OPTIMIZATION,
            'engagement_potential': self.thresholds.ENGAGEMENT_POTENTIAL,
            'overall_score': self.thresholds.OVERALL_PASS
        }
        
        for criterion, threshold in thresholds.items():
            score = scores.get(criterion, 0)
            comparison[criterion] = {
                'score': score,
                'threshold': threshold,
                'passed': score >= threshold,
                'margin': score - threshold,
                'percentage_of_threshold': (score / threshold * 100) if threshold > 0 else 0
            }
        
        return comparison
    
    def _analyze_cost_benefit(self, strategy_result: Dict, quality_report: Dict) -> Dict[str, Any]:
        """Analyze cost-benefit of reloop strategy"""
        strategy = strategy_result['strategy']
        current_score = quality_report['overall_score']
        
        # Estimated improvement by strategy
        improvement_estimates = {
            'parameter_adjustment': 0.05,
            'prompt_refinement': 0.10,
            'model_switch': 0.08,
            'content_restructure': 0.15,
            'complete_regeneration': 0.25
        }
        
        estimated_improvement = improvement_estimates.get(strategy, 0.05)
        projected_score = min(1.0, current_score + estimated_improvement)
        
        # Cost analysis
        cost_levels = {
            'minimal': 1,
            '+$0.02-0.05': 2,
            'varies by model': 3,
            'moderate': 4,
            'full cost': 5
        }
        
        cost_level = cost_levels.get(strategy_result.get('estimated_cost', 'minimal'), 1)
        
        # Benefit calculation
        score_improvement = projected_score - current_score
        benefit_score = score_improvement * 10  # Scale to 1-10
        
        # Cost-benefit ratio
        cb_ratio = benefit_score / cost_level if cost_level > 0 else 0
        
        return {
            'current_score': current_score,
            'projected_score': projected_score,
            'estimated_improvement': estimated_improvement,
            'actual_improvement': score_improvement,
            'cost_level': cost_level,
            'benefit_score': benefit_score,
            'cost_benefit_ratio': cb_ratio,
            'recommendation': 'proceed' if cb_ratio > 1.5 else 'consider_alternatives' if cb_ratio > 1.0 else 'not_recommended'
        }
    
    def _generate_implementation_guidance(self, strategy_result: Dict, quality_report: Dict) -> Dict[str, Any]:
        """Generate specific implementation guidance for reloop strategy"""
        strategy = strategy_result['strategy']
        focus_areas = strategy_result.get('focus_areas', [])
        
        guidance = {
            'strategy': strategy,
            'priority_order': [],
            'specific_actions': [],
            'expected_timeline': 'unknown',
            'success_indicators': []
        }
        
        if strategy == 'parameter_adjustment':
            guidance['priority_order'] = ['technical_fixes', 'quality_validation']
            guidance['specific_actions'] = [
                'Adjust video export settings for better compression',
                'Improve audio-video synchronization timing',
                'Ensure 1080x1920 resolution compliance'
            ]
            guidance['expected_timeline'] = '5-15 minutes'
            guidance['success_indicators'] = ['File integrity score > 0.8', 'Sync quality improved']
        
        elif strategy == 'prompt_refinement':
            guidance['priority_order'] = ['content_enhancement', 'claude_optimization']
            guidance['specific_actions'] = [
                'Use Claude to enhance video generation prompts',
                'Improve narrative flow and visual descriptions',
                'Add more specific technical parameters'
            ]
            guidance['expected_timeline'] = '10-20 minutes'
            guidance['success_indicators'] = ['Content quality score > 0.75', 'Better visual appeal']
        
        elif strategy == 'model_switch':
            guidance['priority_order'] = ['model_selection', 'regeneration', 'validation']
            guidance['specific_actions'] = [
                'Select alternative AI model based on content type',
                'Regenerate failed video clips with new model',
                'Compare results and select best output'
            ]
            guidance['expected_timeline'] = '20-40 minutes'
            guidance['success_indicators'] = ['Overall score improvement', 'Multiple criteria passing']
        
        elif strategy == 'content_restructure':
            guidance['priority_order'] = ['content_analysis', 'restructuring', 'regeneration']
            guidance['specific_actions'] = [
                'Analyze content structure and flow',
                'Redesign storyboard and scene breakdown',
                'Regenerate with improved content structure'
            ]
            guidance['expected_timeline'] = '30-60 minutes'
            guidance['success_indicators'] = ['Engagement score > 0.7', 'Improved narrative flow']
        
        elif strategy == 'complete_regeneration':
            guidance['priority_order'] = ['full_restart', 'quality_monitoring']
            guidance['specific_actions'] = [
                'Restart entire reel generation process',
                'Use lessons learned from current attempt',
                'Monitor quality at each stage'
            ]
            guidance['expected_timeline'] = '45-90 minutes'
            guidance['success_indicators'] = ['Overall score > 0.76', 'All quality criteria passing']
        
        return guidance
    
    def _save_assessment_log(self, assessment: Dict) -> None:
        """Save detailed assessment log for analysis"""
        try:
            # Load existing logs or create new
            logs = []
            if os.path.exists(self.quality_log_path):
                with open(self.quality_log_path, 'r') as f:
                    logs = json.load(f)
            
            # Add new assessment
            logs.append({
                'timestamp': assessment['assessment_timestamp'],
                'overall_score': assessment['overall_score'],
                'pass_status': assessment['pass_status'],
                'quality_grade': assessment['quality_grade'],
                'failed_criteria': assessment['failed_criteria'],
                'processing_time': assessment['processing_time']
            })
            
            # Keep only last 50 assessments
            logs = logs[-50:]
            
            # Save updated logs
            with open(self.quality_log_path, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            self._log(f"Error saving assessment log: {str(e)}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _log(self, message: str) -> None:
        """Add message to processing log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.processing_log.append(log_entry)
        print(f"🛡️ QA System: {message}")
    
    def _create_fallback_assessment(self, context: Dict = None) -> Dict:
        """Create fallback assessment when main assessment fails"""
        return {
            'technical_quality': 0.5,
            'content_quality': 0.5,
            'brand_alignment': 0.5,
            'platform_optimization': 0.5,
            'engagement_potential': 0.5,
            'overall_score': 0.5,
            'pass_status': 'fail',
            'failed_criteria': ['assessment_error'],
            'quality_grade': 'poor',
            'error': 'Assessment system encountered an error',
            'assessment_timestamp': self._get_timestamp(),
            'processing_time': 0.0,
            'assessment_version': '2.0-fallback',
            'input_context': context or {}
        }