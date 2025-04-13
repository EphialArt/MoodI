# combined_mood.py
import csv
from datetime import datetime
import os
from collections import Counter
from datetime import timedelta
import time
from face_emotion import start_emotion_detection, get_last_emotion
from voice_emotion import start_voice_detection, get_last_sentiment
from chatbot import hold_conversation

print("🔄 Starting mood detection...")
start_emotion_detection()
start_voice_detection()

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

try:
    while True:
        face_emotion = get_last_emotion()
        voice_sentiment = get_last_sentiment()

        print("\n--- Mood Snapshot ---")
        print(f"Facial Emotion: {face_emotion}")
        print(f"Voice Sentiment: {voice_sentiment}")

        # Combine the data
        if face_emotion == "happy" and voice_sentiment == "Positive":
            mood = "Good"
            print("User seems genuinely happy.")
        elif face_emotion == "neutral" and voice_sentiment == "Positive":
            mood = "Calm/Content"
            print("User is calm and in a good mental state.")
        elif face_emotion == "neutral" and voice_sentiment == "Negative":
            mood = "Suppressed/Quiet Negative"
            print("User sounds off despite neutral expression.")
        elif face_emotion == "sad" or voice_sentiment == "Negative":
            mood = "Negative"
            print("User might be feeling down.")
        elif face_emotion in ["fear", "disgust", "angry"]:
            if voice_sentiment == "Negative":
                mood = "Distressed"
                print("User is likely distressed or uncomfortable.")
            else:
                mood = "Tense"
                print("User seems tense or alert.")
        elif face_emotion == "surprise":
            if voice_sentiment == "Positive":
                mood = "Excited"
                print("User is surprised in a good way.")
            elif voice_sentiment == "Negative":
                mood = "Alarmed"
                print("User might be reacting to something shocking or alarming.")
            else:
                mood = "Surprised"
                print("User is surprised, but unclear how they feel about it.")
        else:
            mood = "Uncertain"
            print("Mood is unclear or mixed.")

        log_mood(mood)

        # Check average mood and trigger chatbot
        average_mood = get_average_mood()
        if average_mood in ["Negative", "Distressed", "Sad"]:
            hold_conversation(average_mood)

        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Exiting...")