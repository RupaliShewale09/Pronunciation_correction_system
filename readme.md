# 🎙️ Pronunciation Correction System

An advanced **AI-powered Pronunciation Correction System** designed to help users improve their spoken English through intelligent speech analysis, phonetic evaluation, and grammar feedback.

The system leverages **Automatic Speech Recognition (ASR)** and modern **Machine Learning models** to provide:

- Real-time pronunciation analysis
- Phoneme-level evaluation
- AI-assisted grammar correction
- Personalized learning feedback

---

## 🚀 System Modes

The application provides two learning modes tailored for different user needs.

##  1️⃣ Quick Start Mode

Designed for **instant pronunciation feedback without storing user data**.

### Features

- Users can choose between:
  - **Rule-Based Engine** (using Vosk)
  - **ML-Based Engine** (using Whisper)

- Provides immediate pronunciation validation.
- Displays whether the spoken word is **correct or incorrect**.
- Includes **audio playback** for the correct pronunciation.

This mode is ideal for **quick practice and instant feedback**.



## 2️⃣ Practice Mode (ML-Driven)

A **structured learning environment** focused on long-term improvement.

### Features

- Uses the **ML-based Whisper engine exclusively** for maximum accuracy.
- Tracks **user progress over time**.
- Detects **specific mispronounced words**.
- Provides **AI-generated insights and improvement tips**.
- Includes **Text-to-Speech (TTS)** to help users learn correct pronunciation.

This mode is ideal for **serious learners aiming to improve pronunciation gradually**.

---

## 🧠 Models

## 🔹 ML-Based Engine (Primary Engine)

The system uses a **fine-tuned Whisper model** to improve pronunciation evaluation.

### Key Highlights

- The base Whisper model is **fine-tuned to detect subtle pronunciation differences**.
- Provides **context-aware speech recognition**.
- Performs **deep phonetic evaluation**.
- Generates **highly accurate transcription results**.

This engine is particularly suitable for **advanced pronunciation learning**.


## 🔹 Rule-Based Engine

- Powered by **Vosk**
- Uses the **CMU Pronouncing Dictionary (cmudict)** for phoneme comparison.
- Performs **phoneme-level pronunciation validation**.
- Lightweight and fast for **low-resource environments**.


## 🔹 AI Assistance

AI capabilities are integrated using:

- **Google Gemini API** for:
  - Grammar correction
  - Sentence improvement suggestions
  - Personalized AI tutoring

---

# 🛠️ Technology Stack

### 🔹 Backend

* Flask – Web framework
* Flask-SQLAlchemy – Database ORM
* Flask-JWT-Extended – JWT-based authentication

### 🔹 Speech Processing

* Whisper – ML-based high-accuracy transcription
* Vosk – Lightweight rule-based ASR engine
* Librosa – Audio preprocessing
* Pydub – Audio normalization
* CMU Pronouncing Dictionary (cmudict) – Phonetic comparison

### 🔹 AI Integration

* Google Gemini API – Grammar checking and AI tutoring

### 🔹 Frontend

* HTML templates
* Dashboard interface
* AI Tutor panel

---

## ✨ Features

- **Dual Engine Flexibility:** Switch between rule-based speed and ML-based precision.

- **Phonetic Comparison:** Detailed analysis of spoken phonemes against standard English.

- **Grammar Analysis:** Automatically identifies tense and sentence structure errors.

- **Interactive AI Tutor:** Offers structured feedback and a personalized roadmap for improvement.

---


## 🔧 Installation Guide

### Step 1: Clone the Repository

git clone https://github.com/RupaliShewale09/Pronunciation_correction_system.git
cd Pronunciation_correction_system

### Step 2: Install Dependencies

pip install -r requirements.txt

### Step 3: Configure Environment Variables

Create a `.env` file and add:

<pre>
GEMINI_API_KEY=your_api_key
SECRET_KEY=your_flask_secret
JWT_SECRET_KEY=your_jwt_secret
</pre>

### Step 4: Run the Application

> python app.py

The app will run at:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---


## 📌 Future Enhancements

* 📱 Mobile-responsive UI
* 📊 Advanced pronunciation scoring algorithm
* 🌍 Multi-language pronunciation support
* 🎤 Real-time streaming evaluation
* 📈 AI-driven personalized learning roadmap
