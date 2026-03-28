# 🧠 MediScan AI  
**AI Health Report Explainer**

MediScan AI is an AI-powered tool that helps users understand medical reports by extracting key parameters, identifying abnormal values, and providing clear explanations.

It supports both PDF and image-based lab reports and presents insights through an intuitive interface with benchmark-guided interpretation.

---

## ✨ Features

- 📄 Upload medical reports:
  - PDF  
  - PNG  
  - JPG / JPEG  

- 🔍 OCR-based text extraction  
- 🤖 AI-assisted parameter parsing  
- 📊 Benchmark-guided interpretation using lab reference ranges  

### 📂 Categorized Results
- 🚨 Needs Attention  
- ✅ Within Expected Range  
- ⚠️ Uncertain / Not Interpretable  

- 💬 Follow-up chat for report-related queries  
- 🌗 Dark / Light mode  
- 📱 Clean and responsive UI  

---

## 🛠 Tech Stack

### Frontend
- React  
- Vite  
- Tailwind CSS  

### Backend
- FastAPI  
- Pydantic  
- Python  

### AI / OCR
- Groq LLM  
- PDF & Image text extraction  
- Rule-based + AI hybrid interpretation  

---

## 📁 Project Structure

```
AI-Health-Report-Explainer/

├── backend/
│   ├── api/
│   ├── models/
│   ├── prompts/
│   ├── services/
│   ├── main.py
│   └── requirements.txt

├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js

└── README.md
```

---

## ⚙️ How It Works

1. Upload a report (PDF/image)  
2. Backend extracts text using OCR  
3. LLM parses medical parameters into structured data  
4. Values are evaluated using reference ranges  
5. Results are displayed with:
   - Summary  
   - Categorized cards  
   - Urgent flags  

6. Ask follow-up questions via chat  

---

## 📄 Supported File Types

- PDF  
- PNG  
- JPG / JPEG  

> ✅ Clean PDFs give best results  
> ⚠️ OCR quality affects image accuracy  

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/s0r0j/AI-Health-Report-Explainer.git
cd AI-Health-Report-Explainer
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
```

#### Activate Virtual Environment

**Windows**
```bash
.venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Create `.env`

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

#### Run Backend

```bash
uvicorn main:app --reload --port 8000
```

👉 Backend: http://localhost:8000

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

👉 Frontend: http://localhost:5173

---

## 🔌 API Endpoints

### Upload Report

```
POST /api/upload
```

**Form Data**
- `file`
- `language`

---

### Chat

```
POST /api/chat
```

**Request Body**
```json
{
  "question": "What does low hemoglobin mean?",
  "report_context": "Hemoglobin: 10.2 g/dL (low)"
}
```

---

## 🧪 Interpretation System

- Uses standard lab reference ranges  
- Hybrid approach:
  - Rule-based validation  
  - LLM-based explanation  

> ⚠️ Not a diagnostic system  

---

## ⚠️ Disclaimer

This tool is for **informational purposes only**.

- ❌ Not a medical diagnosis tool  
- ❌ Not a replacement for doctors  

👉 Always consult a healthcare professional.

---

## 🚧 Limitations

- OCR depends on input quality  
- Some values may be uncertain  
- Reference ranges vary by lab  
- Images are less reliable than PDFs  

---

## 🔮 Future Improvements

- Better OCR preprocessing  
- Confidence scoring  
- Expanded medical references  
- Exportable summaries  
- Improved multi-language support  

---

## 👥 Contributors

**Team MediScan AI**

---

## 🎯 Demo Tips

- Use a clean PDF  
- Show categorized results  
- Ask follow-up questions  
- Toggle dark/light mode