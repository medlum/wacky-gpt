import datetime
import requests
import streamlit as st
import pytz


# --------- huggingface api inference for text to speech ----------#

def txt2speech(text):
    print("Initializing text-to-speech conversion...")
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {
        "Authorization": f'Bearer {st.secrets["huggingfacehub_api_token"]}'}
    payloads = {'inputs': text}

    response = requests.post(API_URL, headers=headers, json=payloads)

    with open('audio.mp3', 'wb') as file:
        file.write(response.content)


# --------- bucket time for chatbot greetings  ----------#

def get_time_bucket():

    gmt = pytz.timezone('GMT')
    now_gmt = datetime.datetime.now(gmt)
    hour = now_gmt.hour  # now = datetime.datetime.now()
    sg_time = 8  # Singapore is UTC+8

    if hour + sg_time < 12:
        return "Morning greetings!"
    elif hour + sg_time < 17:
        return "Good afternoon!"
    else:
        return "Good evening!"
