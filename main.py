import customtkinter as ctk
from database import Database
from timeout_manager import TimeoutManager

# Set appearance mode (Light, Dark, or System)
ctk.set_appearance_mode("System")  # Default set to System

# Set default colour theme
ctk.set_default_color_theme("blue") # blue is a colour from CTK

def main():
    root = ctk.CTk()
    root.geometry("1200x600")
    
    # Activate timeout manager
    timeout_manager = TimeoutManager()
    timeout_manager.set_root(root)
    timeout_manager.start_timeout_check()
    
    db = Database()
    
    # Check if first run (first time user)
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        from screens.consent_screen import ConsentScreen
        screen = ConsentScreen(root)
        timeout_manager.set_current_screen(screen)
    else:
        from screens.login_screen import LoginScreen
        screen = LoginScreen(root)
        timeout_manager.set_current_screen(screen)
    
    root.mainloop()

if __name__ == "__main__":
    main()