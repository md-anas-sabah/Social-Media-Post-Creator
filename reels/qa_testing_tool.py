"""
CrewAI tool for comprehensive quality assessment and intelligent reloop strategy
Integrates with IntelligentQASystem for multi-dimensional quality analysis
"""

import os
import json
from typing import Dict, Any, Optional
from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from .qa_system import IntelligentQASystem


class QATestingTool(BaseTool):
    name: str = "Advanced QA Testing Tool"
    description: str = """
    Comprehensive quality assessment and intelligent reloop strategy tool.
    
    This tool provides advanced multi-dimensional quality analysis including:
    - Technical quality assessment (file integrity, resolution, sync)
    - Content quality evaluation (narrative flow, visual appeal)
    - Brand alignment assessment (voice consistency, messaging)
    - Platform optimization analysis (requirements compliance)
    - Engagement potential prediction (social media performance)
    - Intelligent reloop strategy determination with cost-benefit analysis
    
    Input format:
    {
        "action": "comprehensive_assessment",  # Required: comprehensive_assessment, reloop_analysis
        "reel_data": {...},                   # Required: Complete reel data from Phase 6
        "context": {...},                     # Required: User context and preferences
        "output_folder": "path",              # Required: Output folder path
        "claude_api_key": "key"               # Optional: Claude API key for enhanced analysis
    }
    
    Returns detailed quality assessment and reloop recommendations.
    """
    
    def _run(self, action: str, reel_data: dict, context: dict, output_folder: str,
             claude_api_key: Optional[str] = None) -> str:
        """
        Execute comprehensive quality assessment and reloop analysis
        
        Args:
            action: Type of analysis (comprehensive_assessment, reloop_analysis)
            reel_data: Complete reel data from Phase 6 synchronization
            context: User context including prompt, platform, mode, etc.
            output_folder: Output folder path for reports and logs
            claude_api_key: Optional Claude API key for enhanced analysis
            
        Returns:
            JSON string with quality assessment and reloop recommendations
        """
        try:
            # Initialize QA system
            qa_system = IntelligentQASystem(output_folder, claude_api_key)
            
            results = {
                'action': action,
                'output_folder': output_folder,
                'processing_steps': [],
                'status': 'processing'
            }
            
            if action == 'comprehensive_assessment':
                # Step 1: Comprehensive quality assessment
                print(f"🛡️ Executing comprehensive quality assessment...")
                
                quality_report = qa_system.comprehensive_assessment(reel_data, context)
                results['quality_assessment'] = quality_report
                results['processing_steps'].append('quality_assessment_completed')
                
                print(f"📊 Quality Assessment Results:")
                print(f"   Overall Score: {quality_report.get('overall_score', 0):.3f}")
                print(f"   Status: {quality_report.get('pass_status', 'unknown').upper()}")
                print(f"   Quality Grade: {quality_report.get('quality_grade', 'unknown').upper()}")
                
                # Step 2: Reloop strategy analysis (always run for comprehensive assessment)
                print(f"🔄 Analyzing reloop strategy requirements...")
                
                reloop_strategy = qa_system.determine_reloop_strategy(quality_report, reel_data, context)
                results['reloop_strategy'] = reloop_strategy
                results['processing_steps'].append('reloop_analysis_completed')
                
                if reloop_strategy['reloop_needed']:
                    print(f"⚠️ Reloop Required: {reloop_strategy['strategy']} (Confidence: {reloop_strategy.get('confidence', 0):.2f})")
                else:
                    print(f"✅ Quality Passed - No reloop needed")
                
                # Step 3: Generate improvement recommendations
                print(f"💡 Generating improvement recommendations...")
                
                recommendations = qa_system.generate_improvement_recommendations(quality_report, reloop_strategy)
                results['improvement_recommendations'] = recommendations
                results['processing_steps'].append('recommendations_generated')
                
                print(f"📝 Generated {len(recommendations.get('priority_improvements', []))} priority improvements")
                
                # Step 4: Save comprehensive QA report
                qa_report_path = os.path.join(output_folder, 'qa_report.json')
                comprehensive_report = {
                    'quality_assessment': quality_report,
                    'reloop_strategy': reloop_strategy,
                    'improvement_recommendations': recommendations,
                    'analysis_metadata': {
                        'claude_api_available': bool(claude_api_key),
                        'context_provided': bool(context),
                        'processing_timestamp': quality_report.get('assessment_timestamp'),
                        'total_processing_time': quality_report.get('processing_time', 0)
                    }
                }
                
                with open(qa_report_path, 'w') as f:
                    json.dump(comprehensive_report, f, indent=2)
                
                results['qa_report_path'] = qa_report_path
                results['processing_steps'].append('qa_report_saved')
                
                print(f"📋 Comprehensive QA report saved: {qa_report_path}")
            
            elif action == 'reloop_analysis':
                # Focus only on reloop analysis for existing quality report
                print(f"🔄 Executing focused reloop analysis...")
                
                # First get current quality status
                quality_report = qa_system.comprehensive_assessment(reel_data, context)
                reloop_strategy = qa_system.determine_reloop_strategy(quality_report, reel_data, context)
                
                results['focused_reloop_analysis'] = {
                    'current_quality_score': quality_report.get('overall_score', 0),
                    'reloop_strategy': reloop_strategy,
                    'cost_benefit_analysis': reloop_strategy.get('cost_benefit_analysis', {}),
                    'implementation_guidance': reloop_strategy.get('implementation_guidance', {})
                }
                results['processing_steps'].append('focused_reloop_analysis_completed')
                
                print(f"🎯 Focused reloop analysis completed")
            
            # Final status and summary
            results['status'] = 'completed'
            results['summary'] = self._create_qa_summary(results)
            
            print(f"🎉 QA Testing completed successfully!")
            print(f"📁 Output folder: {output_folder}")
            
            return json.dumps(results, indent=2)
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'action': action,
                'output_folder': output_folder,
                'processing_steps': results.get('processing_steps', [])
            }
            print(f"❌ Error in QA testing: {str(e)}")
            return json.dumps(error_result, indent=2)
    
    def _create_qa_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive QA testing summary"""
        summary = {
            'action_executed': results.get('action', 'unknown'),
            'processing_steps_completed': len(results.get('processing_steps', [])),
            'status': results.get('status', 'unknown')
        }
        
        # Quality assessment summary
        if 'quality_assessment' in results:
            qa_data = results['quality_assessment']
            summary['quality_summary'] = {
                'overall_score': qa_data.get('overall_score', 0),
                'pass_status': qa_data.get('pass_status', 'unknown'),
                'quality_grade': qa_data.get('quality_grade', 'unknown'),
                'failed_criteria_count': len(qa_data.get('failed_criteria', [])),
                'processing_time': qa_data.get('processing_time', 0)
            }
        
        # Reloop strategy summary
        if 'reloop_strategy' in results:
            reloop_data = results['reloop_strategy']
            summary['reloop_summary'] = {
                'reloop_needed': reloop_data.get('reloop_needed', False),
                'recommended_strategy': reloop_data.get('strategy', 'none'),
                'confidence': reloop_data.get('confidence', 0),
                'estimated_cost': reloop_data.get('estimated_cost', 'unknown'),
                'focus_areas_count': len(reloop_data.get('focus_areas', []))
            }
        
        # Improvement recommendations summary
        if 'improvement_recommendations' in results:
            rec_data = results['improvement_recommendations']
            summary['recommendations_summary'] = {
                'priority_improvements': len(rec_data.get('priority_improvements', [])),
                'technical_fixes': len(rec_data.get('technical_fixes', [])),
                'content_suggestions': len(rec_data.get('content_suggestions', [])),
                'estimated_effort': rec_data.get('estimated_effort', 'unknown')
            }
        
        return summary


# Helper function for auto-detection of reel folder context
def get_reel_context_from_folder():
    """Auto-detect reel folder and extract context"""
    current_dir = os.getcwd()
    
    # Look for reels folder structure
    reels_dir = os.path.join(current_dir, 'reels')
    if os.path.exists(reels_dir):
        # Find the most recent reel folder
        reel_folders = [f for f in os.listdir(reels_dir) 
                       if f.startswith('reel_') and os.path.isdir(os.path.join(reels_dir, f))]
        if reel_folders:
            latest_folder = sorted(reel_folders)[-1]
            folder_path = os.path.join(reels_dir, latest_folder)
            
            # Extract context from folder name
            # Format: reel_{platform}_{prompt_slug}_{timestamp}
            parts = latest_folder.split('_', 3)
            context = {
                'platform': parts[1] if len(parts) > 1 else 'instagram',
                'output_folder': folder_path
            }
            
            # Try to load additional context from metadata files
            try:
                metadata_files = ['reel_metadata.json', 'content_planning_result.json', 'synchronization_metadata.json']
                for metadata_file in metadata_files:
                    metadata_path = os.path.join(folder_path, metadata_file)
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            context.update(metadata.get('context', {}))
                        break
            except Exception:
                pass  # Continue with basic context
            
            return context
    
    return {'platform': 'instagram', 'output_folder': None}


# Helper function for creating QA requests
def create_qa_testing_request(reel_data, action="comprehensive_assessment", context=None):
    """Helper function to create properly formatted QA testing requests"""
    
    # Auto-detect context if not provided
    if context is None:
        context = get_reel_context_from_folder()
    
    # Ensure output folder is available
    output_folder = context.get('output_folder')
    if not output_folder:
        raise Exception("Could not determine output folder for QA testing")
    
    return {
        "action": action,
        "reel_data": reel_data,
        "context": context,
        "output_folder": output_folder,
        "claude_api_key": None  # Will be auto-detected from environment
    }


# Quality threshold validation helper
def validate_quality_thresholds(quality_report):
    """Validate quality report against standard thresholds"""
    from .qa_system import QualityThresholds
    
    thresholds = QualityThresholds()
    
    validation_results = {
        'overall_pass': quality_report.get('overall_score', 0) >= thresholds.OVERALL_PASS,
        'technical_pass': quality_report.get('technical_quality', 0) >= thresholds.TECHNICAL_QUALITY,
        'content_pass': quality_report.get('content_quality', 0) >= thresholds.CONTENT_QUALITY,
        'brand_pass': quality_report.get('brand_alignment', 0) >= thresholds.BRAND_ALIGNMENT,
        'platform_pass': quality_report.get('platform_optimization', 0) >= thresholds.PLATFORM_OPTIMIZATION,
        'engagement_pass': quality_report.get('engagement_potential', 0) >= thresholds.ENGAGEMENT_POTENTIAL
    }
    
    validation_results['all_criteria_pass'] = all(validation_results.values())
    validation_results['passed_count'] = sum(1 for passed in validation_results.values() if passed)
    validation_results['total_criteria'] = len(validation_results) - 2  # Exclude summary fields
    
    return validation_results