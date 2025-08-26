# Dependency Management in AI Note System

This document outlines the dependency management strategy for the AI Note System (Pansophy), including how dependencies are categorized, how version compatibility is checked, how fallback mechanisms work, and best practices for adding new dependencies.

## Dependency Categories

Dependencies in the AI Note System are categorized as follows:

### Core Dependencies

These dependencies are required for the basic functionality of the system:

- **pyyaml**: Configuration loading
- **python-dotenv**: Environment variable loading
- **requests**: API requests
- **tqdm**: Progress bars
- **sqlalchemy**: Database management

### Optional Dependencies

These dependencies are only required for specific features:

- **PDF Processing**: PyMuPDF, pdf2image
- **OCR**: pytesseract
- **Speech Recognition**: SpeechRecognition, openai-whisper
- **YouTube Processing**: yt-dlp, youtube-transcript-api, pydub, opencv-python
- **Visualization**: graphviz, mermaid-cli
- **Data Processing**: pandas, numpy
- **Embeddings**: sentence-transformers
- **Web & API**: fastapi, uvicorn
- **Notion Integration**: notion-client
- **Google Integration**: google-api-python-client
- **Notifications**: win10toast (Windows), pync (macOS), notify2 (Linux)
- **Export**: markdown, weasyprint, genanki
- **Testing**: pytest

## Installation

The system provides a simplified installation script (`install.py`) that allows users to install only the dependencies they need:

```bash
# Install all dependencies
python install.py

# Install only core dependencies
python install.py --categories core

# Install core and specific feature dependencies
python install.py --categories core pdf ocr

# Check which dependencies are missing
python install.py --check
```

The system also provides a Docker configuration for containerized installation, which includes all dependencies.

## Version Compatibility Checking

The system includes a version checker utility (`utils/version_checker.py`) that checks if the installed versions of dependencies meet the requirements:

```python
from ai_note_system.utils.version_checker import check_dependencies, log_dependency_check_results

# Check all dependencies
results = check_dependencies()
log_dependency_check_results(results)

# Check specific dependencies
results = check_dependencies({
    "openai": ">=1.0.0",
    "PyMuPDF": ">=1.20.0"
})
```

The version checker:
- Parses version requirements (e.g., ">=1.0.0")
- Compares installed versions with required versions
- Provides detailed error messages for incompatible versions

## Fallback Mechanisms

The system includes an API fallback utility (`utils/api_fallback.py`) that provides fallback mechanisms for API changes in critical dependencies:

```python
from ai_note_system.utils.api_fallback import with_fallback

@with_fallback("openai", "ChatCompletion.create")
def generate_text_with_openai(prompt, model="gpt-3.5-turbo"):
    # Implementation using the OpenAI API
    # If the API changes or fails, the fallback will be used
```

The fallback mechanism:
- Catches exceptions from API calls
- Uses registered fallback functions
- Handles API changes between different versions
- Provides meaningful error messages

### OpenAI API Fallbacks

The system includes fallbacks for the OpenAI API, which has undergone significant changes between versions 0.x and 1.x:

- **ChatCompletion.create**: Handles the change from `openai.ChatCompletion.create()` to `client.chat.completions.create()`
- **Embedding.create**: Handles the change from `openai.Embedding.create()` to `client.embeddings.create()`

## Runtime Dependency Checking

The system checks for optional dependencies at runtime using the dependency checker utility (`utils/dependency_checker.py`):

```python
from ai_note_system.utils.dependency_checker import optional_dependency

@optional_dependency("youtube")
def process_youtube_video(url):
    # Implementation using YouTube dependencies
    # If dependencies are missing, a helpful error message will be displayed
```

The dependency checker:
- Checks if required packages are installed
- Provides helpful error messages with installation instructions
- Allows functions to gracefully handle missing dependencies

## Best Practices for Adding New Dependencies

When adding a new dependency to the AI Note System, follow these best practices:

1. **Categorize the dependency**: Determine if it's a core dependency or an optional dependency for a specific feature.

2. **Add to requirements.txt**: Add the dependency to the appropriate section in `requirements.txt` with a minimum version requirement.

3. **Add to install.py**: Add the dependency to the appropriate category in `DEPENDENCY_CATEGORIES` in `install.py`.

4. **Add version requirement**: Add the dependency to `VERSION_REQUIREMENTS` in `utils/version_checker.py` if it's a critical dependency.

5. **Use optional_dependency decorator**: If the dependency is optional, use the `@optional_dependency` decorator on functions that require it.

6. **Create fallback mechanisms**: If the dependency has a changing API, create fallback functions and register them with the API fallback manager.

7. **Document the dependency**: Update this document with information about the new dependency.

## Handling Breaking Changes

When a dependency undergoes breaking changes:

1. **Update version requirements**: Update the version requirement in `requirements.txt` and `VERSION_REQUIREMENTS`.

2. **Create fallback mechanisms**: Create fallback functions for the new API version.

3. **Update documentation**: Document the breaking change and how it's handled.

4. **Test with both versions**: Ensure the system works with both the old and new versions of the dependency.

## Dependency Verification

The system includes a dependency verification utility that can be used to verify that all required dependencies are installed:

```bash
# Verify all dependencies
python -m ai_note_system.utils.dependency_verification

# Verify specific categories
python -m ai_note_system.utils.dependency_verification --categories core pdf ocr
```

This utility:
- Checks if required dependencies are installed
- Checks if installed versions meet the requirements
- Provides detailed error messages for missing or incompatible dependencies
- Suggests installation commands for missing dependencies