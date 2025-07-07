# CareerCraft

CareerCraft is a modular, AI-assisted job search productivity tool built using Streamlit. It supports:
- Resume rewriting with RAG-powered suggestions
- STAR story generation and saving
- Job application tracking

## 🔧 Technologies Used
- Streamlit
- SentenceTransformers + FAISS for semantic search
- LLaMA 3 (via local Ollama inference)
- Python

## 📁 Project Structure
- `Home.py`: Landing dashboard
- `pages/Resume Tool.py`: Resume matcher and rewriter
- `pages/Star story.py`: STAR story creator and viewer
- `pages/Application Tracker.py`: Job tracking interface
- `resume_examples.json`: Knowledge base for RAG
- `applications.csv`: Sample job tracking data

## 🛡️ Privacy
All processing is done locally, and no data is shared externally. Ensure you do not upload sensitive data when publishing to GitHub.

---

## 🚀 Getting Started

Install dependencies:

```bash
pip install -r requirements.txt