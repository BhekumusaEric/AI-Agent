"""
Main entry point for the AI Agent application.

This script launches the AI Agent CLI.
"""

from cli import AIAgentCLI

def main():
    """Main function."""
    cli = AIAgentCLI()
    cli.run()

if __name__ == "__main__":
    main()
