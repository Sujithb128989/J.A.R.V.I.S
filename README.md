Note: the code is kinda glitchy after major updates, testors required.
# J.A.R.V.I.S. - Your Personal AI Assistant

This project is a sophisticated, voice-controlled personal AI assistant named J.A.R.V.I.S. It integrates with multiple AI models and services to provide a wide range of functionalities, from answering general questions to automating system tasks.

## Features

*   **Voice Interaction:** Fully voice-controlled activation and interaction.
*   **AI-Powered Chat:** Utilizes powerful language models (like Cohere, Groq, and Gemini) to understand and respond to a wide range of queries.
*   **Real-time Information:** Can access up-to-date information from the internet to answer questions about current events, people, and places.
*   **System Automation:**
    *   Open and close applications.
    *   Control system volume.
    *   Get system stats (CPU, memory, battery).
*   **Web Automation:**
    *   Perform Google and YouTube searches.
    *   Play YouTube videos.
    *   Control YouTube playback (seek, pause, next video, etc.).
*   **Content Generation:**
    *   Generate and write content (emails, code, etc.) to files on your desktop.
    *   Summarize articles and YouTube videos (via transcript).
*   **Image Generation:** Generate images from text prompts using Stable Diffusion.
*   **Reminders and Alarms:** Set reminders for specific activities.
*   **Modern UI:** A clean, modern, and intuitive user interface for displaying conversations and system status.

## Code Structure

The codebase has been significantly refactored for clarity, maintainability, and robustness.

-   `main.py`: The main entry point for the application. It handles threading and the main application loop.
-   `Frontend/`: Contains all the UI-related code.
    -   `Gui.py`: The main UI application, built with PyQt5.
-   `Backend/`: Contains the core logic of the assistant.
    -   `Automation.py`: A dispatcher that routes automation commands to the appropriate modules.
    -   `automation_*.py` modules: Contain the logic for specific automation tasks (e.g., `automation_system.py`, `automation_web.py`).
    -   `utils/`: Contains utility modules for shared functionality.
        -   `tts_utils.py`: Handles text-to-speech.
        -   `llm_utils.py`: Handles interactions with the various language models.
    -   Other modules like `Chatbot.py`, `Model.py`, and `RealTimeSearchEngine.py` handle the core AI and conversation logic.

## Setup and Installation

Follow these steps to get J.A.R.V.I.S. up and running on your system.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set Up Environment Variables

The application requires several API keys to function correctly.

1.  Make a copy of the `.env.example` file and name it `.env`.
2.  Open the `.env` file and fill in the required values:

    ```
    # User and Assistant Names
    Username=YourName
    Assistantname=Jarvis

    # API Keys
    CohereAPIKey=your_cohere_api_key
    GroqAPIKey=your_groq_api_key
    GEMINI_API_KEY=your_gemini_api_key
    HUGGINGFACE_API_KEY=your_huggingface_api_key
    ```

### 3. Install Dependencies

First, ensure you have Python 3 installed. Then, install the required Python packages using pip.

```bash
pip install -r requirements.txt
```

**Note for Linux Users:** Some of the Python audio libraries require system-level packages to be installed. If the `pip install` command fails for `simpleaudio` or `pyaudio`, you may need to install the following development libraries.

On Debian/Ubuntu-based systems, run:
```bash
sudo apt-get update && sudo apt-get install -y libasound2-dev portaudio19-dev
```

**Note for Windows Users:** The application uses some Windows-specific libraries like `wmi` and `pycaw`. These should be installed automatically with the `requirements.txt` file.

## Usage

To run the application, simply execute the `main.py` script:

```bash
python main.py
```

This will launch the user interface, and the assistant will be ready for your commands.
