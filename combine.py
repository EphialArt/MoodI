# combined_mood.py
import csv
from datetime import datetime, timedelta
import os
import time
from collections import Counter
from face_emotion import start_emotion_detection, get_last_emotion
from voice_emotion import start_sentiment_detection, get_last_sentiment
from chatbot import start_voice_detection




face_history = []
voice_history = []
mood_history = []

log_file = "mood_log.csv"

if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Mood"])

def log_mood(mood):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, mood])

def weighting(face_emotion, voice_sentiment, face_weight, vocal_weight):
    face_value = 0
    vocal_value = 0
    if face_emotion in ["angry", "fear", "disgust", "sad"]:
        face_value = -1
    elif face_emotion in ["Undetected", "neutral", "surprise"]:
        face_value = 0
    elif face_emotion == "happy":
        face_value = 1

    if voice_sentiment == "Negative":
        vocal_value = -1
    elif voice_sentiment in ["Neutral", "Unknown"]:
        vocal_value = 0
    elif voice_sentiment == "Positive":
        vocal_value = 1

    combined_mood = (face_value * face_weight) + (vocal_value * vocal_weight)
    return combined_mood

def get_smoothed_mood(current_face_emotion, current_voice_sentiment):
    global face_history, voice_history

    face_history.append(current_face_emotion)
    if len(face_history) > 5:
        face_history.pop(0)
    smoothed_face = Counter(face_history).most_common(1)[0][0] if face_history else "Undetected"

    voice_history.append(current_voice_sentiment)
    if len(voice_history) > 5:
        voice_history.pop(0)
    smoothed_voice = Counter(voice_history).most_common(1)[0][0] if voice_history else "Unknown"

    weighted_mood = weighting(smoothed_face, smoothed_voice, 0.6, 0.4)
    return weighted_mood, smoothed_face, smoothed_voice
   

def get_average_mood():
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    moods = []

    with open(log_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            timestamp, mood = row
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if timestamp >= one_hour_ago:
                moods.append(mood)

    if moods:
        mood_counts = Counter(moods)
        most_common_mood = mood_counts.most_common(1)[0][0]
        return most_common_mood
    return "Uncertain"

start_emotion_detection()
start_sentiment_detection()
time.sleep(5)
print("🔄 Starting mood detection...")
try:
    while True:

        face_emotion = get_last_emotion()
        voice_sentiment = get_last_sentiment()
        weighted_mood, smoothed_face, smoothed_voice = get_smoothed_mood(face_emotion, voice_sentiment)

        print("\n--- Mood Snapshot ---")
        print(f"Facial Emotion: {smoothed_face}")
        print(f" Voice Sentiment: {smoothed_voice}")
        print(f"Mood: {weighted_mood}")

        mood = weighted_mood  
        mood_history.append(mood)

        if len(mood_history) == 60:
            log_mood(Counter(mood_history).most_common(1)[0][0])
            mood_history = []

        average_mood = get_average_mood()
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")