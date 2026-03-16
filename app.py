import streamlit as st
import time
import base64
import json
import os
import edge_tts
import cv2
import numpy as np
from google import genai
from google.genai import types
import asyncio
import speech_recognition as sr
import io
import soundfile as sf

st.set_page_config(page_title="Digital Museum", page_icon='static/page_icon.png.png')
st.logo("static/Logo.png", size='large')

if "first" not in st.session_state:
    st.session_state.first = True
if "is_change" not in st.session_state:
    st.session_state.is_change = False

bg_placeholder = st.empty()
char_placeholder = st.empty()

if st.session_state.is_change:
    bg_placeholder = st.empty()
    # Note: must make a sleep to make streamlit remove the placeholder (don't use it from cache) (best practice) (these made a small latency but these is the only way if using streamlit)
    time.sleep(0.01)
    st.session_state.is_change = False
    st.rerun()

API = os.getenv("GEMINI_API_KEY")

if "chat" not in st.session_state:
    st.session_state.chat = []
# Default character
if "character" not in st.session_state:
    st.session_state.character = "Karim"
if "old_character" not in st.session_state:
    st.session_state.old_character = ""
if "characters_data" not in st.session_state:
    with open('characters.json', 'r', encoding="utf-8") as file:
        st.session_state.characters_data = json.load(file)
if "is_talk" not in st.session_state:
    st.session_state.is_talk = False
# Defauld Language
if "language" not in st.session_state:
    st.session_state.language = "English"
if "image" not in st.session_state:
    st.session_state.image = None
if "transform" not in st.session_state:
    st.session_state.transform = False

# get intro voices
if st.session_state.character:
    if st.session_state.chat:
        lang = st.session_state.language
        with open(f"intro voices/think_{st.session_state.character}_{lang}.mp3", "rb") as f:
                    st.session_state.audio_bytes = f.read()
    else:
        lang = st.session_state.language
        with open(f"intro voices/greeting_{st.session_state.character}_{lang}.mp3", "rb") as f:
                    st.session_state.audio_bytes = f.read()

if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API)

if "change_character" in st.session_state:
    st.session_state.change_character = False

# Change the character
def change_character(name):
    st.session_state.old_character = st.session_state.character
    st.session_state.character = name
    st.session_state.is_change = True
    st.session_state.is_talk = False
    st.session_state.transform = True
    st.session_state.change_character = True
    st.session_state.chat = []
    # st.rerun()



# Gemini Agent returns the output as stream
# async def chat(text):
#     tools = [
#         {
#             "function_declarations": [
#                 {
#                     "name": "change_character",
#                     "description": "Change the museum character that will speak to the user, if the user asks to talk with a certain charavter.",
#                     "parameters": {
#                         "type": "object",
#                         "properties": {
#                             "name": {
#                                 "type": "string",
#                                 "description": "Character name",
#                                 "enum": [
#                                     "Nefertiti",
#                                     "Isaac Newton",
#                                     "Tut Ankh Amon",
#                                     "Leonardo Davinci"
#                                 ]
#                             }
#                         },
#                         "required": ["name"]
#                     }
#                 }
#             ]
#         }
#     ]

#     st.session_state.chat.append({"role":"user","parts":[{"text":text}]})

#     instructions = (st.session_state.characters_data.get(st.session_state.character, {})).get('prompt', '') + f"\nTalk with {st.session_state.language} language"
#     # instructions = f.read()
#     if "agent_session" not in st.session_state or st.session_state.change_character:
#         st.session_state.agent_session = st.session_state.client.aio.chats.create(
#             model="gemini-3.1-flash-lite-preview",
#             config=types.GenerateContentConfig(
#                 system_instruction=instructions,
#                 tools=tools
#             )
#         )
#         st.session_state.change_character = False

#     stream = await st.session_state.agent_session.send_message_stream(text)

#     async for chunk in stream:
#         parts = chunk.candidates[0].content.parts
        
#         if parts[0].function_call:
#             name = parts[0].function_call.args['name']
#             change_character(name)
#             time.sleep(0.1)
#             st.rerun()
            
#         if chunk.text:
#             yield chunk
async def chat(text):
    # client = genai.Client(api_key=API)
    tools = [
        {
            "function_declarations": [
                {
                    "name": "change_character",
                    "description": "Change the museum character that will speak to the user, if the user asks to talk with a sertain charavter.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Character name",
                                "enum": [
                                    "Nefertiti",
                                    "Isaac Newton",
                                    "Tut Ankh Amon",
                                    "Leonardo Davinci"
                                ]
                            }
                        },
                        "required": ["name"]
                    }
                }
            ]
        }
    ]
    st.session_state.chat.append({"role":"user","parts":[{"text":text}]})
    if st.session_state.character:
        instructions = (st.session_state.characters_data.get(st.session_state.character, {})).get('prompt', '') + f"\nTalk with {st.session_state.language} language"
    else:
        with open("main prompt.txt", 'r') as f:
            instructions = f.read()
    stream = st.session_state.client.models.generate_content_stream(
        model="gemini-3.1-flash-lite-preview",
        contents=st.session_state.chat,
        config=types.GenerateContentConfig(
            system_instruction=instructions,
            tools=tools
        )
    )
    for chunk in stream:
        parts = chunk.candidates[0].content.parts
        # for part in parts:
        if parts[0].function_call:
            name = parts[0].function_call.args['name']
            # st.write(parts[0].function_call.args['name'])
            change_character(name)
            time.sleep(0.1)
            st.rerun()
        if chunk.text:
            yield chunk

# st.write(st.session_state.chat)

# Decribe images using Gemini and return output as stream
async def image_recognition(image_bytes):
    "Return the description of an image"
    instructions = f"""Identify the content of this image and retrieve its name and description.\nYou must make your response in small sentences and add at the end of each sentence a dot '.'\nAlways answers in {st.session_state.language}"""
    stream = st.session_state.client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            ),
            instructions
        ]
    )

    for chunk in stream:
        if chunk.text:
            yield chunk

# Voice to Text using Speech_Recognition in Arabic and English
def speech_to_text(path, language):
    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
    if language == 'Arabic':
        text = recognizer.recognize_google(audio, language="ar-EG")
    else:
        text = recognizer.recognize_google(audio, language="en-US")
    return text

# convert video to base64 format
def get_video_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Shows background videos for each character / setting up the environment
def set_bg_video(video_path, char_name):
    path = os.path.basename(video_path)
    path = f"app/static/{path}"
    clean_name = char_name.replace(" ", "_")
    video_id = f"bg-vid-{clean_name}"
    html = f"""
    <style>
    #{video_id} {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        object-fit: cover;
        z-index: -1;
        pointer-events: none;
    }}
    .stApp {{ background: transparent; }}
    </style>
    <video id="{video_id}" autoplay loop muted playsinline>
        <source src="{path}" type="video/webm">
    </video>
    """
    bg_placeholder.markdown(html, unsafe_allow_html=True)

# Show the both character videos idle and talk make one visible and the other not
def show_character_video(idle_path, talk_path, is_talk):
    idle_file = os.path.basename(idle_path)
    talk_file = os.path.basename(talk_path)
    idle_url = f"app/static/{idle_file}"
    talk_url = f"app/static/{talk_file}"
    idle_css = "display: block;" if not is_talk else "display: none;"
    talk_css = "display: block;" if is_talk else "display: none;"

    html_code = f"""
    <div id="character-container" style="
    position: fixed; 
    top: 55%; 
    left: 50%; 
    transform: translate(-50%, -50%); 
    width: 270px; 
    height: 200px; 
    display: flex; 
    justify-content: center; 
    align-items: center;
    pointer-events: none;">
    <video id="idle-video" autoplay loop muted playsinline 
        style="{idle_css} width: 100%; height: auto; background: transparent;">
        <source src="{idle_url}" type="video/webm">
    </video>
    
    <video id="talk-video" autoplay loop muted playsinline 
        style="{talk_css} width: 100%; height: auto; background: transparent;">
        <source src="{talk_url}" type="video/webm">
    </video>
    </div>
    """
    char_placeholder.columns([1, 2, 1])[1].markdown(html_code, unsafe_allow_html=True)

# Create a golden frame arround the uploaded image to view in the museum using opencv
def make_frame(img):
    img = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    if h>w:
        frame = cv2.imread("static/vertical_frame.png", cv2.IMREAD_UNCHANGED)
        x, y = 50, 110
        w, h = 450, 600
    else:
        frame = cv2.imread("static/horizontal_frame.png", cv2.IMREAD_UNCHANGED)
        x, y = 100, 100
        w, h = 600, 400
    img_crop = cv2.resize(img, (w, h))
    result = np.zeros_like(frame)
    result[y:y+h, x:x+w, :3] = img_crop
    result[y:y+h, x:x+w, 3] = 255
    alpha = frame[:, :, 3] / 255.0
    for c in range(3):
        result[:, :, c] = result[:, :, c] * (1 - alpha) + frame[:, :, c] * alpha
    result[:, :, 3] = np.maximum(result[:, :, 3], frame[:, :, 3])
    result = result.astype(np.uint8)
    cv2.imwrite("result.png", result)
    return "result.png"

# Main code show characters and backgrounds
if st.session_state.character:
    if st.session_state.is_talk:
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button(":material/stop: Stop", type='tertiary') and st.session_state.is_talk:
                st.session_state.is_talk = False
                st.session_state.image = None
                st.rerun()
        with col3:
            html_block = """
            <div style="
                text-align: {align};
                padding: 10px;
                border-radius: 8px;
                font-size: 15px;
                line-height: 1.6;
                color: white;
                background:rgba(0,0,0,0.4);                
                backdrop-filter: blur(6px);
                height:{height};
                overflow:auto;
            ">
            {content}
            </div>
            """
            placeholder = st.empty()

    char_data = st.session_state.characters_data.get(st.session_state.character, {})
    back_path = char_data.get('background_path', '')
    idle_path = char_data.get('idle', '')
    talk_path = char_data.get('talk', '')
    name = char_data.get('Name', '')

    if st.session_state.transform and st.session_state.old_character == "Karim":
        set_bg_video(f"{name}_transform.webm", f"{name}_transform")
        st.session_state.transform = False
        time.sleep(4.9)
        st.session_state.is_change = True
        st.rerun()
    set_bg_video(back_path, st.session_state.character)

    show_character_video(
        idle_path = idle_path, 
        talk_path = talk_path, 
        is_talk = st.session_state.is_talk
    )

else:
    set_bg_video("intro.webm","intro")
    st.header("Smart Digital Museum")
    text = """Welcome to the digital museum.
    \nAre you ready to a time travil and talks with your favorite historical people."""
    placeholder = st.empty()
    html_block = """<div style="
        text-align: justify;
        padding: 5px;
        border-radius: 5px;
        font-size: 18px;
        line-height: 1.4;
        color: #ffffff;">
        {content} </div>"""
    streamed_text = ""
    if not st.session_state.first:
        placeholder.markdown(html_block.format(content=text), unsafe_allow_html=True)
    st.write("---")


# Sidebar
# ==========================================
with st.sidebar:
    st.title(":orange[**Characters**] to choose")
    st.caption("Select a character to talk with...")
    st.divider()
    with open('characters_types.json', 'r') as file:
        character_types = json.load(file)
    for t in character_types:
        with st.expander(character_types[t]['header'], expanded=True):
            for c in range(len(character_types[t]['names'])):
                st.subheader(character_types[t]['names'][c], divider='grey')
                col1, col2 = st.columns([1,1])
                with col1:
                    st.image(character_types[t]['icons'][c])
                with col2:
                    st.write("");st.write("");st.write("")
                    st.write(character_types[t]['description'][c])
                    if st.button(f"Talk with {character_types[t]['names'][c].split(' ')[0]}", type='tertiary'):
                        st.write(f":orange[:material/check:] You choose {character_types[t]['names'][c].split(' ')[0]}")
                        change_character(character_types[t]['names'][c])
                        if not st.session_state.first:
                            if st.button("Apply changes", type='primary'):
                                st.session_state.is_change = True
                                st.rerun()
                if len(character_types[t]['names']) > 1:
                    st.divider()
    if st.button(":material/restart_alt: Reset character settings", type='tertiary'):
        if st.session_state.character != "Karim":
            change_character('Karim')
            if st.button("Apply changes ", type='primary'):
                st.session_state.is_change = True
    st.text_input(" ", placeholder='Search...')
    st.write("")
    st.divider()
    st.header(":material/settings: Settings")
    new_lang = st.selectbox(f"**Language** (current is {st.session_state.language})", ('Arabic', 'English'), placeholder='Language..', index=None)
    if new_lang and new_lang != st.session_state.language:
        st.write(f"Language will be change into :orange[{new_lang}]")
        if st.button("Save changes", type='primary'):
            st.session_state.language = new_lang
            st.rerun()


# Edge TTS (Text to Speech in special voices)
async def generate_tts(text, gender, language = st.session_state.language):
    if text:
        if language=='Arabic':
            if gender=='Male':
                communicate = edge_tts.Communicate(text=text,voice="ar-EG-ShakirNeural")
            else:
                communicate = edge_tts.Communicate(text=text,voice="ar-EG-SalmaNeural")
        else:
            voice = st.session_state.characters_data.get(st.session_state.character, {}).get('voice', '')
            
            communicate = edge_tts.Communicate(text=text, voice=voice)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes

# Get Audio time in seconds
def get_audio_duration(audio_bytes):
    data, samplerate = sf.read(io.BytesIO(audio_bytes))
    duration = len(data) / samplerate
    return duration

# play audio sequentially
async def play_audio_bytes(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


if not st.session_state.character:
    for m in st.session_state.chat:
        if m['role'] == "human":
            st.chat_message("user").markdown(m['parts'][0]['text'])
        else:
            st.chat_message("assistant").markdown(m['parts'][0]['text'])

# Spaces to justify page layout (make the chatbar fixed in its place when talk or not)
if not st.session_state.is_talk:
    st.space(340)
else:
    st.space(100)
    placeholder.markdown(html_block.format(align = "justify", content='', height='240px'), unsafe_allow_html=True)

# Chat
with st.columns([0.1,20,0.1])[1]:
    message = st.chat_input("Say something", accept_file=True, file_type=["jpg", "jpeg", "png"], accept_audio=True)

if message:
    # get images input
    if message.files:
        st.session_state.image = message.files[0].read()
        st.session_state.is_talk = True
        st.rerun()
    # get text input
    if message.text:
        if st.session_state.character:
            st.session_state.text = message.text
            st.session_state.is_talk = True
            st.rerun()
        else:
            async def chatting():
                full_text = ""
                async for chunk in chat(message.text):
                    full_text += chunk.text
                st.session_state.chat.append({"role":"model","parts":[{"text":full_text}]})
                st.rerun()
            asyncio.run(chatting())
    # get voice input
    if message.audio:
        with open("user_voice.mp3", "wb") as f:
            f.write(message.audio.read())
        text = speech_to_text("user_voice.mp3", st.session_state.language)
        st.session_state.text = text
        st.session_state.is_talk = True
        st.rerun()

if st.session_state.is_talk and not st.session_state.image:
    text_placeholder = st.empty()
    delimiters = ['.', '?', '!', '\n']
    async def main():
        text = ""
        t = ""
        full_text = ""
        gender = (st.session_state.characters_data.get(st.session_state.character, {})).get('gender', '')
        await play_audio_bytes(st.session_state.audio_bytes)
        duration = get_audio_duration(st.session_state.audio_bytes)
        await asyncio.sleep(max(0, duration-1))

        async for chunk in chat(st.session_state.text):
            full_text += chunk.text
            text += chunk.text
            placeholder.markdown(html_block.format(align = "right" if st.session_state.language=="Arabic" else "justify", content=full_text, height='240px'), unsafe_allow_html=True)
            # delimiters = ['،', ',', '.', '?', '!', '\n']
            for d in delimiters:
                if d in text:
                    t = text.split(d, maxsplit=1)[0].strip()
                    text = text.split(d, maxsplit=1)[1].strip()
                    break
            if t:
                audio_bytes = await generate_tts(t.strip().replace('*','').replace('#',''), gender)
                await play_audio_bytes(audio_bytes)
                duration = get_audio_duration(audio_bytes)
                if st.session_state.language == 'Arabic':
                    if gender == "Male":
                        await asyncio.sleep(max(0, duration-1))
                    else:
                        await asyncio.sleep(max(0, duration-1))
                else:
                    if gender == "Male":
                        await asyncio.sleep(max(0, duration-1))
                    else:
                        await asyncio.sleep(max(0, duration-1))

                t = ""
        if text.strip():
            audio_bytes = await generate_tts(text.strip(), gender)
            await play_audio_bytes(audio_bytes)
            duration = get_audio_duration(audio_bytes)
            await asyncio.sleep(duration-1)
    
        if st.session_state.language == 'Arabic':
            if gender == "Male":
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(2)
        st.session_state.chat.append({"role":"model","parts":[{"text":full_text}]})
    asyncio.run(main())
    st.session_state.is_talk = False
    st.rerun()

if st.session_state.image:
    async def main():
        text = ""
        t = ""
        full_text = ""
        gender = (st.session_state.characters_data.get(st.session_state.character, {})).get('gender', '')
        with open(f"intro voices/see_{st.session_state.character}_{lang}.mp3", "rb") as f:
                    audio_bytes = f.read()
        await play_audio_bytes(audio_bytes)
        duration = get_audio_duration(audio_bytes)
        await asyncio.sleep(max(0, duration-1))
        path = make_frame(st.session_state.image)
        col1, col2 = st.columns([1,1])
        with col1:
            if st.session_state.language == 'Arabic':
                img_placeholder = st.empty()
            else:
                st.image("result.png",caption="Your Antique")
        # ===============================================================
        with col2:
            if st.session_state.language == 'Arabic':
                st.image("result.png",caption="Your Antique")
            else:
                img_placeholder = st.empty()
        async for chunk in image_recognition(st.session_state.image):
            full_text += chunk.text
            text += chunk.text
            placeholder.markdown(html_block.format(align = "right" if st.session_state.language=="Arabic" else "justify" , content=full_text, height='240px'), unsafe_allow_html=True)
            img_placeholder.markdown(html_block.format(align = "right" if st.session_state.language=="Arabic" else "justify" , content=full_text, height='500px'), unsafe_allow_html=True)
            delimiters = ['،', ',', '.', '?', '!', '\n']
            for d in delimiters:
                if d in text:
                    t = text.split(d, maxsplit=1)[0].strip()
                    text = text.split(d, maxsplit=1)[1].strip()
                    break
            if t:
                audio_bytes = await generate_tts(t.strip().replace('*','').replace('#',''), gender)
                await play_audio_bytes(audio_bytes)
                duration = get_audio_duration(audio_bytes)
                if st.session_state.language == 'Arabic':
                    if gender == "Male":
                        await asyncio.sleep(max(0, duration-1))
                    else:
                        await asyncio.sleep(max(0, duration-1))
                else:
                    if gender == "Male":
                        await asyncio.sleep(max(0, duration-1))
                    else:
                        await asyncio.sleep(max(0, duration-1))

                t = ""
        if text.strip():
            audio_bytes = await generate_tts(text.strip(), gender)
            await play_audio_bytes(audio_bytes)
            duration = get_audio_duration(audio_bytes)
            await asyncio.sleep(duration-1)
    
        if st.session_state.language == 'Arabic':
            if gender == "Male":
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(2)
        st.session_state.chat.append({"role":"model","parts":[{"text":full_text}]})

    asyncio.run(main())
    st.session_state.is_talk = False
    st.session_state.image = None
    st.rerun()

if st.session_state.first:
    st.session_state.first = False
