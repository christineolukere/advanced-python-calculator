import statistics
from typing import List
from calculator.core.plugin_interface import Plugin
from calculator.core.repl import Command


class StatisticsCommand(Command):
    """Base class for statistics commands."""
    
    def __init__(self, operation: str, func, min_args: int = 1):
        self.operation = operation
        self.func = func
        self.min_args = min_args
    
    def execute(self, args: List[str]) -> float:
        """Execute statistical operation."""
        if len(args) < self.min_args:
            raise ValueError(f"{self.operation} requires at least {self.min_args} argument(s)")
        
        try:
            numbers = [float(arg) for arg in args]
            if len(numbers) == 0:
                raise ValueError("No valid numbers provided")
            
            result = self.func(numbers)
            return result
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError(f"Invalid number format in arguments")
            raise e
        except statistics.StatisticsError as e:
            raise ValueError(f"Statistics error: {e}")
    
    def get_help(self) -> str:
        return f"{self.get_name()} <number1> [number2 ...] - Calculate {self.operation}"
    
    def get_name(self) -> str:
        return self.operation.lower().replace(' ', '_')


class MeanCommand(StatisticsCommand):
    def __init__(self):
        super().__init__("mean", statistics.mean)


class MedianCommand(StatisticsCommand):
    def __init__(self):
        super().__init__("median", statistics.median)


class ModeCommand(StatisticsCommand):
    def __init__(self):
        super().__init__("mode", statistics.mode)


class StdevCommand(StatisticsCommand):
    def __init__(self):
        super().__init__("standard_deviation", statistics.stdev, min_args=2)


class VarianceCommand(StatisticsCommand):
    def __init__(self):
        super().__init__("variance", statistics.variance, min_args=2)


class StatisticsPlugin(Plugin):
    """Plugin providing statistical functions."""
    
    def get_name(self) -> str:
        return "Statistics Plugin"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def get_description(self) -> str:
        return "Provides statistical calculation functions (mean, median, mode, etc.)"
    
    def get_commands(self) -> List[Command]:
        return [
            MeanCommand(),
            MedianCommand(),
            ModeCommand(),
            StdevCommand(),
            VarianceCommand()
        ]