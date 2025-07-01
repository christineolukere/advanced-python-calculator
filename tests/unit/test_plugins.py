import pytest
import tempfile
import os
from pathlib import Path

from calculator.core.plugin_interface import Plugin, PluginManager
from calculator.plugins.statistics_plugin import StatisticsPlugin, MeanCommand
from calculator.plugins.scientific_plugin import ScientificPlugin, SqrtCommand


class TestStatisticsPlugin:
    """Test statistics plugin functionality."""
    
    def test_plugin_info(self):
        """Test plugin information."""
        plugin = StatisticsPlugin()
        assert plugin.get_name() == "Statistics Plugin"
        assert plugin.get_version() == "1.0.0"
        assert "statistical" in plugin.get_description().lower()
    
    def test_mean_command(self):
        """Test mean calculation."""
        cmd = MeanCommand()
        result = cmd.execute(["1", "2", "3", "4", "5"])
        assert result == 3.0
    
    def test_mean_single_value(self):
        """Test mean with single value."""
        cmd = MeanCommand()
        result = cmd.execute(["42"])
        assert result == 42.0
    
    def test_mean_invalid_input(self):
        """Test mean with invalid input."""
        cmd = MeanCommand()
        with pytest.raises(ValueError, match="Invalid number format"):
            cmd.execute(["abc", "123"])


class TestScientificPlugin:
    """Test scientific plugin functionality."""
    
    def test_plugin_info(self):
        """Test plugin information."""
        plugin = ScientificPlugin()
        assert plugin.get_name() == "Scientific Plugin"
        assert plugin.get_version() == "1.0.0"
        assert "scientific" in plugin.get_description().lower()
    
    def test_sqrt_command(self):
        """Test square root calculation."""
        cmd = SqrtCommand()
        result = cmd.execute(["16"])
        assert result == 4.0
    
    def test_sqrt_negative(self):
        """Test square root of negative number."""
        cmd = SqrtCommand()
        with pytest.raises(ValueError, match="Math error"):
            cmd.execute(["-1"])


class TestPluginManager:
    """Test plugin manager functionality."""
    
    def test_plugin_discovery(self):
        """Test plugin discovery."""
        # Create temporary plugin directory
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_file = Path(temp_dir) / "test_plugin.py"
            plugin_file.write_text("""
from calculator.core.plugin_interface import Plugin
from calculator.core.repl import Command

class TestCommand(Command):
    def execute(self, args):
        return "test"
    def get_help(self):
        return "test command"
    def get_name(self):
        return "test"

class TestPlugin(Plugin):
    def get_name(self):
        return "Test Plugin"
    def get_version(self):
        return "1.0.0"
    def get_description(self):
        return "Test plugin"
    def get_commands(self):
        return [TestCommand()]
""")
            
            manager = PluginManager([temp_dir])
            discovered = manager.discover_plugins()
            
            # Should find our test plugin
            plugin_names = [name for name, path in discovered]
            assert "test_plugin" in plugin_names
    
    def test_load_builtin_plugins(self):
        """Test loading built-in plugins."""
        manager = PluginManager()
        results = manager.load_all_plugins()
        
        # Should have some plugins loaded
        assert len(results) >= 2  # At least statistics and scientific
        
        # Check plugin commands are available
        commands = manager.get_plugin_commands()
        assert "mean" in commands
        assert "sqrt" in commands