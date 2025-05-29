from PIL import Image  # Import Pillow's Image module
import customtkinter as ctk
from datetime import datetime
from tkcalendar import Calendar  # For calendar popup
from database import Database
from utils import toggle_theme
from timeout_manager import TimeoutManager

class PasswordVault:
    def __init__(self, root, master_password):
        self.root = root
        self.root.title("Password Vault")
        self.db = Database()
        self.master_password = master_password  # Store the master password

        # Initialize timeout manager
        self.timeout_manager = TimeoutManager()
        self.timeout_manager.set_current_screen(self)

        # Use CTkFrame instead of tk.Frame
        self.frame = ctk.CTkFrame(root)  # Ensure proper theme inheritance
        self.frame.pack(padx=20, pady=20)

        # Bind mouse movement to update activity
        self.frame.bind("<Motion>", self.update_activity)
        self.frame.bind("<Button-1>", self.update_activity)
        self.frame.bind("<Key>", self.update_activity)
        
        # Top row with title, logout and theme buttons
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
        self.back_button.grid(row=0, column=0, sticky="nw", padx=(50, 10), pady=10)
        
        # Title in center
        ctk.CTkLabel(self.frame, text="Password Vault", font=("Microsoft YaHei UI Light", 24), anchor="center").grid(row=0, column=1, pady=10)
        
        # Theme toggle button in top-right corner
        self.theme_button = ctk.CTkButton(
            self.frame,
            text="🌓",  # Moon/sun emoji
            width=30,
            height=30,
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=2, sticky="ne", padx=10, pady=10)

        # Entry fields for adding new passwords
        ctk.CTkLabel(self.frame, text="Site:").grid(row=1, column=0, sticky="w", padx=20, pady=5)
        self.site_entry = ctk.CTkEntry(self.frame)
        self.site_entry.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.frame, text="Password:").grid(row=2, column=0, sticky="w", padx=20, pady=5)
        self.password_entry = ctk.CTkEntry(self.frame)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        # Custom Date Picker with Icon
        ctk.CTkLabel(self.frame, text="Last Updated:").grid(row=3, column=0, sticky="w", padx=20, pady=5)
        self.date_var = ctk.StringVar()  # To store the selected date
        self.use_current_time = ctk.BooleanVar(value=False)  # Default to using current time
        self.date_entry = ctk.CTkEntry(self.frame, textvariable=self.date_var, state="readonly")
        self.date_entry.grid(row=3, column=1, pady=5)

        # Checkbox to toggle between manual date selection and current time
        self.use_current_checkbox = ctk.CTkCheckBox(
            self.frame,
            text="Use Current Time",
            variable=self.use_current_time,
            command=self.toggle_date_selection
        )
        self.use_current_checkbox.grid(row=4, column=0, columnspan=2, pady=5, padx=(20, 0))

        # Calendar Icon Button (right next to the entry field)
        calendar_image = Image.open("assets/calendar.png")
        self.calendar_icon = ctk.CTkButton(
            self.frame,
            text="",
            image=ctk.CTkImage(light_image=calendar_image, size=(20, 20)),  # Pass the loaded image here
            command=lambda: self.open_calendar(),  # Use a lambda to defer the call
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#D3D3D3"
        )
        self.calendar_icon.place(
            in_=self.date_entry,  # Place the icon relative to the entry field
            relx=1.0,             # Align to the right edge of the entry field
            rely=0.5,             # Center vertically
            anchor="w"            # Anchor the icon to the left of its position
        )

        ctk.CTkButton(self.frame, text="Add Password", command=self.add_password).grid(row=5, column=0, columnspan=2, pady=10, padx=(20, 0))

        # Scrollable Frame for displaying passwords
        self.canvas = ctk.CTkCanvas(self.frame, bg="#276ea7", highlightthickness=4, highlightbackground="#a19f9f", width=800)
        self.scrollbar_y = ctk.CTkScrollbar(self.frame, orientation="vertical", command=self.canvas.yview)
        self.scrollbar_x = ctk.CTkScrollbar(self.frame, orientation="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")  # Match theme

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        # Bind mouse wheel for smooth scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_y)  # Vertical scrolling
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel_x)

        # Configure grid to expand properly
        self.frame.grid_columnconfigure(1, weight=1)  # Allow column to expand
        self.frame.grid_rowconfigure(6, weight=1)  # Allow row to expand

        self.canvas.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=(20, 0))  # Span across all columns
        self.scrollbar_y.grid(row=6, column=3, sticky="ns")  # Vertical scrollbar
        self.scrollbar_x.grid(row=7, column=0, columnspan=3, sticky="ew", padx=(20, 0))  # Horizontal scrollbar

        # Buttons for actions
        button_frame = ctk.CTkFrame(self.frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10, padx=(20, 0))
        
        ctk.CTkButton(button_frame, text="Delete Entry", command=self.delete_entry).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Back to Home", command=self.back_to_home).pack(side="left", padx=5)

        # Track selected row to help with deletion
        self.selected_row = None

        # Label to show selected row to help with deletion
        self.selection_label = ctk.CTkLabel(self.frame, text="No row selected")
        self.selection_label.grid(row=9, column=0, columnspan=3, pady=5, padx=(20, 0))

        # Populate the list of passwords
        self.populate_list()

    def toggle_date_selection(self):
        """Toggle between manual date selection and using the current time."""
        if self.use_current_time.get():
            self.date_entry.configure(state="disabled")
            self.date_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Set to current date and time
        else:
            self.date_entry.configure(state="readonly")
            self.date_var.set("") 

    def open_calendar(self):
        """Open a calendar popup to select a date."""
        def set_date():
            """Set the selected date in the entry field."""
            selected_date = cal.get_date()
            self.date_var.set(selected_date + " 00:00:00")  # Append default time
            calendar_popup.destroy()

        # Create a popup window for the calendar
        calendar_popup = ctk.CTkToplevel(self.root)
        calendar_popup.title("Select Date")
        calendar_popup.geometry("300x250")

        cal = Calendar(calendar_popup, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=10)

        confirm_button = ctk.CTkButton(calendar_popup, text="Confirm", command=set_date)
        confirm_button.pack(pady=10)

    def populate_list(self):
        """Populate the scrollable frame with entries from the database."""
        # Clear existing widgets in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Add headers
        headers = ["ID", "Site", "Password", "Last Updated", "Status"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Helvetica", 12, "bold"), anchor="w")
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Add rows
        for row_idx, entry in enumerate(self.db.get_all_passwords(self.master_password), start=1):
            id_, site, password, last_updated, _ = entry
            status = self.calculate_status(last_updated)

            # Determine background color based on status
            bg_color = "transparent"

            # Create labels for each column
            for col, value in enumerate([id_, site, password, last_updated, status]):
                label = ctk.CTkLabel(self.scrollable_frame, text=value, anchor="w", fg_color=bg_color)
                label.grid(row=row_idx, column=col, padx=5, pady=2, sticky="w")

                # Hover effect
                label.bind("<Enter>", lambda event, lbl=label: lbl.configure(fg_color="#D3D3D3"))
                label.bind("<Leave>", lambda event, lbl=label: lbl.configure(fg_color=bg_color))

                # Click to select row
                label.bind("<Button-1>", lambda event, row=row_idx - 1, site=site: self.select_row(row, site))

    def calculate_status(self, last_updated):
        """Determine the status of a password based on its age."""
        try:
            last_updated_date = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
            current_date = datetime.now()
            age = current_date - last_updated_date
            if age.days > 365:  # More than 12 months
                return "Very Important to Update"
            elif age.days > 90:  # More than 3 months
                return "Recommended to Update"
            else:
                return "Active"
        except ValueError:
            return "Unknown"

    def add_password(self):
        """Add a new password to the database."""
        site = self.site_entry.get().strip()
        password = self.password_entry.get().strip()
        last_updated = self.date_var.get()
        if site and password and last_updated:
            self.db.add_password(site, password, self.master_password)
            cursor = self.db.conn.cursor()
            cursor.execute("UPDATE passwords SET last_updated = ? WHERE site = ?", (last_updated, site))
            self.db.conn.commit()
            self.populate_list()
            self.site_entry.delete(0, ctk.END)
            self.password_entry.delete(0, ctk.END)
            self.date_var.set("")  # Clear the date field
        else:
            self.show_error("Please fill all fields!")

    def delete_entry(self):
        """Delete the selected password entry from the database."""
        if self.selected_row is None:
            self.show_error("Please select an entry to delete.")
            return

        # Get the selected password's ID
        entry = self.db.get_all_passwords(self.master_password)[self.selected_row]
        id_ = entry[0]

        # Confirm deletion
        confirm = ctk.CTkToplevel(self.root)
        confirm.title("Confirm Deletion")
        confirm.geometry("300x100")
        ctk.CTkLabel(confirm, text="Are you sure you want to delete this entry?", text_color="red").pack(pady=20)
        ctk.CTkButton(confirm, text="Yes", command=lambda: self.confirm_delete(id_, confirm)).pack(side="left", padx=10)
        ctk.CTkButton(confirm, text="No", command=confirm.destroy).pack(side="right", padx=10)

    def confirm_delete(self, id_, confirm_dialog):
        """Confirm and delete the selected entry."""
        cursor = self.db.conn.cursor()
        cursor.execute("DELETE FROM passwords WHERE id = ?", (id_,))
        self.db.conn.commit()
        confirm_dialog.destroy()
        self.populate_list()
        self.selected_row = None  # Reset selection
        self.selection_label.configure(text="No row selected", text_color="white")

    def back_to_home(self):
        """Navigate back to the home screen."""
        self.frame.destroy()
        from .home_screen import HomeScreen
        screen = HomeScreen(self.root, self.master_password)
        self.timeout_manager.set_current_screen(screen)

    def select_row(self, row, site):
        """Select a row in the table."""
        self.selected_row = row
        self.selection_label.configure(text=f"Selected: {site}", font=("Helvetica", 18))  # Update dynamically

    def show_error(self, message):
        """Display an error message in a popup dialog."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Error")
        dialog.geometry("300x100")
        ctk.CTkLabel(dialog, text=message, text_color="red", font=("Helvetica", 12)).pack(pady=10)
        ctk.CTkButton(dialog,text="OK", command=dialog.destroy, height=30, font=("Helvetica", 12)).pack(pady=5)

    def _on_mousewheel_y(self, event):
        """Handle vertical scrolling with the mouse wheel."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_x(self, event):
        """Handle horizontal scrolling with Shift + mouse wheel."""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def toggle_theme(self):
        """Toggle between light and dark mode."""
        new_mode = toggle_theme()
        # Update button text based on new mode
        self.theme_button.configure(text="🌞" if new_mode == "Light" else "🌙")
        self.update_activity()

    def update_activity(self, event=None):
        self.timeout_manager.update_activity()

    def logout(self):
        """Navigate to the login screen."""
        self.frame.destroy()
        from screens.login_screen import LoginScreen
        screen = LoginScreen(self.root)
        self.timeout_manager.set_current_screen(screen)