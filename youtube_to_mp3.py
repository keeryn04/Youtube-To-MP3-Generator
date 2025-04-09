import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
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
    progress_bar.pack(pady=10, padx=20)
    progress_bar["value"] = 0
    progress_bar["maximum"] = 100

    def update_status_label(text):
        status_label.config(text=text)

    def process():
        try:
            audio_path = os.path.join(save_path, f"{file_name}.mp4")
            mp3_path = os.path.join(save_path, f"{file_name}.mp3")

            def update_progress(stream, process_type):
                for line in iter(stream.readline, b''):
                    line = line.decode("utf-8")
                    if process_type == "yt-dlp":
                        if "download" in line and "%" in line:
                            try:
                                percent = int(line.split('%')[0].split()[-1])
                                progress_bar["value"] = percent
                                root.update_idletasks()
                            except ValueError:
                                pass
                    elif process_type == "ffmpeg":
                        if "time=" in line:
                            try:
                                time_str = line.split("time=")[1].split()[0]
                                time_parts = time_str.split(":")
                                total_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
                                duration = 600  # 10 minutes as a rough estimate
                                percent = int((total_seconds / duration) * 100)
                                progress_bar["value"] = percent
                                root.update_idletasks()
                            except ValueError:
                                pass

            # Start yt-dlp process
            yt_dlp_process = subprocess.Popen(
                ["yt-dlp", "-f", "bestaudio", "-o", audio_path, url],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            yt_dlp_thread = threading.Thread(target=update_progress, args=(yt_dlp_process.stdout, "yt-dlp"))
            yt_dlp_thread.start()
            yt_dlp_thread.join()
            yt_dlp_process.wait()

            # Start ffmpeg process
            ffmpeg_process = subprocess.Popen(
                ["ffmpeg", "-y", "-i", audio_path, "-q:a", "0", "-map", "a", mp3_path],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            ffmpeg_thread = threading.Thread(target=update_progress, args=(ffmpeg_process.stdout, "ffmpeg"))
            ffmpeg_thread.start()
            ffmpeg_thread.join()
            ffmpeg_process.wait()

            os.remove(audio_path)

            root.after(0, update_status_label, "Download Complete!")
            root.after(0, progress_bar.pack_forget)

        except subprocess.CalledProcessError:
            root.after(0, update_status_label, "Error Occurred!")
            root.after(0, progress_bar.pack_forget)

    threading.Thread(target=process).start()

#Create GUI
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

progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()