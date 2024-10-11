import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from pytubefix import YouTube, Playlist

# Function to get the path to ffmpeg.exe
def get_ffmpeg_path():
    # Get the base directory of the executable or script
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to ffmpeg.exe inside 'ffmpeg' directory
    ffmpeg_path = os.path.join(base_path, 'ffmpeg', 'ffmpeg.exe')
    return ffmpeg_path

def sanitize_filename(filename):
    return "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename)

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def show_success_message(file_path):
    if messagebox.askyesno("Success", f"Download completed successfully. The file(s) are located at {file_path}.\n\nDo you want to open the file location?"):
        open_file_location(file_path)

def open_file_location(file_path):
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "The path does not exist.")
        return

    if os.name == 'nt':  # For Windows
        normalized_path = os.path.normpath(file_path)
        subprocess.run(['explorer', '/select,', normalized_path], shell=True)
    elif os.name == 'posix':  # For MacOS
        subprocess.run(['open', '-R', file_path])
    else:  # Assume Linux
        # Linux file managers like Nautilus do not have a direct way to highlight files.
        directory = os.path.dirname(file_path)
        subprocess.run(['xdg-open', directory])

def is_youtube_link_valid(url):
    try:
        yt = YouTube(url)
        return "valid"
    except Exception as e:
        if "regex" in str(e):
            return "invalid_regex"
        else:
            return "invalid_failed"

def is_youtube_playlist_link_valid(url):
    try:
        playlist = Playlist(url)
        title = playlist.title  # Attempt to access a playlist attribute
        return "valid"
    except Exception as e:
        if "regex" in str(e):
            return "invalid_regex"
        else:
            return "invalid_failed"
        
# Add a global variable to keep track of the current toast
current_toast = None
def show_toast(root, message, button):
    global current_toast

    # Destroy the previous toast if it exists
    if current_toast is not None:
        current_toast.destroy()

    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    current_toast = toast  # Update the global toast reference

    # Create a label to measure the required width
    label = tk.Label(toast, text=message, bg="lightyellow", relief=tk.SOLID, bd=1, padx=5, pady=2)
    label.pack(expand=True, fill=tk.BOTH)

    # Force geometry update to get the label's width
    toast.update_idletasks()
    toast_width = label.winfo_reqwidth() + 10  # Adding extra padding to the width

    # Calculate position to center the toast under the button
    button_x = button.winfo_rootx() + (button.winfo_width() // 2) - (toast_width // 2)
    button_y = button.winfo_rooty() + button.winfo_height()
    toast.geometry(f"{toast_width}x30+{button_x}+{button_y}")  # Set width dynamically based on text

    # Reset the timer and destroy the toast after 1.5 seconds
    if hasattr(toast, "timer"):
        root.after_cancel(toast.timer)  # Cancel any previous timer if it exists
    toast.timer = toast.after(1300, lambda: destroy_toast(toast))

def destroy_toast(toast):
    global current_toast
    if toast == current_toast:
        toast.destroy()
        current_toast = None
