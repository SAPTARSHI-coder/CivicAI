<div align="center">

# 🏛️ CivicAI

**An AI-powered public service assistant bridging the gap between citizens and government.**

[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-blue?style=for-the-badge&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-FFA700?style=for-the-badge)](https://deepmind.google/technologies/gemini/)
[![Ollama](https://img.shields.io/badge/AI-Local_Gemma_4-white?style=for-the-badge)](https://ollama.com/)

*CivicAI helps citizens understand dense official documents, check their eligibility for government programs, and get personalized, step-by-step action plans in their native language.*

**This Project was done by Team Code_Crafters, as their Hackathon Submission for MLH HackDays, hosted by Major League Hacking and GDG on Campus Techno Mains Salt Lake.**

</div>

---

## ✨ Features

- **📄 Document Analysis**: Upload any official PDFs or scanned images. Our pipeline handles parsing and OCR automatically.
- **🧠 Dual AI Engine Architecture**: 
  - ☁️ **Google Gemini API**: Blazing fast, cloud-hosted intelligence.
  - 🔒 **Local Gemma 4 (Ollama)**: 100% private, on-device inference for sensitive documents.
- **🗣️ Multilingual Support**: Break language barriers. Supports English, Hindi, Bengali, Odia, and more.
- **✅ Eligibility & Checklists**: Automatically extracts eligibility status and generates an actionable checklist.
- **⚠️ Missing Document Detection**: Immediately flags any missing supporting documents required for your application.
- **💬 Voice-Enabled Follow-up Chat**: Ask questions about your document in context, using either text or your voice!

---

## 🏗️ Architecture

CivicAI is built with a modern, decoupled stack to ensure maximum performance and flexibility:

- **Frontend**: React, Vite, Framer Motion (for buttery-smooth micro-interactions)
- **Backend**: FastAPI, PyMuPDF, pytesseract (Robust OCR fallback)
- **LLM Engine**: Dual Provider System (Ollama `gemma4:latest` OR Google Gemini API)

### 🔗 Integrations

- **☁️ Cloudinary**: Used for secure and robust document hosting. When users upload official PDFs or images for analysis, CivicAI uploads them to Cloudinary to generate a persistent URL. This enables the frontend to display the original document side-by-side with the AI-generated explanations and checklists, providing essential context.
- **❄️ Snowflake**: Acts as our highly scalable data warehouse. CivicAI uses Snowflake to securely log user analysis sessions, query histories, and eligibility outcomes. This persistent storage allows for analytics on civic engagement, tracking which schemes are most frequently queried, and identifying common document friction points without slowing down the core user experience.

---

## 🚀 Getting Started

Follow these steps to get CivicAI running on your local machine.

### 1. Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **Tesseract OCR** (System dependency for image parsing. Must be in your system `PATH`)
- **Poppler** (System dependency for PDF-to-image fallback. e.g., `brew install poppler` on macOS or via binaries on Windows)

### 2. Setup the AI Engine (Choose One or Both)

CivicAI gives you the flexibility to use a cloud provider or run entirely locally!

**Option A: Local Privacy (Ollama + Gemma 4)**
If you want to run the model locally on your own hardware:
1. Install [Ollama](https://ollama.com/).
2. Open your terminal and pull the Gemma model:
   ```bash
   ollama pull gemma4:latest
   ollama run gemma4:latest
   ```
   *(Keep Ollama running in the background)*

**Option B: Cloud Speed (Google Gemini API)**
If you prefer the speed and power of Gemini:
1. Navigate to the `backend/` directory.
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

---

### 3. Run the Backend

The FastAPI backend handles document parsing, OCR, and AI routing.

1. Open a new terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment (recommended):
   ```bash
   python -m venv .venv
   
   # On Windows:
   .\.venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Uvicorn development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

### 4. Run the Frontend

The React frontend provides the modern, animated user interface.

1. Open a **second** terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to: **`http://localhost:5173`**

*(Note: API requests from the frontend are automatically proxied to the backend running on port 8000).*

---

## 🛠️ Usage

1. **Upload**: Drag and drop a government PDF or image into the upload zone.
2. **Select Preferences**: Choose your preferred Language and toggle between the **Local Gemma** or **Gemini API** provider.
3. **Analyze**: Click "Analyze Document". The system will parse the text (falling back to OCR if needed) and generate a plain-language summary, eligibility check, and action plan.
4. **Chat**: Use the chat panel on the right to ask follow-up questions about your specific document. Click the microphone icon to ask using your voice!

---
<div align="center">
  <i>Built with ❤️ for Civic Innovation.</i>
</div>
