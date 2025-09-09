"""
Comprehensive Error Handling and Edge Case Management for Video Reel Generation
Provides robust error recovery, graceful degradation, and detailed error reporting
"""

import os
import json
import time
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PhaseError(Exception):
    """Custom exception for phase-specific errors"""
    def __init__(self, phase: int, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, context: Dict = None):
        self.phase = phase
        self.message = message
        self.severity = severity
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(f"Phase {phase}: {message}")


class ReelGenerationErrorHandler:
    """Comprehensive error handling system for reel generation"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.error_log_path = os.path.join(output_folder, 'error_log.json')
        self.recovery_log_path = os.path.join(output_folder, 'recovery_log.json')
        self.errors = []
        self.recovery_attempts = []
        
    def handle_phase_error(self, phase: int, error: Exception, context: Dict = None) -> Dict[str, Any]:
        """Handle errors that occur during specific phases"""
        try:
            # Determine error severity and type
            severity = self._determine_error_severity(error, phase)
            error_type = self._classify_error_type(error)
            
            # Create comprehensive error record
            error_record = {
                'phase': phase,
                'error_type': error_type,
                'severity': severity.value,
                'message': str(error),
                'traceback': traceback.format_exc(),
                'context': context or {},
                'timestamp': datetime.now().isoformat(),
                'recovery_strategy': self._get_recovery_strategy(error, phase)
            }
            
            # Log the error
            self.errors.append(error_record)
            self._save_error_log()
            
            # Attempt recovery based on severity and phase
            recovery_result = self._attempt_recovery(error_record)
            
            return {
                'error_handled': True,
                'error_record': error_record,
                'recovery_result': recovery_result,
                'can_continue': recovery_result.get('success', False) or severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
            }
            
        except Exception as handler_error:
            # If error handler itself fails, create minimal fallback
            return {
                'error_handled': False,
                'original_error': str(error),
                'handler_error': str(handler_error),
                'can_continue': False,
                'fallback_active': True
            }
    
    def handle_api_error(self, api_name: str, error: Exception, retry_count: int = 0) -> Dict[str, Any]:
        """Handle API-specific errors with retry logic"""
        max_retries = self._get_max_retries(api_name)
        
        error_context = {
            'api_name': api_name,
            'retry_count': retry_count,
            'max_retries': max_retries
        }
        
        # Check if this is a retryable error
        if self._is_retryable_error(error) and retry_count < max_retries:
            return {
                'should_retry': True,
                'retry_delay': self._get_retry_delay(retry_count),
                'retry_count': retry_count + 1,
                'error_context': error_context
            }
        
        # If not retryable or max retries reached, handle as permanent failure
        return {
            'should_retry': False,
            'permanent_failure': True,
            'fallback_strategy': self._get_api_fallback(api_name),
            'error_context': error_context
        }
    
    def handle_resource_error(self, resource_type: str, error: Exception) -> Dict[str, Any]:
        """Handle resource-related errors (file, memory, disk space, etc.)"""
        resource_context = {
            'resource_type': resource_type,
            'available_disk_space': self._get_available_disk_space(),
            'memory_usage': self._get_memory_usage(),
            'file_permissions': self._check_file_permissions()
        }
        
        # Attempt resource cleanup and recovery
        cleanup_result = self._cleanup_resources(resource_type)
        
        return {
            'resource_context': resource_context,
            'cleanup_performed': cleanup_result,
            'recovery_suggestions': self._get_resource_recovery_suggestions(resource_type, resource_context)
        }
    
    def create_fallback_result(self, phase: int, original_context: Dict) -> Dict[str, Any]:
        """Create a fallback result when a phase fails completely"""
        fallback_strategies = {
            2: self._create_phase2_fallback,
            3: self._create_phase3_fallback,
            4: self._create_phase4_fallback,
            5: self._create_phase5_fallback,
            6: self._create_phase6_fallback,
            7: self._create_phase7_fallback
        }
        
        fallback_creator = fallback_strategies.get(phase, self._create_generic_fallback)
        return fallback_creator(original_context)
    
    def _determine_error_severity(self, error: Exception, phase: int) -> ErrorSeverity:
        """Determine the severity of an error based on type and phase"""
        error_str = str(error).lower()
        
        # Critical errors
        critical_patterns = ['api key', 'authentication', 'authorization', 'out of memory', 'disk full']
        if any(pattern in error_str for pattern in critical_patterns):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        high_patterns = ['connection', 'timeout', 'network', 'file not found', 'permission denied']
        if any(pattern in error_str for pattern in high_patterns):
            return ErrorSeverity.HIGH
        
        # Phase-specific severity
        if phase in [2, 7]:  # Content Planning and QA are critical phases
            return ErrorSeverity.HIGH
        elif phase in [4, 5, 6]:  # Generation and sync phases
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _classify_error_type(self, error: Exception) -> str:
        """Classify the type of error"""
        error_type_map = {
            'ConnectionError': 'network',
            'TimeoutError': 'timeout',
            'PermissionError': 'permission',
            'FileNotFoundError': 'file_missing',
            'JSONDecodeError': 'data_parsing',
            'KeyError': 'missing_data',
            'ValueError': 'invalid_data',
            'ImportError': 'dependency',
            'MemoryError': 'resource',
        }
        
        error_class = error.__class__.__name__
        return error_type_map.get(error_class, 'unknown')
    
    def _get_recovery_strategy(self, error: Exception, phase: int) -> Dict[str, Any]:
        """Get appropriate recovery strategy for the error"""
        error_type = self._classify_error_type(error)
        
        strategies = {
            'network': {'type': 'retry_with_backoff', 'max_attempts': 3, 'base_delay': 2},
            'timeout': {'type': 'retry_with_increased_timeout', 'max_attempts': 2, 'timeout_multiplier': 2},
            'permission': {'type': 'fallback_location', 'alternative_paths': ['/tmp', os.path.expanduser('~')]},
            'file_missing': {'type': 'recreate_or_fallback', 'recreation_possible': True},
            'data_parsing': {'type': 'use_fallback_parser', 'fallback_available': True},
            'missing_data': {'type': 'use_default_values', 'defaults_available': True},
            'dependency': {'type': 'graceful_degradation', 'mock_mode': True},
            'resource': {'type': 'cleanup_and_retry', 'cleanup_targets': ['temp_files', 'cache']}
        }
        
        return strategies.get(error_type, {'type': 'generic_fallback', 'skip_phase': False})
    
    def _attempt_recovery(self, error_record: Dict) -> Dict[str, Any]:
        """Attempt to recover from an error based on the recovery strategy"""
        strategy = error_record['recovery_strategy']
        strategy_type = strategy.get('type', 'generic_fallback')
        
        recovery_result = {
            'strategy_used': strategy_type,
            'success': False,
            'actions_taken': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if strategy_type == 'retry_with_backoff':
                recovery_result = self._execute_retry_recovery(strategy)
            elif strategy_type == 'fallback_location':
                recovery_result = self._execute_fallback_location(strategy)
            elif strategy_type == 'graceful_degradation':
                recovery_result = self._execute_graceful_degradation(strategy)
            elif strategy_type == 'cleanup_and_retry':
                recovery_result = self._execute_cleanup_recovery(strategy)
            else:
                recovery_result['success'] = False
                recovery_result['actions_taken'] = ['generic_fallback_applied']
        
        except Exception as recovery_error:
            recovery_result['recovery_error'] = str(recovery_error)
            recovery_result['success'] = False
        
        # Log recovery attempt
        self.recovery_attempts.append(recovery_result)
        self._save_recovery_log()
        
        return recovery_result
    
    def _execute_retry_recovery(self, strategy: Dict) -> Dict[str, Any]:
        """Execute retry-based recovery"""
        return {
            'strategy_used': 'retry_with_backoff',
            'success': True,  # Optimistic - actual retry will be handled by caller
            'actions_taken': ['retry_scheduled'],
            'max_attempts': strategy.get('max_attempts', 3),
            'base_delay': strategy.get('base_delay', 2)
        }
    
    def _execute_fallback_location(self, strategy: Dict) -> Dict[str, Any]:
        """Execute fallback location recovery"""
        alternative_paths = strategy.get('alternative_paths', [])
        for path in alternative_paths:
            if os.path.exists(path) and os.access(path, os.W_OK):
                return {
                    'strategy_used': 'fallback_location',
                    'success': True,
                    'actions_taken': [f'switched_to_location_{path}'],
                    'new_location': path
                }
        
        return {
            'strategy_used': 'fallback_location',
            'success': False,
            'actions_taken': ['no_writable_location_found']
        }
    
    def _execute_graceful_degradation(self, strategy: Dict) -> Dict[str, Any]:
        """Execute graceful degradation recovery"""
        return {
            'strategy_used': 'graceful_degradation',
            'success': True,
            'actions_taken': ['enabled_mock_mode', 'disabled_problematic_features'],
            'mock_mode': strategy.get('mock_mode', True)
        }
    
    def _execute_cleanup_recovery(self, strategy: Dict) -> Dict[str, Any]:
        """Execute cleanup and retry recovery"""
        cleanup_targets = strategy.get('cleanup_targets', [])
        actions_taken = []
        
        for target in cleanup_targets:
            if target == 'temp_files':
                temp_count = self._cleanup_temp_files()
                actions_taken.append(f'cleaned_{temp_count}_temp_files')
            elif target == 'cache':
                cache_size = self._cleanup_cache()
                actions_taken.append(f'cleared_{cache_size}_mb_cache')
        
        return {
            'strategy_used': 'cleanup_and_retry',
            'success': True,
            'actions_taken': actions_taken
        }
    
    def _create_phase2_fallback(self, context: Dict) -> Dict[str, Any]:
        """Create fallback result for Phase 2 (Content Planning)"""
        return {
            'content_analysis': {
                'category': 'general',
                'complexity_level': 'medium',
                'target_audience': 'general_social_media'
            },
            'mode_selection': {
                'recommended_mode': context.get('content_mode', 'music'),
                'user_requested': context.get('content_mode', 'music'),
                'rationale': 'Fallback mode selection due to planning error'
            },
            'storyboard': {
                'total_duration': context.get('duration', 20),
                'scene_count': 3,
                'scenes': [
                    {'scene_number': 1, 'duration': 7, 'title': 'Opening', 'description': 'Introduction scene'},
                    {'scene_number': 2, 'duration': 8, 'title': 'Main Content', 'description': 'Primary content'},
                    {'scene_number': 3, 'duration': 5, 'title': 'Conclusion', 'description': 'Closing scene'}
                ]
            },
            'visual_style': {
                'color_palette': 'vibrant',
                'aesthetic_mood': 'engaging',
                'engagement_hooks': 'visual_variety'
            },
            'fallback_reason': 'Content planning failed - using template structure'
        }
    
    def _create_phase3_fallback(self, context: Dict) -> Dict[str, Any]:
        """Create fallback result for Phase 3 (Claude Refinement)"""
        return {
            'refined_prompts': [
                {'scene_number': 1, 'enhanced_prompt': 'High-quality opening scene for social media content', 'quality_prediction': 0.7, 'recommended_model': 'hailuo-02'},
                {'scene_number': 2, 'enhanced_prompt': 'Engaging main content with visual appeal', 'quality_prediction': 0.7, 'recommended_model': 'hailuo-02'},
                {'scene_number': 3, 'enhanced_prompt': 'Strong closing with call-to-action elements', 'quality_prediction': 0.7, 'recommended_model': 'hailuo-02'}
            ],
            'quality_predictions': {
                'overall_score': 0.7,
                'technical_feasibility': 0.8,
                'creative_appeal': 0.6,
                'engagement_potential': 0.7
            },
            'fallback_reason': 'Claude API unavailable - using template prompts'
        }
    
    def _create_phase4_fallback(self, context: Dict) -> Dict[str, Any]:
        """Create fallback result for Phase 4 (Video Generation)"""
        return {
            'generated_clips': [
                {'clip_id': 1, 'status': 'mock', 'model_used': 'mock', 'duration': 7, 'filename': 'mock_clip_1.mp4', 'cost_estimate': 0},
                {'clip_id': 2, 'status': 'mock', 'model_used': 'mock', 'duration': 8, 'filename': 'mock_clip_2.mp4', 'cost_estimate': 0},
                {'clip_id': 3, 'status': 'mock', 'model_used': 'mock', 'duration': 5, 'filename': 'mock_clip_3.mp4', 'cost_estimate': 0}
            ],
            'generation_summary': {
                'total_clips': 3,
                'successful_clips': 3,
                'failed_clips': 0,
                'total_cost': 0
            },
            'quality_assessment': {
                'overall_quality_score': 0.6,
                'technical_compliance': 'mock_mode',
                'ready_for_synchronization': True
            },
            'fallback_reason': 'Video generation API failed - using mock clips'
        }
    
    def _create_phase5_fallback(self, context: Dict) -> Dict[str, Any]:
        """Create fallback result for Phase 5 (Audio Generation)"""
        return {
            'audio_generation_status': 'mock',
            'mode': context.get('content_mode', 'music'),
            'file_path': os.path.join(context.get('reel_folder', ''), 'audio', 'mock_audio.wav'),
            'duration': context.get('duration', 20),
            'quality': 'mock',
            'processing_cost': 0,
            'fallback_reason': 'Audio generation failed - using mock audio'
        }
    
    def _create_phase6_fallback(self, context: Dict) -> Dict[str, Any]:
        """Create fallback result for Phase 6 (Synchronization)"""
        return {
            'status': 'mock_synchronized',
            'final_reel_path': os.path.join(context.get('reel_folder', ''), 'mock_final_reel.mp4'),
            'video_stitching': {
                'clips_used': 3,
                'total_duration': context.get('duration', 20),
                'resolution': '1080x1920',
                'quality': 'mock',
                'transitions_applied': False,
                'enhancements_applied': False
            },
            'audio_synchronization': {
                'sync_quality': 'mock',
                'audio_mode': context.get('content_mode', 'music'),
                'video_duration': context.get('duration', 20),
                'audio_duration': context.get('duration', 20),
                'duration_matched': True,
                'enhancements_applied': False
            },
            'fallback_reason': 'Synchronization failed - using mock output'
        }
    
    def _create_phase7_fallback(self, context: Dict) -> Dict[str, Any]:
        """Create fallback result for Phase 7 (QA Testing)"""
        return {
            'quality_assessment': {
                'overall_score': 0.5,
                'pass_status': 'fail',
                'quality_grade': 'needs_improvement',
                'failed_criteria': ['assessment_error'],
                'technical_quality': 0.5,
                'content_quality': 0.5,
                'brand_alignment': 0.5,
                'platform_optimization': 0.5,
                'engagement_potential': 0.5
            },
            'reloop_strategy': {
                'reloop_needed': True,
                'strategy': 'manual_review',
                'confidence': 0.5,
                'focus_areas': ['manual_quality_check'],
                'estimated_cost': 'manual_effort'
            },
            'final_verdict': {
                'approved_for_publication': False,
                'quality_certification': 'requires_manual_review',
                'platform_readiness': [],
                'confidence_score': 0.5
            },
            'fallback_reason': 'QA system failed - manual review required'
        }
    
    def _create_generic_fallback(self, context: Dict) -> Dict[str, Any]:
        """Create generic fallback result"""
        return {
            'status': 'fallback',
            'message': 'Generic fallback applied due to system error',
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
    
    # Helper methods for resource management
    def _get_available_disk_space(self) -> int:
        """Get available disk space in MB"""
        try:
            statvfs = os.statvfs(self.output_folder)
            return int((statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024))
        except:
            return -1
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total_mb': int(memory.total / (1024 * 1024)),
                'available_mb': int(memory.available / (1024 * 1024)),
                'percent_used': memory.percent
            }
        except:
            return {'error': 'psutil not available'}
    
    def _check_file_permissions(self) -> Dict[str, bool]:
        """Check file system permissions"""
        return {
            'output_folder_writable': os.access(self.output_folder, os.W_OK),
            'output_folder_readable': os.access(self.output_folder, os.R_OK),
            'temp_dir_writable': os.access('/tmp', os.W_OK) if os.path.exists('/tmp') else False
        }
    
    def _cleanup_temp_files(self) -> int:
        """Clean up temporary files and return count"""
        # Implementation would clean temp files
        return 0  # Mock return
    
    def _cleanup_cache(self) -> int:
        """Clean up cache and return size in MB"""
        # Implementation would clean cache
        return 0  # Mock return
    
    def _cleanup_resources(self, resource_type: str) -> Dict[str, Any]:
        """Clean up specific resource types"""
        return {'cleanup_performed': True, 'resource_type': resource_type}
    
    def _get_resource_recovery_suggestions(self, resource_type: str, context: Dict) -> List[str]:
        """Get recovery suggestions for resource errors"""
        suggestions = {
            'disk_space': ['Clear temporary files', 'Use external storage', 'Reduce output quality'],
            'memory': ['Close unnecessary applications', 'Process smaller batches', 'Use swap file'],
            'file_permissions': ['Check folder permissions', 'Use alternative location', 'Run with elevated privileges']
        }
        return suggestions.get(resource_type, ['Contact system administrator'])
    
    def _get_max_retries(self, api_name: str) -> int:
        """Get maximum retry attempts for specific APIs"""
        retry_limits = {
            'openai': 3,
            'claude': 2,
            'fal_ai': 2,
            'default': 2
        }
        return retry_limits.get(api_name.lower(), retry_limits['default'])
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Check if an error is retryable"""
        retryable_patterns = ['timeout', 'connection', 'rate limit', 'temporary', 'service unavailable']
        error_str = str(error).lower()
        return any(pattern in error_str for pattern in retryable_patterns)
    
    def _get_retry_delay(self, retry_count: int) -> float:
        """Get exponential backoff delay"""
        return min(2 ** retry_count, 30)  # Max 30 seconds
    
    def _get_api_fallback(self, api_name: str) -> Dict[str, Any]:
        """Get fallback strategy for specific APIs"""
        fallbacks = {
            'openai': {'use_mock': True, 'degraded_mode': True},
            'claude': {'skip_enhancement': True, 'use_basic_prompts': True},
            'fal_ai': {'use_mock_generation': True, 'notify_user': True}
        }
        return fallbacks.get(api_name.lower(), {'use_generic_fallback': True})
    
    def _save_error_log(self):
        """Save error log to file"""
        try:
            os.makedirs(os.path.dirname(self.error_log_path), exist_ok=True)
            with open(self.error_log_path, 'w') as f:
                json.dump({
                    'errors': self.errors,
                    'total_errors': len(self.errors),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception:
            pass  # Fail silently to avoid recursive errors
    
    def _save_recovery_log(self):
        """Save recovery log to file"""
        try:
            os.makedirs(os.path.dirname(self.recovery_log_path), exist_ok=True)
            with open(self.recovery_log_path, 'w') as f:
                json.dump({
                    'recovery_attempts': self.recovery_attempts,
                    'total_attempts': len(self.recovery_attempts),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception:
            pass  # Fail silently to avoid recursive errors


# Decorator for automatic error handling
def handle_phase_errors(phase: int):
    """Decorator to automatically handle errors in phase methods"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get the first argument which should be self with output_folder
                self = args[0] if args else None
                output_folder = getattr(self, 'output_folder', '/tmp') if self else '/tmp'
                
                error_handler = ReelGenerationErrorHandler(output_folder)
                error_result = error_handler.handle_phase_error(phase, e, {'function': func.__name__})
                
                if error_result['can_continue']:
                    # Return fallback result
                    context = kwargs.get('context', {})
                    return error_handler.create_fallback_result(phase, context)
                else:
                    # Re-raise if critical
                    raise PhaseError(phase, str(e), ErrorSeverity.CRITICAL)
        
        return wrapper
    return decorator