import customtkinter as ctk
import pyperclip

class BackupKeyScreen:
    def __init__(self, root, master_password, backup_key):
        self.root = root
        self.master_password = master_password
        self.backup_key = backup_key
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(
            self.frame,
            text="Backup Key Generated",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=20)
        
        # Backup Key Display
        key_frame = ctk.CTkFrame(self.frame)
        key_frame.pack(pady=10)
        
        ctk.CTkLabel(
            key_frame,
            text="Your Backup Key:",
            font=("Arial", 14)
        ).pack(pady=5)
        
        self.key_var = ctk.StringVar(value=self.backup_key)
        key_entry = ctk.CTkEntry(
            key_frame,
            textvariable=self.key_var,
            font=("Courier", 14),
            width=400,
            state="readonly"
        )
        key_entry.pack(pady=5)
        
        # Copy confirmation label
        self.feedback_label = ctk.CTkLabel(
            key_frame,
            text="",
            text_color="green",
            font=("Arial", 12)
        )
        self.feedback_label.pack(pady=2)
        
        # Copy Button
        copy_button = ctk.CTkButton(
            key_frame,
            text="Copy to Clipboard",
            command=self.copy_key,
            font=("Arial", 12)
        )
        copy_button.pack(pady=5)
        
        # Instructions
        instructions = (
            "Please save this key in a secure location.\n"
            "You will need it to recover your account if you forget your master password."
        )
        instructions_label = ctk.CTkLabel(
            self.frame,
            text=instructions,
            font=("Arial", 14),
            wraplength=400
        )
        instructions_label.pack(pady=20)
        
        # Continue button
        continue_button = ctk.CTkButton(
            self.frame,
            text="Continue to Home",
            command=self.continue_to_home,
            font=("Arial", 14)
        )
        continue_button.pack(pady=20)
        
    def copy_key(self):
        pyperclip.copy(self.backup_key)
        self.feedback_label.configure(text="Backup key copied to clipboard!")
        
    def continue_to_home(self):
        self.frame.destroy()
        from screens.home_screen import HomeScreen
        HomeScreen(self.root, self.master_password)