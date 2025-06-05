import os
import webbrowser
import datetime
import speech_recognition as sr
import pyttsx3
import openai
import wikipedia
import subprocess
import time
import threading
import requests
from bs4 import BeautifulSoup
import urllib.request
import re

# Initialize the speech engine
try:
    engine = pyttsx3.init()
except Exception as e:
    engine = None
    print("Warning: pyttsx3 initialization failed. Text-to-speech functionality will be disabled.")

# Initialize recognizer
recognizer = sr.Recognizer()

openai.api_key = 'paste your api key here'

print("API Key:", "Present" if openai.api_key else "Missing")

def speak(text):
    if engine is None:
        print("TTS disabled: " + text)
        return
    engine.say(text)
    engine.runAndWait()

def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio, language='en-US')
        print(f"User said: {query}")
        return query
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def open_chrome():
    speak("Opening Google Chrome")
    try:
        subprocess.Popen("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    except FileNotFoundError:
        speak("Chrome browser not found on your system.")

def set_reminder(reminder_text, delay_seconds):
    def reminder():
        time.sleep(delay_seconds)
        speak(f"Reminder: {reminder_text}")
    reminder_thread = threading.Thread(target=reminder)
    reminder_thread.daemon = True
    reminder_thread.start()
    if delay_seconds < 60:
        time_str = f"{delay_seconds} seconds"
    elif delay_seconds < 3600:
        time_str = f"{delay_seconds // 60} minutes"
    else:
        time_str = f"{delay_seconds // 3600} hours"
    speak(f"Reminder set for {time_str} from now.")

SEARCH_ENGINE_ID = "82b9d3ed58f984546"

def search_google_and_read(query):
    speak("Searching Google...")
    try:
        # Use the Google Custom Search Engine URL directly
        search_url = f"https://cse.google.com/cse?cx={SEARCH_ENGINE_ID}&q={query}"
        webbrowser.open(search_url)
        speak("Search results are on your screen.")
    except Exception as e:
        speak("Sorry, I had trouble opening the search page.")
        print(f"Error opening search page: {e}")

import json
import os

CUSTOM_COMMANDS_FILE = "custom_commands.json"

# Load custom commands from file
def load_custom_commands():
    if os.path.exists(CUSTOM_COMMANDS_FILE):
        with open(CUSTOM_COMMANDS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# Save custom commands to file
def save_custom_commands(commands):
    with open(CUSTOM_COMMANDS_FILE, "w") as f:
        json.dump(commands, f, indent=4)

custom_commands = load_custom_commands()

import os

def perform_task(query):
    import json
    CUSTOM_COMMANDS_FILE = "custom_commands.json"
    try:
        with open(CUSTOM_COMMANDS_FILE, "r") as f:
            custom_commands = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        custom_commands = {}

    if query is None:
        return

    query_lower = query.lower().strip()
    print(f"Recognized query: '{query_lower}'")  # Debug print
    print("Available voice commands:")
    for vc in custom_commands.keys():
        print(f" - '{vc}'")

    # Check custom commands first
    for voice_cmd, app_path in custom_commands.items():
        voice_cmd_lower = voice_cmd.lower().strip()
        # Match if exact or if voice command is a separate word in query
        if query_lower == voice_cmd_lower or f" {voice_cmd_lower} " in f" {query_lower} ":
            print(f"Matched voice command: '{voice_cmd}' with path: '{app_path}'")  # Debug print
            try:
                if app_path.startswith("web://"):
                    webapp_name = app_path[len("web://"):]
                    url = f"{webapp_name}"
                    speak(f"Opening web application {webapp_name}")
                    # Open URL in Chrome
                    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                    webbrowser.get(f'"{chrome_path}" %s').open(url)
                else:
                    # Try to open executable or file with default application
                    if os.path.isfile(app_path):
                        print(f"Path exists: {app_path}")  # Debug print
                        if app_path.lower().endswith(".exe"):
                            print(f"Opening executable: {app_path}")  # Debug print
                            subprocess.Popen(app_path)
                            speak(f"Opening {app_path}")
                        else:
                            print(f"Opening file with default app: {app_path}")  # Debug print
                            os.startfile(app_path)
                            speak(f"Opening file {app_path}")
                    else:
                        print(f"Path does not exist: {app_path}")  # Debug print
                        speak(f"The path {app_path} does not exist.")
            except Exception as e:
                print(f"Exception when opening path: {app_path}, error: {e}")  # Debug print
                speak(f"Failed to open {app_path}. Error: {str(e)}")
            return

    # Basic tasks
    if "hello" in query_lower:
        speak("Hey there! What can I do for you today?")

    elif "what's your name" in query_lower:
        speak("I'm Viky, your friendly assistant. How can I help?")

    elif "what is the time" in query_lower:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"It's {current_time} right now.")

    elif "open google" in query_lower:
        webbrowser.open("https://www.google.com")

    elif "open notepad" in query_lower:
        subprocess.Popen("notepad.exe")
        speak("Opening Notepad")

    elif "open calculator" in query_lower:
        subprocess.Popen("calc.exe")
        speak("Opening Calculator")

    elif "open word" in query_lower:
        try:
            subprocess.Popen(["winword.exe"])
            speak("Opening Microsoft Word")
        except FileNotFoundError:
            speak("Microsoft Word is not installed on this computer")

    elif "open excel" in query_lower:
        try:
            subprocess.Popen(["excel.exe"])
            speak("Opening Microsoft Excel")
        except FileNotFoundError:
            speak("Microsoft Excel is not installed on this computer")

    elif "open chrome" in query_lower:
        open_chrome()

    elif "open youtube" in query_lower:
        webbrowser.open("https://www.youtube.com/")
        speak("Opening YouTube")

    elif "time for workout" in query_lower:
        webbrowser.open("https://workout.lol/")
        speak("Time for a workout!")
        
    elif "start workout" in query_lower:
        webbrowser.open("https://workout.lol/")
        speak("Time for a workout!")

    elif "play music" in query_lower:
        speak("What song would you like me to play?")
        song_query = recognize_speech()
        if song_query:
            search_query = song_query.replace(" ", "+")
            # Search YouTube and get first video
            youtube_url = f"https://www.youtube.com/watch?v=" # Direct video URL format
            search_url = f"https://www.youtube.com/results?search_query={search_query}"
            import urllib.request
            import re
            html = urllib.request.urlopen(search_url)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            if video_ids:
                first_video = youtube_url + video_ids[0]
                webbrowser.open(first_video)
                speak(f"Playing {song_query} from YouTube")
    elif "search" in query_lower:
        search_query = query_lower.replace("search", "").strip()
        if search_query:
            search_url = f"https://www.google.com/search?q={search_query}"
            webbrowser.open(search_url)
            speak("The search results are on your screen.")

    elif "wikipedia" in query_lower:
        speak("What would you like to know about?")
        question = recognize_speech()
        if question:
            try:
                search_term = question.replace("wikipedia", "").strip()
                response = wikipedia.summary(search_term, sentences=3)
                print(f"Wikipedia: {response}")
                speak(response)

                while True:
                    speak("Dose your doubt clear yes or no ")
                    clarity = recognize_speech()

                    if clarity and "yes" in clarity.lower():
                        speak("Do you want to know more about this topic? yes or no")
                        more_info = recognize_speech()
                        if more_info and "yes" in more_info.lower():
                            wiki_page = wikipedia.page(search_term)
                            webbrowser.open(wiki_page.url)
                            speak("I have opened the wikipedia page for more detailed information")
                        break

                    elif clarity and "no" in clarity.lower():
                        speak("let me try to explain it differently")
                        detailed_response = wikipedia.summary(search_term, sentences=5)
                        print(f"Detailed explanation: {detailed_response}")
                        speak(detailed_response)
                    else:
                        break

            except wikipedia.exceptions.DisambiguationError as e:
                speak("there are multiple matches for your query. please be more specific")
            except wikipedia.exceptions.PageError:
                speak("i couldn't find any information about that. let me search google for you")
                search_url = f"https://www.google.com/search?q={question}"
                webbrowser.open(search_url)
        else:
            speak("i didn't catch your question. please try again")

    elif "exit" in query_lower or "stop" in query_lower:
        speak("goodbye!")
        # exit() removed to prevent UI blocking
    elif "quit" in query_lower or "stop" in query_lower:
        speak("goodbye!")
        # exit() removed to prevent UI blocking

# Main loop
if __name__ == "__main__":
    while True:
        query = recognize_speech()
        perform_task(query)

