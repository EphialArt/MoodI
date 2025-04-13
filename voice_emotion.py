# voice_sentiment.py

import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import threading

recognizer = sr.Recognizer()
analyzer = SentimentIntensityAnalyzer()

last_sentiment = "Unknown"
running = True

def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def voice_loop():
    global last_sentiment, running

    while running:
        with sr.Microphone() as source:
            print("🎤 Say something:")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                last_sentiment = analyze_sentiment(text)
                print(f"Sentiment: {last_sentiment}")
            except sr.UnknownValueError:
                print("Couldn't understand audio.")
                last_sentiment = "Unknown"
            except sr.RequestError:
                print("Speech service error.")
                last_sentiment = "Unknown"
            except sr.WaitTimeoutError:
                print("No speech detected.")
                last_sentiment = "Unknown"

def start_voice_detection():
    thread = threading.Thread(target=voice_loop)
    thread.start()

def get_last_sentiment():
    return last_sentiment
