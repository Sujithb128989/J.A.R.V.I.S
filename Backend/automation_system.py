import os
import psutil
import time
import keyboard
import requests
import sys

if sys.platform == 'win32':
    import wmi
    import win32con
    import win32gui
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL

import screen_brightness_control as sbc
import pyaudio
import numpy as np
from scipy.signal import chirp
from .tts_utils import speak

def system(command):
    if command == "mute":
        keyboard.press_and_release("volume mute")
    elif command == "unmute":
        keyboard.press_and_release("volume mute")
    elif command == "volume up":
        keyboard.press_and_release("volume up")
    elif command == "volume down":
        keyboard.press_and_release("volume down")
    return

def systemstats():
    speak("calculations in progress")
    cpu_stats = str(psutil.cpu_percent())
    battery_percent = psutil.sensors_battery().percent
    memory_in_use = psutil.virtual_memory().used / (1024 ** 3)  # Convert to GB
    total_memory = psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
    final_res = f"Currently {cpu_stats} percent of CPU, {memory_in_use:.2f} GB of RAM out of total {total_memory:.2f} GB is being used. and the battery level is at {battery_percent} percent"
    print(final_res)
    speak(final_res)

def isOnline(url="https://www.google.com", timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        status_code = response.status_code

        if 200 <= status_code < 300:
            speak("Your internet is working optimally, sir.")
        else:
            speak(f"Internet check returned status code {status_code}, sir. It might not be working as expected.")

    except requests.ConnectionError:
        speak("Internet is currently down, sir. No connection could be established.")
    except requests.Timeout:
        speak("Internet check timed out, sir. The connection is too slow or unavailable.")
    except requests.RequestException as e:
        speak(f"An error occurred while checking the internet, sir. Details: {str(e)}")

def battery_Alert():
    while True:
        battery = psutil.sensors_battery()
        if battery is None:
            # This will only run on devices without a battery, so no need to speak
            break
        percentage = int(battery.percent)
        if percentage == 100:
            speak(f"Sir, the battery is fully charged at {percentage} percent. Do you need any further assistance?")
        elif percentage <= 5:
            speak(f"Sir, critical alert! The battery is at {percentage} percent. You're doomed lmao")
        elif percentage <= 10:
            speak(f"Sir, urgent warning! The battery is at {percentage} percent. Please plug in now!")
        elif percentage <= 20:
            speak(f"Sir, the battery is at {percentage} percent. Consider charging the device soon.")
        time.sleep(1200)

def check_plug():
    """Instantly detect charger plug/unplug and speak/print once per state change (Windows only)"""
    if sys.platform != 'win32':
        print("Charger plug detection is only supported on Windows.")
        return

    print("_____started___")
    battery = psutil.sensors_battery()
    if battery is None:
        print("Sir, no battery detected to monitor charging status.")
        speak("Sir, no battery detected to monitor charging status.")
        return

    previous_state = battery.power_plugged
    has_reported = False

    def wnd_proc(hwnd, msg, wparam, lparam):
        nonlocal previous_state, has_reported
        if msg == win32con.WM_POWERBROADCAST and wparam == win32con.PBT_APMPOWERSTATUSCHANGE:
            battery = psutil.sensors_battery()
            current_state = battery.power_plugged

            if current_state != previous_state:
                if current_state:
                    print("Sir, the charger has been plugged in.")
                    speak("Sir, the charger has been plugged in.")
                else:
                    print("Sir, the charger has been unplugged.")
                    speak("Sir, the charger has been unplugged.")
                previous_state = current_state
                has_reported = True
            elif has_reported:
                has_reported = False

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    wc = win32gui.WNDCLASS()
    wc.lpszClassName = "PowerMonitor"
    wc.lpfnWndProc = wnd_proc
    win32gui.RegisterClass(wc)

    hwnd = win32gui.CreateWindow(
        wc.lpszClassName,
        "Power Monitor Window",
        0, 0, 0, 0, 0, 0, 0, None, None
    )

    win32gui.PumpMessages()

def check_percentage():
    """Check and return the current battery percentage"""
    battery = psutil.sensors_battery()
    if battery is None:
        speak("Sir, no battery detected on this device.")
        return None

    percent = int(battery.percent)
    speak(f"Sir, the current battery level is {percent} percent.")
    return percent

def get_brightness_windows():
    if sys.platform != 'win32':
        return "Brightness control is only supported on Windows."
    try:
        w = wmi.WMI(namespace='wmi')
        brightness_methods = w.WmiMonitorBrightness()
        brightness_percentage = brightness_methods[0].CurrentBrightness
        return brightness_percentage
    except Exception as e:
        return f"Error: {e}"

def br():
    brightness = get_brightness_windows()
    speak(f"The Current Brightness is {brightness}%,Do you want me Increase, or Decrease the brightness levels; for you. sir?")

def increasebr(brightness):
    sbc.set_brightness(brightness)
    speak(f"The brightness has been set to {brightness}%")

def decreasebr(brightness):
    sbc.set_brightness(brightness)
    speak(f"The brightness has been set to {brightness}%")

def get_mic_health(seconds=5, initial_threshold=500):
    speak(" getting microphone acces ")
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    speak(f"Recording for {seconds} seconds...")
    time.sleep(1)

    sound_count = 0
    total_samples = 0
    noise_floor = 0
    clipping_count = 0
    signal_sum = 0
    noise_sum = 0
    freq_analysis = []

    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        volume = np.linalg.norm(data)

        freqs = np.fft.fftfreq(len(data))
        fft_spectrum = np.abs(np.fft.fft(data))
        freq_analysis.append(fft_spectrum)

        noise_floor = max(noise_floor, np.mean(np.abs(data)) * 1.5)
        dynamic_threshold = max(initial_threshold, noise_floor)

        if volume > dynamic_threshold:
            sound_count += 1
            signal_sum += volume
        else:
            noise_sum += volume

        if np.max(np.abs(data)) >= 32767:
            clipping_count += 1

        total_samples += 1

    mic_health = (sound_count / total_samples) * 100
    avg_signal = signal_sum / max(1, sound_count)
    avg_noise = noise_sum / max(1, (total_samples - sound_count))
    snr = 10 * np.log10(avg_signal / max(1, avg_noise))
    avg_clipping = (clipping_count / total_samples) * 100
    avg_fft_spectrum = np.mean(freq_analysis, axis=0)
    freq_range_coverage = np.mean(avg_fft_spectrum > np.median(avg_fft_spectrum)) * 100

    stream.stop_stream()
    stream.close()
    audio.terminate()

    speak("samples recorded sir. Now i shall dectate the results one by one")
    health_report = f'''Microphone Health (%): {mic_health},
        Average Signal to Noise Ratio (dB): {snr},
        Clipping Percentage (%): {avg_clipping},
        Frequency Range Coverage (%): {freq_range_coverage}'''

    return health_report

def michealth():
    health_metrics = get_mic_health(seconds=5)
    print(health_metrics)

def play_tone(frequency, duration=2, volume=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio_data = (tone * volume * 32767).astype(np.int16)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)
    stream.write(audio_data.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_sweep(duration=5, volume=0.5, sample_rate=44100, start_freq=20, end_freq=20000):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sweep = chirp(t, start_freq, t[-1], end_freq, method='logarithmic')
    audio_data = (sweep * volume * 32767).astype(np.int16)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)
    stream.write(audio_data.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

def speakertest():
    speak("Playing test tones...")
    health_score = 0

    speak("100 Hz tone...")
    play_tone(100, duration=2)
    time.sleep(1)
    health_score += 25

    speak(" 1000 Hz tone...")
    play_tone(1000, duration=2)
    time.sleep(1)

    speak("5000 Hz tone...")
    play_tone(5000, duration=2)
    time.sleep(1)
    health_score += 20

    speak(" 10,000 Hz tone...")
    play_tone(10000, duration=2)
    time.sleep(1)
    health_score += 15

    speak("Playing frequency sweep from 20 Hz to 20,000 Hz...")
    play_sweep(duration=5)
    time.sleep(1)
    health_score += 15

    speak("\nSpeaker health test complete.")
    speak(f"\nSpeaker Health: {health_score}%")
    print(f"\nSpeaker Health: {health_score}%")
    if health_score == 100:
        speak("The speaker is in excellent condition!")
    elif 80 <= health_score < 100:
        speak("The speaker is in good condition.")
    elif 60 <= health_score < 80:
        speak("The speaker is in average condition.")
    else:
        speak("The speaker might be in poor condition.")
