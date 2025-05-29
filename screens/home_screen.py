import customtkinter as ctk
from PIL import Image  # Import Image from Pillow
import os
from utils import toggle_theme
from timeout_manager import TimeoutManager

class HomeScreen:
    def __init__(self, root, master_password):
        self.root = root
        self.root.title("Home")
        self.master_password = master_password  # Store the master password
        
        # Initialize timeout manager
        self.timeout_manager = TimeoutManager()
        self.timeout_manager.set_current_screen(self)
        
        # Load the image using PIL and wrap it with CTkImage
        self.genImg = ctk.CTkImage(
            light_image=Image.open("assets/genLight.png"),  # Image for light mode
            dark_image=Image.open("assets/genDark.png"),    # Image for dark mode
            size=(64, 64)
        )
        self.vaultImg = ctk.CTkImage(
            light_image=Image.open("assets/vaultLight.png"),  # Image for light mode
            dark_image=Image.open("assets/vaultDark.png"),    # Image for dark mode
            size=(64, 64)
        )
        
        # Load recommender system images
        self.rsImg = ctk.CTkImage(
            light_image=Image.open("assets/RSLight.png"),  # Image for light mode
            dark_image=Image.open("assets/RSDark.png"),    # Image for dark mode
            size=(64, 64)
        )
        
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

        # Logout button in top-left corner
        self.logout_button = ctk.CTkButton(
            self.frame,
            text="❌",
            width=30,
            height=30,
            command=self.logout
        )
        self.logout_button.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        ctk.CTkLabel(self.frame, text="Home page", font=("Microsoft YaHei UI Light", 24), anchor="center").grid(row=0, column=0, columnspan=3, pady=10)

        # Password Vault Button
        ctk.CTkButton(self.frame, text="Password Vault", image=self.vaultImg,
                      command=self.open_vault, width=150, height=70).grid(row=1, column=0, padx=10, pady=10)
        
        # Password Generator Button with Image
        ctk.CTkButton(self.frame, text="Password Generator", image=self.genImg,
                      command=self.open_generator, width=150, height=70).grid(row=1, column=1, padx=10, pady=10)
        
        # Recommender System Button
        ctk.CTkButton(self.frame, text="Recommender System", image=self.rsImg,
                      command=self.open_recommender, width=150, height=70).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Bind mouse movement to update activity
        self.frame.bind("<Motion>", self.update_activity)
        self.frame.bind("<Button-1>", self.update_activity)
        self.frame.bind("<Key>", self.update_activity)

    def update_activity(self, event=None):
        self.timeout_manager.update_activity()

    def open_vault(self):
        """Navigate to the Password Vault screen."""
        self.frame.destroy()
        from .password_vault import PasswordVault
        screen = PasswordVault(self.root, self.master_password)
        self.timeout_manager.set_current_screen(screen)

    def open_generator(self):
        """Navigate to the Password Generator screen."""
        self.frame.destroy()
        from screens.password_generator import PasswordGenerator
        screen = PasswordGenerator(self.root, self.master_password)
        self.timeout_manager.set_current_screen(screen)

    def open_recommender(self):
        """Navigate to the Recommender System screen."""
        self.frame.destroy()
        from .recommender_screen import RecommenderScreen
        screen = RecommenderScreen(self.root, self.master_password)
        self.timeout_manager.set_current_screen(screen)

    def logout(self):
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