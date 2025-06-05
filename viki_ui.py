import sys
import subprocess
import importlib
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import cv2
import PIL.Image, PIL.ImageTk
import time
import queue
import viki  # Assuming viki.py is in the same directory and importable
import speech_recognition as sr
import customtkinter as ctk
import tkinter.ttk as ttk
import os # Make sure os is imported for path handling
import winsound # Make sure winsound is imported

# --- Configuration for Module Check ---
APP_NAME = "Viki Voice Assistant"
REQUIRED_MODULES = [
    "pyttsx3",
    "speech_recognition",
    "openai",
    "wikipedia",
    "requests",
    "bs4",
    "cv2",
    "PIL",
    "customtkinter",
]

# --- Helper Functions for Module Check ---

def is_running_in_pyinstaller_bundle():
    """Check if the script is running inside a PyInstaller bundle."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def check_and_install_modules_ui():
    """
    Checks for required modules and offers to install them if missing.
    Uses Tkinter message boxes for user interaction.
    Returns True if all modules are present or successfully installed, False otherwise.
    """
    missing_modules = []
    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_modules.append(module_name)
        except Exception as e:
            messagebox.showerror("Module Check Error", f"Error checking module '{module_name}': {e}\n\n"
                                 "Please ensure Python and its dependencies are correctly installed.")
            return False

    if missing_modules:
        msg = f"Some required Python modules are missing for {APP_NAME}:\n\n" \
              f"{', '.join(missing_modules)}\n\n" \
              "Would you like to attempt to install them now? This requires an internet connection."

        if not is_running_in_pyinstaller_bundle():
            messagebox.showwarning("Missing Modules", "Some modules are missing. "
                                   "Please install them manually using pip:\n\n"
                                   f"pip install {' '.join(missing_modules)}\n\n"
                                   "Then try running the application again.")
            return False

        if messagebox.askyesno("Missing Modules", msg):
            try:
                python_exe = sys.executable

                try:
                    subprocess.run([python_exe, "-m", "pip", "--version"], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    messagebox.showerror("Pip Not Found", "pip could not be found or executed from the bundled Python environment. "
                                         "Please ensure your Python installation is correct or install modules manually.")
                    return False

                command = [python_exe, "-m", "pip", "install"] + missing_modules

                temp_root = tk.Toplevel()
                temp_root.title("Installing Modules")
                temp_root.geometry("300x100")
                temp_root.grab_set()
                tk.Label(temp_root, text="Please wait while modules are being installed.\nThis window will close automatically.", padx=10, pady=10).pack()
                tk.Label(temp_root, text="(Do not close this window)", font=("Arial", 9, "italic")).pack()
                temp_root.update_idletasks()

                process = subprocess.run(command, capture_output=True, text=True, check=True)

                temp_root.destroy()

                messagebox.showinfo("Installation Complete", "Missing modules installed successfully! "
                                    "Please restart the application for changes to take effect.")
                print("--- Pip Installation Output ---")
                print("STDOUT:\n", process.stdout)
                print("STDERR:\n", process.stderr)
                sys.exit()
            except subprocess.CalledProcessError as e:
                temp_root.destroy() if 'temp_root' in locals() else None
                messagebox.showerror("Installation Error", f"Failed to install modules:\n{e.stderr}\n\nPlease install them manually or consult the documentation.")
                return False
            except Exception as e:
                temp_root.destroy() if 'temp_root' in locals() else None
                messagebox.showerror("Error", f"An unexpected error occurred during module installation: {e}")
                return False
        else:
            messagebox.showwarning("Warning", "Some modules are missing. The application may not function correctly without them.")
            return False
    return True

# --- Path Adjustment for Bundled Files ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Opening Video Function ---
def play_opening_video(video_path):
    full_video_path = resource_path(video_path)
    print(f"Attempting to open video: {full_video_path}")
    cap = cv2.VideoCapture(full_video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open opening video at {full_video_path}. Check file path or codecs.")
        return

    # Create a small Tkinter window for the video (optional, depends on UX)
    # You could also use a custom splash screen from scratch.
    splash_root = tk.Tk()
    splash_root.withdraw() # Hide main Tkinter window
    splash_root.overrideredirect(True) # Remove window decorations
    splash_label = tk.Label(splash_root)
    splash_label.pack()

    # Center the splash screen
    screen_width = splash_root.winfo_screenwidth()
    screen_height = splash_root.winfo_screenheight()
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if video_width == 0 or video_height == 0:
        print("Could not get video dimensions. Skipping splash screen.")
        cap.release()
        splash_root.destroy()
        return

    x_pos = (screen_width - video_width) // 2
    y_pos = (screen_height - video_height) // 2
    splash_root.geometry(f"{video_width}x{video_height}+{x_pos}+{y_pos}")
    splash_root.deiconify()


    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert frame to PhotoImage
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        pil_img = PIL.Image.fromarray(cv2image)
        imgtk = PIL.ImageTk.PhotoImage(image=pil_img)

        splash_label.imgtk = imgtk # Keep reference
        splash_label.config(image=imgtk)
        splash_root.update_idletasks()
        splash_root.update()

        if cv2.waitKey(25) & 0xFF == ord('q'): # Adjust waitKey for frame rate
            break
    cap.release()
    cv2.destroyAllWindows()
    splash_root.destroy() # Close the splash screen

# --- Main UI Class ---

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue") # You can try "dark-blue" or "green"

class VikiUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Viki Voice Assistant UI")
        self.root.geometry("900x750") # Slightly taller
        self.root.minsize(700, 600) # Minimum size to prevent layout issues

        # Configure grid rows and columns for responsiveness
        self.root.grid_rowconfigure(0, weight=0) # Logo
        self.root.grid_rowconfigure(1, weight=1) # Chat area
        self.root.grid_rowconfigure(2, weight=0) # Input field
        self.root.grid_rowconfigure(3, weight=0) # Main buttons
        self.root.grid_rowconfigure(4, weight=0) # Video label/indicator (if hidden/shown dynamically)
        self.root.grid_rowconfigure(5, weight=0) # App mapping label frame
        self.root.grid_rowconfigure(6, weight=0) # App mapping input frame
        self.root.grid_rowconfigure(7, weight=0) # Webapp input frame
        self.root.grid_columnconfigure(0, weight=1) # Main content column

        # Add logo image at the top
        try:
            logo_path = resource_path("jarvis/viki_logo.png")
            print(f"Loading logo image from: {logo_path}")
            logo_image = PIL.Image.open(logo_path)
            max_width = 200
            max_height = 100
            logo_image.thumbnail((max_width, max_height), PIL.Image.Resampling.LANCZOS) # Use Resampling.LANCZOS
            self.logo_imgtk = PIL.ImageTk.PhotoImage(logo_image)
            self.logo_label = ctk.CTkLabel(root, image=self.logo_imgtk, text="")
            self.logo_label.grid(row=0, column=0, pady=10) # Use grid for logo
        except Exception as e:
            print(f"Error loading logo image: {e}")
            self.logo_label = ctk.CTkLabel(root, text="Viki Assistant", font=("Segoe UI", 24, "bold"))
            self.logo_label.grid(row=0, column=0, pady=10)

        # Load click sound file path (adjusted for PyInstaller)
        self.click_sound_path = resource_path("click.wav")
        self.bind_button_sounds()

        # Replace text display with canvas for chat bubbles
        self.chat_canvas = tk.Canvas(root, bg=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0], highlightthickness=0) # Use theme color
        self.chat_canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Add a scrollbar for the canvas (using CTkScrollbar)
        self.scrollbar = ctk.CTkScrollbar(root, command=self.chat_canvas.yview)
        self.scrollbar.grid(row=1, column=0, sticky="nse") # Stick to the right of chat_canvas

        # Frame inside canvas to hold messages (using CTkFrame)
        self.messages_frame = ctk.CTkFrame(self.chat_canvas, fg_color="transparent") # Use transparent background
        # Create window inside canvas for messages_frame
        self.canvas_window_id = self.chat_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        self.messages_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        # Bind canvas resize to update the width of the window holding messages_frame
        self.chat_canvas.bind("<Configure>", self._on_canvas_resize)

        # Entry for manual command input with styled frame for rounded corners
        self.input_frame = ctk.CTkFrame(root, corner_radius=10)
        self.input_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1) # Make entry expand

        self.entry = ctk.CTkEntry(self.input_frame, font=("Segoe UI", 14), placeholder_text="Type your command here...", corner_radius=8)
        self.entry.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        self.entry.bind("<Return>", self.send_command)

        self.btn_send = ctk.CTkButton(self.input_frame, text="Send", command=self.send_command, corner_radius=8)
        self.btn_send.grid(row=0, column=1, padx=10, pady=8)

        # Buttons frame (using CTkFrame)
        btn_frame = ctk.CTkFrame(root, fg_color="transparent") # Transparent background
        btn_frame.grid(row=3, column=0, pady=10)
        btn_frame.grid_columnconfigure((0,1,2,3,4,5,6,7,8,9,10), weight=1) # Make columns expand equally

        self.btn_listen = ctk.CTkButton(btn_frame, text="Start Listening", command=self.start_listening, corner_radius=8)
        self.btn_listen.grid(row=0, column=0, padx=5, pady=5)

        self.btn_stop_listen = ctk.CTkButton(btn_frame, text="Stop Listening", command=self.stop_listening, state="disabled", corner_radius=8, fg_color="red")
        self.btn_stop_listen.grid(row=0, column=1, padx=5, pady=5)

        self.status_label = ctk.CTkLabel(btn_frame, text="Status: Idle", font=("Segoe UI", 12, "bold"))
        self.status_label.grid(row=0, column=2, padx=10)

        self.btn_video = ctk.CTkButton(btn_frame, text="Toggle Video Mode", command=self.toggle_video_mode, corner_radius=8)
        self.btn_video.grid(row=0, column=3, padx=5, pady=5)

        # Video recording controls
        self.btn_start_record = ctk.CTkButton(btn_frame, text="Start Recording", command=self.start_recording, state="disabled", corner_radius=8)
        self.btn_start_record.grid(row=0, column=4, padx=5, pady=5)

        self.btn_stop_record = ctk.CTkButton(btn_frame, text="Stop Recording", command=self.stop_recording, state="disabled", corner_radius=8, fg_color="red")
        self.btn_stop_record.grid(row=0, column=5, padx=5, pady=5)

        self.btn_capture_photo = ctk.CTkButton(btn_frame, text="Capture Photo", command=self.capture_photo, state="disabled", corner_radius=8)
        self.btn_capture_photo.grid(row=0, column=6, padx=5, pady=5)

        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear Chat", command=self.clear_text, corner_radius=8)
        self.btn_clear.grid(row=0, column=7, padx=5, pady=5)

        # Video format selection
        self.video_format_var = ctk.StringVar(value="mp4")
        self.video_format_label = ctk.CTkLabel(btn_frame, text="Format:")
        self.video_format_label.grid(row=0, column=8, padx=(20, 5), pady=5)
        self.video_format_option = ctk.CTkComboBox(btn_frame, variable=self.video_format_var, values=["mp4", "avi"], state="readonly", width=80, corner_radius=8)
        self.video_format_option.grid(row=0, column=9, padx=5, pady=5)

        # Theme toggle button
        self.btn_toggle_theme = ctk.CTkButton(btn_frame, text="Switch to Dark Mode", command=self.toggle_theme, corner_radius=8)
        self.btn_toggle_theme.grid(row=0, column=10, padx=5, pady=5)

        # Video display label (initially hidden or small)
        self.video_label = ctk.CTkLabel(root, text="", width=640, height=480) # Placeholder for video
        self.video_label.grid(row=4, column=0, pady=5)
        # Initially hide the video label by setting its state.
        self.video_label.grid_remove() # Hide it initially

        # Listening indicator canvas
        self.indicator_canvas = tk.Canvas(root, width=20, height=20, highlightthickness=0, bg=root.cget("bg"))
        self.indicator_canvas.grid(row=4, column=0, pady=5, sticky="n") # Initially positioned if video is hidden
        self.indicator_oval = self.indicator_canvas.create_oval(2, 2, 18, 18, fill="gray")

        # Initialize recording variables
        self.recording = False
        self.video_writer = None
        self.current_frame = None

        # New frame for application list and voice command mapping
        self.app_frame = ctk.CTkFrame(root, corner_radius=10) # Use CTkFrame
        self.app_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")
        self.app_frame.grid_columnconfigure(0, weight=1) # Make treeview expand

        ctk.CTkLabel(self.app_frame, text="Applications Voice Command Mapping", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        # Treeview for applications and voice commands
        self.app_tree = ttk.Treeview(self.app_frame, columns=("Application", "Voice Command", "Path"), show="headings", height=5)
        self.app_tree.heading("Application", text="Application")
        self.app_tree.heading("Voice Command", text="Voice Command")
        self.app_tree.heading("Path", text="Path")
        self.app_tree.column("Application", width=150, stretch=False)
        self.app_tree.column("Voice Command", width=200, stretch=False)
        self.app_tree.column("Path", width=350, stretch=True) # Path can stretch
        self.app_tree.grid(row=1, column=0, padx=5, pady=5, sticky="nsew") # Use grid

        # Scrollbar for treeview
        self.app_scrollbar = ctk.CTkScrollbar(self.app_frame, command=self.app_tree.yview) # Use CTkScrollbar
        self.app_scrollbar.grid(row=1, column=1, padx=5, pady=5, sticky="ns") # Stick to right of treeview
        self.app_tree.configure(yscrollcommand=self.app_scrollbar.set)


        # Frame for adding new application, voice command and path
        self.add_app_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.add_app_frame.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        self.add_app_frame.grid_columnconfigure((1,3,5), weight=1) # Make entry columns expand

        ctk.CTkLabel(self.add_app_frame, text="Application:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.app_entry = ctk.CTkEntry(self.add_app_frame, width=150, corner_radius=8)
        self.app_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_app_frame, text="Voice Command:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.voice_entry = ctk.CTkEntry(self.add_app_frame, width=150, corner_radius=8)
        self.voice_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_app_frame, text="Path:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.path_entry = ctk.CTkEntry(self.add_app_frame, width=250, corner_radius=8)
        self.path_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        self.btn_browse_path = ctk.CTkButton(self.add_app_frame, text="Browse", command=self.browse_path, corner_radius=8)
        self.btn_browse_path.grid(row=0, column=6, padx=5, pady=5)

        self.btn_add_app = ctk.CTkButton(self.add_app_frame, text="Add App", command=self.add_application, corner_radius=8)
        self.btn_add_app.grid(row=0, column=7, padx=5, pady=5)

        self.btn_edit_app = ctk.CTkButton(self.add_app_frame, text="Edit Selected", command=self.edit_selected_application, corner_radius=8)
        self.btn_edit_app.grid(row=0, column=8, padx=5, pady=5)

        self.btn_delete_app = ctk.CTkButton(self.add_app_frame, text="Delete Selected", command=self.delete_selected_application, corner_radius=8, fg_color="red")
        self.btn_delete_app.grid(row=0, column=9, padx=5, pady=5)


        # Frame for adding new web application and voice command
        self.add_webapp_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.add_webapp_frame.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        self.add_webapp_frame.grid_columnconfigure((1,3), weight=1) # Make entry columns expand

        ctk.CTkLabel(self.add_webapp_frame, text="Web App Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.webapp_entry = ctk.CTkEntry(self.add_webapp_frame, width=150, corner_radius=8)
        self.webapp_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.add_webapp_frame, text="Web App Command:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.webapp_voice_entry = ctk.CTkEntry(self.add_webapp_frame, width=150, corner_radius=8)
        self.webapp_voice_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.btn_add_webapp = ctk.CTkButton(self.add_webapp_frame, text="Add Web App", command=self.add_web_application, corner_radius=8)
        self.btn_add_webapp.grid(row=0, column=4, padx=5, pady=5)

        self.btn_edit_webapp = ctk.CTkButton(self.add_webapp_frame, text="Edit Selected Web", command=self.edit_selected_web_application, corner_radius=8)
        self.btn_edit_webapp.grid(row=0, column=5, padx=5, pady=5)

        self.btn_delete_webapp = ctk.CTkButton(self.add_webapp_frame, text="Delete Selected Web", command=self.delete_selected_web_application, corner_radius=8, fg_color="red")
        self.btn_delete_webapp.grid(row=0, column=6, padx=5, pady=5)

        # Flags and threads
        self.listening = False
        self.video_mode = False
        self.video_thread = None
        self.listen_thread = None
        self.stop_event = threading.Event()

        # Queue for thread-safe UI updates
        self.queue = queue.Queue()

        # Start UI update loop
        self.root.after(100, self.process_queue)

        # Load saved custom commands into the treeview
        self.load_custom_commands()

        # Initialize ttk styling for Treeview
        self._setup_treeview_style()

    def _setup_treeview_style(self):
        style = ttk.Style()
        # Set custom theme for Treeview
        # Example: Using CustomTkinter's default colors for better integration
        current_theme_colors = ctk.ThemeManager.theme.get("CTkFrame", {})

        def safe_get_color(theme_dict, key, default):
            try:
                return theme_dict[key][0]
            except (KeyError, IndexError, TypeError):
                return default

        style.theme_use("default") # Base on default theme first

        # Configure the Treeview itself
        style.configure("Treeview",
                        background=safe_get_color(current_theme_colors, "fg_color", "#FFFFFF"), # Background color
                        foreground=safe_get_color(current_theme_colors, "text_color", "#000000"), # Text color
                        fieldbackground=safe_get_color(current_theme_colors, "fg_color", "#FFFFFF"), # Field background
                        bordercolor=safe_get_color(current_theme_colors, "border_color", "#000000"), # Border color
                        rowheight=25, # Height of rows
                        borderwidth=1,
                        relief="solid"
                        )
        # Configure the Treeview headings
        ctk_button_theme = ctk.ThemeManager.theme.get("CTkButton", {})
        style.configure("Treeview.Heading",
                        background=safe_get_color(ctk_button_theme, "fg_color", "#0078D7"), # Button color
                        foreground=safe_get_color(ctk_button_theme, "text_color", "#FFFFFF"), # Button text color
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=1,
                        relief="raised" # Give it a slightly raised look
                        )
        style.map("Treeview.Heading",
                  background=[('active', safe_get_color(ctk_button_theme, "hover_color", "#005A9E"))])

        # Configure selected item color
        style.map('Treeview',
                  background=[('selected', ctk.ThemeManager.theme.get("CTkButton", {}).get("fg_color", ["#005A9E", "#004578"])[1])], # Selected background (darker blue)
                  foreground=[('selected', ctk.ThemeManager.theme.get("CTkButton", {}).get("text_color", ["#FFFFFF", "#F0F0F0"])[1])] # Selected text (white)
                 )

    def _on_canvas_resize(self, event):
        # Update the width of the frame inside the canvas when canvas resizes
        self.chat_canvas.itemconfig(self.canvas_window_id, width=event.width)


    def load_custom_commands(self):
        import json
        CUSTOM_COMMANDS_FILE = resource_path("custom_commands.json")
        try:
            with open(CUSTOM_COMMANDS_FILE, "r") as f:
                commands = json.load(f)
            for item in self.app_tree.get_children():
                self.app_tree.delete(item)
            for voice_cmd, app_path in commands.items():
                if app_path.startswith("web://"):
                    app_name = app_path[len("web://"):]
                else:
                    app_name = os.path.basename(app_path)
                self.app_tree.insert("", "end", values=(app_name, voice_cmd, app_path))
            self.log_to_chat("Loaded custom commands from file.")
        except FileNotFoundError:
            self.log_to_chat("No custom commands file found to load.")
        except json.JSONDecodeError:
            self.log_to_chat("Error decoding custom commands file. File might be corrupt.")
        except Exception as e:
            self.log_to_chat(f"Error loading custom commands: {e}")

    def update_status(self, status):
        self.status_label.configure(text=f"Status: {status}")

    def update_indicator(self, color):
        self.indicator_canvas.itemconfig(self.indicator_oval, fill=color)

    def clear_text(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self.log_to_chat("Chat cleared.")

    def browse_path(self):
        file_path = filedialog.askopenfilename(title="Select Application Executable")
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

    def add_application(self):
        app_name = self.app_entry.get().strip()
        voice_cmd = self.voice_entry.get().strip()
        app_path = self.path_entry.get().strip()
        if app_name and voice_cmd and app_path:
            if not os.path.isfile(app_path):
                messagebox.showwarning("Input Error", "Please select a valid file for the application path.")
                return
            self.app_tree.insert("", "end", values=(app_name, voice_cmd, app_path))
            self.app_entry.delete(0, tk.END)
            self.voice_entry.delete(0, tk.END)
            self.path_entry.delete(0, tk.END)
            self.log_to_chat(f"Added application '{app_name}'")
            self.save_custom_command(voice_cmd, app_path)
        else:
            messagebox.showwarning("Input Error", "Please enter application name, voice command, and path.")

    def add_web_application(self):
        webapp_name = self.webapp_entry.get().strip()
        voice_cmd = self.webapp_voice_entry.get().strip()
        if webapp_name and voice_cmd:
            webapp_path = f"web://{webapp_name}"
            self.app_tree.insert("", "end", values=(webapp_name, voice_cmd, webapp_path))
            self.webapp_entry.delete(0, tk.END)
            self.webapp_voice_entry.delete(0, tk.END)
            self.log_to_chat(f"Added web application '{webapp_name}'")
            self.save_custom_command(voice_cmd, webapp_path)
        else:
            messagebox.showwarning("Input Error", "Please enter web application name and voice command.")

    def edit_selected_application(self):
        selected = self.app_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an application to edit.")
            return
        item = selected[0]
        values = self.app_tree.item(item, "values")
        if len(values) != 3:
            messagebox.showwarning("Data Error", "Selected item does not have valid data.")
            return
        # Differentiate between regular app and web app
        if values[2].startswith("web://"):
            messagebox.showwarning("Edit Error", "This is a web application. Please use 'Edit Selected Web' button.")
            return

        self.app_entry.delete(0, tk.END)
        self.app_entry.insert(0, values[0])
        self.voice_entry.delete(0, tk.END)
        self.voice_entry.insert(0, values[1])
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, values[2])
        self.btn_add_app.configure(text="Update App", command=lambda: self.update_application(item))

    def edit_selected_web_application(self):
        selected = self.app_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a web application to edit.")
            return
        item = selected[0]
        values = self.app_tree.item(item, "values")
        if len(values) != 3:
            messagebox.showwarning("Data Error", "Selected item does not have valid data.")
            return
        if not values[2].startswith("web://"):
            messagebox.showwarning("Edit Error", "This is a regular application. Please use 'Edit Selected' button.")
            return

        self.webapp_entry.delete(0, tk.END)
        self.webapp_entry.insert(0, values[0])
        self.webapp_voice_entry.delete(0, tk.END)
        self.webapp_voice_entry.insert(0, values[1])
        self.btn_add_webapp.configure(text="Update Web App", command=lambda: self.update_web_application(item))


    def update_application(self, item):
        app_name = self.app_entry.get().strip()
        voice_cmd = self.voice_entry.get().strip()
        app_path = self.path_entry.get().strip()
        if app_name and voice_cmd and app_path:
            self.app_tree.item(item, values=(app_name, voice_cmd, app_path))
            self.app_entry.delete(0, tk.END)
            self.voice_entry.delete(0, tk.END)
            self.path_entry.delete(0, tk.END)
            self.log_to_chat(f"Updated application '{app_name}'")
            self.save_all_custom_commands()
            self.btn_add_app.configure(text="Add App", command=self.add_application)
        else:
            messagebox.showwarning("Input Error", "Please enter application name, voice command, and path.")

    def update_web_application(self, item):
        webapp_name = self.webapp_entry.get().strip()
        voice_cmd = self.webapp_voice_entry.get().strip()
        if webapp_name and voice_cmd:
            webapp_path = f"web://{webapp_name}"
            self.app_tree.item(item, values=(webapp_name, voice_cmd, webapp_path))
            self.webapp_entry.delete(0, tk.END)
            self.webapp_voice_entry.delete(0, tk.END)
            self.log_to_chat(f"Updated web application '{webapp_name}'")
            self.save_all_custom_commands()
            self.btn_add_webapp.configure(text="Add Web App", command=self.add_web_application)
        else:
            messagebox.showwarning("Input Error", "Please enter web application name and voice command.")

    def delete_selected_application(self):
        selected = self.app_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an application to delete.")
            return
        item = selected[0]
        values = self.app_tree.item(item, "values")
        if len(values) != 3:
            messagebox.showwarning("Data Error", "Selected item does not have valid data.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete application '{values[0]}'?"):
            self.app_tree.delete(item)
            self.log_to_chat(f"Deleted application '{values[0]}'")
            self.save_all_custom_commands()

    def delete_selected_web_application(self):
        selected = self.app_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a web application to delete.")
            return
        item = selected[0]
        values = self.app_tree.item(item, "values")
        if len(values) != 3:
            messagebox.showwarning("Data Error", "Selected item does not have valid data.")
            return
        if not values[2].startswith("web://"): # Ensure it's actually a web app
            messagebox.showwarning("Selection Error", "Selected item is not a web application.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete web application '{values[0]}'?"):
            self.app_tree.delete(item)
            self.log_to_chat(f"Deleted web application '{values[0]}'")
            self.save_all_custom_commands()


    def save_all_custom_commands(self):
        try:
            import json
            CUSTOM_COMMANDS_FILE = resource_path("custom_commands.json")
            commands = {}
            for item in self.app_tree.get_children():
                values = self.app_tree.item(item, "values")
                if len(values) == 3:
                    voice_cmd = values[1]
                    app_path = values[2]
                    commands[voice_cmd] = app_path
            with open(CUSTOM_COMMANDS_FILE, "w", encoding="utf-8") as f:
                json.dump(commands, f, indent=4)
            self.log_to_chat("Saved all custom commands.")
            self.save_commands_to_txt()
        except Exception as e:
            self.log_to_chat(f"Error saving all custom commands: {e}")

    def save_custom_command(self, voice_cmd, app_path):
        try:
            import json
            CUSTOM_COMMANDS_FILE = resource_path("custom_commands.json")
            try:
                with open(CUSTOM_COMMANDS_FILE, "r") as f:
                    commands = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                commands = {}
            commands[voice_cmd] = app_path
            with open(CUSTOM_COMMANDS_FILE, "w", encoding="utf-8") as f:
                json.dump(commands, f, indent=4)
            self.log_to_chat(f"Saved custom command '{voice_cmd}'")
            self.save_commands_to_txt()
        except Exception as e:
            self.log_to_chat(f"Error saving single custom command: {e}")

    def save_commands_to_txt(self):
        try:
            CUSTOM_COMMANDS_TXT = resource_path("custom_commands.txt")
            with open(CUSTOM_COMMANDS_TXT, "w", encoding="utf-8") as f:
                for item in self.app_tree.get_children():
                    values = self.app_tree.item(item, "values")
                    if len(values) == 3:
                        voice_cmd = values[1]
                        app_path = values[2]
                        f.write(f"{voice_cmd} : {app_path}\n")
            self.log_to_chat("Saved commands to custom_commands.txt")
        except Exception as e:
            self.log_to_chat(f"Error saving commands to txt: {e}")

    def toggle_listening(self):
        if self.listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        if not self.listening:
            self.listening = True
            self.btn_listen.configure(state="disabled")
            self.btn_stop_listen.configure(state="normal")
            self.update_status("Listening")
            self.update_indicator("green")
            self.stop_event.clear()
            self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.listen_thread.start()
            self.log_to_chat("Listening started...")

    def stop_listening(self):
        if self.listening:
            self.listening = False
            self.btn_listen.configure(state="normal")
            self.btn_stop_listen.configure(state="disabled")
            self.update_status("Idle")
            self.update_indicator("gray")
            self.stop_event.set()
            self.log_to_chat("Listening stopped.")

    def log_to_chat(self, message):
        self.queue.put(("add_message", {"message": message, "sender": "ai"}))

    def add_message(self, message, sender="user"):
        def safe_get_color(theme_dict, key, default):
            try:
                return theme_dict[key][0]
            except (KeyError, IndexError, TypeError):
                return default

        # Determine colors from the current theme
        if sender == "user":
            ctk_button_theme = ctk.ThemeManager.theme.get("CTkButton", {})
            bg_color = safe_get_color(ctk_button_theme, "fg_color", "#0078D7")
            text_color = safe_get_color(ctk_button_theme, "text_color", "#FFFFFF")
            hover_color = safe_get_color(ctk_button_theme, "hover_color", "#005A9E")
            pack_anchor = "e"
            pack_padx = (50, 10) # More padding on left for user
        else:
            ctk_segmented_theme = ctk.ThemeManager.theme.get("CTkSegmentedButton", {})
            ctk_button_theme = ctk.ThemeManager.theme.get("CTkButton", {})
            bg_color = safe_get_color(ctk_segmented_theme, "selected_color", "#A0A0A0")
            text_color = safe_get_color(ctk_button_theme, "text_color", "#F0F0F0")
            hover_color = safe_get_color(ctk_segmented_theme, "selected_hover_color", "#909090")
            pack_anchor = "w"
            pack_padx = (10, 50) # More padding on right for AI

        bubble_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        bubble_frame.pack(fill=tk.X, padx=pack_padx, pady=2, anchor=pack_anchor) # Less pady between bubbles

        msg_label = ctk.CTkLabel(bubble_frame, text=message,
                                 bg_color=bg_color, text_color=text_color,
                                 font=("Segoe UI", 12), wraplength=400, justify=tk.LEFT,
                                 corner_radius=10, padx=15, pady=10) # Apply corner_radius
        msg_label.pack(side=tk.LEFT if sender=="ai" else tk.RIGHT, expand=False, fill=tk.BOTH)

        # Hover effects for dynamic feel
        msg_label.bind("<Enter>", lambda e: msg_label.configure(bg_color=hover_color))
        msg_label.bind("<Leave>", lambda e: msg_label.configure(bg_color=bg_color))

        # Auto-scroll to the bottom
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def add_image_message(self, image_path, sender="ai"):
        try:
            full_image_path = resource_path(image_path)
            img = PIL.Image.open(full_image_path)
            max_width = 400
            max_height = 300
            img.thumbnail((max_width, max_height), PIL.Image.Resampling.LANCZOS)
            imgtk = PIL.ImageTk.PhotoImage(img)

            bubble_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
            if sender == "user":
                pack_anchor = "e"
                pack_padx = (50, 10)
            else:
                pack_anchor = "w"
                pack_padx = (10, 50)

            bubble_frame.pack(fill=tk.X, padx=pack_padx, pady=2, anchor=pack_anchor)

            img_label = ctk.CTkLabel(bubble_frame, image=imgtk, text="") # Use CTkLabel
            img_label.image = imgtk
            img_label.pack(anchor=pack_anchor)

            self.chat_canvas.update_idletasks()
            self.chat_canvas.yview_moveto(1.0)
        except Exception as e:
            self.log_to_chat(f"Error displaying image: {e}")


    def speak(self, text):
        self.queue.put(("add_message", {"message": text, "sender": "ai"})) # Also display what Viki says
        viki.speak(text)

    def listen_loop(self):
        while not self.stop_event.is_set():
            try:
                # Add a message to indicate listening
                self.queue.put(("update_status", "Listening..."))
                self.queue.put(("update_indicator", "green"))
                query = viki.recognize_speech()
                self.queue.put(("update_status", "Processing..."))
                self.queue.put(("update_indicator", "orange")) # Change color during processing
                if query:
                    self.queue.put(("add_message", {"message": query, "sender": "user"}))
                    # Perform task and get response if any
                    viki.perform_task(query)
                self.queue.put(("update_status", "Idle"))
                self.queue.put(("update_indicator", "gray"))

            except sr.UnknownValueError:
                self.queue.put(("add_message", {"message": "Sorry, I didn't catch that.", "sender": "ai"}))
                self.queue.put(("update_status", "Idle"))
                self.queue.put(("update_indicator", "gray"))
            except sr.RequestError as e:
                self.queue.put(("add_message", {"message": f"Could not request results; {e}", "sender": "ai"}))
                self.queue.put(("update_status", "Idle"))
                self.queue.put(("update_indicator", "gray"))
            except Exception as e:
                self.queue.put(("add_message", {"message": f"An unexpected error occurred during listening: {e}", "sender": "ai"}))
                self.queue.put(("update_status", "Idle"))
                self.queue.put(("update_indicator", "gray"))
            time.sleep(0.1)


    def video_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.queue.put(("log_to_chat", "Error: Cannot open webcam. Make sure it's connected and not in use."))
            self.video_mode = False
            self.queue.put(("update_video_button_text", "Toggle Video Mode"))
            self.queue.put(("update_record_buttons_state", "disabled"))
            self.queue.put(("update_capture_button_state", "disabled"))
            self.queue.put(("hide_video_label", None)) # Hide label if webcam fails
            return

        # Ensure video_label is shown when video mode starts
        self.queue.put(("show_video_label", None))
        self.queue.put(("hide_indicator_canvas", None)) # Hide indicator if video is showing

        while self.video_mode and not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                self.queue.put(("log_to_chat", "Failed to grab frame."))
                break
            # Resize frame to 640x480 for display and recording consistency
            frame_resized = cv2.resize(frame, (640, 480))
            cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            self.current_frame = cv2image # Store current frame for photo capture

            # Display frame on Tkinter label
            pil_image = PIL.Image.fromarray(cv2image)
            imgtk = PIL.ImageTk.PhotoImage(image=pil_image)
            self.queue.put(("update_video_frame", imgtk)) # Use queue for thread-safe update

            if self.recording and self.video_writer:
                self.video_writer.write(frame_resized) # Write BGR frame

            time.sleep(0.03) # ~30 fps
        cap.release()
        self.queue.put(("hide_video_label", None)) # Hide label when video stops
        self.queue.put(("show_indicator_canvas", None)) # Show indicator when video stops
        if self.recording:
            self.queue.put(("stop_recording_via_queue", None)) # Signal to stop recording
        self.queue.put(("update_video_button_text", "Toggle Video Mode"))
        self.queue.put(("update_record_buttons_state", "disabled"))
        self.queue.put(("update_capture_button_state", "disabled"))


    def process_queue(self):
        while True:
            try:
                item = self.queue.get_nowait()
                action = item[0]
                data = item[1]

                if action == "log_to_chat":
                    self.add_message(data, sender="ai") # Always from AI for system messages
                elif action == "add_message":
                    self.add_message(data["message"], data["sender"])
                elif action == "update_status":
                    self.update_status(data)
                elif action == "update_indicator":
                    self.update_indicator(data)
                elif action == "update_video_button_text":
                    self.btn_video.configure(text=data)
                elif action == "update_record_buttons_state":
                    self.btn_start_record.configure(state=data)
                    self.btn_stop_record.configure(state="normal" if data=="normal" else "disabled")
                elif action == "update_capture_button_state":
                    self.btn_capture_photo.configure(state=data)
                elif action == "update_video_frame":
                    self.video_label.imgtk = data # Update image on main thread
                    self.video_label.configure(image=data)
                elif action == "show_video_label":
                    self.video_label.grid() # Show the video label
                elif action == "hide_video_label":
                    self.video_label.grid_remove() # Hide the video label
                elif action == "show_indicator_canvas":
                    self.indicator_canvas.grid() # Show the indicator
                elif action == "hide_indicator_canvas":
                    self.indicator_canvas.grid_remove() # Hide the indicator
                elif action == "stop_recording_via_queue":
                    self.stop_recording() # Call stop_recording on main thread

            except queue.Empty:
                break
        self.root.after(100, self.process_queue)


    def send_command(self, event=None):
        command = self.entry.get().strip()
        if command:
            self.add_message(command, sender="user")
            self.entry.delete(0, tk.END)
            # Perform task in a separate thread to keep UI responsive
            threading.Thread(target=viki.perform_task, args=(command,), daemon=True).start()
            self.update_status("Processing command...")
            self.update_indicator("orange")


    def toggle_video_mode(self):
        self.video_mode = not self.video_mode
        if self.video_mode:
            self.btn_video.configure(text="Stop Video Mode")
            self.stop_event.clear()
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()
            self.btn_start_record.configure(state="normal")
            self.btn_capture_photo.configure(state="normal")
            self.log_to_chat("Video mode started.")
        else:
            self.btn_video.configure(text="Toggle Video Mode")
            self.stop_event.set()
            self.btn_start_record.configure(state="disabled")
            self.btn_stop_record.configure(state="disabled")
            self.btn_capture_photo.configure(state="disabled")
            if self.recording:
                self.stop_recording()
            self.log_to_chat("Video mode stopped.")


    def bind_button_sounds(self):
        def play_click(event=None): # Event is optional as sometimes bound without it
            try:
                # Play sound only if the sound file exists
                if os.path.exists(self.click_sound_path):
                    winsound.PlaySound(self.click_sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    print(f"Warning: Click sound file not found at {self.click_sound_path}")
            except Exception as e:
                print(f"Error playing click sound: {e}") # Debugging
                pass # Ignore sound errors

        # Iterate through all widgets and bind them
        def bind_recursively(widget):
            if isinstance(widget, ctk.CTkButton) or isinstance(widget, tk.Button):
                widget.bind("<Button-1>", play_click)
            for child in widget.winfo_children():
                bind_recursively(child)

        bind_recursively(self.root) # Start binding from the root window


    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Light":
            ctk.set_appearance_mode("Dark")
            self.btn_toggle_theme.configure(text="Switch to Light Mode")
        else:
            ctk.set_appearance_mode("Light")
            self.btn_toggle_theme.configure(text="Switch to Dark Mode")
        # Update Treeview style to match new theme colors
        self._setup_treeview_style()


    def start_recording(self):
        if not self.video_mode or self.recording:
            return
        fourcc = None
        ext = self.video_format_var.get()
        # Define the output path for recordings
        output_dir = "recordings"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = int(time.time())
        filename = os.path.join(output_dir, f"viki_recording_{timestamp}.{ext}")

        if ext == "mp4":
            fourcc = cv2.VideoWriter_fourcc(*"mp4v") # For .mp4
        elif ext == "avi":
            fourcc = cv2.VideoWriter_fourcc(*"XVID") # For .avi
        else:
            self.log_to_chat(f"Unsupported video format: {ext}")
            return
        
        # Get frame width and height from the captured frame
        if self.current_frame is not None:
            height, width, _ = self.current_frame.shape
        else:
            # Fallback if no frame is available (shouldn't happen if video_mode is active)
            width, height = 640, 480 # Default to 640x480

        self.video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (width, height))
        if not self.video_writer.isOpened():
            self.log_to_chat("Failed to open video writer. Check codecs or file path permissions.")
            self.video_writer = None
            return
        self.recording = True
        self.btn_start_record.configure(state="disabled")
        self.btn_stop_record.configure(state="normal")
        self.log_to_chat(f"Recording started: {filename}")

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        self.btn_start_record.configure(state="normal")
        self.btn_stop_record.configure(state="disabled")
        self.log_to_chat("Recording stopped.")

    def capture_photo(self):
        if self.current_frame is None:
            self.log_to_chat("No video frame available to capture photo.")
            return
        try:
            output_dir = "photos"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            timestamp = int(time.time())
            filename = os.path.join(output_dir, f"viki_photo_{timestamp}.png")
            # Convert RGB (PIL) to BGR (OpenCV) for imwrite
            cv2.imwrite(filename, cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR))
            self.log_to_chat(f"Photo captured and saved as {filename}")
        except Exception as e:
            self.log_to_chat(f"Failed to capture photo: {e}")


# --- Main Application Entry Point ---

def main():
    try:
        print("Starting Viki UI...")

        # Initialize a temporary Tkinter root for message boxes, then hide it.
        temp_tk_root = tk.Tk()
        temp_tk_root.withdraw()

        if not check_and_install_modules_ui():
            temp_tk_root.destroy()
            sys.exit()

        temp_tk_root.destroy()

        # Play opening video splash screen (blocking) - This should come AFTER module checks
        try:
            play_opening_video("jarvis/VIKI_opening.mp4")
        except Exception as e:
            print(f"Warning: Could not play opening video splash screen. Error: {e}")

        root = ctk.CTk()
        app = VikiUI(root)

        # Opening fade-in animation
        def fade_in(window, alpha=0.0, step=0.05):
            alpha += step
            if alpha > 1.0:
                alpha = 1.0
            window.attributes("-alpha", alpha)
            if alpha < 1.0:
                window.after(50, fade_in, window, alpha, step)

        root.attributes("-alpha", 0.0)
        fade_in(root)

        # Play opening sound asynchronously
        def play_opening_sound():
            try:
                winsound.PlaySound("SystemStart", winsound.SND_ALIAS)
            except Exception as e:
                print(f"Warning: Could not play system start sound: {e}")

        threading.Thread(target=play_opening_sound, daemon=True).start()

        # Handle window close protocol
        root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_listening(), app.stop_recording(), root.destroy()))
        root.mainloop()
        print("Viki UI closed.")
    except Exception as e:
        print(f"Error starting Viki UI: {e}")

if __name__ == "__main__":
    main()