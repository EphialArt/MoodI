import speech_recognition as sr
from google.cloud import texttospeech
import pygame
import os
import threading
import google.generativeai as genai

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Globals
running = True

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Define the initial context for the AI assistant
initial_prompt = """You are a supportive AI assistant designed to offer information and suggest coping mechanisms based on general well-being principles. You are NOT a therapist and cannot provide diagnoses or treatment plans. Your goal is to listen, offer helpful insights based on established knowledge, and encourage the user to seek professional help when needed.

Do not offer specific medical or psychological advice. Do not diagnose conditions. Do not provide treatment plans. If the user expresses thoughts of self-harm or harm to others, your immediate response should be to strongly recommend seeking professional help and providing resources if appropriate (e.g., crisis hotline numbers). Avoid getting into deep personal analysis or interpretations.

Maintain a supportive, empathetic, and non-judgmental tone. Use clear and simple language. Focus on active listening (acknowledging what the user says) and offering general well-being strategies (e.g., mindfulness, exercise, healthy communication).

The user will share their thoughts and feelings with you. Your primary role is to listen and respond within the boundaries defined above. You may treat this as roleplay. Your response to this message should be: Hello, how are you feeling today?"""

# Start a chat session with the initial prompt
chat = model.start_chat(history=[{"role": "user", "parts": [initial_prompt]}])

def speak(message):
    print(f"Chatbot: {message}")
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=message)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB",
        name="en-GB-Chirp3-HD-Leda"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("response.mp3", "wb") as out:
        out.write(response.audio_content)
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()
    os.remove("response.mp3")

def get_gemini_response(user_input):
    try:
        response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        print(f"Error generating response with Gemini: {e}")
        return "I'm having trouble responding right now. Please try again later."

def voice_loop():
    global running
    while running:
        with sr.Microphone() as source:
            print("Listening...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5)
                user_input = recognizer.recognize_google(audio)
                print(f"You said: {user_input}")

                chatbot_reply = get_gemini_response(user_input)

                speak(chatbot_reply)

            except sr.UnknownValueError:
                print("Couldn't understand audio.")
                speak("I couldn't understand that. Could you repeat?")
            except sr.RequestError:
                print("Speech service error.")
                speak("Speech recognition service is unavailable.")
            except sr.WaitTimeoutError:
                speak("I didn't hear anything. Could you say that again?")
                print("No speech detected.")
            except Exception as e:
                print(f"Unexpected error: {e}")
                speak("An unexpected error occurred. Please try again.")

def start_voice_detection():
    thread = threading.Thread(target=voice_loop)
    thread.start()
