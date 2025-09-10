"""
FAL.AI F5 TTS integration with professional audio generation and processing
"""

import os
import requests
import time
import json
from typing import List, Dict, Any, Optional, Union
import fal_client
from decouple import config
try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None
    print("⚠️  pydub not installed. Audio optimization will be limited.")

# Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()


class AudioGenerator:
    """Advanced FAL.AI F5 TTS integration with professional audio processing and intelligent mode selection"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        
        # Load FAL_KEY with multiple fallbacks
        self.fal_key = config('FAL_KEY', default='')
        if not self.fal_key:
            self.fal_key = os.getenv('FAL_KEY', '')
        if not self.fal_key:
            self.fal_key = os.environ.get('FAL_KEY', '')
            
        print(f"🔑 FAL_KEY status: {'✅ Found' if self.fal_key else '❌ Missing'}")
        if self.fal_key:
            print(f"🔑 FAL_KEY prefix: {self.fal_key[:8]}...")
        
        # Validate and ensure audio folder exists
        if not output_folder or not os.path.exists(output_folder):
            raise ValueError(f"Output folder does not exist or is invalid: {output_folder}")
        
        self.audio_folder = os.path.join(output_folder, 'audio')
        try:
            os.makedirs(self.audio_folder, exist_ok=True)
            print(f"📁 Created audio folder: {self.audio_folder}")
        except (PermissionError, OSError) as e:
            raise ValueError(f"Cannot create audio folder {self.audio_folder}: {e}")
        
        # Initialize FAL client
        if self.fal_key:
            fal_client.api_key = self.fal_key
            os.environ['FAL_KEY'] = self.fal_key
        else:
            print("⚠️  FAL_KEY not found. Audio generation will use mock mode.")
        
        # FAL AI F5 TTS Configuration
        self.f5_tts_config = {
            'endpoint': 'fal-ai/f5-tts',
            'cost_per_1000_chars': 0.05,
            'max_duration': 30,  # seconds
            'sample_rate': 44100,
            'supported_formats': ['wav', 'mp3'],
            'voice_options': {
                'professional': 'A professional, clear voice suitable for business content',
                'casual': 'A friendly, approachable voice for lifestyle content',
                'energetic': 'An enthusiastic, upbeat voice for fitness and motivational content',
                'calm': 'A soothing, peaceful voice for wellness and meditation content'
            }
        }
        
        # Music generation configuration (placeholder for future implementation)
        self.music_config = {
            'themes': {
                'upbeat': 'Energetic, motivational background music',
                'cinematic': 'Epic, dramatic orchestral music',
                'ambient': 'Soft, atmospheric background music',
                'corporate': 'Professional, business-appropriate music',
                'trendy': 'Modern, social media trending sounds'
            }
        }
    
    def generate_audio_content(self, video_generation_result: Dict, content_mode: str, context: Dict) -> Dict:
        """Generate audio content based on video generation results and content mode"""
        
        try:
            print(f"🎵 PHASE 5: Audio Generation Starting")
            print(f"   🎚️  Content Mode: {content_mode}")
            print(f"   📁 Output folder: {self.audio_folder}")
            
            # Extract video generation data
            video_data = self._extract_video_generation_data(video_generation_result)
            total_duration = video_data['total_duration']
            video_clips = video_data['generated_clips']
            
            print(f"   ⏱️  Total duration: {total_duration}s")
            print(f"   🎬 Video clips: {len(video_clips)}")
            
            # Generate audio based on content mode
            if content_mode == 'narration':
                audio_result = self._generate_narration_audio(video_data, context)
            else:  # music mode
                audio_result = self._generate_background_music(video_data, context)
            
            # Process and optimize audio
            processed_audio = self._process_and_optimize_audio(audio_result, total_duration)
            
            # Validate audio quality
            quality_assessment = self._validate_audio_quality(processed_audio)
            
            # Build comprehensive result
            result = {
                'audio_generation_status': processed_audio['status'],
                'content_mode': content_mode,
                'generated_audio': processed_audio,
                'generation_summary': {
                    'audio_type': content_mode,
                    'duration': total_duration,
                    'theme': context.get('audio_theme', 'professional'),
                    'cost': processed_audio.get('cost_estimate', 0.0),
                    'status': processed_audio['status']
                },
                'quality_assessment': quality_assessment,
                'next_phase_data': {
                    'audio_folder': self.audio_folder,
                    'final_audio_file': processed_audio.get('filename', ''),
                    'audio_duration': total_duration,
                    'video_clips': len(video_clips),
                    'ready_for_phase_6': quality_assessment.get('ready_for_synchronization', False)
                }
            }
            
            if content_mode == 'narration' and 'script_content' in audio_result:
                result['script_content'] = audio_result['script_content']
            
            print(f"\n🎯 AUDIO GENERATION COMPLETE!")
            print(f"   ✅ Status: {processed_audio['status']}")
            print(f"   💰 Cost: ${processed_audio.get('cost_estimate', 0.0):.3f}")
            print(f"   📊 Quality: {quality_assessment.get('audio_quality_score', 0.0):.2f}")
            print(f"   🚀 Ready for Phase 6: {quality_assessment.get('ready_for_synchronization', False)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Audio generation error: {str(e)}")
            return self._create_error_result(str(e), content_mode, context)
    
    def _extract_video_generation_data(self, video_result: Union[Dict, str]) -> Dict:
        """Extract video generation data from Phase 4 results"""
        try:
            if isinstance(video_result, str):
                video_result = json.loads(video_result)
            
            generated_clips = video_result.get('generated_clips', [])
            total_duration = 0
            
            # Calculate total duration from clips
            for clip in generated_clips:
                if clip.get('status') in ['success', 'mock']:
                    clip_duration = clip.get('duration', 8)
                    total_duration += clip_duration
            
            # Fallback duration calculation
            if total_duration == 0:
                next_phase_data = video_result.get('next_phase_data', {})
                total_duration = next_phase_data.get('total_duration', 20)
            
            return {
                'generated_clips': generated_clips,
                'total_duration': total_duration,
                'clips_folder': video_result.get('next_phase_data', {}).get('clips_folder', ''),
                'video_status': video_result.get('video_generation_status', 'unknown')
            }
            
        except Exception as e:
            print(f"⚠️  Error extracting video data: {e}")
            return {
                'generated_clips': [],
                'total_duration': 20,  # default
                'clips_folder': '',
                'video_status': 'unknown'
            }
    
    def _generate_narration_audio(self, video_data: Dict, context: Dict) -> Dict:
        """Generate narration using FAL AI F5 TTS"""
        
        try:
            # Create intelligent script based on user prompt and video content
            script_content = self._create_intelligent_script(video_data, context)
            audio_theme = context.get('audio_theme', 'professional')
            
            print(f"   📝 Generated script ({len(script_content)} chars)")
            print(f"   🎭 Voice style: {audio_theme}")
            print(f"   💰 Estimated cost: ${self._calculate_tts_cost(script_content):.3f}")
            
            if not self.fal_key:
                return self._create_mock_narration(script_content, video_data['total_duration'], audio_theme)
            
            # Generate TTS using FAL AI F5
            tts_result = self._execute_f5_tts_generation(script_content, audio_theme, video_data['total_duration'])
            
            return {
                'type': 'narration',
                'script_content': script_content,
                'tts_result': tts_result,
                'voice_style': audio_theme,
                'cost_estimate': self._calculate_tts_cost(script_content)
            }
            
        except Exception as e:
            print(f"⚠️  Narration generation error: {e}")
            return self._create_mock_narration(
                "Professional narration placeholder script",
                video_data['total_duration'],
                context.get('audio_theme', 'professional')
            )
    
    def _generate_background_music(self, video_data: Dict, context: Dict) -> Dict:
        """Generate background music (mock implementation for Phase 5)"""
        
        try:
            audio_theme = context.get('audio_theme', 'upbeat')
            duration = video_data['total_duration']
            
            print(f"   🎵 Generating background music")
            print(f"   🎼 Theme: {audio_theme}")
            print(f"   ⏱️  Duration: {duration}s")
            print(f"   💰 Cost: Free (development phase)")
            
            # For Phase 5, create high-quality mock music
            return self._create_mock_background_music(audio_theme, duration)
            
        except Exception as e:
            print(f"⚠️  Music generation error: {e}")
            return self._create_mock_background_music('upbeat', video_data['total_duration'])
    
    def _create_intelligent_script(self, video_data: Dict, context: Dict) -> str:
        """Create intelligent script based on user prompt and video content"""
        
        user_prompt = context.get('user_prompt', 'video content')
        platform = context.get('platform', 'instagram')
        duration = video_data['total_duration']
        
        # Analyze content type and create appropriate script
        content_category = self._analyze_content_category(user_prompt)
        
        if content_category == 'fashion':
            script_templates = [
                "Discover the latest fashion trends with our exclusive collection.",
                "Style meets comfort in every piece.",
                "Transform your wardrobe with these must-have items."
            ]
        elif content_category == 'educational':
            script_templates = [
                "Let me walk you through this step by step.",
                "Here's what you need to know about this topic.",
                "This technique will completely change your approach."
            ]
        elif content_category == 'fitness':
            script_templates = [
                "Ready to transform your fitness routine?",
                "These exercises will target all the right muscles.",
                "Consistency is key to seeing real results."
            ]
        elif content_category == 'food':
            script_templates = [
                "This recipe is about to become your new favorite.",
                "Fresh ingredients make all the difference.",
                "The secret ingredient that changes everything."
            ]
        else:  # general/promotional
            script_templates = [
                f"Introducing our latest {user_prompt.lower()}.",
                f"Everything you need to know about {user_prompt.lower()}.",
                f"This {user_prompt.lower()} will exceed your expectations."
            ]
        
        # Select and adapt script based on duration
        base_script = script_templates[0]  # Use first template
        
        # Adapt script length for duration (approximately 150 words per minute)
        if duration <= 10:
            # Short script for quick reels
            script = f"{base_script} Perfect for {platform}. Don't miss out!"
        elif duration <= 20:
            # Medium script
            script = f"{base_script} We've carefully crafted this to give you exactly what you're looking for. The quality and attention to detail will speak for themselves."
        else:
            # Longer script
            script = f"{base_script} We've carefully crafted this to give you exactly what you're looking for. The quality and attention to detail will speak for themselves. Whether you're just getting started or you're already experienced, this is designed to meet your needs perfectly."
        
        # Add platform-specific call-to-action
        if platform.lower() == 'tiktok':
            script += " Comment below if you want to see more!"
        elif platform.lower() == 'instagram':
            script += " Save this for later and share with friends!"
        else:
            script += " Let us know what you think in the comments!"
        
        return script
    
    def _analyze_content_category(self, user_prompt: str) -> str:
        """Analyze user prompt to determine content category"""
        prompt_lower = user_prompt.lower()
        
        if any(word in prompt_lower for word in ['fashion', 'clothing', 'style', 'outfit', 'brand', 'nike', 'adidas']):
            return 'fashion'
        elif any(word in prompt_lower for word in ['tutorial', 'how to', 'learn', 'guide', 'education']):
            return 'educational'
        elif any(word in prompt_lower for word in ['fitness', 'workout', 'exercise', 'gym', 'muscle']):
            return 'fitness'
        elif any(word in prompt_lower for word in ['food', 'recipe', 'cooking', 'kitchen', 'ingredient']):
            return 'food'
        else:
            return 'general'
    
    def _execute_f5_tts_generation(self, script: str, voice_style: str, target_duration: float) -> Dict:
        """Execute FAL AI F5 TTS generation with proper error handling"""
        
        try:
            # Prepare F5 TTS parameters
            voice_description = self.f5_tts_config['voice_options'].get(
                voice_style, 
                self.f5_tts_config['voice_options']['professional']
            )
            
            # Adjust speech speed to match target duration
            estimated_duration = len(script) / 150 * 60  # rough estimate (150 chars per minute)
            speed_adjustment = estimated_duration / target_duration if target_duration > 0 else 1.0
            speed_adjustment = max(0.7, min(1.3, speed_adjustment))  # limit between 0.7x and 1.3x
            
            tts_params = {
                'text': script,
                'voice_description': voice_description,
                'speed': speed_adjustment,
                'sample_rate': self.f5_tts_config['sample_rate']
            }
            
            print(f"   🎤 Calling FAL AI F5 TTS...")
            print(f"   ⚡ Speed adjustment: {speed_adjustment:.2f}x")
            
            # Submit to FAL AI F5 TTS
            result = fal_client.submit(
                self.f5_tts_config['endpoint'],
                arguments=tts_params
            )
            
            if not result or not hasattr(result, 'request_id'):
                raise Exception("FAL AI F5 TTS submission failed")
            
            print(f"   📋 Request ID: {result.request_id}")
            
            # Wait for result with timeout
            max_wait_time = 120  # 2 minutes for TTS
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    final_result = result.get()
                    elapsed = time.time() - start_time
                    print(f"   ✅ TTS completed in {elapsed:.1f}s")
                    
                    if 'audio' in final_result and 'url' in final_result['audio']:
                        return {
                            'status': 'success',
                            'audio_url': final_result['audio']['url'],
                            'duration': final_result.get('duration', target_duration),
                            'sample_rate': self.f5_tts_config['sample_rate'],
                            'format': 'wav'
                        }
                    else:
                        raise Exception("No audio URL in F5 TTS result")
                        
                except Exception as get_error:
                    if time.time() - start_time > max_wait_time:
                        raise Exception(f"F5 TTS timeout after {max_wait_time}s")
                    time.sleep(5)  # wait 5 seconds before retry
            
            raise Exception(f"F5 TTS timeout after {max_wait_time}s")
            
        except Exception as e:
            print(f"   ❌ F5 TTS generation failed: {str(e)}")
            raise e
    
    def _process_and_optimize_audio(self, audio_result: Dict, target_duration: float) -> Dict:
        """Process and optimize generated audio for social media"""
        
        try:
            audio_type = audio_result.get('type', 'unknown')
            
            if audio_result.get('status') == 'mock':
                # Handle mock audio
                return self._create_mock_audio_file(audio_result, target_duration)
            
            if audio_type == 'narration' and 'tts_result' in audio_result:
                # Process TTS narration
                return self._process_tts_audio(audio_result, target_duration)
            elif audio_type == 'background_music':
                # Process background music
                return self._process_music_audio(audio_result, target_duration)
            else:
                # Fallback to mock
                return self._create_mock_audio_file(audio_result, target_duration)
                
        except Exception as e:
            print(f"⚠️  Audio processing error: {e}")
            return self._create_mock_audio_file(audio_result, target_duration)
    
    def _process_tts_audio(self, audio_result: Dict, target_duration: float) -> Dict:
        """Process TTS audio from FAL AI F5 TTS"""
        
        try:
            tts_result = audio_result.get('tts_result', {})
            
            if tts_result.get('status') == 'success' and 'audio_url' in tts_result:
                # Download audio from FAL AI
                audio_url = tts_result['audio_url']
                audio_filename = f"narration_{int(time.time())}.wav"
                audio_path = os.path.join(self.audio_folder, audio_filename)
                
                print(f"   💾 Downloading TTS audio...")
                success = self._download_audio(audio_url, audio_path)
                
                if success:
                    # Process audio with pydub if available
                    processed_path = self._optimize_audio_file(audio_path, target_duration)
                    
                    return {
                        'file_path': processed_path,
                        'filename': os.path.basename(processed_path),
                        'duration': target_duration,
                        'type': 'narration',
                        'status': 'success',
                        'format': 'wav',
                        'cost_estimate': audio_result.get('cost_estimate', 0.0),
                        'sample_rate': 44100
                    }
                else:
                    raise Exception("Failed to download TTS audio")
            else:
                raise Exception("TTS generation was not successful")
                
        except Exception as e:
            print(f"   ⚠️  TTS processing failed: {e}")
            # Create mock instead
            return self._create_mock_audio_file(audio_result, target_duration)
    
    def _process_music_audio(self, audio_result: Dict, target_duration: float) -> Dict:
        """Process background music (currently mock implementation)"""
        
        # For Phase 5, we'll create high-quality mock music files
        return self._create_mock_audio_file(audio_result, target_duration)
    
    def _create_mock_audio_file(self, audio_result: Dict, target_duration: float) -> Dict:
        """Create high-quality mock audio file for testing"""
        
        try:
            audio_type = audio_result.get('type', 'narration')
            
            # Create mock audio content based on type
            if audio_type == 'narration':
                audio_filename = f"mock_narration_{int(time.time())}.wav"
                mock_content = self._generate_mock_narration_content(target_duration)
            else:  # background_music
                audio_filename = f"mock_music_{int(time.time())}.wav"
                mock_content = self._generate_mock_music_content(target_duration)
            
            audio_path = os.path.join(self.audio_folder, audio_filename)
            
            # Write mock audio file (silence with proper duration and format)
            with open(audio_path, 'wb') as f:
                f.write(mock_content)
            
            print(f"   🧪 Created mock {audio_type}: {audio_filename}")
            
            return {
                'file_path': audio_path,
                'filename': audio_filename,
                'duration': target_duration,
                'type': audio_type,
                'status': 'mock',
                'format': 'wav',
                'cost_estimate': audio_result.get('cost_estimate', 0.0),
                'sample_rate': 44100
            }
            
        except Exception as e:
            print(f"   ❌ Mock audio creation failed: {e}")
            return {
                'file_path': None,
                'filename': None,
                'duration': target_duration,
                'type': audio_result.get('type', 'unknown'),
                'status': 'failed',
                'format': 'wav',
                'cost_estimate': 0.0,
                'error': str(e)
            }
    
    def _generate_mock_narration_content(self, duration: float) -> bytes:
        """Generate mock narration content (WAV format silence)"""
        
        # Create a simple WAV header for the specified duration
        sample_rate = 44100
        channels = 1
        bits_per_sample = 16
        
        num_samples = int(duration * sample_rate)
        data_size = num_samples * channels * (bits_per_sample // 8)
        
        # WAV header
        header = bytearray()
        header.extend(b'RIFF')
        header.extend((data_size + 36).to_bytes(4, 'little'))
        header.extend(b'WAVE')
        header.extend(b'fmt ')
        header.extend((16).to_bytes(4, 'little'))
        header.extend((1).to_bytes(2, 'little'))  # PCM format
        header.extend(channels.to_bytes(2, 'little'))
        header.extend(sample_rate.to_bytes(4, 'little'))
        header.extend((sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little'))
        header.extend((channels * bits_per_sample // 8).to_bytes(2, 'little'))
        header.extend(bits_per_sample.to_bytes(2, 'little'))
        header.extend(b'data')
        header.extend(data_size.to_bytes(4, 'little'))
        
        # Add silence data
        audio_data = b'\x00' * data_size
        
        return bytes(header) + audio_data
    
    def _generate_mock_music_content(self, duration: float) -> bytes:
        """Generate mock music content (WAV format silence)"""
        
        # For Phase 5, same as narration but could be enhanced later
        return self._generate_mock_narration_content(duration)
    
    def _download_audio(self, audio_url: str, output_path: str) -> bool:
        """Download audio from URL to local file"""
        
        try:
            response = requests.get(audio_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"   ❌ Audio download failed: {e}")
            return False
    
    def _optimize_audio_file(self, audio_path: str, target_duration: float) -> str:
        """Optimize audio file using pydub for social media"""
        
        try:
            if AudioSegment is None:
                print(f"   ⚠️  pydub not available, returning original file")
                return audio_path
                
            # Load audio with pydub
            audio = AudioSegment.from_file(audio_path)
            
            # Optimize for social media
            optimized_audio = audio
            
            # Normalize volume
            optimized_audio = optimized_audio.normalize()
            
            # Ensure proper duration (trim or pad if needed)
            current_duration = len(optimized_audio) / 1000.0  # pydub uses milliseconds
            target_duration_ms = target_duration * 1000
            
            if current_duration > target_duration:
                # Trim to target duration
                optimized_audio = optimized_audio[:target_duration_ms]
            elif current_duration < target_duration:
                # Pad with silence to reach target duration
                silence_needed = target_duration_ms - len(optimized_audio)
                silence = AudioSegment.silent(duration=silence_needed)
                optimized_audio = optimized_audio + silence
            
            # Ensure proper format for social media
            optimized_audio = optimized_audio.set_frame_rate(44100).set_channels(1)
            
            # Save optimized version
            optimized_path = audio_path.replace('.wav', '_optimized.wav')
            optimized_audio.export(optimized_path, format='wav')
            
            print(f"   ✅ Audio optimized: {os.path.basename(optimized_path)}")
            return optimized_path
            
        except Exception as e:
            print(f"   ⚠️  Audio optimization failed: {e}")
            return audio_path  # return original if optimization fails
    
    def _validate_audio_quality(self, audio_data: Dict) -> Dict:
        """Validate audio quality for social media standards"""
        
        try:
            file_path = audio_data.get('file_path')
            audio_status = audio_data.get('status', 'unknown')
            
            if not file_path or not os.path.exists(file_path):
                return {
                    'audio_quality_score': 0.0,
                    'sync_ready': False,
                    'format_compliance': False,
                    'ready_for_synchronization': False,
                    'validation_notes': 'Audio file not found'
                }
            
            # Basic file validation
            file_size = os.path.getsize(file_path)
            
            if file_size == 0:
                return {
                    'audio_quality_score': 0.0,
                    'sync_ready': False,
                    'format_compliance': False,
                    'ready_for_synchronization': False,
                    'validation_notes': 'Empty audio file'
                }
            
            # Quality scoring based on status and file size
            if audio_status == 'success':
                quality_score = 0.9
                sync_ready = True
                format_compliance = True
                ready_for_sync = True
                notes = 'Professional quality audio generated successfully'
            elif audio_status == 'mock':
                quality_score = 0.7  # Mock is good enough for testing
                sync_ready = True
                format_compliance = True
                ready_for_sync = True
                notes = 'Mock audio created for testing - ready for synchronization'
            else:
                quality_score = 0.3
                sync_ready = False
                format_compliance = False
                ready_for_sync = False
                notes = f'Audio generation failed with status: {audio_status}'
            
            return {
                'audio_quality_score': quality_score,
                'sync_ready': sync_ready,
                'format_compliance': format_compliance,
                'ready_for_synchronization': ready_for_sync,
                'file_size': file_size,
                'validation_notes': notes
            }
            
        except Exception as e:
            return {
                'audio_quality_score': 0.0,
                'sync_ready': False,
                'format_compliance': False,
                'ready_for_synchronization': False,
                'validation_notes': f'Validation error: {str(e)}'
            }
    
    def _calculate_tts_cost(self, script: str) -> float:
        """Calculate FAL AI F5 TTS cost based on character count"""
        
        char_count = len(script)
        cost = (char_count / 1000) * self.f5_tts_config['cost_per_1000_chars']
        return round(cost, 4)
    
    def _create_mock_narration(self, script: str, duration: float, voice_style: str) -> Dict:
        """Create mock narration result for testing"""
        
        return {
            'type': 'narration',
            'script_content': script,
            'voice_style': voice_style,
            'cost_estimate': self._calculate_tts_cost(script),
            'status': 'mock',
            'tts_result': {
                'status': 'mock',
                'duration': duration,
                'sample_rate': 44100,
                'format': 'wav'
            }
        }
    
    def _create_mock_background_music(self, theme: str, duration: float) -> Dict:
        """Create mock background music result for testing"""
        
        return {
            'type': 'background_music',
            'theme': theme,
            'cost_estimate': 0.0,  # Free for mock
            'status': 'mock',
            'music_result': {
                'status': 'mock',
                'duration': duration,
                'sample_rate': 44100,
                'format': 'wav',
                'theme': theme
            }
        }
    
    def _create_error_result(self, error: str, content_mode: str, context: Dict) -> Dict:
        """Create error result structure"""
        
        return {
            'audio_generation_status': 'failed',
            'content_mode': content_mode,
            'generated_audio': {
                'file_path': None,
                'filename': None,
                'duration': 0,
                'type': content_mode,
                'status': 'failed',
                'format': 'wav',
                'cost_estimate': 0.0,
                'error': error
            },
            'generation_summary': {
                'audio_type': content_mode,
                'duration': 0,
                'theme': context.get('audio_theme', 'unknown'),
                'cost': 0.0,
                'status': 'failed',
                'error': error
            },
            'quality_assessment': {
                'audio_quality_score': 0.0,
                'sync_ready': False,
                'format_compliance': False,
                'ready_for_synchronization': False,
                'validation_notes': f'Generation failed: {error}'
            },
            'next_phase_data': {
                'audio_folder': self.audio_folder,
                'final_audio_file': '',
                'audio_duration': 0,
                'video_clips': 0,
                'ready_for_phase_6': False
            },
            'error': error
        }

    def get_cost_estimates(self) -> Dict:
        """Get cost estimates for different audio generation modes"""
        
        return {
            'narration_mode': {
                'cost_per_1000_chars': self.f5_tts_config['cost_per_1000_chars'],
                'typical_script_chars': 400,  # ~20 second narration
                'estimated_cost': 0.02
            },
            'music_mode': {
                'cost_per_generation': 0.0,  # Free in development phase
                'typical_duration': 20,
                'estimated_cost': 0.0
            }
        }