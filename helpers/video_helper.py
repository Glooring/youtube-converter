# helpers/video_helper.py

import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from pytubefix import YouTube
from helpers.utils import sanitize_filename, get_ffmpeg_path, get_token_file_path, show_success_message

# ----------------- Video Download Functions -----------------
def get_available_resolutions(youtube_link):
    try:
        yt = YouTube(
            youtube_link,
            client='WEB_EMBEDDED_PLAYER',
            use_po_token=True,
            token_file= get_token_file_path()
        )
        video_streams = yt.streams.filter(file_extension='mp4', progressive=False).order_by('resolution').desc()

        unique_resolutions = []
        filtered_streams = []

        for stream in video_streams:
            if stream.resolution not in unique_resolutions:
                unique_resolutions.append(stream.resolution)
                filtered_streams.append(stream)

        return unique_resolutions, filtered_streams

    except Exception as e:
        return str(e), []

def download_video(youtube_link, selected_stream, output_dir, progress_var, progress_text_widget):
    try:
        yt = YouTube(
            youtube_link,
            client='WEB_EMBEDDED_PLAYER',
            use_po_token=True,
            token_file= get_token_file_path()
        )
        sanitized_title = sanitize_filename(yt.title)
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Downloading video...\n")
        progress_text_widget.config(state=tk.DISABLED)
        progress_var.set(50)

        video_file = selected_stream.download(output_path=output_dir, filename=f"{sanitized_title}_video.mp4")
        progress_var.set(80)
        return video_file
    except Exception as e:
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Download failed: {e}\n")
        progress_text_widget.config(state=tk.DISABLED)
        return str(e)

def download_audio(youtube_link, output_dir, progress_var, progress_text_widget):
    try:
        yt = YouTube(
            youtube_link,
            client='WEB_EMBEDDED_PLAYER',
            use_po_token=True,
            token_file= get_token_file_path()
        )

        # Get the audio stream with the highest available bitrate
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Downloading audio...\n")
        progress_text_widget.config(state=tk.DISABLED)
        progress_var.set(30)

        sanitized_title = sanitize_filename(yt.title)
        audio_file = audio_stream.download(output_path=output_dir, filename=f"{sanitized_title}_audio")
        progress_var.set(60)

        return audio_file
    except Exception as e:
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Download failed: {e}\n")
        progress_text_widget.config(state=tk.DISABLED)
        return str(e)

def merge_video_and_audio_simple(video_file, audio_file, output_file, progress_text_widget):
    try:
        normalized_mp4_file = os.path.normpath(output_file) 
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Merging video and audio...\n")
        progress_text_widget.config(state=tk.DISABLED)
        
        ffmpeg_path = get_ffmpeg_path()
        command = f'"{ffmpeg_path}" -y -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}"'
        
        subprocess.run(command, shell=True, check=True)
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Merging successful.\n")
        progress_text_widget.config(state=tk.DISABLED)

        # Delete the temporary video and audio files
        os.remove(video_file)
        os.remove(audio_file)
        
        normalized_mp4_file = os.path.normpath(normalized_mp4_file)
        return normalized_mp4_file
    except Exception as e:
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Merging failed: {e}\n")
        progress_text_widget.config(state=tk.DISABLED)

def start_process_video(youtube_link, resolution_choice, output_dir, progress_var, progress_text_widget, loading_window):
    resolutions, video_streams = get_available_resolutions(youtube_link)
    if isinstance(resolutions, str):
        messagebox.showerror("Error", f"Failed to get resolutions: {resolutions}")
        loading_window.destroy()
        return

    selected_stream = video_streams[resolution_choice]
    selected_resolution = resolutions[resolution_choice]

    video_file = download_video(youtube_link, selected_stream, output_dir, progress_var, progress_text_widget)
    if isinstance(video_file, str) and "failed" in video_file.lower():
        messagebox.showerror("Error", f"Failed to download video: {video_file}")
        loading_window.destroy()
        return

    audio_file = download_audio(youtube_link, output_dir, progress_var, progress_text_widget)
    if isinstance(audio_file, str) and "failed" in audio_file.lower():
        messagebox.showerror("Error", f"Failed to download audio: {audio_file}")
        loading_window.destroy()
        return

    from pytubefix import YouTube as YTCheck  # local import to avoid confusion
    title_yt = YTCheck(
        youtube_link,
        client='WEB_EMBEDDED_PLAYER',
        use_po_token=True,
        token_file= get_token_file_path()
    ).title
    
    output_file = os.path.join(output_dir, f"{sanitize_filename(title_yt)}_{selected_resolution}.mp4")
    merged_file = merge_video_and_audio_simple(video_file, audio_file, output_file, progress_text_widget)

    progress_var.set(100)
    progress_text_widget.config(state=tk.NORMAL)
    progress_text_widget.insert(tk.END, "Download Complete!\n")
    loading_window.title("Finished")
    progress_text_widget.config(state=tk.DISABLED)

    progress_text_widget.config(state=tk.NORMAL)
    progress_text_widget.insert(tk.END, f"File saved to: {merged_file}\n")
    progress_text_widget.config(state=tk.DISABLED)
    loading_window.update_idletasks()

    show_success_message(merged_file)

def get_highest_resolution(youtube_link):
    try:
        yt = YouTube(
            youtube_link,
            client='WEB_EMBEDDED_PLAYER',
            use_po_token=True,
            token_file= get_token_file_path()
        )
        video_streams = yt.streams.filter(file_extension='mp4').order_by('resolution').desc()
        highest_resolution = video_streams.first()
        return highest_resolution
    except Exception:
        return None
