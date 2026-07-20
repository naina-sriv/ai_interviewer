# 🤖 AI Interviewer: End-to-End Architecture & Interview Guide

This document serves as both a comprehensive explanation of how this project works from bare bones and a master guide for defending this architecture in a technical interview.

## 🏗️ 1. Project Overview & Tech Stack

This project is a real-time, voice-conversational AI Interviewer that mimics a human recruiter. It reads a candidate's resume, generates tailored questions (augmented by real company data), listens to the candidate's spoken answers, and dynamically generates follow-up questions.

### The Stack (Bare Bones)
* **Frontend:** React + Vite (Handles UI state and native browser Web Audio APIs).
* **Backend:** Python + FastAPI (Handles routing, PDF extraction, and prompt engineering).
* **State Management:** Redis (Persists session state across serverless instances).
* **AI Engine:** Llama 3.3 70B via Groq API (Ultra-low latency LLM inference).
* **Hosting:** Vercel (Serverless edge deployment).

---

## 🌊 2. How Data Flows (What is happening where?)

### Phase A: Initialization (The Setup)
1. **User Input (Frontend):** The candidate uploads their Resume (PDF), enters the Job Title, Job Description, and optionally, a Target Company (e.g., "Google").
2. **Text Extraction (Backend):** FastAPI receives the PDF and uses `PyPDF2` to extract the raw string text.
3. **RAG Injection (Backend):** If the candidate typed "Google", the backend queries a local mock database (`company_db.py`) and retrieves 5 actual Google interview questions.
4. **Prompt Assembly (Backend):** The backend merges the Resume, Job Description, and Google Questions into a massive System Prompt.
5. **LLM Generation (Groq):** The LLM generates a personalized introduction script and the core interview questions in a strict JSON format.
6. **State Storage (Redis):** The backend saves these questions in Redis under a unique `session_id` and returns the ID to the frontend.

### Phase B: The Conversational Loop (The Interview)
1. **Text-to-Speech (Frontend):** The frontend fetches the question text. It uses the native `window.speechSynthesis` API to speak the question out loud, specifically filtering for natural-sounding voices (like Microsoft Aria).
2. **Speech-to-Text (Frontend):** Once the AI stops speaking, `window.SpeechRecognition` activates the user's microphone. 
3. **Silence Detection (Frontend):** A 3-second debounce timer runs. Every time the user speaks a syllable, the timer resets. When the user pauses for 3 full seconds, the app assumes they are done answering and automatically POSTs the transcribed text to the backend.
4. **Evaluation & Follow-up (Backend & Groq):** The backend pulls the current session from Redis. It sends the user's answer to Groq and asks the AI to evaluate it and generate a dynamic follow-up question.
5. **Loop:** The new question is saved to Redis, sent to the frontend, spoken aloud, and the cycle repeats.

---

## 🛡️ 3. Fail Safes & Edge Cases Handled

To make this application production-ready, several critical fail safes were implemented:

### 1. The Chrome TTS Cutoff Bug
* **The Problem:** Google Chrome has a known bug where `speechSynthesis` abruptly stops speaking if the text takes longer than 15 seconds to read.
* **The Fail Safe:** A background `setInterval` keep-alive was implemented in `audio.js` that briefly pauses and resumes the speech engine every 10 seconds, preventing Chrome from garbage-collecting the audio stream.

### 2. The Chrome STT Auto-Stop Bug
* **The Problem:** Chrome's `SpeechRecognition` will automatically turn off the microphone if it hears absolute silence for ~5 seconds, breaking the interview flow.
* **The Fail Safe:** An `onend` event listener was attached to the microphone. If the microphone turns off but the app is still in the `LISTENING` state, the frontend catches the drop and instantly issues a `recognition.start()` command to reboot the mic without the user noticing.

### 3. The Empty Text Deadlock
* **The Problem:** If the user coughed, the microphone might capture empty noise, wait 3 seconds, and submit an empty string to the backend. The backend would fail, locking the app forever.
* **The Fail Safe:** The frontend checks if the transcribed text `!finalText.trim()`. If it's empty, it ignores the submission, keeps the microphone on, and waits for actual words.

### 4. Serverless State Amnesia
* **The Problem:** Vercel tears down the Python backend after every HTTP request. If we stored the interview questions in a standard Python dictionary, they would be deleted before the user finished answering the first question.
* **The Fail Safe:** All session state (current question index, follow-up count, generated questions) is serialized to JSON and pushed to **Upstash Redis**. When the next request comes in, the backend pulls the state back from Redis.

---

## 🧠 4. Interview Defense Guide

If you are asked about this project in an interview, here are the key concepts you must be prepared to defend:

### "Why did you use RAG instead of Fine-Tuning?"
> *"I used a lightweight Retrieval-Augmented Generation (RAG) pattern to inject company-specific questions into the prompt. Fine-tuning is used to teach a model a new behavior or tone, which is expensive and slow. RAG is used to give a model factual, up-to-date knowledge. By injecting real Google questions into the prompt, I grounded the LLM and prevented it from hallucinating generic questions."*

### "How would you scale the RAG pipeline to 1 million questions?"
> *"Currently, I use a hardcoded Python dictionary as a mock database. To scale, I would build a true vector pipeline. Offline, I would embed 1 million questions into vectors using an embedding model (like `all-MiniLM-L6-v2`) and store them in a Vector Database like Qdrant. At runtime, when the user types 'Google', I would embed their query and perform a Cosine Similarity search in Qdrant to retrieve the top 5 most mathematically relevant questions in milliseconds."*

### "Why didn't you use chunking for the resume?"
> *"Chunking is only necessary when a document is larger than the LLM's context window. A standard resume is 1-2 pages (under 1,000 tokens). Llama 3.3 has a 128,000 token context window. It is an anti-pattern to chunk data that already fits completely inside the context window, because sending the full document gives the LLM 100% perfect context without data loss."*

### "Why Groq instead of OpenAI?"
> *"For a voice-conversational AI, latency is the most critical metric. If there is a 3-second delay, the illusion of a conversation breaks. Groq uses specialized hardware called LPUs (Language Processing Units) that generate tokens significantly faster than traditional GPUs, allowing the backend to evaluate the answer and generate a follow-up almost instantaneously."*
