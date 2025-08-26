"""
Speech generator module for AI Note System.
Converts notes to speech for audio reinforcement while commuting or reviewing on the go.
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.speech_generator")

def generate_speech(
    content: Dict[str, Any],
    output_path: Optional[str] = None,
    voice: str = "en-US-Neural2-F",
    rate: float = 1.0,
    format: str = "mp3",
    summarize: bool = True,
    max_duration_minutes: int = 15,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Generate speech from note content.
    
    Args:
        content (Dict[str, Any]): The content to convert to speech
        output_path (str, optional): Path to save the audio file
        voice (str): Voice ID to use for speech
        rate (float): Speech rate (0.5 to 2.0)
        format (str): Audio format (mp3, wav, ogg)
        summarize (bool): Whether to generate speech from summary instead of full text
        max_duration_minutes (int): Maximum duration of the audio in minutes
        include_metadata (bool): Whether to include metadata in the speech
        
    Returns:
        Dict[str, Any]: Result of the speech generation
    """
    logger.info("Generating speech from note content")
    
    # Create output directory if not provided
    if output_path is None:
        # Create a temporary file with the specified format
        temp_file = tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False)
        output_path = temp_file.name
        temp_file.close()
    else:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Prepare text for speech synthesis
    speech_text = prepare_speech_text(content, summarize, include_metadata, max_duration_minutes)
    
    # Generate speech using the appropriate TTS engine
    try:
        # Try to use the specified TTS engine
        result = generate_speech_with_engine(speech_text, output_path, voice, rate, format)
        
        if result["success"]:
            logger.info(f"Speech generated successfully: {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "duration": result.get("duration", 0),
                "format": format,
                "text_length": len(speech_text)
            }
        else:
            logger.error(f"Error generating speech: {result.get('error', 'Unknown error')}")
            return result
            
    except Exception as e:
        error_msg = f"Error generating speech: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def prepare_speech_text(
    content: Dict[str, Any],
    summarize: bool = True,
    include_metadata: bool = True,
    max_duration_minutes: int = 15
) -> str:
    """
    Prepare text for speech synthesis.
    
    Args:
        content (Dict[str, Any]): The content to convert to speech
        summarize (bool): Whether to generate speech from summary instead of full text
        include_metadata (bool): Whether to include metadata in the speech
        max_duration_minutes (int): Maximum duration of the audio in minutes
        
    Returns:
        str: Text prepared for speech synthesis
    """
    # Start with an empty string
    speech_text = ""
    
    # Add title
    title = content.get("title", "Untitled Note")
    speech_text += f"Note: {title}.\n\n"
    
    # Add metadata if requested
    if include_metadata:
        # Add tags if available
        tags = content.get("tags", [])
        if tags:
            speech_text += f"Tags: {', '.join(tags)}.\n\n"
        
        # Add creation date if available
        timestamp = content.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_date = dt.strftime("%B %d, %Y")
                speech_text += f"Created on {formatted_date}.\n\n"
            except (ValueError, TypeError):
                pass
    
    # Add content based on summarize flag
    if summarize:
        # Use summary if available
        summary = content.get("summary")
        if summary:
            speech_text += "Summary:\n\n"
            speech_text += f"{summary}\n\n"
            
            # Add key points if available
            keypoints = content.get("keypoints", [])
            if keypoints:
                speech_text += "Key points:\n\n"
                for i, point in enumerate(keypoints, 1):
                    if isinstance(point, dict) and "text" in point:
                        speech_text += f"{i}. {point['text']}\n"
                    elif isinstance(point, str):
                        speech_text += f"{i}. {point}\n"
                speech_text += "\n"
        else:
            # If no summary, use the full text but truncate it
            text = content.get("text", "")
            # Estimate max characters based on speaking rate (approx. 150 words per minute)
            max_chars = max_duration_minutes * 150 * 5  # 5 chars per word on average
            if len(text) > max_chars:
                speech_text += f"{text[:max_chars]}...\n\n"
                speech_text += "Note: The content has been truncated due to length.\n\n"
            else:
                speech_text += f"{text}\n\n"
    else:
        # Use the full text but truncate it if needed
        text = content.get("text", "")
        # Estimate max characters based on speaking rate (approx. 150 words per minute)
        max_chars = max_duration_minutes * 150 * 5  # 5 chars per word on average
        if len(text) > max_chars:
            speech_text += f"{text[:max_chars]}...\n\n"
            speech_text += "Note: The content has been truncated due to length.\n\n"
        else:
            speech_text += f"{text}\n\n"
    
    # Add conclusion
    speech_text += "End of note."
    
    return speech_text

def generate_speech_with_engine(
    text: str,
    output_path: str,
    voice: str = "en-US-Neural2-F",
    rate: float = 1.0,
    format: str = "mp3"
) -> Dict[str, Any]:
    """
    Generate speech using the appropriate TTS engine.
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the audio file
        voice (str): Voice ID to use for speech
        rate (float): Speech rate (0.5 to 2.0)
        format (str): Audio format (mp3, wav, ogg)
        
    Returns:
        Dict[str, Any]: Result of the speech generation
    """
    # Try different TTS engines in order of preference
    
    # 1. Try Google Text-to-Speech
    try:
        result = generate_speech_with_gtts(text, output_path, voice, rate, format)
        if result["success"]:
            return result
    except ImportError:
        logger.warning("gTTS package not installed. Trying next TTS engine.")
    except Exception as e:
        logger.warning(f"Error using Google TTS: {str(e)}. Trying next TTS engine.")
    
    # 2. Try pyttsx3 (offline TTS)
    try:
        result = generate_speech_with_pyttsx3(text, output_path, voice, rate, format)
        if result["success"]:
            return result
    except ImportError:
        logger.warning("pyttsx3 package not installed. Trying next TTS engine.")
    except Exception as e:
        logger.warning(f"Error using pyttsx3: {str(e)}. Trying next TTS engine.")
    
    # 3. Try Microsoft Azure TTS
    try:
        result = generate_speech_with_azure(text, output_path, voice, rate, format)
        if result["success"]:
            return result
    except ImportError:
        logger.warning("azure-cognitiveservices-speech package not installed. No more TTS engines to try.")
    except Exception as e:
        logger.warning(f"Error using Azure TTS: {str(e)}. No more TTS engines to try.")
    
    # If all engines fail, return error
    return {"success": False, "error": "All TTS engines failed"}

def generate_speech_with_gtts(
    text: str,
    output_path: str,
    voice: str = "en",
    rate: float = 1.0,
    format: str = "mp3"
) -> Dict[str, Any]:
    """
    Generate speech using Google Text-to-Speech.
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the audio file
        voice (str): Language code (e.g., "en", "fr", "es")
        rate (float): Not used in gTTS
        format (str): Must be "mp3" for gTTS
        
    Returns:
        Dict[str, Any]: Result of the speech generation
    """
    try:
        from gtts import gTTS
        
        # Extract language code from voice parameter
        lang = voice.split("-")[0] if "-" in voice else voice
        
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to file
        tts.save(output_path)
        
        # Estimate duration (rough estimate: 150 words per minute)
        word_count = len(text.split())
        estimated_duration = word_count / 150 * 60  # in seconds
        
        return {
            "success": True,
            "engine": "gtts",
            "output_path": output_path,
            "duration": estimated_duration
        }
        
    except Exception as e:
        return {"success": False, "error": f"Error using Google TTS: {str(e)}"}

def generate_speech_with_pyttsx3(
    text: str,
    output_path: str,
    voice: str = "default",
    rate: float = 1.0,
    format: str = "mp3"
) -> Dict[str, Any]:
    """
    Generate speech using pyttsx3 (offline TTS).
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the audio file
        voice (str): Voice ID or "default"
        rate (float): Speech rate (0.5 to 2.0)
        format (str): Audio format (only "wav" is supported)
        
    Returns:
        Dict[str, Any]: Result of the speech generation
    """
    try:
        import pyttsx3
        
        # Initialize engine
        engine = pyttsx3.init()
        
        # Set properties
        engine.setProperty("rate", int(rate * 200))  # Default rate is 200
        
        # Set voice if not default
        if voice != "default":
            voices = engine.getProperty("voices")
            for v in voices:
                if voice in v.id:
                    engine.setProperty("voice", v.id)
                    break
        
        # Save to file (pyttsx3 only supports WAV)
        temp_wav_path = output_path
        if not output_path.lower().endswith(".wav"):
            temp_wav_path = f"{os.path.splitext(output_path)[0]}.wav"
        
        engine.save_to_file(text, temp_wav_path)
        engine.runAndWait()
        
        # Convert to desired format if not WAV
        if format.lower() != "wav" and not output_path.lower().endswith(".wav"):
            try:
                from pydub import AudioSegment
                
                # Load WAV file
                audio = AudioSegment.from_wav(temp_wav_path)
                
                # Export to desired format
                audio.export(output_path, format=format)
                
                # Remove temporary WAV file
                os.remove(temp_wav_path)
                
            except ImportError:
                logger.warning("pydub package not installed. Keeping WAV format.")
                # Rename the file to the original output path
                os.rename(temp_wav_path, output_path)
        
        # Estimate duration (rough estimate: 150 words per minute)
        word_count = len(text.split())
        estimated_duration = word_count / 150 * 60  # in seconds
        
        return {
            "success": True,
            "engine": "pyttsx3",
            "output_path": output_path,
            "duration": estimated_duration
        }
        
    except Exception as e:
        return {"success": False, "error": f"Error using pyttsx3: {str(e)}"}

def generate_speech_with_azure(
    text: str,
    output_path: str,
    voice: str = "en-US-AriaNeural",
    rate: float = 1.0,
    format: str = "mp3"
) -> Dict[str, Any]:
    """
    Generate speech using Microsoft Azure Cognitive Services.
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the audio file
        voice (str): Voice ID (e.g., "en-US-AriaNeural")
        rate (float): Speech rate (0.5 to 2.0)
        format (str): Audio format (mp3, wav, ogg)
        
    Returns:
        Dict[str, Any]: Result of the speech generation
    """
    try:
        import azure.cognitiveservices.speech as speechsdk
        
        # Get API key and region from environment variables
        speech_key = os.environ.get("AZURE_SPEECH_KEY")
        speech_region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
        
        if not speech_key:
            return {"success": False, "error": "Azure Speech API key not found in environment variables"}
        
        # Configure speech config
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        
        # Set voice
        speech_config.speech_synthesis_voice_name = voice
        
        # Set speech rate
        speech_config.set_speech_synthesis_output_format(getattr(
            speechsdk.SpeechSynthesisOutputFormat,
            format.upper()
        ))
        
        # Create audio config
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        # Create speech synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        # Set speech rate using SSML
        ssml_text = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{voice}">
                <prosody rate="{rate}">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        # Synthesize speech
        result = synthesizer.speak_ssml_async(ssml_text).get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Estimate duration (rough estimate: 150 words per minute)
            word_count = len(text.split())
            estimated_duration = word_count / 150 * 60  # in seconds
            
            return {
                "success": True,
                "engine": "azure",
                "output_path": output_path,
                "duration": estimated_duration
            }
        else:
            error = result.cancellation_details.error_details
            return {"success": False, "error": f"Speech synthesis canceled: {error}"}
        
    except Exception as e:
        return {"success": False, "error": f"Error using Azure TTS: {str(e)}"}

def batch_generate_speech(
    contents: List[Dict[str, Any]],
    output_dir: str,
    voice: str = "en-US-Neural2-F",
    rate: float = 1.0,
    format: str = "mp3",
    summarize: bool = True,
    max_duration_minutes: int = 15,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Generate speech for multiple notes.
    
    Args:
        contents (List[Dict[str, Any]]): List of note contents
        output_dir (str): Directory to save the audio files
        voice (str): Voice ID to use for speech
        rate (float): Speech rate (0.5 to 2.0)
        format (str): Audio format (mp3, wav, ogg)
        summarize (bool): Whether to generate speech from summary instead of full text
        max_duration_minutes (int): Maximum duration of the audio in minutes
        include_metadata (bool): Whether to include metadata in the speech
        
    Returns:
        Dict[str, Any]: Result of the batch speech generation
    """
    logger.info(f"Generating speech for {len(contents)} notes")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate speech for each note
    results = []
    
    for i, content in enumerate(contents):
        # Generate filename from title or index
        title = content.get("title", f"note_{i+1}")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        filename = f"{safe_title}.{format}"
        output_path = os.path.join(output_dir, filename)
        
        # Generate speech
        result = generate_speech(
            content=content,
            output_path=output_path,
            voice=voice,
            rate=rate,
            format=format,
            summarize=summarize,
            max_duration_minutes=max_duration_minutes,
            include_metadata=include_metadata
        )
        
        # Add note info to result
        result["title"] = title
        result["index"] = i + 1
        
        results.append(result)
    
    # Count successes and failures
    successes = sum(1 for r in results if r.get("success", False))
    failures = len(results) - successes
    
    return {
        "success": failures == 0,
        "total": len(results),
        "successes": successes,
        "failures": failures,
        "results": results,
        "output_dir": output_dir
    }

def generate_speech_from_text(
    text: str,
    output_path: str,
    engine: str = "gtts",
    voice: str = "en",
    rate: float = 1.0,
    volume: float = 1.0
) -> str:
    """
    Generate speech from plain text
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        engine: Speech engine to use (gtts, pyttsx3, azure)
        voice: Voice to use
        rate: Speech rate (0.5 to 2.0)
        volume: Volume (0.0 to 1.0)
        
    Returns:
        Path to the generated audio file
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Generate speech using the appropriate TTS engine
    try:
        if engine == "gtts":
            generate_speech_with_gtts(text, output_path, voice, rate)
        elif engine == "pyttsx3":
            generate_speech_with_pyttsx3(text, output_path, voice, rate)
        elif engine == "azure":
            generate_speech_with_azure(text, output_path, voice, rate)
        else:
            # Default to gtts
            generate_speech_with_gtts(text, output_path, voice, rate)
        
        return output_path
    except Exception as e:
        logger.error(f"Error generating speech from text: {str(e)}")
        raise
        
def available_voices() -> Dict[str, List[str]]:
    """
    Get available voices for each speech engine
    
    Returns:
        Dictionary of available voices by engine
    """
    voices = {
        'gtts': ['af', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'en-au', 
                'en-ca', 'en-gb', 'en-gh', 'en-ie', 'en-in', 'en-ng', 'en-nz', 'en-ph', 'en-tz', 
                'en-uk', 'en-us', 'en-za', 'eo', 'es', 'es-es', 'es-us', 'et', 'fi', 'fr', 'fr-ca', 
                'fr-fr', 'gu', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'jw', 'km', 'kn', 
                'ko', 'la', 'lv', 'mk', 'ml', 'mr', 'my', 'ne', 'nl', 'no', 'pl', 'pt', 'pt-br',
                'pt-pt', 'ro', 'ru', 'si', 'sk', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 
                'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw'],
        'pyttsx3': ['default'],
        'azure': ['en-US-AriaNeural', 'en-US-GuyNeural', 'en-US-JennyNeural', 'en-GB-LibbyNeural', 
                 'en-GB-RyanNeural', 'fr-FR-DeniseNeural', 'fr-FR-HenriNeural', 'de-DE-KatjaNeural', 
                 'de-DE-ConradNeural', 'it-IT-ElsaNeural', 'it-IT-DiegoNeural', 'es-ES-ElviraNeural', 
                 'es-ES-AlvaroNeural', 'ja-JP-NanamiNeural', 'ja-JP-KeitaNeural', 'zh-CN-XiaoxiaoNeural', 
                 'zh-CN-YunyangNeural']
    }
    
    # Try to get actual pyttsx3 voices if available
    try:
        import pyttsx3
        engine = pyttsx3.init()
        pyttsx3_voices = engine.getProperty('voices')
        voices['pyttsx3'] = [voice.id for voice in pyttsx3_voices]
        engine.stop()
    except:
        pass
    
    return voices

def main():
    """
    Command-line interface for generating speech from notes.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate speech from notes")
    parser.add_argument("--input", required=True, help="Input note file (JSON) or directory")
    parser.add_argument("--output", help="Output audio file or directory")
    parser.add_argument("--voice", default="en-US-Neural2-F", help="Voice ID")
    parser.add_argument("--rate", type=float, default=1.0, help="Speech rate (0.5 to 2.0)")
    parser.add_argument("--format", default="mp3", choices=["mp3", "wav", "ogg"], help="Audio format")
    parser.add_argument("--summarize", action="store_true", help="Generate speech from summary")
    parser.add_argument("--max-duration", type=int, default=15, help="Maximum duration in minutes")
    parser.add_argument("--include-metadata", action="store_true", help="Include metadata in speech")
    
    args = parser.parse_args()
    
    # Check if input is a file or directory
    input_path = args.input
    
    if os.path.isfile(input_path):
        # Process single file
        try:
            with open(input_path, "r") as f:
                content = json.load(f)
            
            # Generate output path if not provided
            output_path = args.output
            if not output_path:
                output_path = f"{os.path.splitext(input_path)[0]}.{args.format}"
            
            # Generate speech
            result = generate_speech(
                content=content,
                output_path=output_path,
                voice=args.voice,
                rate=args.rate,
                format=args.format,
                summarize=args.summarize,
                max_duration_minutes=args.max_duration,
                include_metadata=args.include_metadata
            )
            
            # Print result
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            
    elif os.path.isdir(input_path):
        # Process directory
        try:
            # Find all JSON files
            json_files = [f for f in os.listdir(input_path) if f.endswith(".json")]
            
            if not json_files:
                print(f"No JSON files found in {input_path}")
                return
            
            # Load contents
            contents = []
            for filename in json_files:
                file_path = os.path.join(input_path, filename)
                try:
                    with open(file_path, "r") as f:
                        content = json.load(f)
                    contents.append(content)
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
            
            # Generate output directory if not provided
            output_dir = args.output
            if not output_dir:
                output_dir = os.path.join(input_path, "audio")
            
            # Generate speech for all notes
            result = batch_generate_speech(
                contents=contents,
                output_dir=output_dir,
                voice=args.voice,
                rate=args.rate,
                format=args.format,
                summarize=args.summarize,
                max_duration_minutes=args.max_duration,
                include_metadata=args.include_metadata
            )
            
            # Print result
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            print(f"Error processing directory: {str(e)}")
            
    else:
        print(f"Input path not found: {input_path}")

if __name__ == "__main__":
    main()