# helpers/audio_helper.py

import os
import subprocess
import tkinter as tk
from pytubefix import YouTube
from helpers.utils import sanitize_filename, get_ffmpeg_path, show_success_message

# Function to download audio and convert to mp3
def download_audio_as_mp3(youtube_link, output_dir, progress_var, progress_text_widget, override=False):
    try:
        yt = YouTube(youtube_link)
        
        # Get the highest bitrate audio stream
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Downloading audio...\n")
        progress_text_widget.config(state=tk.DISABLED)
        progress_var.set(30)
        
        # Download the audio stream in its original format (usually .webm or .m4a)
        sanitized_title = sanitize_filename(yt.title)
        audio_file = audio_stream.download(output_path=output_dir, filename=f"{sanitized_title}_audio")
        progress_var.set(60)
        
        # Convert the downloaded audio to MP3 with a bitrate of 192kbps
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Converting to MP3...\n")
        progress_text_widget.config(state=tk.DISABLED)
        mp3_file = os.path.join(output_dir, f"{sanitized_title}.mp3")
        
        ffmpeg_path = get_ffmpeg_path()  # Get the path to the ffmpeg.exe in data\_internal\ffmpeg
        command = f'"{ffmpeg_path}" -y -i "{audio_file}" -vn -ar 44100 -ac 2 -b:a 192k "{mp3_file}"'
        
        subprocess.run(command, shell=True, check=True)
        progress_var.set(90)
        
        # Delete the original downloaded audio file
        os.remove(audio_file)
        progress_var.set(100)
        
        return mp3_file
    except Exception as e:
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Download failed: {e}\n")
        progress_text_widget.config(state=tk.DISABLED)
        return str(e)

# Function to download audio without conversion (raw format)
def download_raw_audio(youtube_link, output_dir, progress_var, progress_text_widget):
    try:
        yt = YouTube(youtube_link)
        
        # Get the highest bitrate audio stream
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Downloading raw audio...\n")
        progress_text_widget.config(state=tk.DISABLED)
        progress_var.set(30)

        # Download the audio stream in its original format
        sanitized_title = sanitize_filename(yt.title)
        file_extension = audio_stream.mime_type.split('/')[1]
        audio_file = audio_stream.download(output_path=output_dir, filename=f"{sanitized_title}.{file_extension}")
        progress_var.set(100)

        return audio_file
    except Exception as e:
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Download failed: {e}\n")
        progress_text_widget.config(state=tk.DISABLED)
        return str(e)

# Function to start the download based on user's choice (mp3 or raw)
def start_download_audio(youtube_link, output_dir, progress_var, progress_text_widget, loading_window, override=False, convert_to_mp3=True):
    if convert_to_mp3:
        audio_file = download_audio_as_mp3(youtube_link, output_dir, progress_var, progress_text_widget, override=override)
    else:
        audio_file = download_raw_audio(youtube_link, output_dir, progress_var, progress_text_widget)

    if isinstance(audio_file, str) and "failed" in audio_file.lower():
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Download failed.\n")
        progress_text_widget.config(state=tk.DISABLED)
    else:
        normalized_audio_file = os.path.normpath(audio_file)
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Download complete!\nFile saved to: {normalized_audio_file}\n")
        progress_text_widget.config(state=tk.DISABLED)
        loading_window.title("Finished")
        show_success_message(normalized_audio_file)
