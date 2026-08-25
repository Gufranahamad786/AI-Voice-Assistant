import os
import webbrowser
import subprocess
import datetime
import requests
import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv


# LOAD API KEY

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    print("ERROR: OPENROUTER_API_KEY not found in .env")
    exit()

# JARVIS VOICE ENGINE

engine = pyttsx3.init()

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


def speak(text):
    print("JARVIS:", text)

    engine.say(text)
    engine.runAndWait()

# LISTEN


recognizer = sr.Recognizer()


def listen():

    with sr.Microphone() as source:

        print("\nListening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        try:

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

            print("Recognizing...")

            command = recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            print("YOU:", command)

            return command.lower()

        except sr.WaitTimeoutError:

            return ""

        except sr.UnknownValueError:

            speak("Sorry, I didn't understand that.")

            return ""

        except sr.RequestError:

            speak("Speech recognition service is unavailable.")

            return ""



# OPENROUTER / DEEPSEEK


def ask_deepseek(question):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-v3.2",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, a helpful Windows laptop assistant. "
                    "Answer the user's question clearly and briefly. "
                    "Do not pretend that you performed computer actions."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "temperature": 0.5,
        "max_tokens": 500
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:

        print("API ERROR:", e)

        return "Sorry, I could not connect to my AI service."


# WINDOWS COMMANDS


def execute_command(command):

    # ---------- TIME ----------

    if "time" in command:

        current_time = datetime.datetime.now().strftime("%I:%M %p")

        speak(f"The current time is {current_time}")

        return True


    # ---------- DATE ----------

    if "date" in command or "today" in command:

        today = datetime.datetime.now().strftime("%A, %d %B %Y")

        speak(f"Today is {today}")

        return True


    # ---------- YOUTUBE ----------

    if "open youtube" in command:

        speak("Opening YouTube")

        webbrowser.open(
            "https://www.youtube.com"
        )

        return True


    # ---------- GOOGLE ----------

    if "open google" in command:

        speak("Opening Google")

        webbrowser.open(
            "https://www.google.com"
        )

        return True


    # ---------- EDGE ----------

    if "open edge" in command:

        speak("Opening Microsoft Edge")

        subprocess.Popen(
            ["cmd", "/c", "start", "msedge"]
        )

        return True
    
   

    # ---------- NOTEPAD ----------

    if "open notepad" in command:

        speak("Opening Notepad")

        subprocess.Popen(
            ["notepad.exe"]
        )

        return True


    # ---------- CALCULATOR ----------

    if "open calculator" in command:

        speak("Opening Calculator")

        subprocess.Popen(
            ["calc.exe"]
        )

        return True


    # ---------- FILE EXPLORER ----------

    if "open file explorer" in command:

        speak("Opening File Explorer")

        subprocess.Popen(
            ["explorer.exe"]
        )

        return True


    # ---------- YOUTUBE SEARCH ----------

    if command.startswith("search youtube for"):

        query = command.replace(
            "search youtube for",
            ""
        ).strip()

        speak(f"Searching YouTube for {query}")

        url = (
            "https://www.youtube.com/results?search_query="
            + query.replace(" ", "+")
        )

        webbrowser.open(url)

        return True


    # ---------- GOOGLE SEARCH ----------

    if command.startswith("search google for"):

        query = command.replace(
            "search google for",
            ""
        ).strip()

        speak(f"Searching Google for {query}")

        url = (
            "https://www.google.com/search?q="
            + query.replace(" ", "+")
        )

        webbrowser.open(url)

        return True


    # ---------- SHUTDOWN ----------

    if "shutdown computer" in command or "shut down computer" in command:

        speak("Shutdown command detected.")

        confirmation = input(
            "Type YES to shutdown the computer: "
        )

        if confirmation == "YES":

            speak("Shutting down the computer.")

            os.system("shutdown /s /t 5")

        else:

            speak("Shutdown cancelled.")

        return True


    # ---------- RESTART ----------

    if "restart computer" in command:

        speak("Restart command detected.")

        confirmation = input(
            "Type YES to restart the computer: "
        )

        if confirmation == "YES":

            speak("Restarting the computer.")

            os.system("shutdown /r /t 5")

        else:

            speak("Restart cancelled.")

        return True


    # ---------- CANCEL SHUTDOWN ----------

    if "cancel shutdown" in command:

        os.system("shutdown /a")

        speak("Shutdown cancelled.")

        return True


    # ---------- EXIT ----------

    if (
        command == "exit"
        or command == "quit"
        or "goodbye jarvis" in command
        or "stop jarvis" in command
    ):

        speak("Goodbye. See you later.")

        return False


    # Command wasn't found

    return None


# MAIN JARVIS LOOP


def main():

    speak(
    "Hello. I am JARVIS. "
    "How can I help you?"
)

    while True:

        command = listen()

        if not command:
            continue


        # First check local Windows commands

        result = execute_command(command)


        # Exit

        if result is False:
            break


        # If local command was handled

        if result is True:
            continue


        # Otherwise ask DeepSeek

        speak("Let me think.")

        answer = ask_deepseek(command)

        speak(answer)

# START

if __name__ == "__main__":

    main()