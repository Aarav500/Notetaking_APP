"""
Base classes for AI Note System plugins.
Defines the interfaces that plugins must implement.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, Callable, Union

# Setup logging
logger = logging.getLogger("ai_note_system.plugins.plugin_base")

class Plugin(ABC):
    """
    Base class for all plugins.
    All plugins must inherit from this class.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of the plugin.
        
        Returns:
            str: Plugin name
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """
        Get the version of the plugin.
        
        Returns:
            str: Plugin version
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Get the description of the plugin.
        
        Returns:
            str: Plugin description
        """
        pass
    
    @property
    def author(self) -> str:
        """
        Get the author of the plugin.
        
        Returns:
            str: Plugin author
        """
        return "Unknown"
    
    @property
    def dependencies(self) -> List[str]:
        """
        Get the dependencies of the plugin.
        
        Returns:
            List[str]: List of package names required by the plugin
        """
        return []
    
    @property
    def plugin_type(self) -> str:
        """
        Get the type of the plugin.
        
        Returns:
            str: Plugin type
        """
        return "generic"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        return True
    
    def shutdown(self) -> None:
        """
        Perform cleanup when the plugin is being unloaded.
        """
        pass


class VisualizationPlugin(Plugin):
    """
    Base class for visualization plugins.
    Visualization plugins generate visual representations of knowledge.
    """
    
    @property
    def plugin_type(self) -> str:
        """
        Get the type of the plugin.
        
        Returns:
            str: Plugin type
        """
        return "visualization"
    
    @abstractmethod
    def generate_visualization(
        self,
        content: Dict[str, Any],
        output_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a visualization from content.
        
        Args:
            content (Dict[str, Any]): The content to visualize
            output_path (str, optional): Path to save the visualization
            **kwargs: Additional parameters for the visualization
            
        Returns:
            Dict[str, Any]: Result of the visualization generation
        """
        pass


class MLModelPlugin(Plugin):
    """
    Base class for ML model plugins.
    ML model plugins provide custom machine learning models for various tasks.
    """
    
    @property
    def plugin_type(self) -> str:
        """
        Get the type of the plugin.
        
        Returns:
            str: Plugin type
        """
        return "ml_model"
    
    @abstractmethod
    def process(
        self,
        input_data: Any,
        **kwargs
    ) -> Any:
        """
        Process input data using the ML model.
        
        Args:
            input_data (Any): The input data to process
            **kwargs: Additional parameters for processing
            
        Returns:
            Any: The processed output
        """
        pass


class IntegrationPlugin(Plugin):
    """
    Base class for integration plugins.
    Integration plugins connect the system with external tools and services.
    """
    
    @property
    def plugin_type(self) -> str:
        """
        Get the type of the plugin.
        
        Returns:
            str: Plugin type
        """
        return "integration"
    
    @abstractmethod
    def export(
        self,
        content: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Export content to an external tool or service.
        
        Args:
            content (Dict[str, Any]): The content to export
            **kwargs: Additional parameters for the export
            
        Returns:
            Dict[str, Any]: Result of the export operation
        """
        pass
    
    def import_content(
        self,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Import content from an external tool or service.
        
        Args:
            **kwargs: Parameters for the import
            
        Returns:
            Dict[str, Any]: The imported content
        """
        raise NotImplementedError("Import functionality not implemented")


class InputProcessorPlugin(Plugin):
    """
    Base class for input processor plugins.
    Input processor plugins handle processing of specific input types.
    """
    
    @property
    def plugin_type(self) -> str:
        """
        Get the type of the plugin.
        
        Returns:
            str: Plugin type
        """
        return "input_processor"
    
    @abstractmethod
    def process_input(
        self,
        input_data: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process input data.
        
        Args:
            input_data (Any): The input data to process
            **kwargs: Additional parameters for processing
            
        Returns:
            Dict[str, Any]: The processed content
        """
        pass
    
    @property
    @abstractmethod
    def supported_input_types(self) -> List[str]:
        """
        Get the input types supported by this processor.
        
        Returns:
            List[str]: List of supported input types
        """
        pass


class OutputFormatterPlugin(Plugin):
    """
    Base class for output formatter plugins.
    Output formatter plugins handle formatting and exporting content to various formats.
    """
    
    @property
    def plugin_type(self) -> str:
        """
        Get the type of the plugin.
        
        Returns:
            str: Plugin type
        """
        return "output_formatter"
    
    @abstractmethod
    def format_output(
        self,
        content: Dict[str, Any],
        output_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Format content for output.
        
        Args:
            content (Dict[str, Any]): The content to format
            output_path (str, optional): Path to save the formatted output
            **kwargs: Additional parameters for formatting
            
        Returns:
            Dict[str, Any]: Result of the formatting operation
        """
        pass
    
    @property
    @abstractmethod
    def supported_output_formats(self) -> List[str]:
        """
        Get the output formats supported by this formatter.
        
        Returns:
            List[str]: List of supported output formats
        """
        pass