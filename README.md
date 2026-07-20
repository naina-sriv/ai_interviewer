# 🤖 AI Interviewer: The Ultimate Architecture & Interview Master Guide

This repository contains a real-time, voice-conversational AI Interviewer. It reads a candidate's resume, generates tailored questions augmented by a company-specific database, listens to spoken answers, and dynamically generates conversational follow-ups.

This `README.md` is designed as a **Master Interview Guide**. If you are reviewing this project, this document explains every technical decision, architecture tradeoff, data flow, fail-safe, and theoretical concept used to build it.

---

## 🏗️ 1. Project Overview & Tech Stack

### The Stack (Bare Bones)
* **Frontend:** React + Vite (Handles UI state and native browser Web Audio APIs).
* **Backend:** Python + FastAPI (Handles routing, PDF extraction, and AI orchestration).
* **State Management:** Upstash Redis (Persists session state across stateless serverless instances).
* **AI Engine:** Llama 3.3 70B via Groq API (Ultra-low latency LLM inference).
* **Hosting:** Vercel (Serverless edge deployment for both frontend and backend).

---

## 🌊 2. How Data Flows (End-to-End)

### Phase A: Initialization & Context Generation
1. **User Input:** The candidate uploads their Resume (PDF), enters the Job Title, Job Description, and optionally, a Target Company (e.g., "Google").
2. **Text Extraction:** FastAPI receives the `multipart/form-data`. It uses `PyPDF2` to extract the raw string text from the PDF.
3. **Retrieval (RAG):** If the candidate typed "Google", the backend queries a local mock database (`company_db.py`) to retrieve real, historically asked Google interview questions.
4. **Prompt Assembly:** The backend constructs a massive System Prompt. It injects the Resume, Job Description, and the retrieved Google Questions. It sets strict formatting constraints (e.g., `response_format: { "type": "json_object" }`).
5. **LLM Generation:** Groq processes the prompt and generates a personalized introduction script and 5 tailored questions.
6. **State Storage:** The backend saves this state (the questions, the current index, the follow-up count) in **Redis** under a unique `session_id`. It returns the ID to the frontend.

### Phase B: The Conversational Loop
1. **Text-to-Speech (TTS):** The frontend fetches the first question. It uses the browser's native `window.speechSynthesis` API to speak the question out loud. A custom filter selects natural-sounding voices (e.g., "Microsoft Aria" or "Google UK Female") instead of robotic defaults.
2. **Speech-to-Text (STT):** Once the TTS finishes, `window.SpeechRecognition` activates the user's microphone in `continuous` mode.
3. **Silence Detection (Debounce):** The app does not require a "Submit" button. A 3-second debounce timer runs in the background. Every time the user speaks a syllable, the timer resets. When the user pauses for 3 full seconds, the app assumes they are done and POSTs the transcribed text to the backend.
4. **Evaluation & Follow-up:** The backend pulls the session from Redis. It sends the user's answer to Groq, instructing the AI to:
   - Evaluate the answer.
   - Generate a conversational acknowledgment (*"That's a great point about scalability..."*).
   - Generate a dynamic follow-up question based on the user's answer.
5. **Loop:** The follow-up is saved to Redis, sent to the frontend, spoken aloud, and the cycle repeats.

---

## ⚖️ 3. Architecture Tradeoffs & "Why" Decisions

### Tradeoff 1: Native Browser Speech APIs vs. Cloud APIs (Whisper / ElevenLabs)
* **The Choice:** I used `window.SpeechRecognition` and `window.speechSynthesis` instead of paying for OpenAI Whisper (STT) or ElevenLabs (TTS).
* **The Why:**
  - **Latency:** Sending audio files over the network to Whisper takes 1-3 seconds. Native browser APIs transcribe locally in real-time (0ms network latency).
  - **Cost:** Native APIs are 100% free. Cloud APIs charge per minute of audio.
  - **Complexity:** Streaming audio bytes from a browser to a Python backend requires WebSockets. By handling speech entirely in the browser, the backend remains a simple REST API that only handles text strings.
* **The Downside:** Browser APIs depend on the user's browser (Chrome works perfectly, Firefox lacks support). Cloud APIs guarantee consistent voice quality across all devices.

### Tradeoff 2: Serverless (Vercel) vs. Stateful Server (EC2 / Render)
* **The Choice:** I deployed the Python FastAPI backend on Vercel (Serverless).
* **The Why:** Serverless is infinitely scalable, requires zero server maintenance, and is free for hobby tiers.
* **The Downside (The "Amnesia" Problem):** Serverless functions spin down immediately after an HTTP response. If I stored the interview questions in a standard Python dictionary `{}`, that memory is wiped before the user answers the first question.
* **The Fix:** I introduced **Redis** as a centralized state store. The stateless serverless function pulls the state from Redis, processes the logic, and saves the new state back to Redis before spinning down.

### Tradeoff 3: Groq (Llama 3) vs. OpenAI (GPT-4o)
* **The Choice:** I chose Groq API hosting Llama 3.3 70B over OpenAI.
* **The Why:** **Time-to-First-Token (TTFT).** In a voice application, if there is a 3-second silence between the user finishing their answer and the AI speaking, the illusion of a conversation breaks. Groq uses proprietary hardware called LPUs (Language Processing Units) that generate text at ~800 tokens per second. The AI response is generated almost instantaneously.

### Tradeoff 4: Lightweight Prompt RAG vs. Vector Database RAG
* **The Choice:** For the company-specific questions, I used a Python dictionary to inject questions directly into the prompt instead of setting up a Vector Database like Qdrant.
* **The Why:** For an MVP portfolio project with only a few companies, a Vector DB is over-engineering. However, in a production environment with 10,000 companies and millions of questions, a Vector DB is mandatory (see the Advanced Questions below for how this works).

---

## 🛡️ 4. Fail Safes & Edge Cases

1. **The Chrome TTS Cutoff Bug:** Chrome aggressively garbage-collects `speechSynthesis` if text takes longer than 15 seconds to read. 
   - *Fix:* Implemented a background `setInterval` keep-alive that briefly pauses and resumes the speech engine every 10 seconds.
2. **The STT Auto-Stop Drop:** Chrome's microphone automatically shuts off if it hears absolute silence for 5 seconds. 
   - *Fix:* Attached an `onend` event listener. If the mic drops but the UI status is still `LISTENING`, the app instantly issues a `recognition.start()` command to reboot the mic invisibly.
3. **The Empty Noise Deadlock:** If the user coughs, the mic captures empty noise, waits 3 seconds, and submits an empty string. The backend errors out, locking the UI forever. 
   - *Fix:* The frontend checks `!finalText.trim()`. If empty, it ignores the submission, keeping the mic active.

---

## 🧠 5. The Ultimate Q&A Defense Guide

If you are asked about GenAI, LLMs, or RAG in an interview, here are the exact answers you need.

### Fundamentals (Level 1)

**Q: What is a Token?**
> A token is the fundamental unit of data processed by an LLM. It is not necessarily a full word; it is usually a chunk of characters. On average, 1 token is about 4 characters of English text. "Apple" is 1 token, but "Unbelievable" might be split into 3 tokens.

**Q: What is the Context Window?**
> The context window is the "short-term memory" of the LLM. It is the maximum number of tokens the model can process in a single request (input + output). In this project, Llama 3.3 has a 128,000 token context window, which means I can comfortably pass an entire 2-page resume (which is only ~1,000 tokens) in a single prompt without chunking it.

**Q: What does Temperature do?**
> Temperature controls the randomness or "creativity" of the model's output. A temperature of 0 makes the model deterministic (it will always pick the most statistically probable next token). A temperature of 1 makes it highly creative. For this project, I used **0.7**, which allows the AI to be conversational and creative, but strict enough to not hallucinate fake interview concepts.

### RAG & Chunking (Level 2)

**Q: What is RAG and why did you use it instead of Fine-Tuning?**
> RAG (Retrieval-Augmented Generation) is a technique where you retrieve external data from a database and inject it into the LLM's prompt. 
> I chose RAG over Fine-Tuning because **Fine-tuning is for teaching a model a new behavior or style**, which is slow and expensive. **RAG is for giving a model factual, up-to-date knowledge.** I didn't need to change how the LLM talks; I just needed it to know specific Google interview questions, which RAG handles perfectly.

**Q: What is an Embedding?**
> An embedding is a mathematical translation of text. It converts a sentence into a high-dimensional vector (an array of thousands of numbers). This allows computers to understand semantic meaning. For example, the vector for "Backend Developer" and the vector for "Server-side Engineer" will be mathematically very close to each other, even though they share no letters.

**Q: What are the different types of Chunking?**
> Chunking is breaking large documents into smaller pieces before vectorizing them.
> 1. **Fixed-size chunking:** Splitting by a hard character limit (e.g., 500 characters).
> 2. **Recursive Character chunking:** The most popular method. It tries to split by paragraphs first, then sentences, then words, to keep related thoughts together.
> 3. **Document-based chunking:** Splitting based on Markdown headers or HTML tags.
> 4. **Semantic chunking:** Using embeddings to detect where the topic of the text naturally shifts, and splitting there.

**Q: Did you chunk the Resume before sending it to the LLM?**
> No! Chunking is an anti-pattern if the document already fits inside the Context Window. A resume is very short. Because modern LLMs have massive context windows (128k+), sending the full document is best practice because it gives the LLM 100% perfect context without data loss.

### Advanced Architecture (Level 3)

**Q: How exactly does a Vector Database find the right data during Retrieval?**
> When a user queries a Vector Database, the backend converts their text query into a vector using an Embedding Model. The Vector DB then uses a mathematical formula—most commonly **Cosine Similarity** or **Euclidean Distance**—to measure the angle or distance between the query vector and millions of stored vectors. It returns the vectors with the smallest distance, which represents the most semantically similar text.

**Q: Walk me through how you would scale your RAG pipeline to 1,000,000 company questions using Qdrant.**
> I would build a two-part pipeline:
> 1. **Offline Ingestion:** I would take a massive CSV of questions. I would run every question through an embedding model (like `all-MiniLM-L6-v2`) to turn it into a vector. I would upload those vectors to Qdrant, attaching metadata "payloads" (like `company="Google"` and `role="Frontend"`).
> 2. **Real-Time Retrieval:** When a user starts an interview for Google Frontend, my backend embeds that query string. I query Qdrant using Cosine Similarity, but I apply a **Metadata Filter** to explicitly only search vectors where `company="Google"`. Qdrant returns the top 5 matches in milliseconds, which I inject into the LLM prompt.

**Q: What is a 'Hallucination' and how did your architecture prevent it?**
> A hallucination is when an LLM confidently fabricates false information. I mitigated this by heavily **grounding** the prompt. I explicitly pass the user's actual resume text and real company questions into the system prompt. I strictly instruct the model: *"Questions must be related ONLY to skills mentioned in the resume and job description."* By forcing the model to rely on provided context rather than its pre-trained memory, hallucinations are drastically reduced. 

**Q: How do you force the LLM to return data that your code can actually parse?**
> I use **Structured Output Constraints**. When calling the Groq API, I pass `response_format: { "type": "json_object" }`. Inside the system prompt, I explicitly define the expected JSON schema (e.g., telling it to return `questions: array`, `introText: string`). This guarantees the LLM returns a parseable JSON string rather than a conversational essay, preventing backend crashes.
