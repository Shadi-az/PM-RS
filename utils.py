import hashlib
import random
import string
import pyperclip
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import customtkinter as ctk

def toggle_theme():
    """Toggle between light and dark mode."""
    current_mode = ctk.get_appearance_mode()
    new_mode = "Light" if current_mode == "Dark" else "Dark"
    ctk.set_appearance_mode(new_mode)
    return new_mode

def hash_password(password):
    # Hash a password using SHA-256.
    return hashlib.sha256(password.encode()).hexdigest()

def derive_key_from_password(password):
    # Derive a Fernet key from the master password using PBKDF2.

    # Convert password to bytes
    password = password.encode()
    
    # Generate a salt
    salt = b'password_manager_salt'
    
    # Use PBKDF2 to derive a key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_password(password, master_password):
    """
    Encrypt a password using the master password.
    """
    key = derive_key_from_password(master_password)
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password, master_password):
    """
    Decrypt a password using the master password.
    """
    key = derive_key_from_password(master_password)
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

def copy_to_clipboard(text):
    """
    Copy text to the clipboard.
    """
    pyperclip.copy(text)