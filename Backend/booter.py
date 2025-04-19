import numpy as np
import cv2
import pygame
from pygame import mixer

# Initialize mixer
mixer.init()

# Define absolute paths (adjust based on your project structure)
base_dir = r"C:\Users\Asus\Desktop\Jarvisxalucard"
video_file = r"Backend\vid\vi.mp4"
audio_file = r"Backend/vid/vi2.mp3"  # Ensure this file exists in the project root or specify full path
window_name = "window"
interframe_wait_ms = 30  # Default, will adjust based on FPS

# Construct full paths
video_path = rf"{base_dir}\{video_file}"
audio_path = rf"{base_dir}\{audio_file}"

# Open video capture
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Could not open video file '{video_path}'.")
    exit()

# Get video FPS for better synchronization
fps = cap.get(cv2.CAP_PROP_FPS)
if fps > 0:
    interframe_wait_ms = int(1000 / fps)  # Adjust delay to match video FPS
else:
    print("Warning: Could not retrieve FPS, using default 30ms.")

# Set up full-screen window
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Load and play audio
try:
    mixer.music.load(audio_path)
    mixer.music.play()
except Exception as e:
    print(f"Error loading audio file '{audio_path}': {e}")
    # Optionally continue without audio
    # mixer.quit()

# Playback loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Reached end of video, exiting.")
        break

    cv2.imshow(window_name, frame)
    if cv2.waitKey(interframe_wait_ms) & 0x7F == ord('q'):
        print("Exit requested.")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
mixer.quit()  # Clean up mixer