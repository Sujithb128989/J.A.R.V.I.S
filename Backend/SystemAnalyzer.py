import pygame
import psutil
import time
import random
import os
import logging
from pygame import Surface
from math import sin, cos, pi
from pathlib import Path
import subprocess
import platform
import re
import sys
import io
from contextlib import redirect_stdout

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename="jarvis_analyzer.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Fallbacks for Automation module
try:
    from Automation import speak, michealth, speakertest, systemstats
    AUTOMATION_AVAILABLE = True
    print("Automation module loaded successfully")
except ImportError:
    AUTOMATION_AVAILABLE = False
    print("Automation module not found, using fallbacks")
    def speak(text, *args, **kwargs):
        logging.warning(f"Speak function unavailable, logging instead: {text}")
        print(f"[Speak Fallback] {text}")
    def michealth():
        logging.warning("michealth unavailable, returning default")
        print("Microphone Health: N/A")
    def speakertest():
        logging.warning("speakertest unavailable, logging default")
        print("Speaker Health: N/A")
    def systemstats():
        logging.warning("systemstats unavailable, logging basic stats")
        return "CPU: N/A, Memory: N/A"

# Initialize Pygame
try:
    pygame.init()
    print("Pygame initialized successfully")
except Exception as e:
    logging.error(f"Pygame initialization failed: {e}")
    print(f"Error: Pygame failed to initialize: {e}")
    input("Press Enter to exit...")
    exit(1)

WIDTH, HEIGHT = 800, 600
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("JARVIS System Analyzer")
    print("Display set up successfully")
except Exception as e:
    logging.error(f"Display setup failed: {e}")
    print(f"Error: Display setup failed: {e}")
    input("Press Enter to exit...")
    pygame.quit()
    exit(1)

# Fonts
try:
    font = pygame.font.SysFont("monospace", 28, bold=True)
    small_font = pygame.font.SysFont("monospace", 20)
    title_text = font.render("JARVIS System Analyzer", True, (100, 200, 255))
    startup_text = small_font.render("Initializing JARVIS System Analysis...", True, (0, 150, 255))
    print("Fonts loaded successfully")
except Exception as e:
    logging.error(f"Font loading failed: {e}")
    print(f"Error: Font loading failed: {e}")
    input("Press Enter to exit...")
    pygame.quit()
    exit(1)

# JARVIS-inspired theme
JARVIS_THEME = {
    "BG_COLOR": (15, 15, 25),
    "TEXT_COLOR": (100, 200, 255),
    "ACCENT_COLOR": (0, 150, 255),
    "ERROR_COLOR": (255, 80, 80),
    "SCAN_COLOR": (0, 200, 255),
    "GRID_COLOR": (50, 100, 150, 100),
    "GLOW_COLOR": (0, 255, 255, 50)
}

# Particles
particles = []
def update_particles():
    global particles
    if len(particles) < 20 and random.random() < 0.05:
        particles.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 1.5),
                         random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), JARVIS_THEME["ACCENT_COLOR"]])
    particles = [[x + dx, y + dy, s * 0.98, dx, dy, c] for x, y, s, dx, dy, c in particles if s > 0.1]

# System stats check
def check_system_stats():
    stats = {"CPU": 0, "Memory": 0}
    try:
        stats["CPU"] = psutil.cpu_percent(interval=None)
        stats["Memory"] = psutil.virtual_memory().percent
    except Exception as e:
        logging.error(f"Error in stats: {e}")
        speak(f"Error retrieving system stats: {str(e)}")
    return stats

# Parse michealth console output
def parse_michealth(output):
    logging.debug(f"Raw michealth output: {repr(output)}")
    try:
        if isinstance(output, str) and "Microphone Health" in output:
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            logging.debug(f"Parsed michealth lines: {lines}")
            metrics = {}
            for line in lines:
                if "Microphone Health (%)" in line:
                    match = re.search(r"Microphone Health[^:]*:?\s*([\d.]+)", line)
                    if match:
                        metrics["health"] = float(match.group(1))
                elif "Signal to Noise Ratio (dB)" in line:
                    match = re.search(r"[\d.]+", line)
                    if match:
                        metrics["snr"] = float(match.group())
                elif "Clipping Percentage (%)" in line:
                    match = re.search(r"[\d.]+", line)
                    if match:
                        metrics["clipping"] = float(match.group())
                elif "Frequency Range Coverage (%)" in line:
                    match = re.search(r"[\d.]+", line)
                    if match:
                        metrics["freq_range"] = float(match.group())
            if len(metrics) == 4:
                metrics["full_text"] = output.strip()
                logging.debug(f"Parsed michealth metrics: {metrics}")
                return metrics
        logging.warning(f"Invalid michealth format: {repr(output)}")
        return {"health": 0, "snr": 0, "clipping": 0, "freq_range": 0, "full_text": "N/A"}
    except Exception as e:
        logging.error(f"Error parsing michealth: {e}")
        return {"health": 0, "snr": 0, "clipping": 0, "freq_range": 0, "full_text": f"Error: {str(e)}"}

# Parse speakertest console output
def parse_speakertest(output):
    logging.debug(f"Raw speakertest output: {repr(output)}")
    try:
        if isinstance(output, str) and "Speaker Health" in output:
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            logging.debug(f"Parsed speakertest lines: {lines}")
            metrics = {}
            for line in lines:
                if "Speaker Health" in line:
                    match = re.search(r"Speaker Health[^:]*:?\s*([\d.]+)%", line)
                    if match:
                        metrics["health"] = float(match.group(1))
            if "health" in metrics:
                metrics["full_text"] = output.strip()
                logging.debug(f"Parsed speakertest metrics: {metrics}")
                return metrics
        logging.warning(f"Invalid speakertest format: {repr(output)}")
        return {"health": 0, "full_text": "N/A"}
    except Exception as e:
        logging.error(f"Error parsing speakertest: {e}")
        return {"health": 0, "full_text": f"Error: {str(e)}"}

# Run test with console capture
def run_test_with_capture(test_func):
    output = io.StringIO()
    with redirect_stdout(output):
        test_func()
    time.sleep(12)  # Wait for speakertest's ~11-second runtime
    captured_output = output.getvalue()
    logging.debug(f"Captured output for {test_func.__name__}: {repr(captured_output)}")
    return captured_output

# Test definitions
TESTS = [
    {"name": "CPU Usage", "func": check_system_stats, "key": "CPU", "type": "percent"},
    {"name": "Memory Usage", "func": check_system_stats, "key": "Memory", "type": "percent"},
    {"name": "Microphone Health", "func": lambda: run_test_with_capture(michealth), "parser": parse_michealth, "type": "percent"},
    {"name": "Speaker Health", "func": lambda: run_test_with_capture(speakertest), "parser": parse_speakertest, "type": "percent"},
]

# Draw HUD
def draw_hud(screen, progress, results, current_test, stats):
    try:
        screen.fill(JARVIS_THEME["BG_COLOR"])
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, JARVIS_THEME["GRID_COLOR"], (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(screen, JARVIS_THEME["GRID_COLOR"], (0, y), (WIDTH, y))
        glow_surface = Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, JARVIS_THEME["GLOW_COLOR"],
                        (WIDTH // 2 - title_text.get_width() // 2 - 10, 15, title_text.get_width() + 20, title_text.get_height() + 10),
                        border_radius=5)
        screen.blit(glow_surface, (0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))
        current_text = small_font.render(f"Scanning: {current_test}", True, JARVIS_THEME["ACCENT_COLOR"])
        screen.blit(current_text, (WIDTH // 2 - current_text.get_width() // 2, 60))
        scan_line_y = int(HEIGHT * progress) % HEIGHT
        scan_surface = Surface((WIDTH, 10), pygame.SRCALPHA)
        pygame.draw.line(scan_surface, (*JARVIS_THEME["SCAN_COLOR"], 200), (0, 5), (WIDTH, 5), 5)
        screen.blit(scan_surface, (0, scan_line_y - 5))
        update_particles()
        for x, y, s, dx, dy, c in particles:
            pygame.draw.circle(screen, c, (int(x), int(y)), int(s))
        
        y_offset = 100
        for name, value, status, details in results:
            color = JARVIS_THEME["TEXT_COLOR"] if status == "OK" else JARVIS_THEME["ERROR_COLOR"]
            if name == "Microphone Health":
                texts = [
                    f"{name}: {details['health']:.1f}%",
                    f"SNR: {details['snr']:.1f} dB",
                    f"Clipping: {details['clipping']:.1f}%",
                    f"Frequency Range: {details['freq_range']:.1f}%"
                ]
                for i, text in enumerate(texts):
                    result_text = small_font.render(text, True, color)
                    screen.blit(result_text, (50, y_offset + i * 25))
                filled_width = (details['health'] / 100) * 250
                pygame.draw.rect(screen, JARVIS_THEME["ACCENT_COLOR"], (300, y_offset + 5, filled_width, 25))
                pygame.draw.rect(screen, JARVIS_THEME["TEXT_COLOR"], (300, y_offset + 5, 250, 25), 2)
                y_offset += 100
            elif name == "Speaker Health":
                text = f"{name}: {details['health']:.1f}%"
                result_text = small_font.render(text, True, color)
                screen.blit(result_text, (50, y_offset))
                filled_width = (details['health'] / 100) * 250
                pygame.draw.rect(screen, JARVIS_THEME["ACCENT_COLOR"], (300, y_offset + 5, filled_width, 25))
                pygame.draw.rect(screen, JARVIS_THEME["TEXT_COLOR"], (300, y_offset + 5, 250, 25), 2)
                y_offset += 50
            else:
                result_text = small_font.render(f"{name}: {value}", True, color)
                screen.blit(result_text, (50, y_offset))
                filled_width = (float(value.strip("%")) / 100) * 250
                pygame.draw.rect(screen, JARVIS_THEME["ACCENT_COLOR"], (300, y_offset + 5, filled_width, 25))
                pygame.draw.rect(screen, JARVIS_THEME["TEXT_COLOR"], (300, y_offset + 5, 250, 25), 2)
                y_offset += 50
        
        stats_text = small_font.render(f"CPU: {stats['CPU']:.1f}% | Mem: {stats['Memory']:.1f}%", 
                                     True, JARVIS_THEME["TEXT_COLOR"])
        screen.blit(stats_text, (50, HEIGHT - 50))
        pygame.display.flip()
    except Exception as e:
        logging.error(f"Error in draw_hud: {e}")
        speak(f"Rendering error: {str(e)}")

# Nebula in space
def draw_nebula_space(screen, angle, pulse):
    try:
        screen.fill((0, 0, 10))  # Dark space background
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            brightness = random.randint(50, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)

        for i in range(3):
            nebula_surface = Surface((150, 80), pygame.SRCALPHA)
            nebula_colors = [
                (50, 50, 150, 100),
                (100, 50, 200, 120),
                (150, 100, 255, 100),
                (200, 200, 255, 80)
            ]
            nebula_size = 80 + 15 * sin(pulse + i)
            nebula_alpha = 80 + 40 * sin(pulse + i * 2)
            for j, color in enumerate(nebula_colors):
                pygame.draw.rect(nebula_surface, (*color[:3], int(color[3] * (nebula_alpha / 255))),
                                (j * 8, j * 4, nebula_size - j * 16, nebula_size // 2 - j * 8))
            nebula_angle = angle * 0.3 + i * (2 * pi / 3)
            nebula_x = WIDTH // 2 + (150 + i * 50) * cos(nebula_angle) - nebula_surface.get_width() // 2
            nebula_y = HEIGHT // 2 + (150 + i * 50) * sin(nebula_angle) - nebula_surface.get_height() // 2
            screen.blit(nebula_surface, (int(nebula_x), int(nebula_y)))

        for _ in range(10):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.uniform(1, 3)
            color = random.choice([(100, 100, 255), (200, 150, 255), (255, 255, 200)])
            pygame.draw.circle(screen, color, (int(x), int(y)), int(size))

        pygame.display.flip()
    except Exception as e:
        logging.error(f"Error in draw_nebula_space: {e}")
        speak(f"Nebula rendering error: {str(e)}")

# Save and open results
def save_and_open_results(results):
    try:
        content = "JARVIS System Analysis Results\n\n"
        for name, value, status, details in results:
            if name == "Microphone Health":
                content += (f"{name}: {value}, Status: {status}\n"
                           f"Details:\n"
                           f"  Health: {details['health']:.1f}%\n"
                           f"  SNR: {details['snr']:.1f} dB\n"
                           f"  Clipping: {details['clipping']:.1f}%\n"
                           f"  Frequency Range: {details['freq_range']:.1f}%\n\n")
            elif name == "Speaker Health":
                content += (f"{name}: {value}, Status: {status}\n"
                           f"Details:\n"
                           f"  Health: {details['health']:.1f}%\n\n")
            else:
                content += f"{name}: {value}, Status: {status}\nDetails: {details}\n\n"
        desktop = Path.home() / "Desktop"
        file_path = desktop / "System_Analysis_Results.txt"
        file_path.write_text(content)
        speak("Analysis complete. Results saved to Desktop and opening now, sir.")
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", file_path])
        else:
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        logging.error(f"Error saving results: {e}")
        speak(f"Error saving results: {str(e)}")

# Main analyzer function
def run_system_analyzer():
    print("Starting JARVIS System Analyzer...")
    running = True
    results = []
    current_test = 0
    test_progress = 0
    test_start_time = time.time()
    stats = check_system_stats()
    last_stats_time = time.time()
    angle = 0
    pulse = 0
    clock = pygame.time.Clock()

    # Startup screen
    startup_start = pygame.time.get_ticks()
    startup_duration = 3000
    while running and (pygame.time.get_ticks() - startup_start) < startup_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                speak("System analysis terminated, sir.")
                logging.info("User closed window during startup")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    speak("System analysis terminated, sir.")
                    logging.info("User pressed Escape during startup")
                else:
                    logging.debug(f"Key pressed during startup: {event.key}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logging.debug(f"Mouse clicked at {event.pos} during startup")
            elif event.type == pygame.WINDOWFOCUSLOST:
                logging.debug("Window lost focus during startup")
            else:
                logging.debug(f"Unhandled event during startup: {event.type}")
        screen.fill(JARVIS_THEME["BG_COLOR"])
        screen.blit(startup_text, (WIDTH // 2 - startup_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        clock.tick(60)
    speak("Initiating JARVIS System Analysis, sir.")
    print("Startup screen complete")

    # Test phase
    while running and current_test < len(TESTS):
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                speak("System analysis terminated, sir.")
                logging.info("User closed window")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    speak("System analysis terminated, sir.")
                    logging.info("User pressed Escape")
                else:
                    logging.debug(f"Key pressed: {event.key}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logging.debug(f"Mouse clicked at {event.pos}")
            elif event.type == pygame.WINDOWFOCUSLOST:
                logging.debug("Window lost focus")
            else:
                logging.debug(f"Unhandled event: {event.type}")

        test_progress = min((current_time - test_start_time) / 12.0, 1.0)
        overall_progress = (current_test + test_progress) / len(TESTS)
        draw_hud(screen, overall_progress, results, TESTS[current_test]["name"], stats)

        if test_progress >= 1.0:
            try:
                test = TESTS[current_test]
                name = test["name"]
                result = test["func"]()
                if name in ["Microphone Health", "Speaker Health"]:
                    result = test["parser"](result)
                    value = f"{result['health']:.1f}%"
                    status = "OK" if result['health'] < 80 else "Warning" if result['health'] < 90 else "Error"
                    details = result
                    speak(f"{name} scan complete: {value}, Status: {status}. Detailed metrics will be printed on screen.")
                    logging.info(f"Test {name} completed: {value}, {status}, Details: {result['full_text']}")
                else:
                    value = f"{result[test['key']]:.1f}%"
                    status = "OK" if result[test['key']] < 80 else "Warning" if result['key'] < 90 else "Error"
                    details = f"{name}: {value}"
                    speak(f"{name} scan complete: {value}, Status: {status}.")
                    logging.info(f"Test {name} completed: {value}, {status}")
                results.append((name, value, status, details))
            except Exception as e:
                logging.error(f"Test {TESTS[current_test]['name']} failed: {e}")
                speak(f"Test {TESTS[current_test]['name']} failed: {str(e)}")
                results.append((TESTS[current_test]["name"], "N/A", "Error", f"Test failed: {str(e)}"))
            current_test += 1
            test_start_time = current_time

        if current_time - last_stats_time >= 1:
            stats = check_system_stats()
            last_stats_time = current_time

        clock.tick(60)

    if current_test >= len(TESTS):
        save_and_open_results(results)

    start_time = time.time()
    while running and (time.time() - start_time) < 15:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                speak("Shutting down JARVIS System Analyzer, sir.")
                logging.info("User closed window in nebula phase")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    running = False
                    speak("Shutting down JARVIS System Analyzer, sir.")
                    logging.info("User exited nebula phase")
                else:
                    logging.debug(f"Key pressed in nebula phase: {event.key}")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                logging.debug(f"Mouse clicked at {event.pos} in nebula phase")
            elif event.type == pygame.WINDOWFOCUSLOST:
                logging.debug("Window lost focus in nebula phase")
            else:
                logging.debug(f"Unhandled event in nebula phase: {event.type}")
        draw_nebula_space(screen, angle, pulse)
        angle += 0.03
        pulse += 0.08
        clock.tick(60)

    pygame.quit()
    logging.info("JARVIS System Analyzer terminated")
    print("Program terminated")

if __name__ == "__main__":
    run_system_analyzer()