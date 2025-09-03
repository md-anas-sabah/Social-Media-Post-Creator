"""
Quality assessment and reloop system for video reels
"""

import os
from typing import Dict, List, Any
from .claude_refinement import ClaudeRefinementService


class QualityThresholds:
    """Quality assessment thresholds"""
    TECHNICAL_QUALITY = 0.8
    CONTENT_QUALITY = 0.75
    BRAND_ALIGNMENT = 0.85
    PLATFORM_OPTIMIZATION = 0.8
    ENGAGEMENT_POTENTIAL = 0.7
    OVERALL_PASS = 0.76


class IntelligentQASystem:
    """Comprehensive quality assessment with reloop capabilities"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.claude_reviewer = ClaudeRefinementService()
        self.thresholds = QualityThresholds()
        
        # QA output path
        self.qa_report_path = os.path.join(output_folder, 'qa_report.json')
    
    def comprehensive_assessment(self, reel_data: Dict) -> Dict:
        """Multi-dimensional quality analysis"""
        try:
            technical_score = self._assess_technical_quality(reel_data)
            content_score = self._assess_content_quality(reel_data)
            brand_score = self._assess_brand_alignment(reel_data)
            platform_score = self._assess_platform_optimization(reel_data)
            engagement_score = self._assess_engagement_potential(reel_data)
            
            overall_score = (
                technical_score * 0.25 +
                content_score * 0.25 +
                brand_score * 0.2 +
                platform_score * 0.15 +
                engagement_score * 0.15
            )
            
            assessment = {
                'technical_quality': technical_score,
                'content_quality': content_score,
                'brand_alignment': brand_score,
                'platform_optimization': platform_score,
                'engagement_potential': engagement_score,
                'overall_score': overall_score,
                'pass_status': self._determine_pass_status(overall_score),
                'failed_criteria': self._identify_failed_criteria({
                    'technical_quality': technical_score,
                    'content_quality': content_score,
                    'brand_alignment': brand_score,
                    'platform_optimization': platform_score,
                    'engagement_potential': engagement_score
                }),
                'timestamp': self._get_timestamp()
            }
            
            return assessment
        except Exception as e:
            print(f"Error in comprehensive assessment: {e}")
            return self._create_fallback_assessment()
    
    def determine_reloop_strategy(self, quality_report: Dict) -> Dict:
        """Smart failure recovery decisions"""
        if quality_report.get('pass_status') == 'pass':
            return {'reloop_needed': False, 'strategy': 'none'}
        
        failed_criteria = quality_report.get('failed_criteria', [])
        overall_score = quality_report.get('overall_score', 0)
        
        # Determine best reloop strategy based on failures
        if 'technical_quality' in failed_criteria:
            return {
                'reloop_needed': True,
                'strategy': 'parameter_adjustment',
                'focus_areas': ['resolution', 'sync', 'compression'],
                'estimated_cost': 'minimal'
            }
        
        if 'content_quality' in failed_criteria:
            return {
                'reloop_needed': True,
                'strategy': 'prompt_refinement',
                'focus_areas': ['narrative_flow', 'visual_appeal'],
                'estimated_cost': '+$0.02-0.05'
            }
        
        if overall_score < 0.5:
            return {
                'reloop_needed': True,
                'strategy': 'content_restructure',
                'focus_areas': ['complete_regeneration'],
                'estimated_cost': 'moderate'
            }
        
        return {
            'reloop_needed': True,
            'strategy': 'model_switch',
            'focus_areas': failed_criteria,
            'estimated_cost': 'varies'
        }
    
    def _assess_technical_quality(self, reel_data: Dict) -> float:
        """Assess technical aspects (resolution, sync, compression)"""
        # Placeholder technical quality assessment
        score = 0.8
        
        # Check if file exists and has content
        if reel_data.get('file_path') and os.path.exists(reel_data['file_path']):
            file_size = os.path.getsize(reel_data['file_path'])
            if file_size > 0:
                score += 0.1
        
        return min(score, 1.0)
    
    def _assess_content_quality(self, reel_data: Dict) -> float:
        """Assess content quality (narrative flow, visual appeal)"""
        # Placeholder content quality assessment
        return 0.75
    
    def _assess_brand_alignment(self, reel_data: Dict) -> float:
        """Assess brand voice consistency"""
        # Placeholder brand alignment assessment
        return 0.85
    
    def _assess_platform_optimization(self, reel_data: Dict) -> float:
        """Assess platform-specific requirements"""
        # Placeholder platform optimization assessment
        return 0.8
    
    def _assess_engagement_potential(self, reel_data: Dict) -> float:
        """Predict social media performance"""
        # Placeholder engagement potential assessment
        return 0.7
    
    def _determine_pass_status(self, overall_score: float) -> str:
        """Determine if quality passes threshold"""
        return 'pass' if overall_score >= self.thresholds.OVERALL_PASS else 'fail'
    
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
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _create_fallback_assessment(self) -> Dict:
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
            'error': 'Assessment system encountered an error'
        }