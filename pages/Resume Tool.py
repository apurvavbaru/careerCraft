import streamlit as st
import faiss
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
from PyPDF2 import PdfReader
import re

st.set_page_config(page_title="CareerCraft Resume Tool", layout="wide")
st.title("Resume Evaluation & Enhancement")

# --------- LOAD EMBEDDINGS + EXAMPLES ----------
@st.cache_resource
def load_bullet_examples():
    with open("pages/resume_examples.json", "r") as f:
        bullets = json.load(f)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(bullets)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return bullets, model, index

examples, embed_model, faiss_index = load_bullet_examples()

# --------- RESUME INPUT METHOD ----------
input_method = st.radio("Choose input method:", ["Paste manually", "Smart resume picker"])

resume = ""
job_desc = st.text_area("Paste the job description here", height=250)
job_desc_for_match = job_desc

if input_method == "Paste manually":
    resume = st.text_area("Paste your resume here", height=300)
else:
    uploaded_files = st.file_uploader("Upload one or more resume files (PDF only)", type=["pdf"], accept_multiple_files=True)
    selected_file = None
    if uploaded_files and job_desc_for_match:
        jd_embed = embed_model.encode([job_desc_for_match])[0]
        scores = []
        file_texts = []
        for file in uploaded_files:
            reader = PdfReader(file)
            text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
            file_texts.append(text)
            file_embed = embed_model.encode([text])[0]
            score = np.dot(jd_embed, file_embed) / (np.linalg.norm(jd_embed) * np.linalg.norm(file_embed))
            scores.append(score)
        best_idx = int(np.argmax(scores))
        selected_file = uploaded_files[best_idx].name
        resume = file_texts[best_idx]
        st.success(f"Best matching resume selected: {selected_file}")

# --------- TOOL EXTRACTION HELPER ----------
def extract_tools(text):
    keywords = ["Power BI", "Tableau", "SQL", "Python", "R", "SSRS", "SSIS", "DAX", "Power Query", "Databricks", "Azure", "Spark", "Excel", "JIRA"]
    found = [kw for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)]
    return set(found)

# --------- MATCH SCORE + ANALYSIS ----------
if st.button("Analyze Resume"):
    if not resume or not job_desc:
        st.warning("Please provide both resume and job description.")
    else:
        jd_embedding = embed_model.encode([job_desc])[0]
        # NEW: Split resume into bullet-like chunks for better granularity
        resume_chunks = [chunk.strip() for chunk in re.split(r'\n|\u2022|- ', resume) if chunk.strip()]
        resume_chunk_embeddings = embed_model.encode(resume_chunks)
        avg_resume_embedding = np.mean(resume_chunk_embeddings, axis=0)
        score = np.dot(jd_embedding, avg_resume_embedding) / (np.linalg.norm(jd_embedding) * np.linalg.norm(avg_resume_embedding))
        match_score = round(score * 100)

        st.metric("Resume–JD Match Score", f"{match_score} %")

        # Skill overlap extraction
        resume_tools = extract_tools(resume)
        jd_tools = extract_tools(job_desc)
        matched = sorted(resume_tools & jd_tools)
        missing = sorted(jd_tools - resume_tools)

        st.markdown("### Tool Match Analysis")
        st.markdown(f"**Matched Tools:** {', '.join(matched) if matched else 'None'}")
        st.markdown(f"**Missing Tools (from JD):** {', '.join(missing) if missing else 'None'}")

        with st.spinner("Analyzing strengths and weaknesses..."):
            # Summarize top relevant resume chunks for faster LLM input
            top_chunks = "\n".join(resume_chunks[:6])
            analysis_prompt = f"""
You are a career coach. Below is a RESUME SUMMARY and a JOB DESCRIPTION. Analyze and output:
1. Key Strengths
2. Weaknesses or gaps
3. Suggestions for improvement

--- RESUME SUMMARY ---
{top_chunks}

--- JOB DESCRIPTION ---
{job_desc}
"""
            analysis_response = ollama.chat(
                model="llama3:instruct",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            st.markdown("### Resume Analysis")
            st.markdown(analysis_response["message"]["content"])

# --------- RAG-ENHANCED REWRITE ----------
if st.button("Suggest Resume Improvements"):
    if not resume or not job_desc:
        st.warning("Please provide both resume and job description.")
    else:
        jd_vector = embed_model.encode([job_desc])
        _, indices = faiss_index.search(jd_vector, k=5)
        retrieved_examples = [examples[i] for i in indices[0]]

        context = "\n".join(retrieved_examples)

        with st.spinner("Generating RAG-enhanced resume suggestions..."):
            rag_prompt = f"""
Use the following resume bullet examples as reference:

--- EXAMPLES ---
{context}

Now improve this resume section based on the job description below:

--- RESUME ---
{resume}

--- JOB DESCRIPTION ---
{job_desc}

Output 3 improved bullet points tailored to the job, using action verbs and specific impact.
"""
            rag_response = ollama.chat(
                model="llama3:instruct",
                messages=[{"role": "user", "content": rag_prompt}]
            )

            st.markdown("### Suggested Resume Bullets")
            st.markdown(rag_response["message"]["content"])
