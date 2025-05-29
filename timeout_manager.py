from datetime import datetime, timedelta

class TimeoutManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimeoutManager, cls).__new__(cls)
            cls._instance.last_activity = datetime.now()
            cls._instance.timeout_duration = timedelta(minutes=1)  # 1 minute timeout if inactive
            cls._instance.root = None
            cls._instance.current_screen = None
        return cls._instance
    
    def set_root(self, root):
        self.root = root
    
    def set_current_screen(self, screen):
        self.current_screen = screen
        self.update_activity()  # Reset activity timer when screen changes
    
    def update_activity(self):
        self.last_activity = datetime.now()
    
    def check_timeout(self):
        if datetime.now() - self.last_activity > self.timeout_duration:
            self.handle_timeout()
            return True
        return False
    
    def handle_timeout(self):
        if self.current_screen and hasattr(self.current_screen, 'frame'):
            self.current_screen.frame.destroy()
        from screens.login_screen import LoginScreen
        screen = LoginScreen(self.root)
        self.set_current_screen(screen)  # Set the new login screen as current screen
    
    def start_timeout_check(self):
        def check():
            if not self.check_timeout():
                self.root.after(1000, check)  # Check for activity every second.
        check() 