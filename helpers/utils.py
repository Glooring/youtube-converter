# helpers/utils.py

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from pytubefix import YouTube, Playlist

import os
import sys

def resource_path(relative_path):
    """
    Returnează calea absolută către resursa specificată, indiferent dacă rulăm
    din surse sau din executabilul PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Aplicația este congelată: sys._MEIPASS este directorul temporar ce conține resursele
        base_path = sys._MEIPASS
    else:
        # În modul dezvoltare, presupunem că acest fișier se află în <project_root>/helpers,
        # așa că directorul proiectului este folderul părinte al folderului helpers.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

def get_token_file_path():
    # Deoarece la build folosim --add-data "helpers/token_file/token_file.json;helpers/token_file"
    # iar în structura sursă token_file.json se află în <project_root>/helpers/token_file/token_file.json,
    # apelăm resource_path cu calea relativă de la directorul proiectului.
    return resource_path(os.path.join('helpers', 'token_file', 'token_file.json'))

def get_ffmpeg_path():
    return resource_path(os.path.join('helpers', 'ffmpeg', 'ffmpeg.exe'))


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
    if messagebox.askyesno(
        "Success",
        f"Download completed successfully. The file(s) are located at {file_path}.\n\nDo you want to open the file location?"
    ):
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
        directory = os.path.dirname(file_path)
        subprocess.run(['xdg-open', directory])

def is_youtube_link_valid(url):
    """
    Returns:
      - "valid": if the link is a valid YouTube video
      - "invalid_regex": if there's a known regex error
      - "invalid_failed": if something else went wrong
    """
    try:
        _ = YouTube(
            url,
            client='WEB_EMBEDDED_PLAYER',
            use_po_token=True,
            token_file= get_token_file_path()
        )
        return "valid"
    except Exception as e:
        if "regex" in str(e):
            return "invalid_regex"
        else:
            return "invalid_failed"

def is_youtube_playlist_link_valid(url):
    try:
        _ = Playlist(
            url,
            client='WEB_EMBEDDED_PLAYER',
            use_po_token=True,
            token_file= get_token_file_path()
        )
        return "valid"
    except Exception as e:
        if "regex" in str(e):
            return "invalid_regex"
        else:
            return "invalid_failed"

# Toast logic to show a quick message under a button
current_toast = None
def show_toast(root, message, button):
    global current_toast
    if current_toast is not None:
        current_toast.destroy()

    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    current_toast = toast

    label = tk.Label(toast, text=message, bg="lightyellow", relief=tk.SOLID, bd=1, padx=5, pady=2)
    label.pack(expand=True, fill=tk.BOTH)

    toast.update_idletasks()
    toast_width = label.winfo_reqwidth() + 10

    button_x = button.winfo_rootx() + (button.winfo_width() // 2) - (toast_width // 2)
    button_y = button.winfo_rooty() + button.winfo_height()
    toast.geometry(f"{toast_width}x30+{button_x}+{button_y}")

    if hasattr(toast, "timer"):
        root.after_cancel(toast.timer)
    toast.timer = toast.after(1300, lambda: destroy_toast(toast))

def destroy_toast(toast):
    global current_toast
    if toast == current_toast:
        toast.destroy()
        current_toast = None
