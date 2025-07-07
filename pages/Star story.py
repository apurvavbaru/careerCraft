import streamlit as st
import json
from pathlib import Path
import ollama
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# --- CONFIG ---
st.set_page_config(page_title="CareerCraft Star Story Generator", layout="wide")
st.title("STAR Story Generator")

# --- RAG DATA: Resume Bullets ---
RESUME_FILE = "pages/resume_examples.json"

@st.cache_resource
def load_resume_examples():
    with open(RESUME_FILE, "r") as f:
        bullets = json.load(f)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(bullets)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return bullets, model, index

resume_bullets, embed_model, faiss_index = load_resume_examples()

# --- STAR STORY SAVING ---
STORY_FILE = Path.home() / ".star_stories" / "saved_star_stories.json"
STORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_stories():
    if STORY_FILE.exists():
        try:
            with open(STORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_stories(stories):
    with open(STORY_FILE, "w") as f:
        json.dump(stories, f, indent=2)

saved_stories = load_stories()

# --- USER INPUT ---
#st.subheader("Create a STAR Story")

question = st.text_input("Interview question:")
rough_story = st.text_area("Your rough story or notes:", height=200)
job_role = st.text_input("Optional: Target job role (e.g., Data Analyst)")
resume_text = st.text_area("Optional: Paste your resume", height=200)

# --- RAG RETRIEVAL FUNCTION ---
def retrieve_examples(text, k=3):
    if not text.strip():
        return []
    query_embed = embed_model.encode([text])
    D, I = faiss_index.search(np.array(query_embed), k)
    return [resume_bullets[i] for i in I[0]]

# --- MAIN PROCESSING ---
if st.button("Refine into STAR Format"):
    query_for_rag = " ".join([question, rough_story, job_role or "", resume_text or ""])
    top_examples = retrieve_examples(query_for_rag, k=3)

    context_block = "\n".join(f"- {ex}" for ex in top_examples)

    prompt = f"""
You are a career coach. Help format the following story into a STAR response.
Use only the user's input and relevant resume bullets (if any).
Focus especially on clear Action and Result. Where appropriate, include quantifiable metrics or specific outcomes.

--- INTERVIEW QUESTION ---
{question}

--- USER STORY ---
{rough_story}

--- OPTIONAL JOB ROLE ---
{job_role}

--- OPTIONAL RESUME ---
{resume_text}

--- RELEVANT EXAMPLES ---
{context_block}

Format your response like:
Situation:
Task:
Action:
Result:
"""

    with st.spinner("Generating STAR story..."):
        response = ollama.chat(
            model="llama3:instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        star_output = response["message"]["content"]

        st.markdown("### STAR-Formatted Story")
        st.text_area("Formatted Story", value=star_output, height=300)

