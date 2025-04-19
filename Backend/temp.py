import pygame
import psutil
import time
import random
import os
import logging
from pygame import Surface
from math import sin, cos, pi

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename="jarvis_analyzer.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Try to import Automation functions, use fallbacks if unavailable
try:
    from Automation import speak, michealth, speakertest, systemstats
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    def speak(text, *args, **kwargs):
        logging.warning(f"Speak function unavailable, logging instead: {text}")
        print(f"[Speak Fallback] {text}")
    def michealth():
        logging.warning("michealth unavailable, returning default")
        return "Microphone Health: N/A"
    def speakertest():
        logging.warning("speakertest unavailable, logging default")
        print("[Speaker Test Fallback] Speaker Health: N/A")
    def systemstats():
        logging.warning("systemstats unavailable, logging basic stats")
        return "CPU: N/A, Memory: N/A"

# Initialize Pygame
try:
    pygame.init()
    pygame.mixer.init()
except Exception as e:
    logging.error(f"Pygame initialization failed: {e}")
    print(f"Error: Pygame failed to initialize: {e}")
    exit(1)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JARVIS System Analyzer")
clock = pygame.time.Clock()

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

# Fonts
font = pygame.font.SysFont("consolas", 28, bold=True)
small_font = pygame.font.SysFont("consolas", 20)
title_text = font.render("JARVIS System Analyzer", True, JARVIS_THEME["TEXT_COLOR"])
startup_text = small_font.render("Initializing JARVIS System Analysis...", True, JARVIS_THEME["ACCENT_COLOR"])

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
        stats["CPU"] = psutil.cpu_percent(interval=1)
        time.sleep(0.1)
        stats["Memory"] = psutil.virtual_memory().percent
    except Exception as e:
        logging.error(f"Error in stats: {e}")
        speak(f"Error retrieving system stats: {str(e)}")
    return stats

# Test definitions
TESTS = [
    {"name": "CPU Usage", "func": lambda: check_system_stats()["CPU"], "type": "percent"},
    {"name": "Memory Usage", "func": lambda: check_system_stats()["Memory"], "type": "percent"},
    {"name": "Microphone Health", "func": lambda: parse_michealth(michealth()), "type": "percent"},
    {"name": "Speaker Health", "func": lambda: parse_speakertest(speakertest()), "type": "percent"},
]

# Parse michealth output
def parse_michealth(result):
    try:
        if isinstance(result, str) and "Microphone Health" in result:
            health = float(result.split("Microphone Health (%):")[1].split(",")[0].strip())
            return health
        return 0
    except Exception as e:
        logging.error(f"Error parsing michealth: {e}")
        return 0

# Parse speakertest output
def parse_speakertest(result):
    try:
        if isinstance(result, str) and "Speaker Health" in result:
            health = float(result.split("Speaker Health:")[1].split("%")[0].strip())
            return health
        return 0
    except Exception as e:
        logging.error(f"Error parsing speakertest: {e}")
        return 0

# Draw HUD
def draw_hud(screen, progress, results, current_test, stats):
    try:
        screen.fill(JARVIS_THEME["BG_COLOR"])

        # Background grid
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, JARVIS_THEME["GRID_COLOR"], (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(screen, JARVIS_THEME["GRID_COLOR"], (0, y), (WIDTH, y))

        # Title with glow
        glow_surface = Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, JARVIS_THEME["GLOW_COLOR"],
                        (WIDTH // 2 - title_text.get_width() // 2 - 10, 15, title_text.get_width() + 20, title_text.get_height() + 10),
                        border_radius=5)
        screen.blit(glow_surface, (0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        # Current test
        current_text = small_font.render(f"Scanning: {current_test}", True, JARVIS_THEME["ACCENT_COLOR"])
        screen.blit(current_text, (WIDTH // 2 - current_text.get_width() // 2, 60))

        # Scan line
        scan_line_y = int(HEIGHT * progress) % HEIGHT
        scan_surface = Surface((WIDTH, 10), pygame.SRCALPHA)
        pygame.draw.line(scan_surface, (*JARVIS_THEME["SCAN_COLOR"], 200), (0, 5), (WIDTH, 5), 5)
        screen.blit(scan_surface, (0, scan_line_y - 5))

        # Particles
        update_particles()
        for x, y, s, dx, dy, c in particles:
            pygame.draw.circle(screen, c, (int(x), int(y)), int(s))

        # Results
        for i, (name, value, status, details) in enumerate(results):
            color = JARVIS_THEME["TEXT_COLOR"] if status == "OK" else JARVIS_THEME["ERROR_COLOR"]
            result_text = small_font.render(f"{name}: {value}", True, color)
            screen.blit(result_text, (50, 100 + i * 50))
            filled_width = (float(value.strip("%")) / 100) * 250
            pygame.draw.rect(screen, JARVIS_THEME["ACCENT_COLOR"], (300, 105 + i * 50, filled_width, 25))
            pygame.draw.rect(screen, JARVIS_THEME["TEXT_COLOR"], (300, 105 + i * 50, 250, 25), 2)

        # System stats
        stats_text = small_font.render(f"CPU: {stats['CPU']:.1f}% | Mem: {stats['Memory']:.1f}%", 
                                     True, JARVIS_THEME["TEXT_COLOR"])
        screen.blit(stats_text, (50, HEIGHT - 50))

        pygame.display.flip()
    except Exception as e:
        logging.error(f"Error in draw_hud: {e}")
        speak(f"Rendering error: {str(e)}")

# Holographic ring
def draw_holographic_ring(screen, angle, pulse):
    try:
        screen.fill(JARVIS_THEME["BG_COLOR"])
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, JARVIS_THEME["GRID_COLOR"], (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(screen, JARVIS_THEME["GRID_COLOR"], (0, y), (WIDTH, y))

        points = []
        radius = 120 + 30 * sin(pulse)
        for i in range(360):
            rad = i * pi / 180
            x = radius * cos(rad) * cos(angle) + WIDTH // 2
            y = radius * sin(rad) + HEIGHT // 2
            z = radius * cos(rad) * sin(angle)
            if -200 < z < 0:
                alpha = int(255 * (1 + z / 200))
                points.append((int(x), int(y), alpha))
        
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            pygame.draw.line(screen, (*JARVIS_THEME["ACCENT_COLOR"], p1[2]), (p1[0], p1[1]), (p2[0], p2[1]), 3)
        
        for i in range(8):
            orbit_angle = angle + i * (2 * pi / 8)
            orbit_radius = 150 + 20 * sin(pulse + i)
            x = orbit_radius * cos(orbit_angle) + WIDTH // 2
            y = orbit_radius * sin(orbit_angle) + HEIGHT // 2
            pygame.draw.circle(screen, JARVIS_THEME["SCAN_COLOR"], (int(x), int(y)), 5)
        
        pygame.display.flip()
    except Exception as e:
        logging.error(f"Error in draw_holographic_ring: {e}")
        speak(f"Ring rendering error: {str(e)}")

# Save and open results
def save_and_open_results(results):
    try:
        content = "JARVIS System Analysis Results\n\n"
        for name, value, status, details in results:
            content += f"{name}: {value}, Status: {status}\nDetails: {details}\n\n"
        file_path = os.path.join(os.path.expanduser("~/Desktop"), "System_Analysis_Results.txt")
        with open(file_path, "w") as f:
            f.write(content)
        speak("Analysis complete. Results saved to Desktop and opening now, sir.")
        os.startfile(file_path)
    except Exception as e:
        logging.error(f"Error saving results: {e}")
        speak(f"Error saving results: {str(e)}")

# Main analyzer function
def run_system_analyzer():
    running = True
    results = []
    current_test = 0
    test_progress = 0
    test_start_time = time.time()
    stats = check_system_stats()
    last_stats_time = time.time()
    angle = 0
    pulse = 0

    # Startup screen
    screen.fill(JARVIS_THEME["BG_COLOR"])
    screen.blit(startup_text, (WIDTH // 2 - startup_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    speak("Initiating JARVIS System Analysis, sir.")
    time.sleep(3)  # Show startup for 3 seconds

    # Test phase (8 seconds per test)
    while current_test < len(TESTS):
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                speak("System analysis terminated, sir.")
                logging.info("User terminated analysis")

        test_progress = min((current_time - test_start_time) / 8.0, 1.0)  # 8 seconds per test
        overall_progress = (current_test + test_progress) / len(TESTS)

        draw_hud(screen, overall_progress, results, TESTS[current_test]["name"], stats)

        if test_progress >= 1.0:
            try:
                result = TESTS[current_test]["func"]()
                value = f"{result:.1f}%"
                status = "OK" if result < 80 else "Warning" if result < 90 else "Error"
                results.append((TESTS[current_test]["name"], value, status, f"{TESTS[current_test]['name']}: {value}"))
                speak(f"{TESTS[current_test]['name']} scan complete: {value}, Status: {status}.")
                logging.info(f"Test {TESTS[current_test]['name']} completed: {value}, {status}")
            except Exception as e:
                logging.error(f"Test {TESTS[current_test]['name']} failed: {e}")
                speak(f"Test {TESTS[current_test]['name']} failed: {str(e)}")
                results.append((TESTS[current_test]["name"], "N/A", "Error", f"Test failed: {str(e)}"))
            current_test += 1
            test_start_time = current_time

        if current_time - last_stats_time >= 1:
            stats = check_system_stats()
            last_stats_time = current_time

        clock.tick(30)
        if not running:
            break

    # Save results
    if current_test >= len(TESTS):
        save_and_open_results(results)

    # Holographic ring phase
    start_time = time.time()
    while running and (time.time() - start_time) < 15:  # Run for 15 seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                speak("Shutting down JARVIS System Analyzer, sir.")
                logging.info("User exited ring phase")
        draw_holographic_ring(screen, angle, pulse)
        angle += 0.05
        pulse += 0.1
        clock.tick(60)

    pygame.quit()
    logging.info("JARVIS System Analyzer terminated")

