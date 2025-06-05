# Voice-Interactive-Knowledge-Interface-(VIKI)-

## Project Overview

The "Viki Voice Assistant" is a robust desktop application developed using Python, designed to provide users with an intuitive and efficient way to interact with their computer and the internet through voice commands. This project aims to simplify daily computing tasks and enhance accessibility by offering a conversational interface.

## Features

Viki Voice Assistant comes packed with a variety of functionalities to assist users:

### Core Voice Interaction
* **Speech Recognition**: Utilizes the `speech_recognition` library to accurately convert spoken commands into text, allowing for hands-free operation.
* **Text-to-Speech (TTS)**: Employs the `pyttsx3` library to provide verbal responses and feedback to the user, creating a natural conversational flow.

### Basic & Advanced Functionalities
* **Time Inquiry**: Provides the current time upon request.
* **Web Browse**: Opens specified websites (e.g., Google, YouTube) and performs general Google searches directly from voice commands.
* **Application Launching**: Launches common desktop applications such as Notepad, Calculator, Microsoft Word, and Excel.
* **Wikipedia Integration**: Fetches and summarizes information from Wikipedia based on user queries. It also includes a unique clarification loop to provide more detailed explanations or open the full Wikipedia page if needed.
* **Music Playback**: Searches for and plays songs on YouTube based on user requests.
* **Reminders**: Sets simple, time-based reminders to help users stay organized.
* **Workout Assistant**: Opens a dedicated workout website, encouraging physical activity.

### Customizable Commands
* **Personalized Automation**: Users can define and save custom voice commands to launch specific applications or web applications.
* **Persistent Storage**: Custom commands are stored in `custom_commands.json` to ensure they are available across sessions.
* **Dynamic Management**: The UI allows for easy addition, editing, and deletion of these custom commands, providing full control to the user.

### Interactive User Interface (UI)
* **Modern Design**: Built with `customtkinter`, the UI offers a clean, modern aesthetic with customizable themes (Light/Dark mode).
* **Chat Interface**: Features a dynamic chat-like display that shows both user commands and Viki's responses in styled message bubbles.
* **Real-time Status**: Provides visual cues through a status label and a color-changing indicator (gray for idle, green for listening, orange for processing).
* **Webcam Integration (Video Mode)**:
    * Displays a live webcam feed within the UI using `OpenCV (cv2)`.
    * Enables recording of video from the webcam in MP4 or AVI formats.
    * Allows capturing still photos from the live feed.
* **User-friendly Controls**: Includes buttons for starting/stopping listening, toggling video mode, managing recordings, capturing photos, and clearing the chat.

### Robustness & User Experience
* **Module Dependency Check**: At startup, the application verifies essential Python module installations and offers to install missing ones, simplifying setup.
* **PyInstaller Compatibility**: Designed with `resource_path()` to correctly locate files when bundled into a standalone executable using PyInstaller.
* **Opening Splash Screen**: Features an engaging video splash screen at startup (`VIKI_opening.mp4`).
* **Sound Feedback**: Incorporates auditory cues like button click sounds and a system start sound for enhanced interactivity.
* **Concurrency**: Utilizes `threading` to perform background tasks (listening, video processing) without freezing the UI, ensuring a smooth user experience.
* **Thread-Safety**: Employs a `queue` for safe communication between background threads and the main UI thread, preventing common concurrency issues.

## Technical Stack

* **Programming Language**: Python
* **Core Libraries**:
    * `speech_recognition`: Speech-to-Text conversion.
    * `pyttsx3`: Text-to-Speech synthesis.
    * `openai`: For potential future integration with AI language models (though currently not actively used in `perform_task` for core responses).
    * `wikipedia`: Information retrieval from Wikipedia.
    * `webbrowser`: Opening web pages.
    * `subprocess`: Launching system applications.
    * `datetime`: Date and time operations.
    * `threading`: Concurrency management.
    * `tkinter`, `customtkinter`, `ttk`: Graphical User Interface development.
    * `cv2` (OpenCV): Webcam access, video recording, and photo capture.
    * `PIL` (Pillow): Image processing for UI display.
    * `json`: Data serialization for custom commands.
    * `os`: Operating system interactions (file paths, directories).
    * `winsound`: Playing system sounds (Windows-specific).
    * `requests`, `bs4`, `urllib.request`, `re`: Used for web interactions, though some YouTube specific URLs might be illustrative or require updates.

## Project Structure

The project is organized into the following key files and directories:

*viki-voice-assistant/
├── viki.py                   # Core voice assistant logic, command processing, and external API interactions.

├── viki_ui.py                # Graphical User Interface (GUI) implementation and interaction with core logic.

├── custom_commands.json      # (Generated) Stores user-defined custom voice commands.

├── custom_commands.txt       # (Generated) Plain text listing of custom commands.

├── click.wav                 # Sound effect for UI button clicks.

├── jarvis/

│   ├── viki_logo.png         # Application logo image.

│   └── VIKI_opening.mp4      # Opening video splash screen.

├── photos/                   # (Auto-created) Directory for captured webcam photos.

└── recordings/               # (Auto-created) Directory for saved video recordings.


