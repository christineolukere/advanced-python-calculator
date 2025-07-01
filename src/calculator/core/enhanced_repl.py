from calculator.core.repl import REPLEngine, CommandRegistry
from calculator.core.plugin_interface import PluginManager, MenuCommand


class EnhancedCommandRegistry(CommandRegistry):
    """Enhanced command registry with plugin support."""
    
    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()
        self._setup_plugin_commands()
    
    def _setup_plugin_commands(self):
        """Set up plugin system and load plugins."""
        # Load all plugins
        load_results = self.plugin_manager.load_all_plugins()
        
        # Register plugin commands
        plugin_commands = self.plugin_manager.get_plugin_commands()
        for command_name, command in plugin_commands.items():
            self.commands[command_name] = command
        
        # Add menu command
        menu_cmd = MenuCommand(self.plugin_manager, self)
        self.register_command(menu_cmd)
        
        # Print plugin loading results
        successful_plugins = sum(1 for success in load_results.values() if success)
        total_plugins = len(load_results)
        if total_plugins > 0:
            print(f"Plugin system initialized: {successful_plugins}/{total_plugins} plugins loaded")


class EnhancedREPLEngine(REPLEngine):
    """Enhanced REPL engine with plugin support."""
    
    def __init__(self):
        super().__init__()
        self.command_registry = EnhancedCommandRegistry()
