import customtkinter as ctk
from utils import toggle_theme
import sys

"""
this is the consent screen for the application, it is the first screen that the user sees before getting access to the app.
"""
class ConsentScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Privacy Consent")
        
        # Set up CTkFrame
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20, expand=True)
        
        # Configure grid to center content
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Theme toggle button in top-right corner
        self.theme_button = ctk.CTkButton(
            self.frame,
            text="🌓",  # Moon/sun emoji to refer to theme
            width=30,
            height=30,
            command=self.toggle_theme
        )
        self.theme_button.place(relx=0.95, rely=0.05, anchor="ne")

        ctk.CTkLabel( # frame title
            self.frame, 
            text="Privacy Consent", 
            font=("Microsoft YaHei UI Light", 36), 
            anchor="center"
        ).grid(row=0, column=0, pady=(20, 10), sticky="n")

        # Consent text
        consent_text = (
            "Welcome, it is great to see you take a step towards better password management and hygiene. \n\n"
            "- It is recommended to keep your passwords safe and up-to-date, this app can help you do it all! \n\n"
            "- It is important to note that this application uses zero-knowledge encryption to protect your data. \n\n"
            "Zero-knowledge encryption means that all your data is encrypted on your device "
            "before it is stored, and only you can decrypt it with your master password. \n\n"
            "- All data entered by you is safe and secure. Not even the developers "
            "can access your stored passwords or personal information. \n\n"
            "- There are different options of password generation. If you would like to use the Recommender system please give the screen time to load when used for the first time, and please note; memorable passwords generation is not the most secure, as it uses common words.\n\n"
            "* By clicking 'I Agree', you consent to these terms and acknowledge that "
            "if you forget your master password and backup key, your data cannot be recovered."
            "\n\n           Please note that this application is tsted but is still in development and may contain bugs."
        )
        

        self.consent_textbox = ctk.CTkTextbox(self.frame, width=600, height=320)
        self.consent_textbox.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="n")
        self.consent_textbox.insert("1.0", consent_text)
        self.consent_textbox.configure(state="disabled", wrap="word")  # Make it read-only with word wrapping

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, pady=(0, 10), sticky="n")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        # I Agree Button
        ctk.CTkButton(
            buttons_frame, 
            text="I Agree", 
            command=self.on_agree,
            width=150
        ).grid(row=0, column=0, padx=20, pady=10, sticky="e")

        # I Don't Agree Button
        ctk.CTkButton(
            buttons_frame, 
            text="I Don't Agree", 
            command=self.on_disagree,
            width=150
        ).grid(row=0, column=1, padx=20, pady=10, sticky="w")

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        new_mode = toggle_theme()
        # Update button text based on new mode
        self.theme_button.configure(text="🌞" if new_mode == "Light" else "🌙")

    def on_agree(self):
        """User agreed to the consent, proceed to setup screen."""
        self.frame.destroy()
        from .setup_screen import SetupScreen
        screen = SetupScreen(self.root)

    def on_disagree(self):
        """User disagreed with the consent, close the application."""
        self.root.destroy()  # Close the window
        sys.exit()  # Ensure the application fully exits