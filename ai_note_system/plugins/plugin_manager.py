"""
Plugin manager for AI Note System.
Handles plugin discovery, loading, and registration.
"""

import os
import sys
import logging
import importlib
import inspect
import pkgutil
from typing import Dict, Any, List, Optional, Type, Set, Union
from pathlib import Path

from .plugin_base import Plugin

# Setup logging
logger = logging.getLogger("ai_note_system.plugins.plugin_manager")

class PluginManager:
    """
    Manager for discovering, loading, and registering plugins.
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_dirs (List[str], optional): List of directories to search for plugins
        """
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_classes: Dict[str, Type[Plugin]] = {}
        self.plugin_dirs = plugin_dirs or []
        
        # Add default plugin directories
        self._add_default_plugin_dirs()
    
    def _add_default_plugin_dirs(self) -> None:
        """
        Add default plugin directories.
        """
        # Add built-in plugins directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        builtin_plugins_dir = os.path.join(current_dir, "builtin")
        if os.path.exists(builtin_plugins_dir) and builtin_plugins_dir not in self.plugin_dirs:
            self.plugin_dirs.append(builtin_plugins_dir)
        
        # Add user plugins directory
        user_plugins_dir = os.path.expanduser("~/.pansophy/plugins")
        if os.path.exists(user_plugins_dir) and user_plugins_dir not in self.plugin_dirs:
            self.plugin_dirs.append(user_plugins_dir)
    
    def discover_plugins(self) -> Dict[str, Type[Plugin]]:
        """
        Discover available plugins in plugin directories.
        
        Returns:
            Dict[str, Type[Plugin]]: Dictionary of discovered plugin classes
        """
        logger.info("Discovering plugins...")
        
        discovered_plugins: Dict[str, Type[Plugin]] = {}
        
        # Discover plugins in each directory
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
            
            logger.debug(f"Searching for plugins in: {plugin_dir}")
            
            # Add plugin directory to sys.path temporarily
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
                remove_from_path = True
            else:
                remove_from_path = False
            
            try:
                # Walk through the directory and import Python modules
                for _, name, is_pkg in pkgutil.iter_modules([plugin_dir]):
                    if is_pkg:
                        # Skip packages for now
                        continue
                    
                    try:
                        # Import the module
                        module = importlib.import_module(name)
                        
                        # Find plugin classes in the module
                        for item_name, item in inspect.getmembers(module, inspect.isclass):
                            # Check if the class is a Plugin subclass (but not Plugin itself)
                            if (issubclass(item, Plugin) and 
                                item is not Plugin and 
                                not inspect.isabstract(item)):
                                
                                # Create a unique ID for the plugin class
                                plugin_id = f"{name}.{item_name}"
                                
                                # Add to discovered plugins
                                discovered_plugins[plugin_id] = item
                                logger.debug(f"Discovered plugin: {plugin_id}")
                    
                    except (ImportError, AttributeError) as e:
                        logger.warning(f"Error importing module {name}: {e}")
            
            finally:
                # Remove plugin directory from sys.path if it was added
                if remove_from_path:
                    sys.path.remove(plugin_dir)
        
        # Update plugin classes
        self.plugin_classes.update(discovered_plugins)
        
        logger.info(f"Discovered {len(discovered_plugins)} plugins")
        return discovered_plugins
    
    def load_plugin(self, plugin_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Plugin]:
        """
        Load a plugin by ID.
        
        Args:
            plugin_id (str): ID of the plugin to load
            config (Dict[str, Any], optional): Configuration for the plugin
            
        Returns:
            Optional[Plugin]: Loaded plugin instance or None if loading failed
        """
        logger.info(f"Loading plugin: {plugin_id}")
        
        # Check if plugin class is available
        if plugin_id not in self.plugin_classes:
            logger.error(f"Plugin not found: {plugin_id}")
            return None
        
        # Get plugin class
        plugin_class = self.plugin_classes[plugin_id]
        
        try:
            # Create plugin instance
            plugin = plugin_class()
            
            # Initialize plugin
            if config is None:
                config = {}
            
            if not plugin.initialize(config):
                logger.error(f"Failed to initialize plugin: {plugin_id}")
                return None
            
            # Check dependencies
            missing_deps = self._check_dependencies(plugin)
            if missing_deps:
                logger.error(f"Plugin {plugin_id} is missing dependencies: {', '.join(missing_deps)}")
                return None
            
            # Register plugin
            self.plugins[plugin_id] = plugin
            
            logger.info(f"Loaded plugin: {plugin.name} v{plugin.version} ({plugin.plugin_type})")
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}")
            return None
    
    def load_plugins(
        self,
        plugin_ids: Optional[List[str]] = None,
        plugin_types: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Plugin]:
        """
        Load multiple plugins.
        
        Args:
            plugin_ids (List[str], optional): IDs of plugins to load (all if None)
            plugin_types (List[str], optional): Types of plugins to load
            config (Dict[str, Any], optional): Configuration for the plugins
            
        Returns:
            Dict[str, Plugin]: Dictionary of loaded plugin instances
        """
        logger.info("Loading plugins...")
        
        # Discover plugins if not already discovered
        if not self.plugin_classes:
            self.discover_plugins()
        
        # Determine which plugins to load
        if plugin_ids is not None:
            # Load specific plugins by ID
            plugins_to_load = [pid for pid in plugin_ids if pid in self.plugin_classes]
        else:
            # Load all discovered plugins
            plugins_to_load = list(self.plugin_classes.keys())
        
        # Filter by plugin type if specified
        if plugin_types is not None:
            filtered_plugins = []
            for pid in plugins_to_load:
                plugin_class = self.plugin_classes[pid]
                # Create a temporary instance to check the plugin type
                try:
                    temp_plugin = plugin_class()
                    if temp_plugin.plugin_type in plugin_types:
                        filtered_plugins.append(pid)
                except Exception:
                    pass
            plugins_to_load = filtered_plugins
        
        # Load each plugin
        loaded_plugins = {}
        for pid in plugins_to_load:
            plugin = self.load_plugin(pid, config)
            if plugin:
                loaded_plugins[pid] = plugin
        
        logger.info(f"Loaded {len(loaded_plugins)} plugins")
        return loaded_plugins
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin by ID.
        
        Args:
            plugin_id (str): ID of the plugin to unload
            
        Returns:
            bool: True if the plugin was unloaded, False otherwise
        """
        logger.info(f"Unloading plugin: {plugin_id}")
        
        # Check if plugin is loaded
        if plugin_id not in self.plugins:
            logger.warning(f"Plugin not loaded: {plugin_id}")
            return False
        
        # Get plugin instance
        plugin = self.plugins[plugin_id]
        
        try:
            # Call shutdown method
            plugin.shutdown()
            
            # Remove from loaded plugins
            del self.plugins[plugin_id]
            
            logger.info(f"Unloaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    def unload_all_plugins(self) -> None:
        """
        Unload all loaded plugins.
        """
        logger.info("Unloading all plugins...")
        
        # Get a copy of plugin IDs to avoid modifying the dictionary during iteration
        plugin_ids = list(self.plugins.keys())
        
        # Unload each plugin
        for pid in plugin_ids:
            self.unload_plugin(pid)
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Get a loaded plugin by ID.
        
        Args:
            plugin_id (str): ID of the plugin
            
        Returns:
            Optional[Plugin]: Plugin instance or None if not loaded
        """
        return self.plugins.get(plugin_id)
    
    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, Plugin]:
        """
        Get all loaded plugins of a specific type.
        
        Args:
            plugin_type (str): Type of plugins to get
            
        Returns:
            Dict[str, Plugin]: Dictionary of plugin instances
        """
        return {pid: plugin for pid, plugin in self.plugins.items() 
                if plugin.plugin_type == plugin_type}
    
    def _check_dependencies(self, plugin: Plugin) -> List[str]:
        """
        Check if all dependencies of a plugin are installed.
        
        Args:
            plugin (Plugin): Plugin to check dependencies for
            
        Returns:
            List[str]: List of missing dependencies
        """
        missing_deps = []
        
        for dep in plugin.dependencies:
            try:
                importlib.import_module(dep.split('==')[0].strip())
            except ImportError:
                missing_deps.append(dep)
        
        return missing_deps
    
    def add_plugin_dir(self, plugin_dir: str) -> None:
        """
        Add a directory to search for plugins.
        
        Args:
            plugin_dir (str): Directory path
        """
        if os.path.exists(plugin_dir) and plugin_dir not in self.plugin_dirs:
            self.plugin_dirs.append(plugin_dir)
            logger.debug(f"Added plugin directory: {plugin_dir}")
    
    def get_plugin_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all loaded plugins.
        
        Returns:
            List[Dict[str, Any]]: List of plugin information dictionaries
        """
        plugin_info = []
        
        for pid, plugin in self.plugins.items():
            info = {
                "id": pid,
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author,
                "type": plugin.plugin_type,
                "dependencies": plugin.dependencies
            }
            plugin_info.append(info)
        
        return plugin_info


# Create a global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager instance.
    
    Returns:
        PluginManager: Plugin manager instance
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager