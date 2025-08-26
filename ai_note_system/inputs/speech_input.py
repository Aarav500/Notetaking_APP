"""
Speech input module for AI Note System.
Handles conversion of speech to text using various engines.
"""

import os
import logging
import tempfile
import time
from typing import Dict, Any, Optional, Tuple, BinaryIO
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.speech_input")

# Import text_input for processing transcribed text
from . import text_input

def transcribe_audio(
    audio_path: str,
    engine: str = "whisper",
    save_raw: bool = True,
    raw_dir: Optional[str] = None,
    language: Optional[str] = None,
    model_size: str = "base"
) -> Dict[str, Any]:
    """
    Transcribe audio to text.
    
    Args:
        audio_path (str): Path to the audio file
        engine (str): Engine to use for transcription ('whisper' or 'speechrecognition')
        save_raw (bool): Whether to save the transcribed text to disk
        raw_dir (str, optional): Directory to save raw text. If None, uses default.
        language (str, optional): Language code for transcription. If None, auto-detect.
        model_size (str): Model size for Whisper ('tiny', 'base', 'small', 'medium', 'large')
        
    Returns:
        Dict[str, Any]: Dictionary containing transcribed text information
    """
    logger.info(f"Transcribing audio: {audio_path}")
    
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return {"error": f"Audio file not found: {audio_path}"}
    
    # Transcribe audio based on the specified engine
    if engine.lower() == "whisper":
        text, duration = transcribe_with_whisper(audio_path, language, model_size)
    elif engine.lower() == "speechrecognition":
        text, duration = transcribe_with_speechrecognition(audio_path, language)
    else:
        logger.error(f"Unsupported transcription engine: {engine}")
        return {"error": f"Unsupported transcription engine: {engine}"}
    
    if not text:
        logger.error(f"Failed to transcribe audio: {audio_path}")
        return {"error": f"Failed to transcribe audio: {audio_path}"}
    
    # Generate title from filename
    filename = os.path.basename(audio_path)
    title = os.path.splitext(filename)[0].replace('_', ' ')
    
    # Process the transcribed text
    result = text_input.process_text(
        text=text,
        title=title,
        tags=["audio", "transcription"],
        save_raw=save_raw,
        raw_dir=raw_dir
    )
    
    # Add audio-specific metadata
    result["source_type"] = "audio"
    result["source_path"] = audio_path
    result["duration"] = duration
    
    logger.debug(f"Audio transcribed: {title} ({result['word_count']} words, {duration:.2f} seconds)")
    return result

def transcribe_with_whisper(
    audio_path: str,
    language: Optional[str] = None,
    model_size: str = "base"
) -> Tuple[str, float]:
    """
    Transcribe audio using OpenAI's Whisper.
    
    Args:
        audio_path (str): Path to the audio file
        language (str, optional): Language code for transcription. If None, auto-detect.
        model_size (str): Model size ('tiny', 'base', 'small', 'medium', 'large')
        
    Returns:
        Tuple[str, float]: Transcribed text and audio duration in seconds
    """
    try:
        import whisper
        import torch
        
        logger.debug(f"Loading Whisper model: {model_size}")
        
        # Load model
        model = whisper.load_model(model_size)
        
        # Transcribe audio
        logger.debug(f"Transcribing audio with Whisper: {audio_path}")
        
        # Set transcription options
        options = {}
        if language:
            options["language"] = language
        
        # Perform transcription
        result = model.transcribe(audio_path, **options)
        
        text = result["text"]
        duration = result.get("duration", 0.0)
        
        logger.debug(f"Transcribed {len(text)} characters from audio")
        return text, duration
        
    except ImportError:
        logger.error("Whisper not installed. Install with: pip install openai-whisper")
        return "", 0.0
        
    except Exception as e:
        logger.error(f"Error transcribing with Whisper: {e}")
        return "", 0.0

def transcribe_with_speechrecognition(
    audio_path: str,
    language: Optional[str] = None
) -> Tuple[str, float]:
    """
    Transcribe audio using SpeechRecognition library.
    
    Args:
        audio_path (str): Path to the audio file
        language (str, optional): Language code for transcription. If None, uses 'en-US'.
        
    Returns:
        Tuple[str, float]: Transcribed text and audio duration in seconds
    """
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        
        logger.debug(f"Opening audio with SpeechRecognition: {audio_path}")
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Set language
        if not language:
            language = "en-US"
        
        # Get audio duration
        audio = AudioSegment.from_file(audio_path)
        duration = len(audio) / 1000.0  # Convert milliseconds to seconds
        
        # Load audio file
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio_data, language=language)
        
        logger.debug(f"Transcribed {len(text)} characters from audio")
        return text, duration
        
    except ImportError:
        logger.error("SpeechRecognition not installed. Install with: pip install SpeechRecognition pydub")
        return "", 0.0
        
    except Exception as e:
        logger.error(f"Error transcribing with SpeechRecognition: {e}")
        return "", 0.0

def record_audio(
    output_path: Optional[str] = None,
    duration: int = 10,
    sample_rate: int = 16000
) -> str:
    """
    Record audio from microphone.
    
    Args:
        output_path (str, optional): Path to save the recorded audio. If None, uses a temp file.
        duration (int): Duration to record in seconds
        sample_rate (int): Sample rate for recording
        
    Returns:
        str: Path to the recorded audio file
    """
    try:
        import pyaudio
        import wave
        
        logger.info(f"Recording audio for {duration} seconds")
        
        # Create output path if not specified
        if not output_path:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"recording_{int(time.time())}.wav")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open stream
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        logger.debug("Recording started")
        
        # Record audio
        frames = []
        for _ in range(0, int(sample_rate / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)
        
        logger.debug("Recording finished")
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save to WAV file
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        
        logger.info(f"Audio saved to {output_path}")
        return output_path
        
    except ImportError:
        logger.error("PyAudio not installed. Install with: pip install pyaudio")
        return ""
        
    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        return ""