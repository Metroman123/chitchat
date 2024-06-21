# NOT ALL LIBRARIES ARE BEING UTILIZED
import tkinter as tk
from tkinter import *
import speech_recognition as sr
import pyaudio
import tiktoken
import librosa as lb
import requests
import os
import tkinter
from pydub import AudioSegment
import winsound
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

# Speech Recognition Initiation
MODEL_PATH = "vosk-model-small-en-us-0.15"
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)
speech = sr.Recognizer()
text = None

# Main TKinter Initiation
main = tk.Tk()
main.geometry("400x400")
main.resizable(False, False)
main.title("ChitChat")
main.configure(background='lightblue')

# Global Variables
pressed = False
held = False
MAX_LENGTH = 3000
p = pyaudio.PyAudio()
devices = p.get_device_count()
print(devices)

# Image Initiation
height = main.winfo_screenheight()
width = main.winfo_screenwidth()
bg_photo = ImageTk.PhotoImage(Image.open("background.png"))
main.bg_image = bg_photo
bg_label = tk.Label(main, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

image = Image.open("chitchat.png")
image = image.resize((100, 100), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(image)
canvas = tk.Label(main, image=photo, bg="black")
canvas.place(x=80, y=10)

label = Label(main)
label.place(relx=0.5, rely=0.5, anchor="center")

#Context Variable
conversation_history = []

# Software TopBar System
menu = tk.Menu(main)
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Export")
file_menu.add_command(label="Settings")
file_menu.add_command(label="Exit", command=quit)
main.config(menu=menu)


# Function so the send button can be used just by pressing enter.



# Function for when voice chat button is pressed
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


# Function for when user speech to text is collected.
def release():
    global pressed, held,text, conversation_history, MAX_LENGTH
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
    if len(conversation_history) > MAX_LENGTH:
        middle_index = len(conversation_history) // 2
        conversation_history = conversation_history[:middle_index] + conversation_history[-middle_index:]

# Function for Text Chat
def Chat():
    global text, conversation_history, MAX_LENGTH
    winsound.PlaySound("Audio/Mouse_click_noise.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
    user_input = entry.get()
    if user_input:
        entry.delete(0, tk.END)  # Clear the entry box

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
                {"role": "user", "content": f""" {user_input}
    
                                 """}
            ]
        }

        response = requests.post(url, json=payload, headers=headers)
        extracted_response = response.text
        clean_response = extracted_response.replace(r"\n", "\n").replace("\"", "").replace("\\", "")
        print(clean_response)

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": clean_response})
        reply_text.config(state='normal')  # Enable the text widget temporarily
        reply_text.delete('1.0', tk.END)  # Clear the text widget
        reply_text.insert(tk.END, clean_response)
        reply_text.config(state='disabled')  # Disable the text widget again
        winsound.PlaySound("Audio/Chatroom_Received2.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        return clean_response
        print(conversation_history)
        if len(conversation_history) > MAX_LENGTH:
            middle_index = len(conversation_history) // 2
            conversation_history = conversation_history[:middle_index] + conversation_history[-middle_index:]
def on_enter(event):
    user_input = entry.get()
    if user_input:
        Chat()

def exit():
    quit()




# Text Windows and Buttons
entry = tk.Entry(main, width=30,relief="solid")
entry.bind('<Return>', lambda event: Chat())
entry.bind('<KP_Enter>', lambda event: Chat())
entry_label = tk.Label(main, text="Type here: ", bg="lightblue")
entry_label.pack(side=tk.LEFT, anchor=tk.SW)
entry.pack(side=tk.BOTTOM, anchor=tk.SW)


reply_text = tk.Text(main, height=15,width=35, state="disabled", relief="solid", font=("Arial", 10), wrap="word")
reply_text.place(relx=0, rely=0.65, anchor="w")

send_button = tk.Button(main, text="Send", command=Chat)
send_button.config(height=1)
send_button.place(relx=0.72, rely=1, anchor="se")
talkButton = tk.Button(main, text="Voice Chat", padx=10, pady=30,command=Hold, bg='red',anchor="e", fg='white',)
talkButton.place(relx=1, rely=1, anchor="se")

label.pack()
main.mainloop()
