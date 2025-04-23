#chatbot.py
import speech_recognition as sr
from google.cloud import texttospeech
import pygame
import os
import threading
import google.generativeai as genai
import time  
from speech_recognition_local import get_exception, get_message, start_speech_recognition 

# Globals
running = True
opening_message = ""
chat = None
chatbot_exit_event = threading.Event()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# Define the initial context for the AI assistant
default_initial_prompt = """You are a supportive AI assistant designed to offer information and suggest coping mechanisms based on general well-being principles. You are NOT a therapist and cannot provide diagnoses or treatment plans. Your goal is to listen, offer helpful insights based on established knowledge, and encourage the user to seek professional help when needed.

Do not offer specific medical or psychological advice. Do not diagnose conditions. Do not provide treatment plans. If the user expresses thoughts of self-harm or harm to others, your immediate response should be to strongly recommend seeking professional help and providing resources if appropriate (e.g., crisis hotline numbers). Avoid getting into deep personal analysis or interpretations.

Maintain a supportive, empathetic, and non-judgmental tone. Use clear and simple language. Avoid lengthy messages. Focus on active listening (acknowledging what the user says) and offering general well-being strategies (e.g., mindfulness, exercise, healthy communication).

The user will share their thoughts and feelings with you. Your primary role is to listen and respond within the boundaries defined above. You may treat this as roleplay. Your response to this message should be: """
initial_prompt = default_initial_prompt

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

def chatbot_loop():
    global running
    while running:
        user_input = get_message() 
        error = get_exception() 

        if error:
            print(error)
            if error == sr.UnknownValueError:
                print("Chatbot couldn't understand audio.")
                speak("I couldn't understand that. Could you repeat?")
            elif error == sr.RequestError:
                print("Chatbot speech service error.")
                speak("Speech recognition service is unavailable.")
            elif error == sr.WaitTimeoutError:
                print("Took too long to speak")
                speak("I didn't hear anything. Could you say that again?")
            else:
                print(f"Chatbot unexpected speech error: {error}")
                speak("An unexpected error occurred with speech input. Please try again")

        elif user_input:
            if user_input == "relief":
                pass
            else:
                print(f"You said (for chatbot): {user_input}")
                if user_input.lower() == "exit":
                    print("Exiting chatbot...")
                    running = False
                    chatbot_exit_event.set()
                    break

                chatbot_reply = get_gemini_response(user_input)
                speak(chatbot_reply)

        time.sleep(5)

def voice_loop_control():
    global running, opening_message, chat, initial_prompt
    if chat is None:
        chat = model.start_chat(history=[{"role": "user", "parts": [initial_prompt]}])
        if opening_message != "":
            chatbot_reply = get_gemini_response(opening_message)
            speak(chatbot_reply)
            opening_message = ""
            running = True
            chatbot_loop()  
        else:
            running = True
            chatbot_loop()  
    else:
        running = True
        chatbot_loop() 

def set_opening_message(message):
    global opening_message
    opening_message = message
    print(opening_message)

def start_voice_detection():
    global running
    thread = threading.Thread(target=voice_loop_control)
    thread.start()

def set_initial_prompt(message):
    global initial_prompt
    initial_prompt = default_initial_prompt + message

if __name__ == '__main__':
    start_speech_recognition()
    start_voice_detection()
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping chatbot.")
        running = False