"""This module defines the REPL engine and its commands for the calculator."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import sys


class Command(ABC):
    """Abstract base class for all REPL commands."""

    @abstractmethod
    def execute(self, args: List[str]) -> Any:
        """Execute the command with given arguments."""
        pass

    @abstractmethod
    def get_help(self) -> str:
        """Return help text for this command."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the command name."""
        pass


class ArithmeticCommand(Command):
    """Base class for arithmetic operations."""

    def __init__(self, operation: str, func: Callable[[float, float], float]):
        self.operation = operation
        self.func = func

    def execute(self, args: List[str]) -> float:
        """Execute arithmetic operation."""
        if len(args) != 2:
            raise ValueError(f"{self.operation} requires exactly 2 arguments")

        try:
            num1 = float(args[0])
            num2 = float(args[1])
            return self.func(num1, num2)
        except ValueError as exc:
            raise ValueError(f"Invalid number format: {exc}") from exc
        except ZeroDivisionError as exc:
            raise ValueError("Division by zero is not allowed") from exc

    def get_help(self) -> str:
        return f"{self.get_name()} <number1> <number2> - Perform {self.operation}"

    def get_name(self) -> str:
        return self.operation.lower()


class HelpCommand(Command):
    """Command to display help information."""

    def __init__(self, command_registry):
        self.command_registry = command_registry

    def execute(self, args: List[str]) -> str:
        if args:
            command_name = args[0].lower()
            if command_name in self.command_registry.commands:
                return self.command_registry.commands[command_name].get_help()
            return f"Unknown command: {command_name}"

        help_text = ["Available commands:"]
        for command in self.command_registry.commands.values():
            help_text.append(f"  {command.get_help()}")
        help_text.append("  help [command] - Show help for all commands or specific command")
        help_text.append("  history - Show calculation history")
        help_text.append("  exit/quit - Exit the calculator")
        return "\n".join(help_text)

    def get_help(self) -> str:
        return "help [command] - Show help information"

    def get_name(self) -> str:
        return "help"


class ExitCommand(Command):
    """Command to exit the REPL."""

    def execute(self, args: List[str]) -> str:
        return "EXIT"

    def get_help(self) -> str:
        return "exit/quit - Exit the calculator"

    def get_name(self) -> str:
        return "exit"


class CommandRegistry:
    """Registry for managing all available commands."""

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self._setup_basic_commands()

    def _setup_basic_commands(self):
        self.register_command(ArithmeticCommand("add", lambda x, y: x + y))
        self.register_command(ArithmeticCommand("subtract", lambda x, y: x - y))
        self.register_command(ArithmeticCommand("multiply", lambda x, y: x * y))
        self.register_command(ArithmeticCommand("divide", lambda x, y: x / y))
        self.register_command(HelpCommand(self))
        exit_cmd = ExitCommand()
        self.register_command(exit_cmd)
        self.commands["quit"] = exit_cmd

    def register_command(self, command: Command):
        self.commands[command.get_name()] = command

    def get_command(self, name: str) -> Optional[Command]:
        return self.commands.get(name.lower())

    def list_commands(self) -> List[str]:
        return list(self.commands.keys())


class HistoryTracker:
    """Tracks interaction history for the REPL session."""

    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add_entry(self, command: str, args: List[str], result: Any, success: bool = True):
        self.history.append({
            'command': command,
            'args': args,
            'result': result,
            'success': success,
            'timestamp': self._get_timestamp()
        })

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history.copy()

    def clear_history(self):
        self.history.clear()

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class REPLEngine:
    """Main REPL engine that handles the interactive loop."""

    def __init__(self):
        self.command_registry = CommandRegistry()
        self.history_tracker = HistoryTracker()
        self.running = False

    def start(self):
        self.running = True
        self._print_welcome()

        while self.running:
            try:
                user_input = input("calc> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "history":
                    self._show_history()
                    continue

                self._process_command(user_input)

            except KeyboardInterrupt:
                print("\nUse 'exit' or 'quit' to leave the calculator.")
            except EOFError:
                print("\nGoodbye!")
                break

    def _print_welcome(self):
        print("=" * 50)
        print("  Advanced Python Calculator")
        print("  Type 'help' for available commands")
        print("  Type 'exit' or 'quit' to leave")
        print("=" * 50)

    def _process_command(self, user_input: str):
        parts = user_input.split()
        command_name = parts[0].lower()
        args = parts[1:]

        command = self.command_registry.get_command(command_name)

        if not command:
            error_msg = f"Unknown command: {command_name}. Type 'help' for available commands."
            print(error_msg)
            self.history_tracker.add_entry(command_name, args, error_msg, False)
            return

        try:
            result = command.execute(args)

            if result == "EXIT":
                self.running = False
                print("Goodbye!")
                return

            if isinstance(result, (int, float)):
                print(f"Result: {result}")
            else:
                print(result)

            self.history_tracker.add_entry(command_name, args, result, True)

        except ValueError as exc:
            error_msg = f"Error: {exc}"
            print(error_msg)
            self.history_tracker.add_entry(command_name, args, error_msg, False)

    def _show_history(self):
        history = self.history_tracker.get_history()

        if not history:
            print("No history available.")
            return

        print("\nCalculation History:")
        print("-" * 60)

        for i, entry in enumerate(history[-10:], 1):
            status = "✓" if entry['success'] else "✗"
            command_str = f"{entry['command']} {' '.join(entry['args'])}"
            print(f"{i:2d}. [{status}] {entry['timestamp']} | {command_str}")
            print(f"     {entry['result']}")

        if len(history) > 10:
            print(f"... ({len(history) - 10} more entries)")
        print("-" * 60)
