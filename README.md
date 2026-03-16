# 🏛️ The Voices of History (Interactive Digital Museum)

An AI-powered interactive museum that allows users to talk with historical figures, explore artifacts, and experience history through conversational AI, voice interaction, and computer vision.

---

# 🌍 Overview

The **Interactive Digital Museum** is an immersive AI application that simulates conversations with historical characters such as:

* Historical characters
  * TutAnkhAmun
  * Nefertiti
* Scientific characters
  * Isaac Newton
* Artistic characters
  * Leonardo da Vinci
* Main Character
  * Karim (this virtual character works as the tour guide for the digital museum)

<table align="center">
<tr>
<td align="center">
<img src="static/tut icon.png" width="180"><br>
Tut Ankh Amun
</td>

<td align="center">
<img src="static/nefertiti icon.png" width="180"><br>
Nefertiti
</td>

<td align="center">
<img src="static/newton icon.png" width="180"><br>
Isaac Newton
</td>

<td align="center">
<img src="static/davinci icon.png" width="180"><br>
Leonardo Da Vinci
</td>

</tr>
</table>

Users can interact using **text, voice, or images**, and the system responds with spoken explanations with animation in real time.

The goal of the project is to transform the traditional museum experience into an **interactive AI-driven learning environment**.

---

# 🎯 Key Features

### 🧠 AI Historical Characters
Talk with famous historical figures who respond according to their personalities and historical context.

### 🎤 Voice Interaction
Users can speak directly to the characters using speech recognition.

### 🔊 AI Voice Responses
The characters respond using natural neural voices.

### 🏞️ Artifact Recognition
Upload an image of an object or artifact and receive an explanation about it.

### ⏳ Real-Time AI Streaming
AI responses are streamed token by token for faster interaction.

### 🎭 Character Animation
Each character has animated states:
* Idle animation
* Talking animation
* Environment background animation

### 🌍 Multilingual Support
Supports:
* English
* Arabic

---

# 🧰 Technologies Used

### AI Models

* Gemini 3.1 Flash Lite (for text conversations)
* Gemini 2.5 Flash (for image recognition and description)

### Backend
* 🐍 Python

### Framework
* Streamlit

### Speech Processing
* Speech Recognition
* Edge TTS (for customizing special voice for each character)

### Computer Vision
* OpenCV
* NumPy
* Gemini 2. flash

### AI Integration
* Google GenAI SDK

---

# 🏗 System Architecture

The application consists of several main components:

1. User Interface (Streamlit)
2. AI Conversation Engine (Gemini)
3. Speech Recognition
4. Text-to-Speech Engine
5. Computer Vision Module
6. Character Management System

---

# 🚀 Installation

Test the project

https://interactive-digital-museum-614445730433.europe-west1.run.app/

Clone the repository

```bash
git clone https://github.com/Abdallah-Fekry/Interactive-Digital-Museum
```

Install dependencies

```bash
pip install -r requirements.txt
```

Set environment variable

```bash
export GEMINI_API_KEY=your_api_key
```

Run the application

```bash
streamlit run test.py --server.enableStaticServing true
```

---

# 🔮 Future Improvements

* Multi-Agent Architecture
* Lip-Sync Character Animation
* 3D Museum Environment
* Mobile Version
* AR/VR Integration

---

# 👨‍💻 Author

Abdallah Fekry

AI/ML Engineer

---

# ⭐ Project Goal

This project demonstrates how **multimodal AI systems** can transform traditional educational experience and museum experience into interactive learning platforms.
