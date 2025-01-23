import whisper
import ffmpeg
import openai
import os
import subprocess
from django.conf import settings
import torch
import shutil
import librosa
import numpy as np

def get_ffmpeg_path():
    """Get the path to ffmpeg executable"""
    # First try the settings
    if hasattr(settings, 'FFMPEG_BIN'):
        return settings.FFMPEG_BIN
    
    # Then try to find ffmpeg in PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # Default to common Windows installation path
    default_path = r"C:\ffmpeg\bin\ffmpeg.exe"
    if os.path.exists(default_path):
        return default_path
    
    raise FileNotFoundError("Could not find ffmpeg executable")

def load_audio(file_path, sr=16000):
    """Load audio file using librosa"""
    try:
        # Load audio file
        audio, _ = librosa.load(file_path, sr=sr)
        return audio
    except Exception as e:
        print(f"Error loading audio: {str(e)}")
        raise

def generate_video_summary(video_path):
    """
    Generate a summary of a video by transcribing its audio and using AI to summarize the content.
    
    Args:
        video_path: Path to the video file to be summarized
    Returns:
        str: The generated summary text, or None if an error occurs
    """
    audio_file = None
    try:
        # Debug print - only print what we know exists
        print(f"Video path: {video_path}")
        print(f"Media root: {settings.MEDIA_ROOT}")

        # Get ffmpeg path
        ffmpeg_path = get_ffmpeg_path()
        print(f"Using FFmpeg from: {ffmpeg_path}")

        # Verify video file exists
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Create temp directory
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        print(f"Temp directory: {temp_dir}")
        os.makedirs(temp_dir, exist_ok=True)

        # Set audio file path
        audio_file = os.path.join(temp_dir, "temp_audio.wav")
        
        # Extract audio from MP4 file using ffmpeg
        print("Extracting audio from video file using FFmpeg...")
        try:
            command = [
                ffmpeg_path,
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # Audio codec
                '-ar', '16000',  # Sample rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite output file
                audio_file
            ]
            print(f"Running command: {' '.join(command)}")  # Debug print
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Audio extraction completed successfully")
            
            # Verify audio file was created
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file was not created: {audio_file}")
            print(f"Audio file size: {os.path.getsize(audio_file)} bytes")
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return None

        # Load the audio file
        print("Loading audio file...")
        audio_data = load_audio(audio_file)
        print(f"Audio data shape: {audio_data.shape}")

        # Load the Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("small")

        # Transcribe the audio
        print("Transcribing audio...")
        result = model.transcribe(audio_data)
        transcription_text = result["text"]
        print("Transcription:", transcription_text)

        # Initialize the Sambanova API client
        print("Initializing Sambanova API client...")
        client = openai.Client(
            api_key="89b0dcfb-f902-4920-8bfd-ec6bd4015960",
            base_url="https://api.sambanova.ai/v1"
        )

        # Create a prompt to summarize the transcription
        print("Generating summary using Sambanova API...")
        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text: {transcription_text}"}
            ],
            temperature=0.1,
            top_p=0.1
        )

        # Print the summarized response
        summary = response.choices[0].message.content
        print("Summary:", summary)
        return summary

    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace
        return None

    finally:
        # Clean up temporary audio file
        if audio_file and os.path.exists(audio_file):
            try:
                print("Cleaning up temporary audio file...")
                os.remove(audio_file)
                print("Cleanup completed")
            except Exception as e:
                print(f"Error removing temporary file: {str(e)}") 