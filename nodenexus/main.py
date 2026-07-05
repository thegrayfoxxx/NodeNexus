import asyncio
from nodenexus.plugins.interfaces.cli import run


def main():
    """Main entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
