import customtkinter as ctk
import random
import string
import pyperclip
from utils import toggle_theme
from timeout_manager import TimeoutManager

class PasswordGenerator:
    def __init__(self, root, master_password):
        self.root = root
        self.master_password = master_password
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20)
        
        # Initialize timeout manager
        self.timeout_manager = TimeoutManager()
        self.timeout_manager.set_current_screen(self)
        
        # Bind mouse movement to update activity
        self.frame.bind("<Motion>", self.update_activity)
        self.frame.bind("<Button-1>", self.update_activity)
        self.frame.bind("<Key>", self.update_activity)
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Theme toggle button in top-right corner
        self.theme_button = ctk.CTkButton(
            self.frame,
            text="🌓",  # Moon/sun emoji
            width=30,
            height=30,
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        # Logout button in top-left corner
        self.logout_button = ctk.CTkButton(
            self.frame,
            text="❌",
            width=30,
            height=30,
            command=self.logout,
        )
        self.logout_button.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        # Back to Home button next to logout button
        self.back_button = ctk.CTkButton(
            self.frame,
            text="←",
            width=30,
            height=30,
            command=self.back_to_home,
            font= ("Arial", 16)
        )
        self.back_button.grid(row=0, column=0, sticky="nw", padx=(50, 10), pady=10)

        # Title
        ctk.CTkLabel(self.frame, text="Password Generator", font=("Microsoft YaHei UI Light", 24), anchor="center").grid(row=0, column=0, columnspan=2, pady=10)
        
        # Main content frame
        content_frame = ctk.CTkFrame(self.frame)
        content_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Length slider
        length_frame = ctk.CTkFrame(content_frame)
        length_frame.pack(pady=10)
        
        ctk.CTkLabel(
            length_frame,
            text="Password Length:",
            font=("Arial", 14)
        ).pack(side="left", padx=5)
        
        self.length_var = ctk.StringVar(value="12")
        length_entry = ctk.CTkEntry(
            length_frame,
            textvariable=self.length_var,
            width=50
        )
        length_entry.pack(side="left", padx=5)
        
        # Character options
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.pack(pady=10)
        
        self.use_uppercase = ctk.BooleanVar(value=True)
        self.use_lowercase = ctk.BooleanVar(value=True)
        self.use_numbers = ctk.BooleanVar(value=True)
        self.use_special = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(
            options_frame,
            text="Uppercase Letters",
            variable=self.use_uppercase
        ).pack(side="left", padx=5)
        
        ctk.CTkCheckBox(
            options_frame,
            text="Lowercase Letters",
            variable=self.use_lowercase
        ).pack(side="left", padx=5)
        
        ctk.CTkCheckBox(
            options_frame,
            text="Numbers",
            variable=self.use_numbers
        ).pack(side="left", padx=5)
        
        ctk.CTkCheckBox(
            options_frame,
            text="Special Characters",
            variable=self.use_special
        ).pack(side="left", padx=5)
        
        # Generated password display
        self.password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            content_frame,
            textvariable=self.password_var,
            font=("Courier", 14),
            width=400
        )
        password_entry.pack(pady=10)
        
        # Feedback label for both copy confirmation and errors
        self.feedback_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=("Arial", 12)
        )
        self.feedback_label.pack(pady=2)
        
        # Buttons
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Generate",
            command=self.generate_password
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Copy",
            command=self.copy_password
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Back to Home",
            command=self.back_to_home
        ).pack(side="left", padx=5)
        
    def generate_password(self):
        try:
            length = int(self.length_var.get())
            if length < 4:
                self.feedback_label.configure(
                    text="Password length is too short. A longer password is recommended for better security.",
                    text_color="red"
                )
                return
                
            characters = ""
            if self.use_uppercase.get():
                characters += string.ascii_uppercase
            if self.use_lowercase.get():
                characters += string.ascii_lowercase
            if self.use_numbers.get():
                characters += string.digits
            if self.use_special.get():
                characters += string.punctuation
                
            if not characters:
                self.feedback_label.configure(
                    text="Please select at least one character type for password generation.",
                    text_color="red"
                )
                return
                
            password = ''.join(random.choice(characters) for _ in range(length))
            self.password_var.set(password)
            self.feedback_label.configure(text="")  # Clear any previous messages
            
        except ValueError:
            self.feedback_label.configure(
                text="Please enter a valid number for password length.",
                text_color="red"
            )
            
    def copy_password(self):
        password = self.password_var.get()
        if password and not password.startswith("Error:"):
            pyperclip.copy(password)
            self.feedback_label.configure(
                text="Password copied to clipboard!",
                text_color="green"
            )
            
    def back_to_home(self):
        self.frame.destroy()
        from screens.home_screen import HomeScreen
        screen = HomeScreen(self.root, self.master_password)
        self.timeout_manager.set_current_screen(screen)

    def logout(self):
        """Navigate to the login screen."""
        self.frame.destroy()
        from screens.login_screen import LoginScreen
        screen = LoginScreen(self.root)
        self.timeout_manager.set_current_screen(screen)

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        new_mode = toggle_theme()
        # Update button text based on new mode
        self.theme_button.configure(text="🌞" if new_mode == "Light" else "🌙")
        self.update_activity()

    def update_activity(self, event=None):
        self.timeout_manager.update_activity()