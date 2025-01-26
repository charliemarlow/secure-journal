"""Entry point for secure-journal CLI."""

import argparse
import getpass
import sys

from .journal import SecureJournal


def main() -> None:
    """Parse CLI arguments and route them to journal functionality."""
    parser = argparse.ArgumentParser(description="Secure journaling utility")
    parser.add_argument("directory", help="Journal directory")
    parser.add_argument("--read", help="Read specific entry by filename")
    parser.add_argument("--therapy", help="Use deepseek to analyze the entry")
    args = parser.parse_args()

    journal = SecureJournal(args.directory)

    try:
        password = getpass.getpass("Enter password: ")

        if args.read:
            journal.read_entry(args.read, password)
        elif args.therapy:
            journal.request_therapy(args.therapy, password)
        else:
            journal.create_entry(password)
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(0)


if __name__ == "__main__":
    main()
