import os
import time
import subprocess
import sys
import urllib.request
import zipfile
import platform

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

# RTSP Stream URL and Credentials
rtsp_url = "rtsp://gate-2:node@123@10.1.58.77/stream1"
output_dir = "audio_chunks"

# Create directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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
        time.sleep(1)  # Wait 1 second before starting the next recording

if __name__ == "__main__":
    extract_audio(rtsp_url, output_dir)
