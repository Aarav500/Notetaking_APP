# Plugin System for AI Note System

The AI Note System (Pansophy) includes a plugin system that allows you to extend its functionality with custom plugins. This document explains how to use and develop plugins.

## Using Plugins

You can manage plugins using the `plugins` command in the CLI:

```bash
# List all available plugins
python main.py plugins list

# List only visualization plugins
python main.py plugins list --type visualization

# List only loaded plugins
python main.py plugins list --loaded

# Load a plugin
python main.py plugins load plugin_module.PluginClass

# Unload a plugin
python main.py plugins unload plugin_module.PluginClass

# Add a plugin directory
python main.py plugins add-dir /path/to/plugins
```

## Developing Plugins

To create a plugin, you need to create a Python module that defines a class inheriting from one of the plugin base classes.

### Plugin Types

The plugin system supports several types of plugins:

1. **Visualization Plugins**: Generate visual representations of knowledge
2. **ML Model Plugins**: Provide custom machine learning models
3. **Integration Plugins**: Connect with external tools and services
4. **Input Processor Plugins**: Handle processing of specific input types
5. **Output Formatter Plugins**: Handle formatting and exporting content

### Plugin Base Classes

All plugins must inherit from one of the following base classes:

- `Plugin`: Base class for all plugins
- `VisualizationPlugin`: For visualization plugins
- `MLModelPlugin`: For ML model plugins
- `IntegrationPlugin`: For integration plugins
- `InputProcessorPlugin`: For input processor plugins
- `OutputFormatterPlugin`: For output formatter plugins

### Example Plugin

Here's an example of a simple visualization plugin that generates a word cloud:

```python
from ai_note_system.plugins.plugin_base import VisualizationPlugin

class WordCloudVisualizationPlugin(VisualizationPlugin):
    """
    Plugin for generating word cloud visualizations.
    """
    
    @property
    def name(self) -> str:
        return "Word Cloud Visualization"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Generates a word cloud visualization from text content."
    
    @property
    def author(self) -> str:
        return "AI Note System Team"
    
    @property
    def dependencies(self) -> List[str]:
        return ["wordcloud", "matplotlib", "numpy"]
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        # Check if dependencies are installed
        try:
            import wordcloud
            import matplotlib
            import numpy
            return True
        except ImportError as e:
            return False
    
    def generate_visualization(
        self,
        content: Dict[str, Any],
        output_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Implementation of word cloud generation
        # ...
        
    def shutdown(self) -> None:
        # Cleanup when plugin is unloaded
        pass
```

### Plugin Directory Structure

Plugins can be placed in the following directories:

1. Built-in plugins: `ai_note_system/plugins/builtin/`
2. User plugins: `~/.pansophy/plugins/`
3. Custom directories added with `plugins add-dir`

Each plugin should be in a separate Python module (`.py` file) in one of these directories.

### Plugin Lifecycle

1. **Discovery**: The plugin manager discovers available plugins in the plugin directories.
2. **Loading**: When a plugin is loaded, its `initialize` method is called with the configuration.
3. **Usage**: The plugin's functionality is used through its methods.
4. **Unloading**: When a plugin is unloaded, its `shutdown` method is called for cleanup.

### Plugin Dependencies

Plugins can specify their dependencies in the `dependencies` property. These dependencies will be checked when the plugin is loaded, and the plugin will not be loaded if any dependencies are missing.

## Built-in Plugins

The AI Note System comes with several built-in plugins:

1. **Word Cloud Visualization**: Generates word clouds from text content.
2. (More built-in plugins will be added in the future)

## Plugin Configuration

Plugins can be configured through the `initialize` method, which receives a configuration dictionary. The configuration can be provided when loading the plugin:

```python
plugin_manager = get_plugin_manager()
plugin_manager.load_plugin("plugin_module.PluginClass", config={"option": "value"})
```

## Plugin API

For detailed information about the plugin API, see the docstrings in the `plugin_base.py` file.