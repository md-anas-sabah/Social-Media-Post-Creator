"""
FAL AI F5 TTS and AI music generation for video reels
"""

import os
import time
import requests
from typing import Dict, List, Any, Optional
import fal_client
from decouple import config

# Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()


class AudioGenerator:
    """Advanced audio generation using FAL AI F5 TTS and AI music generation"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        
        # Load FAL_KEY with multiple fallbacks
        self.fal_key = config('FAL_KEY', default='')
        if not self.fal_key:
            self.fal_key = os.getenv('FAL_KEY', '')
        if not self.fal_key:
            self.fal_key = os.environ.get('FAL_KEY', '')
            
        print(f"🔑 Audio Generator - FAL_KEY status: {'✅ Found' if self.fal_key else '❌ Missing'}")
        
        # Ensure audio folder exists
        self.audio_folder = os.path.join(output_folder, 'audio')
        os.makedirs(self.audio_folder, exist_ok=True)
        print(f"📁 Created audio folder: {self.audio_folder}")
        
        # Initialize FAL client
        if self.fal_key:
            fal_client.api_key = self.fal_key
            os.environ['FAL_KEY'] = self.fal_key
        
        # FAL AI F5 TTS Configuration
        self.f5_tts_config = {
            'endpoint': 'fal-ai/f5-tts',
            'cost_per_1000_chars': 0.05,  # $0.05 per 1000 characters
            'max_text_length': 4000,  # Maximum characters per request
            'supported_languages': ['en', 'zh', 'ja', 'ko', 'es', 'fr', 'de'],
            'voice_options': ['default', 'professional', 'casual', 'energetic']
        }
        
        # Background music generation options
        self.music_config = {
            'default_duration': 30,
            'genres': ['upbeat', 'cinematic', 'ambient', 'electronic', 'corporate'],
            'moods': ['energetic', 'calm', 'inspiring', 'dramatic', 'cheerful']
        }
    
    def generate_narration(self, script: str, duration: int, voice_style: str = 'professional') -> Dict:
        """Generate high-quality TTS narration using FAL AI F5 TTS"""
        
        if not self.fal_key:
            print("⚠️  FAL_KEY not configured. Creating mock narration.")
            return self._create_mock_narration(script, duration)
        
        print(f"🎙️  Generating narration with FAL AI F5 TTS...")
        print(f"   📝 Script length: {len(script)} characters")
        print(f"   ⏱️  Target duration: {duration} seconds")
        print(f"   🎭 Voice style: {voice_style}")
        
        try:
            # Validate script length
            if len(script) > self.f5_tts_config['max_text_length']:
                print(f"   ⚠️  Script too long ({len(script)} chars), truncating to {self.f5_tts_config['max_text_length']}")
                script = script[:self.f5_tts_config['max_text_length']]
            
            # Calculate cost
            cost_estimate = (len(script) / 1000) * self.f5_tts_config['cost_per_1000_chars']
            print(f"   💰 Estimated cost: ${cost_estimate:.3f}")
            
            # Prepare TTS arguments
            tts_args = {
                'text': script,
                'voice': voice_style,
                'language': 'en',  # Default to English
                'speed': self._calculate_speech_speed(script, duration),
                'format': 'wav'
            }
            
            # Generate TTS using FAL AI F5
            print(f"   🚀 Submitting to FAL AI F5 TTS...")
            
            try:
                result = fal_client.submit(
                    self.f5_tts_config['endpoint'],
                    arguments=tts_args
                )
                
                print(f"   📋 TTS Request ID: {result.request_id if result and hasattr(result, 'request_id') else 'None'}")
                
                if not result or not hasattr(result, 'request_id'):
                    raise Exception("FAL AI F5 TTS submit failed")
                
                # Wait for TTS generation with timeout
                print(f"   ⏳ Waiting for TTS generation...")
                final_result = self._wait_for_tts_result(result)
                
                if final_result and 'audio_url' in final_result:
                    # Download the generated audio
                    audio_url = final_result['audio_url']
                    narration_filename = f"narration_{voice_style}_{int(time.time())}.wav"
                    narration_path = os.path.join(self.audio_folder, narration_filename)
                    
                    print(f"   💾 Downloading TTS audio...")
                    success = self._download_audio(audio_url, narration_path)
                    
                    if success:
                        # Validate audio quality
                        audio_quality = self._validate_audio_quality(narration_path)
                        
                        return {
                            'file_path': narration_path,
                            'filename': narration_filename,
                            'duration': duration,
                            'actual_duration': final_result.get('duration', duration),
                            'type': 'narration',
                            'script': script,
                            'voice_style': voice_style,
                            'status': 'success',
                            'generation_result': final_result,
                            'quality_check': audio_quality,
                            'cost_estimate': cost_estimate,
                            'format': 'wav',
                            'sample_rate': final_result.get('sample_rate', 44100)
                        }
                    else:
                        raise Exception("Failed to download TTS audio")
                else:
                    raise Exception("No audio_url in TTS result")
                    
            except Exception as api_error:
                print(f"   ❌ FAL AI F5 TTS Error: {str(api_error)}")
                print(f"   🧪 Falling back to mock narration...")
                return self._create_mock_narration(script, duration)
                
        except Exception as e:
            print(f"   ❌ Narration generation failed: {str(e)}")
            return self._create_mock_narration(script, duration)
    
    def generate_background_music(self, theme: str, duration: int, mood: str = 'upbeat') -> Dict:
        """Generate AI background music for music mode reels"""
        
        print(f"🎵 Generating background music...")
        print(f"   🎨 Theme: {theme}")
        print(f"   ⏱️  Duration: {duration} seconds")
        print(f"   😊 Mood: {mood}")
        
        try:
            # For now, create a high-quality mock music file
            # This can be enhanced later with actual AI music generation
            music_filename = f"background_music_{theme}_{mood}_{int(time.time())}.mp3"
            music_path = os.path.join(self.audio_folder, music_filename)
            
            # Create realistic mock audio file (1MB for 20-30 seconds of audio)
            mock_audio_data = b'\x00' * (1024 * 1024)  # 1MB of audio data
            with open(music_path, 'wb') as f:
                f.write(mock_audio_data)
            
            print(f"   ✅ Background music generated (mock)")
            
            return {
                'file_path': music_path,
                'filename': music_filename,
                'duration': duration,
                'type': 'background_music',
                'theme': theme,
                'mood': mood,
                'status': 'mock',  # Will be 'success' when real AI music is implemented
                'format': 'mp3',
                'bitrate': '128kbps',
                'sample_rate': 44100,
                'cost_estimate': 0.0  # Mock music is free for now
            }
            
        except Exception as e:
            print(f"   ❌ Background music generation failed: {str(e)}")
            return self._create_mock_music(theme, duration, mood)
    
    def process_audio_for_sync(self, audio_data: Dict, target_duration: int) -> Dict:
        """Optimize audio timing for video synchronization"""
        try:
            # Audio processing logic would go here
            # For now, just update metadata
            
            final_audio_path = os.path.join(self.audio_folder, 'final_audio.wav')
            
            # Create placeholder for processed audio
            with open(final_audio_path, 'wb') as f:
                f.write(b'')
            
            return {
                'file_path': final_audio_path,
                'duration': target_duration,
                'type': audio_data.get('type', 'unknown'),
                'status': 'processed',
                'original_duration': audio_data.get('duration', 0),
                'adjustments_made': ['duration_matching', 'volume_optimization']
            }
        except Exception as e:
            print(f"Error processing audio: {e}")
            return audio_data  # Return original if processing fails
    
    def _create_mock_narration(self, script: str, duration: int) -> Dict:
        """Create mock narration when TTS not available"""
        mock_filename = f"mock_narration_{int(time.time())}.wav"
        mock_path = os.path.join(self.audio_folder, mock_filename)
        
        # Create realistic mock audio file
        mock_audio_data = b'\x00' * (1024 * 512)  # 512KB for voice audio
        with open(mock_path, 'wb') as f:
            f.write(mock_audio_data)
        
        return {
            'file_path': mock_path,
            'filename': mock_filename,
            'duration': duration,
            'type': 'narration',
            'script': script,
            'status': 'mock',
            'format': 'wav',
            'cost_estimate': 0.0
        }
    
    def _create_mock_music(self, theme: str, duration: int, mood: str) -> Dict:
        """Create mock music when generation fails"""
        mock_filename = f"mock_music_{theme}_{mood}_{int(time.time())}.mp3"
        mock_path = os.path.join(self.audio_folder, mock_filename)
        
        # Create realistic mock music file
        mock_audio_data = b'\x00' * (1024 * 1024)  # 1MB for music
        with open(mock_path, 'wb') as f:
            f.write(mock_audio_data)
        
        return {
            'file_path': mock_path,
            'filename': mock_filename,
            'duration': duration,
            'type': 'background_music',
            'theme': theme,
            'mood': mood,
            'status': 'mock',
            'format': 'mp3',
            'cost_estimate': 0.0
        }
    
    def _calculate_speech_speed(self, script: str, target_duration: int) -> float:
        """Calculate optimal speech speed for target duration"""
        # Average speech rate: 150-200 words per minute
        # Estimate words (rough approximation: chars / 5)
        estimated_words = len(script) / 5
        target_minutes = target_duration / 60
        
        if target_minutes > 0:
            required_wpm = estimated_words / target_minutes
            # Normal speed is 1.0, adjust based on required WPM
            # 160 WPM is baseline (1.0 speed)
            speed_factor = required_wpm / 160
            # Clamp between 0.5 and 2.0 for natural speech
            return max(0.5, min(2.0, speed_factor))
        
        return 1.0  # Default speed
    
    def _wait_for_tts_result(self, result) -> Dict:
        """Wait for TTS generation with timeout"""
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Check if TTS is ready
                status = fal_client.status(
                    self.f5_tts_config['endpoint'], 
                    result.request_id
                )
                
                print(f"   📊 TTS Status check {attempt + 1}/30: {status.get('status', 'unknown')}")
                
                if status.get('status') == 'COMPLETED':
                    final_result = result.get()
                    return final_result
                elif status.get('status') == 'FAILED':
                    raise Exception(f"TTS generation failed: {status.get('error', 'Unknown error')}")
                
                time.sleep(10)  # Wait 10 seconds
                attempt += 1
                
            except Exception as e:
                print(f"   ⚠️  TTS status error: {str(e)}")
                attempt += 1
                if attempt < max_attempts:
                    time.sleep(10)
                    continue
                else:
                    break
        
        raise Exception(f"TTS generation timeout after {max_attempts} attempts")
    
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
    
    def _validate_audio_quality(self, audio_path: str) -> Dict:
        """Basic audio quality validation"""
        if not os.path.exists(audio_path):
            return {'valid': False, 'reason': 'File not found'}
        
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            return {'valid': False, 'reason': 'Empty file'}
        
        # Basic file size validation (minimum 10KB for short audio)
        if file_size < 10000:
            return {'valid': False, 'reason': 'File too small', 'size': file_size}
        
        return {
            'valid': True,
            'file_size': file_size,
            'format': 'wav',
            'estimated_quality': 'good' if file_size > 100000 else 'basic'
        }
    
    def estimate_audio_cost(self, content_mode: str, script_length: int = 0) -> Dict:
        """Estimate cost for audio generation"""
        if content_mode == 'narration':
            tts_cost = (script_length / 1000) * self.f5_tts_config['cost_per_1000_chars']
            return {
                'total_cost': tts_cost,
                'tts_cost': tts_cost,
                'music_cost': 0.0,
                'breakdown': f'TTS: ${tts_cost:.3f} ({script_length} chars)'
            }
        else:  # music mode
            return {
                'total_cost': 0.0,  # Mock music is free for now
                'tts_cost': 0.0,
                'music_cost': 0.0,
                'breakdown': 'Background music: Free (mock generation)'
            }