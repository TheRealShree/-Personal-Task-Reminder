import time
import pandas as pd
from datetime import datetime
import pyttsx3  # voice assistant

# -----------------------------
# Initialize voice engine (Windows)
# -----------------------------
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # select first voice
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# -----------------------------
# Load CSV and clean data
# -----------------------------
df = pd.read_csv("TT-Shree.csv")
df.columns = df.columns.str.strip().str.lower()  # lowercase column names
df = df.dropna(subset=["day", "time", "task"])   # remove empty rows

print(df.columns)
print("✅ Weekly Reminder loaded\n")

# -----------------------------
# Triggered set to avoid repetition
# -----------------------------
triggered = set()

# -----------------------------
# Get current day in lowercase
# -----------------------------
current_day = datetime.now().strftime("%A").lower()

# -----------------------------
# Announce today's tasks
# -----------------------------
today_tasks = df[df['day'].str.strip().str.lower() == current_day]

if today_tasks.empty:
    print(f"No tasks for today ({current_day.capitalize()}) 🎉")
else:
    print(f"📌 Tasks for today ({current_day.capitalize()}):")
    for i, row in today_tasks.iterrows():
        task_time = str(row["time"]).strip()
        task_msg = str(row["task"]).strip()
        print(f"{task_time} → {task_msg}")
        engine.say(f"Hello Shree! Today's task at {task_time}: {task_msg}")
    engine.runAndWait()

print("\n⏰ Real-time reminders starting...\n")

# -----------------------------
# Real-time reminder loop
# -----------------------------
while True:
    now = datetime.now()
    current_dt = now  # full datetime with date + time
    current_time = now.strftime("%H:%M:%S")  # real time with seconds

    print(f"⏱ Current time: {current_time}", end="\r")  # overwrite same line

    for index, row in today_tasks.iterrows():
        task_time = str(row["time"]).strip()
        task_msg = str(row["task"]).strip()

        try:
            start_str, end_str = task_time.split("-")
            start_dt = datetime.strptime(start_str.strip(), "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            end_dt = datetime.strptime(end_str.strip(), "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
        except:
            continue

        # Unique trigger key
        today_trigger = f"{index}_{now.strftime('%Y-%m-%d')}"

        # Case 1: On-time
        if start_dt <= current_dt <= end_dt and today_trigger not in triggered:
            text = f"Hello Shree! It's time for {task_msg}. Current time is {now.strftime('%H:%M')}"
            print("\n" + text)
            engine.say(text)
            engine.runAndWait()
            triggered.add(today_trigger)

        # Case 2: Before start
        elif current_dt < start_dt and today_trigger not in triggered:
            remaining = int((start_dt - current_dt).total_seconds() // 60)
            text = f"Hello Shree! {task_msg} will start in {remaining} minutes, at {start_str.strip()}"
            print("\n" + text)
            engine.say(text)
            engine.runAndWait()
            triggered.add(today_trigger)

        # Case 3: Late
        elif current_dt > end_dt and today_trigger not in triggered:
            late_by = int((current_dt - end_dt).total_seconds() // 60)
            text = f"Hello Shree! You are late by {late_by} minutes for {task_msg}, scheduled at {task_time}"
            print("\n" + text)
            engine.say(text)
            engine.runAndWait()
            triggered.add(today_trigger)

    time.sleep(1)  # check every second
