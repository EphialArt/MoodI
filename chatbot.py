import speech_recognition as sr
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from google.cloud import texttospeech
import pygame
import os
import threading

# Load BlenderBot model and tokenizer
tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-400M-distill")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Globals
running = True

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
def get_blenderbot_response(user_input):
    try:
        inputs = tokenizer(user_input, return_tensors="pt")
        reply_ids = model.generate(inputs["input_ids"], max_length=100)
        response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm having trouble responding right now. Please try again later."

def voice_loop():
    global running

    while running:
        with sr.Microphone() as source:
            print("Listening...")
            try:
                # Adjust for ambient noise (optional, improves recognition in noisy environments)
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Capture user input
                audio = recognizer.listen(source, timeout=5)
                user_input = recognizer.recognize_google(audio)
                print(f"You said: {user_input}")

                # Generate bot response
                chatbot_reply = get_blenderbot_response(user_input)

                # Speak the bot's response
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
    """Start the voice detection loop in a separate thread."""
    thread = threading.Thread(target=voice_loop)
    thread.start()


start_voice_detection()