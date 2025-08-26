"""
Word Cloud Visualization Plugin for AI Note System.
Generates a word cloud from text content.
"""

import os
import logging
from typing import Dict, Any, List, Optional

from ai_note_system.plugins.plugin_base import VisualizationPlugin

# Setup logging
logger = logging.getLogger("ai_note_system.plugins.builtin.wordcloud_plugin")

class WordCloudVisualizationPlugin(VisualizationPlugin):
    """
    Plugin for generating word cloud visualizations.
    """
    
    @property
    def name(self) -> str:
        """
        Get the name of the plugin.
        
        Returns:
            str: Plugin name
        """
        return "Word Cloud Visualization"
    
    @property
    def version(self) -> str:
        """
        Get the version of the plugin.
        
        Returns:
            str: Plugin version
        """
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """
        Get the description of the plugin.
        
        Returns:
            str: Plugin description
        """
        return "Generates a word cloud visualization from text content."
    
    @property
    def author(self) -> str:
        """
        Get the author of the plugin.
        
        Returns:
            str: Plugin author
        """
        return "AI Note System Team"
    
    @property
    def dependencies(self) -> List[str]:
        """
        Get the dependencies of the plugin.
        
        Returns:
            List[str]: List of package names required by the plugin
        """
        return ["wordcloud", "matplotlib", "numpy"]
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        logger.info("Initializing Word Cloud Visualization Plugin")
        
        # Check if dependencies are installed
        try:
            import wordcloud
            import matplotlib
            import numpy
            logger.info("All dependencies are installed")
            return True
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return False
    
    def generate_visualization(
        self,
        content: Dict[str, Any],
        output_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a word cloud visualization from content.
        
        Args:
            content (Dict[str, Any]): The content to visualize
            output_path (str, optional): Path to save the visualization
            **kwargs: Additional parameters for the visualization
                - width (int): Width of the word cloud image (default: 800)
                - height (int): Height of the word cloud image (default: 400)
                - background_color (str): Background color (default: "white")
                - max_words (int): Maximum number of words to include (default: 200)
                - colormap (str): Matplotlib colormap name (default: "viridis")
                - contour_width (int): Width of the contour (default: 0)
                - contour_color (str): Color of the contour (default: "steelblue")
            
        Returns:
            Dict[str, Any]: Result of the visualization generation
        """
        logger.info("Generating word cloud visualization")
        
        try:
            # Import required libraries
            import matplotlib.pyplot as plt
            from wordcloud import WordCloud, STOPWORDS
            import numpy as np
            
            # Get text from content
            text = ""
            if "text" in content:
                text = content["text"]
            elif "summary" in content:
                text = content["summary"]
            else:
                logger.error("No text or summary found in content")
                return {"success": False, "error": "No text or summary found in content"}
            
            # Get parameters from kwargs
            width = kwargs.get("width", 800)
            height = kwargs.get("height", 400)
            background_color = kwargs.get("background_color", "white")
            max_words = kwargs.get("max_words", 200)
            colormap = kwargs.get("colormap", "viridis")
            contour_width = kwargs.get("contour_width", 0)
            contour_color = kwargs.get("contour_color", "steelblue")
            
            # Create stopwords set
            stopwords = set(STOPWORDS)
            additional_stopwords = kwargs.get("stopwords", [])
            for word in additional_stopwords:
                stopwords.add(word)
            
            # Create word cloud
            wc = WordCloud(
                width=width,
                height=height,
                background_color=background_color,
                max_words=max_words,
                colormap=colormap,
                stopwords=stopwords,
                contour_width=contour_width,
                contour_color=contour_color
            )
            
            # Generate word cloud
            wc.generate(text)
            
            # Create figure
            plt.figure(figsize=(width/100, height/100), dpi=100)
            plt.imshow(wc, interpolation='bilinear')
            plt.axis("off")
            
            # Save figure if output path is provided
            if output_path:
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # Save figure
                plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
                plt.close()
                
                logger.info(f"Word cloud saved to {output_path}")
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "visualization_type": "word_cloud"
                }
            else:
                # Convert figure to image data
                from io import BytesIO
                import base64
                
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
                plt.close()
                
                # Encode image data as base64
                buf.seek(0)
                img_data = base64.b64encode(buf.read()).decode('utf-8')
                
                return {
                    "success": True,
                    "image_data": img_data,
                    "image_format": "png",
                    "visualization_type": "word_cloud"
                }
                
        except Exception as e:
            logger.error(f"Error generating word cloud: {str(e)}")
            return {"success": False, "error": f"Error generating word cloud: {str(e)}"}
    
    def shutdown(self) -> None:
        """
        Perform cleanup when the plugin is being unloaded.
        """
        logger.info("Shutting down Word Cloud Visualization Plugin")
        # No cleanup needed for this plugin