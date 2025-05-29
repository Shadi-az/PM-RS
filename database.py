import sqlite3
import random
import string
from utils import hash_password, encrypt_password, decrypt_password
import hashlib
import os
import secrets

class Database:
    def __init__(self):
        self.db_name = 'password_manager.db'
        self.conn = sqlite3.connect(self.db_name)
        self.create_tables()

    def create_tables(self):
        """Create the necessary tables if they don't already exist."""
        cursor = self.conn.cursor()

        # Users Table: Stores master password hash and backup key hash
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                master_password_hash TEXT NOT NULL,
                backup_key_hash TEXT NOT NULL
            )
        ''')

        # Passwords Table: Stores site-specific passwords (what the user enters to it)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY,
                site TEXT NOT NULL,
                password TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Active'
            )
        ''')
        self.conn.commit()

    def save_master_password(self, master_password, backup_key):
        """Save the master password and backup key hashes to the database."""
        cursor = self.conn.cursor()
        
        # Hash both the master password and backup key
        master_password_hash = hashlib.sha256(master_password.encode()).hexdigest()
        backup_key_hash = hashlib.sha256(backup_key.encode()).hexdigest()
        
        # Insert both hashes into the database
        cursor.execute("""
            INSERT INTO users (master_password_hash, backup_key_hash)
            VALUES (?, ?)
        """, (master_password_hash, backup_key_hash))
        
        self.conn.commit()

    def verify_master_password(self, master_password):
        cursor = self.conn.cursor()
        master_password_hash = hashlib.sha256(master_password.encode()).hexdigest()
        
        cursor.execute("""
            SELECT master_password_hash FROM users LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            return result[0] == master_password_hash
        return False

    def verify_backup_key(self, backup_key):
        cursor = self.conn.cursor()
        backup_key_hash = hashlib.sha256(backup_key.encode()).hexdigest()
        
        cursor.execute("""
            SELECT backup_key_hash FROM users LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            return result[0] == backup_key_hash
        return False

    def generate_backup_key(self):
        """
        Generate a random 16-character alphanumeric backup key.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def generate_new_backup_key(self):
        """
        Generate and save a new backup key for the user.
        """
        new_backup_key = self.generate_backup_key()
        new_backup_key_hash = hash_password(new_backup_key)  # Hash the new backup key
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET backup_key_hash = ? WHERE id = 1", (new_backup_key_hash,))
        self.conn.commit()
        return new_backup_key

    def add_password(self, site, password, master_password):
        """
        Add a new password entry for a specific site.
        """
        encrypted_password = encrypt_password(password, master_password)
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO passwords (site, password) VALUES (?, ?)',
                      (site, encrypted_password))
        self.conn.commit()

    def get_all_passwords(self, master_password):
        """
        Retrieve all password entries from the database and decrypt them.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, site, password, last_updated, status FROM passwords')
        results = cursor.fetchall()
        
        # Decrypt passwords
        decrypted_results = []
        for row in results:
            id_, site, encrypted_password, last_updated, status = row
            try:
                decrypted_password = decrypt_password(encrypted_password, master_password)
                decrypted_results.append((id_, site, decrypted_password, last_updated, status))
            except:
                # If decryption fails, return the encrypted password
                decrypted_results.append((id_, site, encrypted_password, last_updated, status))
        
        return decrypted_results

    def delete_password(self, password_id):
        """
        Delete a password entry by its ID.
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
        self.conn.commit()

    def update_password(self, password_id, new_password, master_password):
        """
        Update a password entry by its ID.
        """
        encrypted_password = encrypt_password(new_password, master_password)
        cursor = self.conn.cursor()
        cursor.execute('UPDATE passwords SET password = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?',
                      (encrypted_password, password_id))
        self.conn.commit()

    def get_backup_key(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT backup_key_hash FROM users LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else None

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()