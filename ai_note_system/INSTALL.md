# AI Note System (Pansophy) Installation Guide

This guide provides instructions for installing and setting up the AI Note System (Pansophy) using either the installation script or Docker.

## System Requirements

- Python 3.8 or higher
- Sufficient disk space for dependencies and data (at least 2GB recommended)
- Internet connection for downloading dependencies

## Installation Methods

Choose one of the following installation methods based on your preferences and environment:

### Method 1: Using the Installation Script

The installation script provides a flexible way to install the AI Note System with options to customize the installation process.

#### Basic Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-note-system.git
   cd ai-note-system
   ```

2. Run the installation script:
   ```
   python install.py
   ```

   This will:
   - Check if your Python version is compatible
   - Install all required dependencies
   - Set up the database
   - Create a default configuration file

3. Edit the configuration file:
   ```
   # Open the configuration file in your preferred editor
   # On Windows:
   notepad config\config.yaml
   
   # On macOS/Linux:
   nano config/config.yaml
   ```

4. Set your API keys and other settings in the configuration file.

#### Advanced Installation Options

The installation script provides several options for customizing the installation:

- Check dependencies without installing:
  ```
  python install.py --check
  ```

- Install specific dependency categories:
  ```
  python install.py --categories core llm pdf
  ```

  Available categories:
  - `core`: Essential dependencies
  - `llm`: Language model dependencies
  - `pdf`: PDF processing dependencies
  - `ocr`: OCR dependencies
  - `speech`: Speech recognition dependencies
  - `youtube`: YouTube processing dependencies
  - `visualization`: Visualization dependencies
  - `data`: Data processing dependencies
  - `embeddings`: Embedding model dependencies
  - `web`: Web interface dependencies
  - `export`: Export format dependencies
  - `notion`: Notion integration dependencies
  - `google`: Google API dependencies
  - `testing`: Testing dependencies

- Install all dependencies, even if already installed:
  ```
  python install.py --all
  ```

- Skip database setup:
  ```
  python install.py --no-db
  ```

- Skip configuration setup:
  ```
  python install.py --no-config
  ```

### Method 2: Using Docker

Docker provides a containerized installation that handles all dependencies automatically.

#### Prerequisites

- Docker installed on your system
- Basic knowledge of Docker commands

#### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-note-system.git
   cd ai-note-system
   ```

2. Build the Docker image:
   ```
   docker build -t pansophy .
   ```

3. Create directories for data and configuration:
   ```
   mkdir -p ~/pansophy/data ~/pansophy/config
   ```

4. Create a configuration file:
   ```
   # Copy the default configuration file
   cp config/config.yaml ~/pansophy/config/
   
   # Edit the configuration file
   nano ~/pansophy/config/config.yaml
   ```

5. Run the container:
   ```
   docker run -it --name pansophy-app \
     -v ~/pansophy/data:/app/data \
     -v ~/pansophy/config:/app/config \
     -p 8000:8000 \
     pansophy
   ```

#### Using the Docker Container

- Run a specific command:
  ```
  docker run -it --rm \
    -v ~/pansophy/data:/app/data \
    -v ~/pansophy/config:/app/config \
    pansophy python main.py process --input "Your text here" --type text
  ```

- Start an existing container:
  ```
  docker start -i pansophy-app
  ```

- Stop the container:
  ```
  docker stop pansophy-app
  ```

## Environment-Specific Configuration

The AI Note System supports different environments (development, testing, production) with appropriate defaults for each. You can specify the environment using the `PANSOPHY_ENV` environment variable:

```
# On Windows:
set PANSOPHY_ENV=development
python main.py

# On macOS/Linux:
export PANSOPHY_ENV=development
python main.py

# With Docker:
docker run -it --rm -e PANSOPHY_ENV=development pansophy
```

## Troubleshooting

### Missing Dependencies

If you encounter errors related to missing dependencies, you can install them manually:

```
pip install package-name
```

Or use the installation script to install specific categories:

```
python install.py --categories category-name
```

### Configuration Issues

If you encounter configuration-related errors:

1. Check that your API keys are correctly set in the configuration file.
2. Ensure the configuration file is in the correct location.
3. Verify that the database path is correct.

### Docker Issues

If you encounter Docker-related issues:

1. Ensure Docker is running on your system.
2. Check that the volumes are correctly mounted.
3. Verify that the configuration file exists in the mounted volume.

## Getting Help

If you need further assistance, please:

1. Check the documentation in the `docs` directory.
2. Look for similar issues in the issue tracker.
3. Create a new issue if your problem is not already addressed.

## Next Steps

After installation, you can:

1. Run the test script to verify the installation:
   ```
   python test_system.py
   ```

2. Process your first note:
   ```
   python main.py process --input "Your text here" --type text
   ```

3. Explore the various commands available in the README.md file.