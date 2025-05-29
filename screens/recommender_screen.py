import customtkinter as ctk
import pyperclip
import sys
import os
from timeout_manager import TimeoutManager
from utils import toggle_theme

# Add the recommender system directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recommender system'))

# Import the PasswordGenerator class from the recommender system module
from recommender_system import PasswordGenerator as MLPasswordGenerator
from recommender_system_memorable import PasswordGenerator as MemorablePasswordGenerator

class RecommenderScreen:
    def __init__(self, root, master_password):
        self.root = root
        self.root.title("Recommender System")
        self.master_password = master_password
        
        # Initialize timeout manager
        self.timeout_manager = TimeoutManager()
        self.timeout_manager.set_current_screen(self)
        
        # Initialize password generators
        self.ml_generator = None
        self.memorable_generator = MemorablePasswordGenerator(max_length=15)
        self.is_model_loading = False
        
        # Use CTkFrame instead of tk.Frame
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20)

        # Create UI elements
        self.create_widgets()
        
        # Bind mouse movement to update activity
        self.frame.bind("<Motion>", self.update_activity)
        self.frame.bind("<Button-1>", self.update_activity)
        self.frame.bind("<Key>", self.update_activity)
    
    def create_widgets(self):
        # Theme toggle button in top-right corner
        self.theme_button = ctk.CTkButton(
            self.frame,
            text="🌓",  # Moon/sun emoji
            width=30,
            height=30,
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=2, sticky="ne", padx=10, pady=10)

        # Logout button in top-left corner
        self.logout_button = ctk.CTkButton(
            self.frame,
            text="❌",
            width=30,
            height=30,
            command=self.logout
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
        self.back_button.grid(row=0, column=0, sticky="nw", padx=(50, 0), pady=10)

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=2) 
        self.frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(self.frame, text="Password Recommender System", font=("Microsoft YaHei UI Light", 24), anchor="center").grid(row=0, column=1, pady=10, padx=20)
        
        content_frame = ctk.CTkFrame(self.frame)
        content_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10)
        
        # Generator type options
        options_frame = ctk.CTkFrame(content_frame)
        options_frame.pack(pady=10)
        
        self.generator_type = ctk.StringVar(value="ml")
        
        ctk.CTkRadioButton(
            options_frame,
            text="AI-Generated Passwords",
            variable=self.generator_type,
            value="ml",
            command=self.update_warning_label
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            options_frame,
            text="Memorable Passwords",
            variable=self.generator_type,
            value="memorable",
            command=self.update_warning_label
        ).pack(side="left", padx=10)
        
        # Add warning label
        self.warning_label = ctk.CTkLabel(
            content_frame,
            text="Generate a secure password using advanced AI or memorable patterns",
            font=("Arial", 12)
        )
        self.warning_label.pack(pady=(0, 10))
        
        # Generated password display
        self.password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            content_frame,
            textvariable=self.password_var,
            font=("Courier", 14),
            width=400
        )
        password_entry.pack(pady=10)
        
        # Feedback label for both status messages and copy confirmation
        self.feedback_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=("Arial", 12)
        )
        self.feedback_label.pack(pady=2)
        
        # Buttons
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(pady=10)
        
        self.generate_button = ctk.CTkButton(
            button_frame,
            text="Generate Password",
            command=self.generate_password
        )
        self.generate_button.pack(side="left", padx=5)
        
        self.copy_button = ctk.CTkButton(
            button_frame,
            text="Copy",
            command=self.copy_password
        )
        self.copy_button.pack(side="left", padx=5)

    def generate_password(self):
        # Disable generate button to prevent multiple clicks
        self.generate_button.configure(state="disabled")
        
        try:
            if self.generator_type.get() == "ml":
                if not self.is_model_loading:
                    # Initialize ML generator if not already done
                    if self.ml_generator is None:
                        self.is_model_loading = True
                        self.feedback_label.configure(
                            text="Initializing AI model (this may take a moment)...",
                            text_color="orange"
                        )
                        self.root.update()
                        
                        try:
                            self.ml_generator = MLPasswordGenerator(max_length=15)
                            self.ml_generator.train(epochs=5)  # Reduced epochs for faster training
                            self.is_model_loading = False
                        except Exception as e:
                            self.is_model_loading = False
                            raise e
                    
                    # Generate password using ML model
                    self.feedback_label.configure(
                        text="AI is generating password...",
                        text_color="orange"
                    )
                    self.root.update()
                    
                    passwords = self.ml_generator.generate_multiple(1)
                    if passwords:
                        self.password_var.set(passwords[0])
                        self.feedback_label.configure(
                            text="AI-generated password ready!",
                            text_color="green"
                        )
                    else:
                        self.password_var.set("")
                        self.feedback_label.configure(
                            text="Failed to generate password. Please try again.",
                            text_color="red"
                        )
                else:
                    self.feedback_label.configure(
                        text="Please wait, AI model is still initializing...",
                        text_color="orange"
                    )
            else:  # memorable
                # Generate memorable password
                self.feedback_label.configure(
                    text="Generating memorable password...",
                    text_color="orange"
                )
                self.root.update()
                
                passwords = self.memorable_generator.generate_multiple(1)
                if passwords:
                    self.password_var.set(passwords[0])
                    self.feedback_label.configure(
                        text="Memorable password ready!",
                        text_color="green"
                    )
                else:
                    self.password_var.set("")
                    self.feedback_label.configure(
                        text="Failed to generate password. Please try again.",
                        text_color="red"
                    )
        except Exception as e:
            self.password_var.set("")
            self.feedback_label.configure(
                text=f"Error: {str(e)}",
                text_color="red"
            )
    
    def copy_password(self):
        password = self.password_var.get().strip()  # Strip any leading/trailing spaces
        if password:
            pyperclip.copy(password)
            self.feedback_label.configure(
                text="Password copied to clipboard!",
                text_color="green"
            )
        else:
            self.feedback_label.configure(
                text="No password to copy. Generate a password first.",
                text_color="red"
            )
    
    def back_to_home(self):
        """Navigate back to the home screen."""
        self.frame.destroy()
        from .home_screen import HomeScreen
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
        
    def update_warning_label(self):
        """Update warning label text and visibility based on generator type."""
        if self.generator_type.get() == "memorable":
            self.warning_label.configure(
                text="Note: Memorable password generation is not the most secure \nas the model for it uses common words",
                text_color="orange"
            )

    def update_activity(self, event=None):
        self.timeout_manager.update_activity()