"""Core functionality for the secure journaling utility.

Orchestrates the encryption, editing, and therapy analysis of journal entries.
"""

import time
from pathlib import Path

from .crypto import JournalCrypto
from .editor import Editor
from .therapy import TherapySession


class SecureJournal:
    """A secure journaling utility that integrates with Emacs."""

    def __init__(self, directory: str | Path) -> None:
        """Initialize a secure journal in the specified directory.

        Args:
            directory: Path to the journal directory

        """
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.crypto = JournalCrypto(self.directory)
        self.therapy = TherapySession()
        self.editor = Editor()

    def create_entry(self, password: str) -> None:
        """Create a new journal entry.

        Args:
            password: The password to encrypt the entry with

        """
        if not self.crypto.verify_password(password):
            print("Incorrect password for this journal directory")
            return

        content = self.editor.open_buffer(None)
        if content and content != "nil":
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            encrypted_file = self.directory / f"{timestamp}.enc"

            # Encrypt and save
            encrypted_content = self.crypto.encrypt(content, password)
            encrypted_file.write_bytes(encrypted_content)
            print(f"Entry saved as {encrypted_file.name}")

            self.request_therapy(encrypted_file.name, password)
        else:
            print("No content written, entry discarded")

    def read_entry(self, filename: str, password: str) -> None:
        """Read and decrypt a specific journal entry.

        Args:
            filename: Name of the encrypted file to read
            password: The password to decrypt the entry with

        """
        if not self.crypto.verify_password(password):
            print("Incorrect password for this journal directory")
            return

        entry_path = self.directory / filename
        if not entry_path.exists():
            print(f"Entry {filename} not found")
            return

        try:
            encrypted_content = entry_path.read_bytes()
            decrypted_content = self.crypto.decrypt(
                encrypted_content,
                password,
            )

            updated_content = self.editor.open_buffer(decrypted_content)

            reencrypted_content = self.crypto.encrypt(
                updated_content,
                password,
            )
            entry_path.write_bytes(reencrypted_content)
        except Exception as e:
            print(f"Error reading entry: {e}")

    def request_therapy(self, entry_filename: str, password: str) -> None:
        """Request therapy analysis of a specific entry.

        Args:
            entry_filename: Name of the entry file to analyze
            password: Encryption password

        """
        if not self.crypto.verify_password(password):
            print("Incorrect password for this journal directory")
            return

        entry_path = self.directory / entry_filename
        if not entry_path.exists():
            print(f"Entry {entry_filename} not found")
            return

        try:
            encrypted_content = entry_path.read_bytes()
            content = self.crypto.decrypt(encrypted_content, password)
            print("Analyzing entry with AI therapist...")
            result = self.therapy.analyze_entry(content)

            final_content = self.editor.open_buffer(result)
            if final_content:
                # Save the edited content
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                therapy_file = self.directory / f"{timestamp}_therapy.enc"
                encrypted_response = self.crypto.encrypt(
                    final_content,
                    password,
                )
                therapy_file.write_bytes(encrypted_response)
                print(f"\nTherapy response saved as {therapy_file.name}")

        except Exception as e:
            print(f"Error generating therapy response: {e}")
