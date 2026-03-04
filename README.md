# 🌾 Agriculture RAG Chatbot

An AI-powered Agriculture Question Answering Chatbot built using **FastAPI + FAISS + LLM (RAG Architecture).**

This system helps farmers, agriculture students, and researchers get accurate answers about:

- Crops
- Soil management
- Fertilizers
- Irrigation
- Pest control
- Farming techniques

It uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant agricultural documents and generate intelligent responses grounded in real data.

---

## 🧠 How It Works (RAG Architecture)

1. Agriculture documents (PDF / Text) are loaded  
2. Text is split into chunks  
3. Embeddings are created  
4. FAISS stores vectors  
5. User asks a question  
6. Relevant chunks are retrieved  
7. LLM generates final answer using retrieved context  

---

## 🏗️ Project Folder Structure

```
Agriculture-RAG-Chatbot/
│
├── backend/
│   ├── app.py
│   ├── rag_engine.py
│   ├── vector_store.py
│   ├── document_loader.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env
│
├── data/
│   └── agriculture_docs/
│
├── frontend/ (optional)
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── venv/
├── README.md
└── .gitignore
```

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/MushfiqurRashid/Agriculture-RAG-Chatbot.git
cd Agriculture-RAG-Chatbot
```

### 2️⃣ Create Virtual Environment

#### Windows

```bash
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

#### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4️⃣ Setup Environment Variables

Create a `.env` file inside the `backend` folder:

```
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
```

---

## 📚 Add Agriculture Documents

Place PDFs or text files inside:

```
data/agriculture_docs/
```

---

## 🚀 Run Backend Server

```bash
uvicorn backend.app:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

Swagger Docs:

```
http://127.0.0.1:8000/docs
```

---

## 💬 API Usage

### POST `/chat`

### Request Body

```json
{
  "session_id": "12345",
  "message": "What fertilizer is best for rice crops?"
}
```

### Response Example

```json
{
  "response": "Nitrogen-based fertilizers like urea are commonly used for rice...",
  "source_documents": [
    "Rice cultivation guide 2023",
    "Soil nutrition manual"
  ]
}
```

---

## 🛠️ requirements.txt Example

```
fastapi
uvicorn
langchain
faiss-cpu
openai
python-dotenv
pypdf
tiktoken
```

---

## 🔥 Example Curl Test

```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d "{\"message\":\"How to prevent tomato leaf disease?\"}"
```

---

## 🌍 Deployment (Optional)

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 10000
```

---

## 🎯 Tech Stack

- Python
- FastAPI
- FAISS
- OpenAI / LLM
- LangChain
- HTML/CSS/JS

---

## 👨‍💻 Author

**Mushfiqur Rashid**  
GitHub: https://github.com/MushfiqurRashid

---

## 📜 License

MIT License
