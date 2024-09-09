import requests
import streamlit as st


def txt2speech(text):
    print("Initializing text-to-speech conversion...")
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {
        "Authorization": f'Bearer {st.secrets["huggingfacehub_api_token"]}'}
    payloads = {'inputs': text}

    response = requests.post(API_URL, headers=headers, json=payloads)

    with open('audio.mp3', 'wb') as file:
        file.write(response.content)
