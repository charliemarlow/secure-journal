import base64
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class JournalCrypto:
    """Handles encryption and password management for the journal."""

    def __init__(self, directory: Path) -> None:
        """Initialize crypto manager for a journal directory.

        Args:
            directory: Path to the journal directory

        """
        self.directory = directory
        self.salt_file = directory / ".salt"
        self.config_file = directory / ".config"
        self.salt = self._get_or_create_salt()

    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create a new one for the directory.

        Returns:
            bytes: The salt used for key derivation

        """
        if self.salt_file.exists():
            return self.salt_file.read_bytes()
        salt = os.urandom(16)
        self.salt_file.write_bytes(salt)
        return salt

    def _generate_key(self, password: str) -> Fernet:
        """Generate encryption key from password using PBKDF2.

        Args:
            password: The password to derive the key from

        Returns:
            Fernet: The encryption/decryption object

        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def verify_password(self, password: str) -> bool:
        """Verify if the password matches the directory's password.

        Args:
            password: Password to verify

        Returns:
            bool: True if password is correct

        """
        if not self.config_file.exists():
            # First time setup - save a test value
            fernet = self._generate_key(password)
            config = {"test": fernet.encrypt(b"test").decode()}
            self.config_file.write_text(json.dumps(config))
            return True

        config = json.loads(self.config_file.read_text())
        fernet = self._generate_key(password)
        try:
            fernet.decrypt(config["test"].encode())
        except Exception:
            return False
        else:
            return True

    def encrypt(self, content: str, password: str) -> bytes:
        """Encrypt content with the given password.

        Args:
            content: Content to encrypt
            password: Password to use for encryption

        Returns:
            bytes: Encrypted content

        """
        fernet = self._generate_key(password)
        return fernet.encrypt(content.encode())

    def decrypt(self, encrypted_content: bytes, password: str) -> str:
        """Decrypt content with the given password.

        Args:
            encrypted_content: Content to decrypt
            password: Password to use for decryption

        Returns:
            str: Decrypted content

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails

        """
        fernet = self._generate_key(password)
        return fernet.decrypt(encrypted_content).decode()
