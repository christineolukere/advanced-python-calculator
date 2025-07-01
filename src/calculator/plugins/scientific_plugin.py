import math
from typing import List
from calculator.core.plugin_interface import Plugin
from calculator.core.repl import Command


class ScientificCommand(Command):
    """Base class for scientific commands."""
    
    def __init__(self, operation: str, func, arg_count: int = 1):
        self.operation = operation
        self.func = func
        self.arg_count = arg_count
    
    def execute(self, args: List[str]) -> float:
        """Execute scientific operation."""
        if len(args) != self.arg_count:
            raise ValueError(f"{self.operation} requires exactly {self.arg_count} argument(s)")
        
        try:
            if self.arg_count == 1:
                number = float(args[0])
                result = self.func(number)
            else:
                numbers = [float(arg) for arg in args]
                result = self.func(*numbers)
            
            return result
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError(f"Invalid number format: {e}")
            raise ValueError(f"Math error: {e}")
        except (OverflowError, ZeroDivisionError) as e:
            raise ValueError(f"Math error: {e}")
    
    def get_help(self) -> str:
        arg_text = " ".join([f"<number{i+1}>" for i in range(self.arg_count)])
        return f"{self.get_name()} {arg_text} - Calculate {self.operation}"
    
    def get_name(self) -> str:
        return self.operation.lower()


class SqrtCommand(ScientificCommand):
    def __init__(self):
        super().__init__("sqrt", math.sqrt)


class PowerCommand(ScientificCommand):
    def __init__(self):
        super().__init__("power", pow, 2)


class LogCommand(ScientificCommand):
    def __init__(self):
        super().__init__("log", math.log10)


class LnCommand(ScientificCommand):
    def __init__(self):
        super().__init__("ln", math.log)


class SinCommand(ScientificCommand):
    def __init__(self):
        super().__init__("sin", math.sin)


class CosCommand(ScientificCommand):
    def __init__(self):
        super().__init__("cos", math.cos)


class TanCommand(ScientificCommand):
    def __init__(self):
        super().__init__("tan", math.tan)


class ScientificPlugin(Plugin):
    """Plugin providing scientific mathematical functions."""
    
    def get_name(self) -> str:
        return "Scientific Plugin"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Provides scientific mathematical functions (sqrt, power, log, trig, etc.)"
    
    def get_commands(self) -> List[Command]:
        return [
            SqrtCommand(),
            PowerCommand(),
            LogCommand(),
            LnCommand(),
            SinCommand(),
            CosCommand(),
            TanCommand()
        ]