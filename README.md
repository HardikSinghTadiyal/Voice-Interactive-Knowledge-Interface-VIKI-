# Voice Interactive Knowledge Interface (VIKI)



Viki is a versatile voice assistant built with Python, featuring speech recognition, text-to-speech capabilities, integration with OpenAI , web Browse, application launching, and a dynamic graphical user interface. Users can interact with Viki through voice commands or by typing, manage custom application mappings, and even use webcam functionalities for recording and photo capture.

## Features

* **Voice Interaction:** Speak commands to Viki, and it will respond verbally.
* **ChatGPT Integration:** Utilizes OpenAI's GPT-3.5 Turbo for intelligent conversational responses.
* **Application Launcher:** Open common applications like Notepad, Calculator, Microsoft Word, and Excel with voice commands.
* **Web Browser Control:** Open websites like Google, YouTube, and custom URLs.
* **Wikipedia Search:** Get quick summaries from Wikipedia or open full articles in your browser.
* **Reminders:** Set voice-activated reminders for specific times.
* **Custom Commands:** Define personalized voice commands to launch any application or open any website on your system. These commands are saved to `custom_commands.json`.
* **Video & Photo Capture:** Access your webcam to record videos in MP4/AVI or capture still photos directly from the UI.
* **Intuitive GUI:** A modern and user-friendly interface built with `customtkinter`, featuring chat bubbles, status indicators, and dedicated controls for all functionalities.
* **Dynamic Theming:** Switch between light and dark modes effortlessly.
* **Module Auto-Installer:** Automatically checks for and offers to install missing Python dependencies when running the bundled application.

## Technologies Used

* **Python:** The core programming language.
* [cite_start]**`pyttsx3`:** Text-to-speech engine.
* [cite_start]**`SpeechRecognition`:** For converting speech to text.
* [cite_start]**`openai`:** Python client for the OpenAI API.
* [cite_start]**`wikipedia`:** Python library to access and parse data from Wikipedia.
* [cite_start]**`requests`:** For making HTTP requests.
* [cite_start]**`beautifulsoup4` (bs4):** For parsing HTML and XML documents.
* [cite_start]**`opencv-python` (cv2):** For video capture, processing, and image manipulation.
* [cite_start]**`Pillow` (PIL):** For image processing, used with Tkinter.
* [cite_start]**`customtkinter`:** Modern and customizable Tkinter widgets.
* **`tkinter` (tk):** Standard Python GUI library.
* **`json`:** For saving and loading custom commands.
* **`subprocess`:** For launching external applications.
* **`webbrowser`:** For opening web pages.
* **`threading`:** For running tasks concurrently without freezing the UI.
* **`winsound`:** For playing system sounds (Windows-specific).

# How to install 
## 1. Insatll Python Latest Verson 
## 2. After installing python. Open command prompt and type following commands
* pip install pyttsx3
* pip install SpeechRecognition
* pip install pyttsx3 SpeechRecognition openai wikipedia requests beautifulsoup4 opencv-python Pillow customtkinter

     ### This command will install all the modules listed in your requirements.txt.txt file. ###
## Important Notes:
* Internet Connection: You need an active internet connection for pip to download the modules.
* Virtual Environments: For project-specific dependencies, it's best practice to use a virtual environment. This prevents conflicts between different projects. If you're using a virtual environment, make sure it's activated before running pip install.
* Permissions: On some systems, you might need administrator privileges to install packages globally. If you encounter permission errors, consider using a virtual environment or try pip install --user <module_name>



###  Voice Interactive: Directly refers to the core method of interaction with the assistant – through voice commands and spoken responses.
###  Knowledge: Emphasizes its ability to access and provide information, whether from Wikipedia, web searches, or potentially through an integrated AI.
###  Interface: Highlights its role as a user-friendly system that allows interaction with a computer and various services.
