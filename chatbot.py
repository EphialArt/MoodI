import openai
import pyttsx3
import speech_recognition as sr

# Initialize text-to-speech engine
engine = pyttsx3.init()

# OpenAI API key (replace with your actual key)
openai.api_key = "your_openai_api_key"

# Maintain conversation history for context
conversation_history = [
    {"role": "system", "content": "You are a helpful and empathetic assistant."}
]

# Initialize speech recognizer
recognizer = sr.Recognizer()

def speak(message):
    """Speak the chatbot's response."""
    print(f"🤖 Chatbot: {message}")
    engine.say(message)
    engine.runAndWait()

def get_chatbot_response(user_input):
    """Get a response from OpenAI's GPT model."""
    try:
        # Add user input to the conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Get the chatbot's response
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_history
        )
        chatbot_reply = response['choices'][0]['message']['content']

        # Add the chatbot's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": chatbot_reply})

        return chatbot_reply
    except Exception as e:
        print(f"Error: {e}")
        return "I'm having trouble responding right now. Please try again later."

def listen_to_user():
    """Listen to the user's voice input and return the transcribed text."""
    with sr.Microphone() as source:
        print("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input
        except sr.UnknownValueError:
            return "I couldn't understand that."
        except sr.RequestError:
            return "Speech recognition service is unavailable."
        except sr.WaitTimeoutError:
            return ""

def hold_conversation(mood):
    """Start a conversation based on the user's mood."""
    # Define an initial message based on the mood
    if mood == "Negative":
        initial_message = "I noticed you've been feeling down. What's on your mind?"
    elif mood == "Distressed":
        initial_message = "You seem stressed. Is there something specific bothering you?"
    elif mood == "Sad":
        initial_message = "I'm here for you. Would you like to talk about why you're feeling sad?"
    elif mood == "Tense":
        initial_message = "You seem tense. Is there something I can help you with?"
    elif mood == "Good":
        initial_message = "You seem happy! What's been going well for you?"
    else:
        initial_message = "How are you feeling today?"

    # Speak the initial message and start the conversation
    speak(initial_message)

    while True:
        # Listen to the user's voice input
        user_input = listen_to_user()

        # Check for specific phrases to trigger immediate responses
        if user_input.lower() in ["i want to talk", "i need to talk"]:
            chatbot_reply = "No problem, let's speak."
        elif user_input.lower() in ["exit", "quit", "stop"]:
            speak("Okay, take care!")
            break
        else:
            # Get the chatbot's response
            chatbot_reply = get_chatbot_response(user_input)

        # Speak the chatbot's response
        speak(chatbot_reply)