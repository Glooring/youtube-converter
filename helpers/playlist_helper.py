# helpers/playlist_helper.py

import os
import subprocess
import tkinter as tk
from datetime import datetime
from pytubefix import Playlist, YouTube
from helpers.utils import sanitize_filename, get_ffmpeg_path, get_token_file_path, show_success_message
from helpers.audio_helper import download_audio_as_mp3
from helpers.video_helper import get_highest_resolution, download_video, download_audio

# ----------------- Playlist Download Functions -----------------
def download_playlist_audio(playlist_url, output_dir, progress_var, progress_text_widget):
    playlist = Playlist(
        playlist_url,
        client='WEB_EMBEDDED_PLAYER',
        use_po_token=True,
        token_file= get_token_file_path()
    )

    # Generate a timestamp in the format yyyyMMdd_HHmmss_SSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    # Create the playlist directory
    playlist_dir = os.path.join(output_dir, f"Playlist_audio_{timestamp}")
    os.makedirs(playlist_dir, exist_ok=True)

    playlist_file = os.path.join(playlist_dir, "playlist.txt")

    with open(playlist_file, 'w', encoding='utf-8') as file:
        for video in playlist.videos:
            yt_link = video.watch_url
            title = video.title
            file.write(f"{yt_link} - {title}\n")
            progress_text_widget.config(state=tk.NORMAL)
            progress_text_widget.insert(tk.END, f"Downloading audio: {title}\n")
            progress_text_widget.config(state=tk.DISABLED)

            # Download audio and convert to MP3
            mp3_file = download_audio_as_mp3(yt_link, playlist_dir, progress_var, progress_text_widget)
            if isinstance(mp3_file, Exception):
                progress_text_widget.config(state=tk.NORMAL)
                progress_text_widget.insert(tk.END, "Failed to download and convert audio.\n")
                progress_text_widget.config(state=tk.DISABLED)
                continue

    return playlist_dir

def download_playlist_video(playlist_url, output_dir, progress_var, progress_text_widget):
    playlist = Playlist(
        playlist_url,
        client='WEB_EMBEDDED_PLAYER',
        use_po_token=True,
        token_file= get_token_file_path()
    )

    # Generate a timestamp in the format yyyyMMdd_HHmmss_SSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    # Create the playlist directory
    playlist_dir = os.path.join(output_dir, f"Playlist_video_{timestamp}")
    os.makedirs(playlist_dir, exist_ok=True)

    playlist_file = os.path.join(playlist_dir, "playlist.txt")

    with open(playlist_file, 'w', encoding='utf-8') as file:
        for video in playlist.videos:
            yt_link = video.watch_url
            title = video.title
            file.write(f"{yt_link} - {title}\n")
            progress_text_widget.config(state=tk.NORMAL)
            progress_text_widget.insert(tk.END, f"Downloading video: {title}\n")
            progress_text_widget.config(state=tk.DISABLED)

            # Get the highest resolution video stream
            highest_res_stream = get_highest_resolution(yt_link)
            if highest_res_stream is None:
                progress_text_widget.config(state=tk.NORMAL)
                progress_text_widget.insert(tk.END, f"Skipping video due to resolution issues: {title}\n")
                progress_text_widget.config(state=tk.DISABLED)
                continue

            # Extract resolution (e.g., 1080p) from the stream
            resolution = highest_res_stream.resolution

            # Download video without audio
            video_file = download_video(yt_link, highest_res_stream, playlist_dir, progress_var, progress_text_widget)
            
            # Download audio
            audio_file = download_audio(yt_link, playlist_dir, progress_var, progress_text_widget)
            if isinstance(audio_file, Exception):
                progress_text_widget.config(state=tk.NORMAL)
                progress_text_widget.insert(tk.END, "Failed to download audio.\n")
                progress_text_widget.config(state=tk.DISABLED)
                continue

            # Merge video and audio with resolution in filename
            output_file = os.path.join(playlist_dir, f"{sanitize_filename(title)}_{resolution}.mp4")
            merge_video_and_audio_playlist(video_file, audio_file, output_file, progress_var, progress_text_widget)

    return playlist_dir

def start_download_playlist(youtube_link, output_dir, progress_var, progress_text_widget, loading_window, download_type):
    playlist_dir = None

    if download_type == 1:  # Audio
        playlist_dir = download_playlist_audio(youtube_link, output_dir, progress_var, progress_text_widget)
    elif download_type == 2:  # Video
        playlist_dir = download_playlist_video(youtube_link, output_dir, progress_var, progress_text_widget)

    progress_text_widget.config(state=tk.NORMAL)
    progress_text_widget.insert(tk.END, "Download Complete!\n")
    loading_window.title("Finished")
    progress_text_widget.config(state=tk.DISABLED)

    if playlist_dir:
        show_success_message(playlist_dir)


def merge_video_and_audio_playlist(video_file, audio_file, output_file, progress_var, progress_text_widget):
    try:
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, "Merging video and audio...\n")
        progress_text_widget.config(state=tk.DISABLED)
        
        ffmpeg_path = get_ffmpeg_path()
        command = f'"{ffmpeg_path}" -y -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}"'

        subprocess.run(command, shell=True, check=True)
        progress_var.set(90)
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Merging successful.\n")
        progress_text_widget.config(state=tk.DISABLED)

        # Delete the temporary video and audio files
        os.remove(video_file)
        os.remove(audio_file)
        progress_var.set(100)
        
    except Exception as e:
        progress_text_widget.config(state=tk.NORMAL)
        progress_text_widget.insert(tk.END, f"Merging failed: {e}\n")
        progress_text_widget.config(state=tk.DISABLED)
