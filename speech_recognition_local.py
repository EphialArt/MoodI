#speech_recognition_local.py
import speech_recognition as sr
import threading
import time

running = True
recognizer = sr.Recognizer()
message = ""
last_exception = None

def speech_loop():
    global message, last_exception
    while running:
        with sr.Microphone() as source:
            print("Say something:")
            try:
                audio = recognizer.listen(source, timeout=10)
                message = recognizer.recognize_google(audio)
                print(f"You said: {message}")
                last_exception = None  
            except sr.UnknownValueError:
                last_exception = sr.UnknownValueError
                print(f"SpeechService erro {last_exception}")
            except sr.RequestError as e:
                last_exception = sr.RequestError
                message = "" 
                print(f"Speech service error: {e}")
            except sr.WaitTimeoutError:
                last_exception = sr.WaitTimeoutError
                print(f"SpeechService erro {last_exception}")
            except Exception as e:
                last_exception = e
                print(f"An unexpected error occurred during speech recognition: {e}")
            time.sleep(2)

def get_message():
    global message
    return message

def get_exception():
    return last_exception

def start_speech_recognition():
    thread = threading.Thread(target=speech_loop)
    thread.start()

def stop_speech_recognition():
    global running
    running = False

if __name__ == '__main__':
    start_speech_recognition()
    try:
        pass
    except KeyboardInterrupt:
        print("Stopping speech recognition...")
        stop_speech_recognition()