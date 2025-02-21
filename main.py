import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread
import os
from pytubefix import YouTube

# Import helper functions
from helpers.utils import (
    sanitize_filename,
    center_window,
    is_youtube_link_valid,
    is_youtube_playlist_link_valid,
    show_toast,
    get_token_file_path
)
from helpers.audio_helper import (
    start_download_audio,
)
from helpers.playlist_helper import (
    start_download_playlist,
)
from helpers.video_helper import (
    get_available_resolutions,
    start_process_video,
)

# ----------------- Main Application Window -----------------

def on_closing():
    window.destroy()

# Function to handle the audio download button
def run_audio_script():
    global result_label_audio
    root = tk.Toplevel(window)
    root.title("YouTube MP3 Downloader")
    root.geometry("400x130")
    center_window(root, 400, 130)

    tk.Label(root, text="Enter the YouTube link:").pack(pady=10)
    entry = tk.Entry(root, width=50)
    entry.pack(pady=5)

    tk.Button(root, text="Download", command=lambda: on_submit_audio(entry, root)).pack(pady=10)

    result_label_audio = tk.Label(root, text="")
    result_label_audio.pack(pady=10)

def on_submit_audio(entry, parent_window):
    youtube_link = entry.get()
    if youtube_link:
        if is_youtube_link_valid(youtube_link) != "valid":
            messagebox.showerror("Invalid Link", "The provided YouTube link is invalid. Please enter a valid link.")
            return
        try:
            yt = YouTube(
                youtube_link,
                client='WEB_EMBEDDED_PLAYER',
                use_po_token=True,
                token_file= get_token_file_path()
            )
            sanitized_title = sanitize_filename(yt.title)
        except Exception:
            messagebox.showerror("Invalid Link", "The provided YouTube link is invalid. Please enter a valid link.")
            return

        initial_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        output_dir = filedialog.askdirectory(initialdir=initial_dir, title="Select Download Folder", parent=parent_window)

        if not output_dir:
            return

        mp3_file_path = os.path.join(output_dir, f"{sanitized_title}.mp3")

        override = True
        if os.path.exists(mp3_file_path):
            should_override = messagebox.askyesno("File Exists", f"'{sanitized_title}.mp3' already exists. Do you want to override it?", parent=parent_window)
            if not should_override:
                return
            else:
                override = True

        # Create the loading window
        loading_window = tk.Toplevel(parent_window)
        loading_window.title("Processing")
        loading_window.geometry("400x300")
        loading_window.transient(parent_window)
        loading_window.grab_set()
        center_window(loading_window, 400, 300)

        progress_var = tk.IntVar()

        main_frame = tk.Frame(loading_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=0)

        text_frame = tk.Frame(main_frame)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        progress_text_widget = tk.Text(text_frame, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
        progress_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=progress_text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        progress_text_widget.config(yscrollcommand=scrollbar.set)

        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(side=tk.BOTTOM, fill=tk.X)

        progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
        progress_bar.pack(side=tk.BOTTOM, pady=(15, 15))

        thread = Thread(target=start_download_audio, args=(youtube_link, output_dir, progress_var, progress_text_widget, loading_window, override))
        thread.start()
    else:
        messagebox.showerror("Error", "Please enter a valid YouTube link.")

# Function to handle the playlist download button
def run_playlist_script():
    global result_label_playlist, start_button_playlist
    root = tk.Toplevel(window)
    root.title("YouTube Playlist Downloader")
    root.geometry("400x200")
    center_window(root, 400, 200)

    tk.Label(root, text="Enter the YouTube playlist link:").pack(pady=10)

    entry = tk.Entry(root, width=50)
    entry.pack(pady=5)

    download_type_var = tk.IntVar(value=-1)
    tk.Radiobutton(root, text="Download audio as .mp3", variable=download_type_var, value=1).pack(anchor=tk.W)
    tk.Radiobutton(root, text="Download video at the highest resolution", variable=download_type_var, value=2).pack(anchor=tk.W)

    start_button_playlist = tk.Button(root, text="Start Download", command=lambda: on_submit_playlist(entry, root, download_type_var))
    start_button_playlist.pack(pady=10)

    result_label_playlist = tk.Label(root, text="")
    result_label_playlist.pack(pady=10)

def on_submit_playlist(entry, parent_window, download_type_var):
    youtube_link = entry.get()
    download_type = download_type_var.get()

    if download_type == -1:
        show_toast(parent_window, "Please select an option", start_button_playlist)
        return

    if youtube_link:
        if is_youtube_playlist_link_valid(youtube_link) != "valid":
            show_toast(parent_window, "Please enter a valid YouTube playlist link", start_button_playlist)
            return

        initial_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        output_dir = filedialog.askdirectory(initialdir=initial_dir, title="Select Download Folder", parent=parent_window)

        if not output_dir:
            show_toast(parent_window, "Download canceled.", start_button_playlist)
            return

        loading_window = tk.Toplevel(parent_window)
        loading_window.title("Processing")
        loading_window.geometry("400x300")
        loading_window.transient(parent_window)
        loading_window.grab_set()
        center_window(loading_window, 400, 300)

        progress_var = tk.IntVar()

        main_frame = tk.Frame(loading_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=0)

        text_frame = tk.Frame(main_frame)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        progress_text_widget = tk.Text(text_frame, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
        progress_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=progress_text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        progress_text_widget.config(yscrollcommand=scrollbar.set)

        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(side=tk.BOTTOM, fill=tk.X)

        progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
        progress_bar.pack(side=tk.BOTTOM, pady=(15, 15))

        thread = Thread(target=start_download_playlist, args=(youtube_link, output_dir, progress_var, progress_text_widget, loading_window, download_type))
        thread.start()
    else:
        show_toast(parent_window, "Please enter a YouTube playlist link", start_button_playlist)

# Function to handle the video download button
def run_video_script():
    global result_label_video
    root = tk.Toplevel(window)
    root.title("YouTube Video Downloader")
    root.geometry("400x130")
    center_window(root, 400, 130)

    tk.Label(root, text="Enter the YouTube link:").pack(pady=10)

    entry = tk.Entry(root, width=50)
    entry.pack(pady=5)

    tk.Button(root, text="Start Process", command=lambda: on_submit_video(entry, root)).pack(pady=10)

    result_label_video = tk.Label(root, text="")
    result_label_video.pack(pady=10)

def on_submit_video(entry, parent_window):
    youtube_link = entry.get()
    if youtube_link:
        if is_youtube_link_valid(youtube_link) != "valid":
            messagebox.showerror("Invalid Link", "The provided YouTube link is invalid. Please enter a valid link.", parent=parent_window)
            return

        initial_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        output_dir = filedialog.askdirectory(initialdir=initial_dir, title="Select Download Folder", parent=parent_window)

        if not output_dir:
            result_label_video.config(text="Download canceled.")
            return

        resolutions, video_streams = get_available_resolutions(youtube_link)
        if isinstance(resolutions, str):
            messagebox.showerror("Error", f"Failed to get resolutions: {resolutions}")
            return

        resolution_window = tk.Toplevel(parent_window)
        resolution_window.title("Select Resolution")

        num_resolutions = len(resolutions)
        button_height = 40
        resolution_window_height = max(150, 30 * num_resolutions + button_height + 20)

        resolution_window.geometry(f"300x{resolution_window_height}")
        center_window(resolution_window, 300, resolution_window_height)

        tk.Label(resolution_window, text="Select the resolution:").pack(pady=10)

        resolution_var = tk.IntVar(value=0)
        for idx, resolution in enumerate(resolutions):
            tk.Radiobutton(resolution_window, text=resolution, variable=resolution_var, value=idx).pack(anchor="w")

        def on_resolution_select():
            resolution_choice = resolution_var.get()
            resolution_window.destroy()

            loading_window = tk.Toplevel(parent_window)
            loading_window.title("Processing")
            loading_window.geometry("400x300")
            loading_window.transient(parent_window)
            loading_window.grab_set()
            center_window(loading_window, 400, 300)

            progress_var = tk.IntVar()

            main_frame = tk.Frame(loading_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=0)

            text_frame = tk.Frame(main_frame)
            text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            progress_text_widget = tk.Text(text_frame, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
            progress_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(text_frame, command=progress_text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            progress_text_widget.config(yscrollcommand=scrollbar.set)

            progress_frame = tk.Frame(main_frame)
            progress_frame.pack(side=tk.BOTTOM, fill=tk.X)

            progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
            progress_bar.pack(side=tk.BOTTOM, pady=(15, 15))

            thread = Thread(target=start_process_video, args=(youtube_link, resolution_choice, output_dir, progress_var, progress_text_widget, loading_window))
            thread.start()

        tk.Button(resolution_window, text="Download", command=on_resolution_select).pack(pady=10)
    else:
        messagebox.showerror("Error", "Please enter a valid YouTube link.", parent=parent_window)

window = tk.Tk()
window.title("Download YouTube")
center_window(window, 300, 190)
window.geometry("300x190")

audio_button = tk.Button(window, text="Simple link to audio", command=run_audio_script, width=20, height=2)
audio_button.pack(pady=10)

video_button = tk.Button(window, text="Simple link to video", command=run_video_script, width=20, height=2)
video_button.pack(pady=10)

playlist_button = tk.Button(window, text="Playlist link", command=run_playlist_script, width=20, height=2)
playlist_button.pack(pady=10)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
