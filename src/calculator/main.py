# File: src/calculator/main.py
"""
Main entry point for the Advanced Python Calculator.
"""

from calculator.core.enhanced_repl import EnhancedREPLEngine


def main():
    """Main entry point for the calculator application."""
    try:
        repl = EnhancedREPLEngine()
        repl.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())