# voice_emotion.py
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import threading
import time
from speech_recognition_local import get_exception, get_message, start_speech_recognition  

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

def sentiment_loop():
    global last_sentiment, running

    while running:
        text = get_message()
        error = get_exception()

        if error:
            if isinstance(error, sr.UnknownValueError):
                print("Couldn't understand audio (for sentiment).")
                last_sentiment = "Unknown"
            elif isinstance(error, sr.RequestError):
                print("Speech service error (for sentiment).")
                last_sentiment = "Unknown"
            elif isinstance(error, sr.WaitTimeoutError):
                pass 
            else:
                print(f"Speech recognition error (for sentiment): {error}")
                last_sentiment = "Unknown"
            time.sleep(5) 
            continue

        if text:
            print(f"Analyzing sentiment for: {text}")
            last_sentiment = analyze_sentiment(text)
            print(f"Sentiment: {last_sentiment}")
            time.sleep(5) 

        time.sleep(5)

def start_sentiment_detection():
    thread = threading.Thread(target=sentiment_loop)
    thread.daemon = True
    thread.start()

def get_last_sentiment():
    return last_sentiment

if __name__ == '__main__':
    start_speech_recognition() 
    start_sentiment_detection()
    try:
        pass
    except KeyboardInterrupt:
        print("Stopping sentiment detection.")
        running = False