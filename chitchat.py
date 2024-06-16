import tkinter as tk
from tkinter import *
import speech_recognition as sr
import pyaudio
import requests
import tkinter
from elevenlabs import Voice, VoiceSettings, voice_generation, play, voices
import customtkinter
from tkinter import ttk
from pyaudio import *
import io
from elevenlabs.client import ElevenLabs
import torch
from env import ELEVEN_LABS_API_KEY, PERSONALITY, VOICE
import vosk
import queue
from PIL import Image, ImageTk
import json
import time
from vispy import app, gloo
import numpy as np
MODEL_PATH = "vosk-model-small-en-us-0.15"
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)
speech = sr.Recognizer()
text = None
main = tk.Tk()
main.geometry("200x300")
main.resizable(False, False)
main.title("ChitChat")
main.configure(background= 'white')
pressed = False
held = False
p = pyaudio.PyAudio()
devices = p.get_device_count()
print(devices)

height = main.winfo_screenheight()
width = main.winfo_screenwidth()
image = Image.open("bot2.png")
image = image.resize((100, 100), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(image)

label = Label(main, image=photo)
label.place(relx=0.5, rely=0.5, anchor="center")

conversation_history = []

def Hold():
    global pressed, held, text
    pressed = True
    print("Listening....")
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()


    while pressed == True:
        data = stream.read(4096)
        if recognizer.AcceptWaveform(data):
            results = recognizer.Result()
            if results:
                text = json.loads(results)["text"]
                print(text)
                time.sleep(1)
                release()

def release():
    global pressed, held,text
    pressed = False
    held = False
    url = "http://192.168.50.22:8000/generate/"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {"role": "system",
             "content": f"{PERSONALITY}"},
            *conversation_history,
            {"role": "user", "content": f""" {text}

                         """}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    extracted_response = response.text
    clean_response = extracted_response.replace(r"\n", "\n").replace("\"", "").replace("\\", "")
    print(clean_response)

    conversation_history.append({"role": "user", "content": text})
    conversation_history.append({"role": "assistant", "content": clean_response})

    client = ElevenLabs(
        api_key=ELEVEN_LABS_API_KEY,  # Defaults to ELEVEN_API_KEY
    )

    hearing = client.generate(text = clean_response, voice = f"{VOICE}", model="eleven_multilingual_v2")
    audio = play(hearing)



talkButton = tk.Button(main, text="Press to talk", padx=20, pady=20,command=Hold, bg='red',anchor='s', fg='white',)
talkButton.pack(side=tk.BOTTOM)

label.pack()
main.mainloop()
