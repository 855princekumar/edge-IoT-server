import os
import subprocess
import sys
import urllib.request
import zipfile
import platform
import threading
import time
import wave
import numpy as np
import matplotlib.pyplot as plt
import csv

# List of required dependencies
REQUIRED_DEPENDENCIES = [
    "opencv-python",
    "ffmpeg-python",
    "pydub",
    "librosa",
    "numpy",
    "matplotlib",
]

# Function to check if a package is installed
def is_package_installed(package):
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

# Function to install required packages
def install_package(package):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing {package}. Trying with --break-system-packages flag...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", package], check=True)

# Function to install all required dependencies
def install_dependencies():
    for package in REQUIRED_DEPENDENCIES:
        if not is_package_installed(package):
            print(f"{package} not found. Installing {package}...")
            install_package(package)
        else:
            print(f"{package} is already installed.")

# Function to check if ffmpeg is installed
def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

# Function to download and install ffmpeg
def install_ffmpeg():
    system = platform.system().lower()
    if system == 'windows':
        print("FFmpeg not found. Installing FFmpeg for Windows...")
        ffmpeg_url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-release-essentials.zip'
        install_dir = os.path.join(os.getcwd(), 'ffmpeg')
        os.makedirs(install_dir, exist_ok=True)

        # Download ffmpeg zip
        zip_file_path = os.path.join(install_dir, 'ffmpeg.zip')
        urllib.request.urlretrieve(ffmpeg_url, zip_file_path)

        # Extract the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)

        # Remove the zip file after extraction
        os.remove(zip_file_path)

        # Add ffmpeg to the system path
        ffmpeg_bin_path = os.path.join(install_dir, 'ffmpeg-*-essentials_build', 'bin')
        os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

        print(f"FFmpeg installed successfully and added to PATH from {ffmpeg_bin_path}.")
        print("Please restart the script to use ffmpeg.")
    else:
        print("FFmpeg installation is only automated for Windows. Please install it manually on other platforms.")
        sys.exit(1)

# Check if ffmpeg is installed, if not, install it
if not is_ffmpeg_installed():
    install_ffmpeg()

# Install required dependencies
install_dependencies()

# RTSP Stream URL and Credentials
rtsp_url = "rtsp://gate-2:node@123@10.1.58.77/stream1"
output_dir = "audio_chunks"
csv_log_file = "audio_chunks/noise_level_log.csv"

# Create directories if they don't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Initialize CSV logging
if not os.path.exists(csv_log_file):
    with open(csv_log_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Noise_Level'])

# Function to calculate RMS for noise level
def calculate_rms(audio_file):
    with wave.open(audio_file, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        samples = np.frombuffer(frames, dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(samples)))
    return rms

# Function to plot noise level graph
def plot_noise_level(noise_levels, timestamps, output_dir):
    plt.figure()
    plt.plot(timestamps, noise_levels, label='Noise Level (RMS)', color='blue')
    plt.xlabel('Time (Seconds)')
    plt.ylabel('Noise Level (RMS)')
    plt.title('Noise Level Over Time')
    plt.legend()
    
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    graph_path = os.path.join(output_dir, f"noise_level_graph_{timestamp}.png")
    plt.savefig(graph_path)
    plt.close()

# Function to append data to CSV
def log_noise_level(timestamp, noise_level):
    with open(csv_log_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, noise_level])

# Function to extract audio and save it in 1-minute chunks
def extract_audio(rtsp_url, output_dir):
    while True:
        # Get the current timestamp for naming the file
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(output_dir, f"audio_{timestamp}.wav")
        
        print(f"Recording started at {timestamp}, saving to {output_file}")
        
        # Use ffmpeg to capture 1 minute of audio from RTSP stream
        subprocess.run([
            "ffmpeg", "-i", rtsp_url, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "44100",
            "-t", "60", output_file
        ])
        
        print(f"Audio saved to {output_file}")
        
        # Analyze and log the noise level
        noise_level = calculate_rms(output_file)
        print(f"Noise Level (RMS): {noise_level}")
        
        # Log the noise level to CSV
        timestamp_for_csv = time.strftime("%Y-%m-%d %H:%M:%S")
        log_noise_level(timestamp_for_csv, noise_level)
        
        # Plot the graph (in a separate thread)
        threading.Thread(target=plot_noise_level, args=([noise_level], [timestamp_for_csv], output_dir)).start()

        # Wait 1 second before starting the next recording
        time.sleep(1)

if __name__ == "__main__":
    extract_audio(rtsp_url, output_dir)
