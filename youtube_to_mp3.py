import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

def download_audio():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    
    save_path = filedialog.askdirectory(title="Select Save Folder")
    if not save_path:
        return
    
    file_name = file_name_entry.get().strip()
    if not file_name:
        messagebox.showerror("Error", "Please enter a file name")
        return
    
    status_label.config(text="Downloading...")
    
    def process():
        try:
            audio_path = os.path.join(save_path, f"{file_name}.mp4")
            mp3_path = os.path.join(save_path, f"{file_name}.mp3")
            
            # Download audio using yt-dlp
            subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", audio_path, url], check=True)
            
            # Convert to MP3 using ffmpeg
            subprocess.run(["ffmpeg", "-i", audio_path, "-q:a", "0", "-map", "a", mp3_path], check=True)
            
            os.remove(audio_path)  # Remove the original file
            
            messagebox.showinfo("Success", f"MP3 saved at: {mp3_path}")
            status_label.config(text="Download Complete!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to download or convert audio. Make sure yt-dlp and ffmpeg are installed.")
            status_label.config(text="Error occurred!")
    
    threading.Thread(target=process).start()

# Create GUI
root = tk.Tk()
root.title("YouTube Audio Downloader")
root.geometry("400x250")

frame = tk.Frame(root)
frame.pack(pady=20)

tk.Label(frame, text="Enter YouTube URL:").pack()
url_entry = tk.Entry(frame, width=50)
url_entry.pack()

tk.Label(frame, text="Enter File Name:").pack()
file_name_entry = tk.Entry(frame, width=50)
file_name_entry.pack()

download_button = tk.Button(frame, text="Download Audio", command=download_audio)
download_button.pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()