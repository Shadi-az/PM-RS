import customtkinter as ctk
from database import Database
from utils import toggle_theme
from timeout_manager import TimeoutManager

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.db = Database()

        # Initialize timeout manager
        self.timeout_manager = TimeoutManager()
        self.timeout_manager.set_current_screen(self)

        # Set up CTkFrame
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20)

        # Bind mouse movement to update activity
        self.frame.bind("<Motion>", self.update_activity)
        self.frame.bind("<Button-1>", self.update_activity)
        self.frame.bind("<Key>", self.update_activity)

        # Theme toggle button in top-right corner
        self.theme_button = ctk.CTkButton(
            self.frame,
            text="🌓",  # Moon/sun emoji
            width=30,
            height=30,
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=1, sticky="ne", padx=10, pady=10)
        
        # Master Password Label and Entry
        ctk.CTkLabel(self.frame, text="Login", font=("Microsoft YaHei UI Light", 28), anchor="center").grid(row=0, column=0, columnspan=2, pady=10)
        ctk.CTkLabel(self.frame, text="Master Password:").grid(row=1, column=0, padx=10, pady=5)
        self.password_entry = ctk.CTkEntry(self.frame, show="*")  # Initially hide the password
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)

        # Show Password Checkbox
        self.show_password_var = ctk.BooleanVar()  # Variable to track checkbox state
        self.show_password_checkbox = ctk.CTkCheckBox(
            self.frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        self.show_password_checkbox.grid(row=2, column=0, columnspan=2, pady=5)

        # Error Label (initially empty)
        self.error_label = ctk.CTkLabel(self.frame, text="", text_color="red")
        self.error_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Login Button
        ctk.CTkButton(self.frame, text="Login", command=self.login).grid(row=4, column=0, columnspan=2, pady=10)

        # Forgot Password Button
        ctk.CTkButton(self.frame, text="Forgot Password?", command=self.open_recovery_screen).grid(row=5, column=0, columnspan=2, pady=5)

    def update_activity(self, event=None):
        self.timeout_manager.update_activity()

    def toggle_password_visibility(self):
        """Toggle the visibility of the password based on the checkbox state."""
        if self.show_password_var.get():  # If checkbox is checked
            self.password_entry.configure(show="")  # Show the password as plain text
        else:  # If checkbox is unchecked
            self.password_entry.configure(show="*")  # Hide the password
        self.update_activity()

    def login(self):
        """Verify the master password and navigate to the home screen."""
        password = self.password_entry.get()
        if self.db.verify_master_password(password):
            # Clear any previous error message
            self.error_label.configure(text="")
            self.frame.destroy()
            from .home_screen import HomeScreen
            screen = HomeScreen(self.root, password)
            self.timeout_manager.set_current_screen(screen)
        else:
            # Display error message below the input field
            self.error_label.configure(text="Incorrect password!")
            self.update_activity()

    def open_recovery_screen(self):
        """Navigate to the recovery screen."""
        self.frame.destroy()
        from .recovery_screen import RecoveryScreen
        screen = RecoveryScreen(self.root)
        self.timeout_manager.set_current_screen(screen)

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        new_mode = toggle_theme()
        # Update button text based on new mode
        self.theme_button.configure(text="🌞" if new_mode == "Light" else "🌙")
        self.update_activity()