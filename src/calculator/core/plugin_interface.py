import os
import sys
import importlib
import importlib.util
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from pathlib import Path

from calculator.core.repl import Command


class Plugin(ABC):
    """Abstract base class for all calculator plugins."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return the plugin version."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return the plugin description."""
        pass
    
    @abstractmethod
    def get_commands(self) -> List[Command]:
        """Return list of commands provided by this plugin."""
        pass
    
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        return True
    
    def cleanup(self) -> bool:
        """Clean up plugin resources. Return True if successful."""
        return True


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugin_dirs = plugin_dirs or []
        self.loaded_plugins: Dict[str, Plugin] = {}
        self.plugin_commands: Dict[str, Command] = {}
        self.plugin_info: Dict[str, Dict[str, Any]] = {}
        
        # Add default plugin directory
        default_plugin_dir = Path(__file__).parent.parent / "plugins"
        self.plugin_dirs.append(str(default_plugin_dir))
    
    def discover_plugins(self) -> List[str]:
        """Discover all available plugins in plugin directories."""
        discovered_plugins = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                # Check for Python files (excluding __init__.py)
                if item.endswith('.py') and item != '__init__.py':
                    plugin_name = item[:-3]  # Remove .py extension
                    discovered_plugins.append((plugin_name, item_path))
                
                # Check for plugin packages (directories with __init__.py)
                elif os.path.isdir(item_path):
                    init_file = os.path.join(item_path, '__init__.py')
                    if os.path.exists(init_file):
                        discovered_plugins.append((item, item_path))
        
        return discovered_plugins
    
    def load_plugin(self, plugin_name: str, plugin_path: str) -> bool:
        """Load a single plugin."""
        try:
            # Load the module
            if os.path.isfile(plugin_path):
                # Single file plugin
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not load spec for {plugin_name}")
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Package plugin
                sys.path.insert(0, os.path.dirname(plugin_path))
                try:
                    module = importlib.import_module(plugin_name)
                finally:
                    sys.path.pop(0)
            
            # Find plugin class
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                raise ImportError(f"No Plugin class found in {plugin_name}")
            
            # Instantiate and initialize plugin
            plugin_instance = plugin_class()
            if not plugin_instance.initialize():
                raise RuntimeError(f"Failed to initialize plugin {plugin_name}")
            
            # Store plugin info
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_info[plugin_name] = {
                'name': plugin_instance.get_name(),
                'version': plugin_instance.get_version(),
                'description': plugin_instance.get_description(),
                'path': plugin_path
            }
            
            # Register plugin commands
            commands = plugin_instance.get_commands()
            for command in commands:
                command_name = command.get_name()
                self.plugin_commands[command_name] = command
            
            print(f"Loaded plugin: {plugin_instance.get_name()} v{plugin_instance.get_version()}")
            return True
            
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def _find_plugin_class(self, module) -> Optional[Type[Plugin]]:
        """Find the Plugin class in a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Plugin) and 
                attr is not Plugin):
                return attr
        return None
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        results = {}
        discovered_plugins = self.discover_plugins()
        
        for plugin_name, plugin_path in discovered_plugins:
            results[plugin_name] = self.load_plugin(plugin_name, plugin_path)
        
        return results
    
    def get_plugin_commands(self) -> Dict[str, Command]:
        """Get all commands from loaded plugins."""
        return self.plugin_commands.copy()
    
    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all loaded plugins."""
        return self.plugin_info.copy()
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.loaded_plugins:
            return False
        
        try:
            plugin = self.loaded_plugins[plugin_name]
            plugin.cleanup()
            
            # Remove plugin commands
            commands = plugin.get_commands()
            for command in commands:
                command_name = command.get_name()
                if command_name in self.plugin_commands:
                    del self.plugin_commands[command_name]
            
            # Remove plugin
            del self.loaded_plugins[plugin_name]
            del self.plugin_info[plugin_name]
            
            return True
        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False


class MenuCommand(Command):
    """Command to display available plugins and commands."""
    
    def __init__(self, plugin_manager: PluginManager, command_registry):
        self.plugin_manager = plugin_manager
        self.command_registry = command_registry
    
    def execute(self, args: List[str]) -> str:
        """Display menu of available plugins and commands."""
        output = ["=" * 60]
        output.append("CALCULATOR MENU")
        output.append("=" * 60)
        
        # Core commands
        output.append("\n📋 CORE COMMANDS:")
        core_commands = ["add", "subtract", "multiply", "divide", "help", "history", "exit", "quit"]
        for cmd_name in core_commands:
            if cmd_name in self.command_registry.commands:
                cmd = self.command_registry.commands[cmd_name]
                output.append(f"  • {cmd.get_help()}")
        
        # Plugin information
        plugin_info = self.plugin_manager.get_plugin_info()
        if plugin_info:
            output.append(f"\n🔌 LOADED PLUGINS ({len(plugin_info)}):")
            for plugin_name, info in plugin_info.items():
                output.append(f"  📦 {info['name']} v{info['version']}")
                output.append(f"     {info['description']}")
                
                # Show plugin commands
                plugin_commands = []
                for cmd_name, cmd in self.plugin_manager.get_plugin_commands().items():
                    plugin_commands.append(f"     • {cmd.get_help()}")
                
                if plugin_commands:
                    output.extend(plugin_commands)
                output.append("")
        else:
            output.append("\n🔌 PLUGINS: No plugins loaded")
        
        output.append("=" * 60)
        output.append("Type 'help <command>' for detailed help on any command")
        
        return "\n".join(output)
    
    def get_help(self) -> str:
        return "menu - Display all available commands and plugins"
    
    def get_name(self) -> str:
        return "menu"