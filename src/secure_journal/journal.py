# src/secure_journal/journal.py
import json
import subprocess
import time
from pathlib import Path

from .crypto import JournalCrypto


class SecureJournal:
    """A secure journaling utility that integrates with Emacs."""

    def __init__(self, directory: str | Path):
        """Initialize a secure journal in the specified directory.

        Args:
            directory: Path to the journal directory
        """
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.crypto = JournalCrypto(self.directory)

    def _start_emacs_server(self) -> None:
        """Start Emacs server if not already running."""
        try:
            # Check if server is running
            subprocess.run(
                ["emacsclient", "--eval", "t"], check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            # Start server if not running
            subprocess.Popen(
                ["emacs", "--daemon"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Wait for server to start
            time.sleep(1)

    def create_entry(self, password: str) -> None:
        """Create a new journal entry.

        Args:
            password: The password to encrypt the entry with
        """
        if not self.crypto.verify_password(password):
            print("Incorrect password for this journal directory")
            return

        self._start_emacs_server()

        # Create new buffer in Emacs and get its name
        get_buffer_cmd = """
        (progn
            (setq buf (generate-new-buffer "*journal*"))
            (with-current-buffer buf
                (setq buffer-file-name nil)
                (setq auto-save-default nil)
                (setq make-backup-files nil)
                (setq create-lockfiles nil))
            (buffer-name buf))
        """

        result = subprocess.run(
            ["emacsclient", "--eval", get_buffer_cmd],
            capture_output=True,
            text=True,
            check=True,
        )
        buffer_name = result.stdout.strip().strip('"')

        # Open buffer in Emacs
        subprocess.run(
            ["emacsclient", "-c", "--eval", f'(switch-to-buffer "{buffer_name}")'],
            check=True,
        )

        # Get buffer content after editing
        get_content_cmd = f"""
        (with-current-buffer "{buffer_name}"
            (prog1
                (buffer-string)
                (kill-buffer)))
        """

        result = subprocess.run(
            ["emacsclient", "--eval", get_content_cmd],
            capture_output=True,
            text=True,
            check=True,
        )

        content = result.stdout.strip().strip('"')
        if content and content != "nil":
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            encrypted_file = self.directory / f"{timestamp}.enc"

            # Encrypt and save
            encrypted_content = self.crypto.encrypt(content, password)
            encrypted_file.write_bytes(encrypted_content)
            print(f"Entry saved as {encrypted_file.name}")
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

            self._start_emacs_server()

            # Create new read-only buffer with content
            eval_cmd = f"""
            (progn
                (switch-to-buffer (generate-new-buffer "*journal-read*"))
                (insert {json.dumps(decrypted_content)})
                (read-only-mode)
                (not-modified))
            """

            subprocess.run(
                ["emacsclient", "-c", "--eval", eval_cmd],
                check=True,
            )
        except Exception as e:
            print(f"Error reading entry: {e}")
