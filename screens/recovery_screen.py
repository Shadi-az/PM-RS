import customtkinter as ctk
from database import Database
import hashlib

class RecoveryScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Recovery")
        self.db = Database()
        
        # Use CTkFrame instead of tk.Frame
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20)

        # Add a larger centered "Recovery" label inside the frame
        ctk.CTkLabel(self.frame, text="Recovery", font=("Microsoft YaHei UI Light", 28), anchor="center").grid(row=0, column=0, columnspan=2, pady=10)

        # Backup Key Label and Entry
        ctk.CTkLabel(self.frame, text="Enter Backup Key:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.backup_key_entry = ctk.CTkEntry(self.frame)
        self.backup_key_entry.grid(row=1, column=1, padx=10, pady=5)

        # New Master Password Label and Entry
        ctk.CTkLabel(self.frame, text="New Master Password:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.new_password_entry = ctk.CTkEntry(self.frame, show="*")  # Initially hide the password
        self.new_password_entry.grid(row=2, column=1, padx=10, pady=5)

        # Confirm New Password Label and Entry
        ctk.CTkLabel(self.frame, text="Confirm New Password:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.confirm_password_entry = ctk.CTkEntry(self.frame, show="*")  # Initially hide the password
        self.confirm_password_entry.grid(row=3, column=1, padx=10, pady=5)

        # Show Password Checkbox
        self.show_password_var = ctk.BooleanVar()  # Variable to track checkbox state
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        self.show_password_checkbox.grid(row=4, column=0, columnspan=2, pady=5)

        # Reset Password Button
        ctk.CTkButton(self.frame, text="Reset Password", command=self.reset_password).grid(row=5, column=0, columnspan=2, pady=10)

        # Back to Login Button
        ctk.CTkButton(self.frame, text="Back to Login", command=self.back_to_login).grid(row=6, column=0, columnspan=2, pady=5)

        # Reusable Message Label (initially empty)
        self.message_label = ctk.CTkLabel(self.frame, text="", text_color="red")
        self.message_label.grid(row=7, column=0, columnspan=2, pady=5)

    def toggle_password_visibility(self):
        """Toggle the visibility of the password fields based on the checkbox state."""
        if self.show_password_var.get():  # If checkbox is checked
            self.new_password_entry.configure(show="")  # Show the password as plain text
            self.confirm_password_entry.configure(show="")
        else:  # If checkbox is unchecked
            self.new_password_entry.configure(show="*")  # Hide the password
            self.confirm_password_entry.configure(show="*")

    def reset_password(self):
        """Reset the master password using the backup key."""
        backup_key = self.backup_key_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validate inputs
        if not backup_key or not new_password or not confirm_password:
            self.show_message("All fields are required!", color="red")
            return
        if new_password != confirm_password:
            self.show_message("Passwords do not match!", color="red")
            return
        if len(new_password) < 8:
            self.show_message("Password must be at least 8 characters long!", color="red")
            return

        # Verify the backup key
        if not self.db.verify_backup_key(backup_key):
            self.show_message("Invalid backup key!", color="red")
            return

        # Update the master password in the database
        master_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE users SET master_password_hash = ? WHERE id = 1", (master_password_hash,))
        self.db.conn.commit()

        # Generate a new backup key
        new_backup_key = self.db.generate_new_backup_key()
        self.show_message("Master password has been reset successfully!", color="green")

        # Navigate to the backup key screen
        self.frame.destroy()
        from screens.backup_key_screen import BackupKeyScreen
        BackupKeyScreen(self.root, new_password, new_backup_key)

    def back_to_login(self):
        """Navigate back to the login screen."""
        self.frame.destroy()
        from screens.login_screen import LoginScreen
        LoginScreen(self.root)

    def show_message(self, message, color="red"):
        """Display a message in the reusable message label."""
        self.message_label.configure(text=message, text_color=color)