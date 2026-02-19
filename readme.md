# 🎙️ Pronunciation Correction System

An advanced **AI-powered Pronunciation Correction System** designed to help users improve their spoken English through intelligent speech analysis, phonetic evaluation, and grammar feedback.

This system leverages **Automatic Speech Recognition (ASR)** and modern **Machine Learning models** to provide real-time pronunciation accuracy, phoneme-level insights, and AI-driven grammar correction.

---

## 🚀 Overview

The application allows users to record their speech and evaluate pronunciation using two distinct evaluation engines:

* 🧠 **ML-Based Engine (Whisper)**
* ⚡ **Rule-Based Engine (Vosk + CMU Dictionary)**

The backend is built with **Flask**, and the platform provides:

* Accurate speech-to-text transcription
* Word-level pronunciation feedback
* Phonetic comparison
* Grammar analysis using AI
* Personalized learning insights
* Secure user authentication

This makes it a complete **AI-assisted spoken English improvement platform**.

---

## 🛠️ Technology Stack

### 🔹 Backend

* Flask – Web framework
* Flask-SQLAlchemy – Database ORM
* Flask-JWT-Extended – JWT-based authentication

### 🔹 Speech Processing

* Whisper (Transformers + PyTorch) – ML-based high-accuracy transcription
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

### 1️⃣ Dual Evaluation Modes

#### 🧠 ML-Based Mode (Whisper)

* Context-aware speech recognition
* High transcription accuracy
* Deep phonetic evaluation
* Suitable for advanced learners

#### ⚡ Rule-Based Mode (Vosk)

* Lightweight and fast processing
* Phoneme-level pronunciation comparison
* Efficient performance on low-resource systems
* Ideal for quick checks

---

### 2️⃣ Practice Mode

Designed for continuous learning and measurable improvement:

* 📊 Saved progress tracking
* 🎯 Identification of mispronounced words
* 🔊 Built-in Text-to-Speech (TTS) for correct pronunciation
* 📈 Performance monitoring over time

---

### 3️⃣ AI Tutor & Grammar Check

#### 📝 Grammar Analysis

* Automatically analyzes transcript grammar
* Identifies tense and sentence structure errors
* Suggests corrections and improvements

#### 🤖 AI Tutor Interface

* Interactive AI guidance
* Personalized learning suggestions
* Structured improvement feedback

---



## 🔧 Installation Guide

### Step 1: Clone the Repository

git clone <your-repo-link>
cd <project-folder>

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
