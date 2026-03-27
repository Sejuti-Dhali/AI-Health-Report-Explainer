# AI-Health-Report-Explainer

\# MediScan AI



MediScan AI is an AI-powered health report explainer that helps users upload medical reports, extract key parameters, understand abnormal findings, and ask follow-up questions in natural language.



It supports PDF and image-based lab reports and presents results through a clean, interactive interface with benchmark-guided interpretation.



\---



\## Features



\- Upload medical reports in:

&#x20; - PDF

&#x20; - PNG

&#x20; - JPG / JPEG

\- OCR-based text extraction

\- AI-assisted parameter parsing

\- Benchmark-guided interpretation using standard lab reference intervals

\- Categorized result view:

&#x20; - Needs attention

&#x20; - Within expected range

&#x20; - Could not be confidently interpreted

\- Follow-up chat about the uploaded report

\- Dark / Light mode

\- Clean and responsive UI



\---



\## Tech Stack



\### Frontend

\- React

\- Vite

\- Tailwind CSS



\### Backend

\- FastAPI

\- Pydantic

\- Python



\### AI / OCR

\- Groq LLM

\- PDF / image text extraction pipeline

\- Rule-assisted interpretation and fallback reference mapping



\---



\## Project Structure



```text

AI-Health-Report-Explainer/

│

├── backend/

│   ├── api/

│   │   └── routes.py

│   ├── models/

│   │   └── schemas.py

│   ├── prompts/

│   │   ├── prompts.py

│   │   └── reference\_ranges.py

│   ├── services/

│   │   ├── llm\_parser.py

│   │   ├── ocr\_engine.py

│   │   └── reference\_ranges.py

│   ├── main.py

│   └── requirements.txt

│

├── frontend/

│   ├── src/

│   │   ├── components/

│   │   │   ├── ChatBox.jsx

│   │   │   ├── ResultCard.jsx

│   │   │   └── UrgentBanner.jsx

│   │   ├── pages/

│   │   │   ├── UploadPage.jsx

│   │   │   └── ResultPage.jsx

│   │   ├── utils/

│   │   │   └── api.js

│   │   ├── App.jsx

│   │   └── main.jsx

│   ├── package.json

│   └── tailwind.config.js

│

└── README.md

How It Works

The user uploads a report file.

The backend extracts report text from the PDF or image.

The LLM parses key medical parameters into structured JSON.

The system evaluates available values using benchmark-guided logic and standard lab reference intervals.

The frontend displays:

summary

grouped result cards

urgent flag when needed

The user can ask follow-up questions through the chat box.

Supported File Types

PDF

PNG

JPG

JPEG



Clean PDF reports usually produce the best results.

Image-based reports are supported, but OCR quality may affect extraction accuracy.



Setup Instructions

1\. Clone the repository

git clone https://github.com/s0r0j/AI-Health-Report-Explainer.git

cd AI-Health-Report-Explainer

2\. Backend setup

cd backend

python -m venv .venv

Activate virtual environment on Windows

.venv\\Scripts\\activate

Install dependencies

pip install -r requirements.txt

Create .env



Create a file named .env inside backend/ and add:



GROQ\_API\_KEY=your\_groq\_api\_key\_here

GROQ\_MODEL=llama-3.3-70b-versatile

Run backend

uvicorn main:app --reload --port 8000



Backend runs at:



http://localhost:8000

3\. Frontend setup



Open a new terminal:



cd frontend

npm install

npm run dev



Frontend runs at:



http://localhost:5173

API Endpoints

Upload report

POST /api/upload



Form data:



file

language

Ask follow-up question

POST /api/chat



JSON body:



{

&#x20; "question": "What does low hemoglobin mean?",

&#x20; "report\_context": "Hemoglobin: 10.2 g/dL (low)"

}

UI Highlights

Result dashboard with grouped sections

Parameter cards with:

test name

value

reference

interpretation

reference basis

Benchmark-guided tags

Follow-up chat section

Theme toggle for dark/light mode

Benchmark-Guided Interpretation



The system uses benchmark-guided interpretation based on standard lab reference intervals and fallback rule-based logic where applicable.



Exact source labels are shown only where available.

Interpretations should be considered assistive, not definitive.



Disclaimer



This tool provides AI-generated explanations for informational purposes only.

It does not replace a doctor, a diagnostic workflow, or a certified medical report review.



Always consult a qualified healthcare professional before making any medical decision.



Current Limitations

OCR quality affects extraction quality

Some values may remain uncertain if the report text is incomplete or ambiguous

Reference intervals can vary by lab, demographics, and clinical context

Image-based reports may be less reliable than clean PDFs

Future Improvements

Stronger benchmark provenance per parameter

Better image preprocessing for OCR

Expanded clinical reference mapping

Confidence scoring

Exportable patient-friendly summary

Multi-language support improvements

Contributors

Team MediScan AI

Demo Notes



For the best demo experience:



use a clean PDF report

show grouped result cards

ask a follow-up question in chat

toggle dark/light mode

