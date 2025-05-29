import customtkinter as ctk
import secrets
import string
from database import Database
from utils import toggle_theme

class SetupScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("First-Time Setup")
        self.db = Database()
        
        # Use CTkFrame instead of tk.Frame
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20)

        # Theme toggle button in top-right corner
        self.theme_button = ctk.CTkButton(
            self.frame,
            text="🌓",  # Moon/sun emoji
            width=30,
            height=30,
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        # Add a larger centered "Welcome" label inside the frame
        ctk.CTkLabel(self.frame, text="Welcome!", font=("Microsoft YaHei UI Light", 24), anchor="center").grid(row=0, column=0, columnspan=2, pady=10)

        # Set Master Password Label and Entry
        ctk.CTkLabel(self.frame, text="Set Master Password:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.password_entry = ctk.CTkEntry(self.frame, show="*")  # Initially hide the password
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        # Confirm Password Label and Entry
        ctk.CTkLabel(self.frame, text="Confirm Password:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.confirm_entry = ctk.CTkEntry(self.frame, show="*")  # Initially hide the password
        self.confirm_entry.grid(row=2, column=1, padx=10, pady=5)

        # Show Password Checkbox
        self.show_password_var = ctk.BooleanVar()  # Variable to track checkbox state
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        self.show_password_checkbox.grid(row=3, column=0, columnspan=2, pady=5)

        # Submit Button
        ctk.CTkButton(self.frame, text="Submit", command=self.submit).grid(row=4, column=0, columnspan=2, pady=10)

        # Reusable Message Label (initially empty)
        self.message_label = ctk.CTkLabel(self.frame, text="", text_color="red")
        self.message_label.grid(row=5, column=0, columnspan=2, pady=5)

    def toggle_password_visibility(self):
        """Toggle the visibility of the password fields based on the checkbox state."""
        if self.show_password_var.get():  # If checkbox is checked
            self.password_entry.configure(show="")  # Show the password as plain text
            self.confirm_entry.configure(show="")
        else:  # If checkbox is unchecked
            self.password_entry.configure(show="*")  # Hide the password
            self.confirm_entry.configure(show="*")

    def submit(self):
        """Save the master password after validation."""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        # Validate inputs
        if not password or not confirm:
            self.show_message("All fields are required!", color="red")
            return
        if password != confirm:
            self.show_message("Passwords do not match!", color="red")
            return
        if len(password) < 8:
            self.show_message("Password must be at least 8 characters long!", color="red")
            return

        # Generate backup key
        backup_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Save to database
        self.db.save_master_password(password, backup_key)
        self.show_message("Master password set successfully!", color="green")

        # Navigate to the backup key screen
        self.frame.destroy()
        from .backup_key_screen import BackupKeyScreen
        BackupKeyScreen(self.root, password, backup_key)

    def show_message(self, message, color="red"):
        """Display a message in the reusable message label."""
        self.message_label.configure(text=message, text_color=color)

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        new_mode = toggle_theme()
        # Update button text based on new mode
        self.theme_button.configure(text="🌞" if new_mode == "Light" else "🌙")