import os
import textwrap

import gradio as gr
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader

# --------- Config: update these filenames/links ----------
RESUME_PDF = "docs/Jayavardhan_Reddy_Samidi_Resume.pdf"
PROJECT1_PDF = "docs/Project_1.pdf"
PROJECT2_PDF = "docs/Project_2.pdf"

LINKEDIN_URL = "https://www.linkedin.com/in/jayavardhan-s"
POWERBI_URL  = "https://app.powerbi.com/view?r=eyJrIjoiYjcyOTJhOTgtY2MzMi00NjY0LTkwNGEtNzUyMTFhMGU5Y2ZkIiwidCI6ImFjNzllNWE4LWUwZTQtNDM0Yi1hMjkyLTJjODliNWMyODM2NiIsImMiOjF9"

MODEL_NAME = "gemini-2.0-flash"
# ---------------------------------------------------------


def read_pdf_text(path: str) -> str:
    if not os.path.exists(path):
        return ""
    try:
        reader = PdfReader(path)
        pages = []
        for p in reader.pages:
            t = p.extract_text() or ""
            pages.append(t)
        return "\n".join(pages)
    except Exception as e:
        print(f"[warn] Could not read {path}: {e}")
        return ""


def build_system_context() -> str:
    resume_txt  = read_pdf_text(RESUME_PDF)
    proj1_txt   = read_pdf_text(PROJECT1_PDF)
    proj2_txt   = read_pdf_text(PROJECT2_PDF)

    def trim(txt, limit=16000):
        return txt[:limit]

    resume_txt = trim(resume_txt, 10000)
    proj1_txt  = trim(proj1_txt, 7000)
    proj2_txt  = trim(proj2_txt, 7000)

    context = f"""
You are a career assistant grounded strictly in the following sources.

Resume
{resume_txt}

Project 1
{proj1_txt}

Project 2
{proj2_txt}

Reference Links
LinkedIn {LINKEDIN_URL}
Power BI {POWERBI_URL}

Instructions
1. Answer using only the resume and project details above. If something is not supported by these sources, say you are unsure.
2. Prefer concrete skills, tools, metrics, and outcomes that appear in the sources.
3. Keep responses concise and professional.
"""
    return textwrap.dedent(context).strip()


def init_gemini_chat():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in .env")

    genai.configure(api_key=api_key)

    system_context = build_system_context()
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=system_context,
    )
    chat = model.start_chat(history=[])
    return chat


# Initialize once at startup
chat = init_gemini_chat()


def respond(message, history):
    """
    Gradio passes:
      - message: latest user message (string)
      - history: list of [user, bot] pairs (not used for Gemini here; Gemini keeps its own history)
    """
    user_text = message.strip()

    # shortcut like in CLI app
    if user_text.lower() == "summary":
        user_text = (
            "Create a 60 second professional summary matching my resume and projects. "
            "Highlight key tools, measurable outcomes, and industries."
        )

    try:
        response = chat.send_message(user_text)
        answer = response.text
    except Exception as e:
        answer = f"Gemini encountered an error: {e}"

    # Gradio expects: bot_message, updated_history
    return answer


if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=respond,
        title="Jay's Gemini Career Assistant",
        description=(
            "Ask about your resume, projects, skills, interview answers, and more. "
            "Grounded in your PDF files."
        ),
        examples=[
            ["summary"],
            ["What are my top 5 skills?"],
            ["Give me a STAR story I can use in interviews."],
            ["Tailor a 60-second pitch for a data analyst role."],
        ],
    )

    # Use the same port that we know works (8505) and bind to localhost
    demo.launch(server_name="127.0.0.1", server_port=8505)
