"""
Performance Optimization and Resource Management for Video Reel Generation
Optimizes memory usage, processing speed, and resource allocation across all phases
"""

import os
import time
import json
import psutil
import gc
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class PerformanceMonitor:
    """Monitor system performance during reel generation"""
    
    def __init__(self):
        self.metrics = []
        self.start_time = None
        self.phase_timings = {}
        self.memory_snapshots = []
        self.peak_memory = 0
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.metrics = []
        self.memory_snapshots = []
        self.peak_memory = 0
        
    def record_phase_start(self, phase: int, phase_name: str):
        """Record the start of a phase"""
        current_time = time.time()
        memory_info = self._get_memory_info()
        
        self.phase_timings[phase] = {
            'name': phase_name,
            'start_time': current_time,
            'start_memory': memory_info['used_mb']
        }
        
        self.memory_snapshots.append({
            'phase': phase,
            'timestamp': current_time,
            'memory_mb': memory_info['used_mb'],
            'event': 'phase_start'
        })
        
    def record_phase_end(self, phase: int):
        """Record the end of a phase"""
        if phase not in self.phase_timings:
            return
            
        current_time = time.time()
        memory_info = self._get_memory_info()
        
        phase_data = self.phase_timings[phase]
        phase_data['end_time'] = current_time
        phase_data['duration'] = current_time - phase_data['start_time']
        phase_data['end_memory'] = memory_info['used_mb']
        phase_data['memory_delta'] = memory_info['used_mb'] - phase_data['start_memory']
        
        self.memory_snapshots.append({
            'phase': phase,
            'timestamp': current_time,
            'memory_mb': memory_info['used_mb'],
            'event': 'phase_end'
        })
        
        # Update peak memory
        self.peak_memory = max(self.peak_memory, memory_info['used_mb'])
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            'total_duration_seconds': total_time,
            'phase_timings': self.phase_timings,
            'memory_usage': {
                'peak_memory_mb': self.peak_memory,
                'current_memory_mb': self._get_memory_info()['used_mb'],
                'memory_snapshots': self.memory_snapshots
            },
            'performance_metrics': self._calculate_metrics(),
            'resource_efficiency': self._calculate_efficiency(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get current memory information"""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            return {
                'used_mb': int(process.memory_info().rss / (1024 * 1024)),
                'system_total_mb': int(memory.total / (1024 * 1024)),
                'system_available_mb': int(memory.available / (1024 * 1024)),
                'system_percent': memory.percent
            }
        except Exception:
            return {
                'used_mb': 0,
                'system_total_mb': 0,
                'system_available_mb': 0,
                'system_percent': 0,
                'error': 'psutil_unavailable'
            }
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.phase_timings:
            return {}
        
        phase_durations = [p.get('duration', 0) for p in self.phase_timings.values() if 'duration' in p]
        
        return {
            'average_phase_duration': sum(phase_durations) / len(phase_durations) if phase_durations else 0,
            'slowest_phase': max(self.phase_timings.items(), key=lambda x: x[1].get('duration', 0))[0] if phase_durations else None,
            'fastest_phase': min(self.phase_timings.items(), key=lambda x: x[1].get('duration', 0))[0] if phase_durations else None,
            'total_memory_allocated': sum(p.get('memory_delta', 0) for p in self.phase_timings.values()),
            'phases_completed': len([p for p in self.phase_timings.values() if 'duration' in p])
        }
    
    def _calculate_efficiency(self) -> Dict[str, Any]:
        """Calculate resource efficiency metrics"""
        total_time = sum(p.get('duration', 0) for p in self.phase_timings.values())
        
        return {
            'time_efficiency': 'good' if total_time < 300 else 'moderate' if total_time < 600 else 'slow',
            'memory_efficiency': 'good' if self.peak_memory < 500 else 'moderate' if self.peak_memory < 1000 else 'high',
            'overall_rating': self._get_overall_efficiency_rating()
        }
    
    def _get_overall_efficiency_rating(self) -> str:
        """Get overall efficiency rating"""
        total_time = sum(p.get('duration', 0) for p in self.phase_timings.values())
        
        if total_time < 180 and self.peak_memory < 400:
            return 'excellent'
        elif total_time < 300 and self.peak_memory < 600:
            return 'good'
        elif total_time < 600 and self.peak_memory < 1000:
            return 'acceptable'
        else:
            return 'needs_optimization'


class ResourceManager:
    """Manage system resources during reel generation"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.temp_files = []
        self.active_processes = []
        self.resource_limits = {
            'max_memory_mb': 1000,
            'max_temp_files': 50,
            'max_concurrent_requests': 3
        }
        self.cleanup_registry = []
        
    @contextmanager
    def managed_resource(self, resource_type: str, resource_data: Dict):
        """Context manager for automatic resource cleanup"""
        resource_id = f"{resource_type}_{int(time.time())}"
        
        try:
            # Register resource
            self.cleanup_registry.append({
                'id': resource_id,
                'type': resource_type,
                'data': resource_data,
                'created_at': time.time()
            })
            
            yield resource_id
            
        finally:
            # Cleanup resource
            self._cleanup_resource(resource_id)
    
    def allocate_temp_space(self, size_mb: int) -> str:
        """Allocate temporary space with automatic cleanup"""
        temp_dir = os.path.join(self.output_folder, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Check available space
        available_space = self._get_available_space_mb()
        if available_space < size_mb * 2:  # Require 2x the space for safety
            self._cleanup_old_temp_files()
            
        temp_id = f"temp_{int(time.time())}"
        temp_path = os.path.join(temp_dir, temp_id)
        
        self.temp_files.append({
            'id': temp_id,
            'path': temp_path,
            'size_mb': size_mb,
            'created_at': time.time()
        })
        
        return temp_path
    
    def optimize_for_phase(self, phase: int) -> Dict[str, Any]:
        """Optimize resources for specific phase requirements"""
        optimizations = {
            2: self._optimize_for_content_planning,
            3: self._optimize_for_claude_processing,
            4: self._optimize_for_video_generation,
            5: self._optimize_for_audio_processing,
            6: self._optimize_for_video_editing,
            7: self._optimize_for_qa_processing
        }
        
        optimizer = optimizations.get(phase, self._default_optimization)
        return optimizer()
    
    def _optimize_for_content_planning(self) -> Dict[str, Any]:
        """Optimize for Phase 2 - Content Planning"""
        # Lightweight optimization for text processing
        gc.collect()  # Clean up memory
        
        return {
            'optimization_applied': 'content_planning',
            'memory_cleaned': True,
            'concurrent_limit': 2,
            'timeout_seconds': 60
        }
    
    def _optimize_for_claude_processing(self) -> Dict[str, Any]:
        """Optimize for Phase 3 - Claude Processing"""
        return {
            'optimization_applied': 'claude_processing',
            'api_timeout': 45,
            'retry_limit': 2,
            'concurrent_requests': 1
        }
    
    def _optimize_for_video_generation(self) -> Dict[str, Any]:
        """Optimize for Phase 4 - Video Generation"""
        # Prepare for high resource usage
        self._cleanup_old_temp_files()
        gc.collect()
        
        return {
            'optimization_applied': 'video_generation',
            'temp_space_allocated': True,
            'memory_limit_mb': 800,
            'concurrent_generations': min(2, self._get_optimal_concurrency()),
            'timeout_minutes': 10
        }
    
    def _optimize_for_audio_processing(self) -> Dict[str, Any]:
        """Optimize for Phase 5 - Audio Processing"""
        return {
            'optimization_applied': 'audio_processing',
            'buffer_size': 'optimal',
            'concurrent_limit': 1,
            'temp_audio_cleanup': True
        }
    
    def _optimize_for_video_editing(self) -> Dict[str, Any]:
        """Optimize for Phase 6 - Video Editing"""
        # Ensure maximum available memory for MoviePy
        self._cleanup_all_temp_files()
        gc.collect()
        
        return {
            'optimization_applied': 'video_editing',
            'moviepy_threads': min(4, os.cpu_count()),
            'temp_video_space': True,
            'memory_priority': 'high'
        }
    
    def _optimize_for_qa_processing(self) -> Dict[str, Any]:
        """Optimize for Phase 7 - QA Processing"""
        return {
            'optimization_applied': 'qa_processing',
            'analysis_depth': 'comprehensive',
            'concurrent_assessments': 1
        }
    
    def _default_optimization(self) -> Dict[str, Any]:
        """Default optimization for unknown phases"""
        return {
            'optimization_applied': 'default',
            'memory_cleanup': True
        }
    
    def _get_optimal_concurrency(self) -> int:
        """Calculate optimal concurrency based on system resources"""
        try:
            memory = psutil.virtual_memory()
            cpu_count = os.cpu_count() or 1
            
            # Conservative approach: limit based on available memory
            available_gb = memory.available / (1024 ** 3)
            
            if available_gb > 8:
                return min(3, cpu_count)
            elif available_gb > 4:
                return min(2, cpu_count)
            else:
                return 1
        except:
            return 1  # Safe fallback
    
    def _get_available_space_mb(self) -> int:
        """Get available disk space in MB"""
        try:
            statvfs = os.statvfs(self.output_folder)
            return int((statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024))
        except:
            return 1000  # Default assumption
    
    def _cleanup_old_temp_files(self):
        """Clean up old temporary files"""
        current_time = time.time()
        cleaned_count = 0
        
        for temp_file in self.temp_files[:]:
            if current_time - temp_file['created_at'] > 3600:  # 1 hour old
                try:
                    if os.path.exists(temp_file['path']):
                        if os.path.isdir(temp_file['path']):
                            import shutil
                            shutil.rmtree(temp_file['path'])
                        else:
                            os.remove(temp_file['path'])
                    self.temp_files.remove(temp_file)
                    cleaned_count += 1
                except:
                    pass  # Ignore cleanup errors
        
        return cleaned_count
    
    def _cleanup_all_temp_files(self):
        """Clean up all temporary files"""
        cleaned_count = 0
        
        for temp_file in self.temp_files[:]:
            try:
                if os.path.exists(temp_file['path']):
                    if os.path.isdir(temp_file['path']):
                        import shutil
                        shutil.rmtree(temp_file['path'])
                    else:
                        os.remove(temp_file['path'])
                self.temp_files.remove(temp_file)
                cleaned_count += 1
            except:
                pass  # Ignore cleanup errors
        
        return cleaned_count
    
    def _cleanup_resource(self, resource_id: str):
        """Clean up a specific resource"""
        for resource in self.cleanup_registry[:]:
            if resource['id'] == resource_id:
                try:
                    resource_type = resource['type']
                    
                    if resource_type == 'temp_file':
                        path = resource['data'].get('path')
                        if path and os.path.exists(path):
                            os.remove(path)
                    elif resource_type == 'temp_dir':
                        path = resource['data'].get('path')
                        if path and os.path.exists(path):
                            import shutil
                            shutil.rmtree(path)
                    
                    self.cleanup_registry.remove(resource)
                except:
                    pass  # Ignore cleanup errors
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get summary of resource usage"""
        return {
            'temp_files_active': len(self.temp_files),
            'cleanup_registry_size': len(self.cleanup_registry),
            'memory_usage': self._get_current_memory_usage(),
            'disk_usage': self._get_disk_usage(),
            'system_resources': self._get_system_resource_info()
        }
    
    def _get_current_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        try:
            process = psutil.Process()
            return {
                'process_memory_mb': int(process.memory_info().rss / (1024 * 1024)),
                'memory_percent': process.memory_percent()
            }
        except:
            return {'error': 'unable_to_get_memory_info'}
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            usage = psutil.disk_usage(self.output_folder)
            return {
                'total_gb': int(usage.total / (1024 ** 3)),
                'used_gb': int(usage.used / (1024 ** 3)),
                'free_gb': int(usage.free / (1024 ** 3)),
                'percent_used': (usage.used / usage.total) * 100
            }
        except:
            return {'error': 'unable_to_get_disk_info'}
    
    def _get_system_resource_info(self) -> Dict[str, Any]:
        """Get system resource information"""
        try:
            return {
                'cpu_count': os.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'system_memory_gb': int(psutil.virtual_memory().total / (1024 ** 3)),
                'available_memory_gb': int(psutil.virtual_memory().available / (1024 ** 3))
            }
        except:
            return {'error': 'unable_to_get_system_info'}


class ConcurrencyManager:
    """Manage concurrent operations to optimize performance"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.active_futures = []
        self.completed_results = []
        
    @contextmanager
    def parallel_execution(self, max_workers: Optional[int] = None):
        """Context manager for parallel execution"""
        workers = max_workers or self.max_workers
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            try:
                yield executor
            finally:
                # Ensure all futures are completed or cancelled
                for future in self.active_futures:
                    if not future.done():
                        future.cancel()
                self.active_futures.clear()
    
    def execute_parallel_tasks(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """Execute multiple tasks in parallel"""
        results = []
        
        with self.parallel_execution() as executor:
            # Submit all tasks
            futures = []
            for task in tasks:
                future = executor.submit(task['function'], *task.get('args', []), **task.get('kwargs', {}))
                futures.append({
                    'future': future,
                    'task_id': task.get('id', len(futures)),
                    'task_name': task.get('name', 'unnamed_task')
                })
                self.active_futures.append(future)
            
            # Collect results as they complete
            for future_data in as_completed([f['future'] for f in futures]):
                try:
                    result = future_data.result(timeout=300)  # 5 minute timeout
                    
                    # Find the corresponding task info
                    task_info = next((f for f in futures if f['future'] == future_data), None)
                    
                    results.append({
                        'task_id': task_info['task_id'] if task_info else len(results),
                        'task_name': task_info['task_name'] if task_info else 'unknown',
                        'result': result,
                        'status': 'completed',
                        'completion_time': time.time()
                    })
                    
                except Exception as e:
                    task_info = next((f for f in futures if f['future'] == future_data), None)
                    results.append({
                        'task_id': task_info['task_id'] if task_info else len(results),
                        'task_name': task_info['task_name'] if task_info else 'unknown',
                        'result': None,
                        'error': str(e),
                        'status': 'failed',
                        'completion_time': time.time()
                    })
        
        self.completed_results.extend(results)
        return results
    
    def optimize_task_scheduling(self, tasks: List[Dict], system_resources: Dict) -> List[Dict]:
        """Optimize task scheduling based on system resources"""
        # Sort tasks by priority and resource requirements
        cpu_intensive_tasks = [t for t in tasks if t.get('type') == 'cpu_intensive']
        io_intensive_tasks = [t for t in tasks if t.get('type') == 'io_intensive']
        network_tasks = [t for t in tasks if t.get('type') == 'network']
        
        # Determine optimal scheduling based on system resources
        available_memory = system_resources.get('available_memory_gb', 4)
        cpu_count = system_resources.get('cpu_count', 2)
        
        optimized_schedule = []
        
        # Schedule network tasks first (they can run in parallel with others)
        optimized_schedule.extend(network_tasks)
        
        # Schedule IO tasks next
        optimized_schedule.extend(io_intensive_tasks)
        
        # Schedule CPU tasks last, with concurrency based on available cores
        if available_memory > 6 and cpu_count > 2:
            optimized_schedule.extend(cpu_intensive_tasks)
        else:
            # Serialize CPU tasks if resources are limited
            for task in cpu_intensive_tasks:
                task['force_serial'] = True
                optimized_schedule.append(task)
        
        return optimized_schedule


def optimize_reel_generation_performance(output_folder: str) -> Dict[str, Any]:
    """Main function to set up performance optimization for reel generation"""
    
    # Initialize components
    monitor = PerformanceMonitor()
    resource_manager = ResourceManager(output_folder)
    concurrency_manager = ConcurrencyManager()
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Get system information for optimization
    system_info = resource_manager._get_system_resource_info()
    
    # Apply general optimizations
    gc.collect()  # Clean up memory
    
    optimization_config = {
        'performance_monitoring': True,
        'resource_management': True,
        'concurrency_optimization': True,
        'system_info': system_info,
        'optimization_level': _determine_optimization_level(system_info),
        'recommended_settings': _get_recommended_settings(system_info)
    }
    
    return {
        'monitor': monitor,
        'resource_manager': resource_manager,
        'concurrency_manager': concurrency_manager,
        'config': optimization_config
    }


def _determine_optimization_level(system_info: Dict) -> str:
    """Determine appropriate optimization level based on system resources"""
    try:
        memory_gb = system_info.get('system_memory_gb', 4)
        cpu_count = system_info.get('cpu_count', 2)
        
        if memory_gb >= 16 and cpu_count >= 8:
            return 'high_performance'
        elif memory_gb >= 8 and cpu_count >= 4:
            return 'balanced'
        elif memory_gb >= 4 and cpu_count >= 2:
            return 'conservative'
        else:
            return 'minimal'
    except:
        return 'conservative'


def _get_recommended_settings(system_info: Dict) -> Dict[str, Any]:
    """Get recommended settings based on system capabilities"""
    try:
        memory_gb = system_info.get('system_memory_gb', 4)
        cpu_count = system_info.get('cpu_count', 2)
        
        settings = {
            'max_concurrent_requests': min(3, cpu_count),
            'memory_limit_mb': min(1000, int(memory_gb * 200)),  # 200MB per GB of RAM
            'temp_cleanup_interval': 30,  # minutes
            'performance_logging': True
        }
        
        # Adjust based on available resources
        if memory_gb < 4:
            settings.update({
                'enable_aggressive_cleanup': True,
                'reduce_quality_for_speed': True,
                'max_file_cache_size': 10
            })
        elif memory_gb >= 8:
            settings.update({
                'enable_parallel_processing': True,
                'cache_intermediate_results': True,
                'max_file_cache_size': 50
            })
        
        return settings
    
    except:
        return {
            'max_concurrent_requests': 1,
            'memory_limit_mb': 500,
            'conservative_mode': True
        }