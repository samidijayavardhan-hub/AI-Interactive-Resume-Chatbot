import os
import textwrap

import streamlit as st
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
    """Extract plain text from a PDF. Returns empty string if file missing or unreadable."""
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


@st.cache_resource(show_spinner="Loading resume & project context...")
def build_system_context() -> str:
    """Build a concise system instruction from your resume and project PDFs plus link refs."""
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


@st.cache_resource(show_spinner="Initializing Gemini model...")
def init_gemini_chat():
    """Configure Gemini and start a chat session with the system context."""
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


def main():
    st.set_page_config(
        page_title="Jay's Career Chatbot",
        page_icon="💼",
    )

    st.title("💼 Jay's Gemini Career Assistant")
    st.caption("Grounded in your resume + project PDFs. Ask about summaries, skills, interview answers, etc.")

    # Initialise chat object once per session
    if "gemini_chat" not in st.session_state:
        st.session_state.gemini_chat = init_gemini_chat()
        st.session_state.messages = []  # store chat history for UI

    chat = st.session_state.gemini_chat

    # Sidebar tips
    with st.sidebar:
        st.subheader("Quick Prompts")
        st.write("- `summary` → 60-sec professional intro")
        st.write("- “What are my top 5 skills?”")
        st.write("- “Give me a STAR story for an interview.”")
        st.write("- “Tailor a pitch for a data analyst role.”")

    # Show past messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask something about your career, skills, or projects:")
    if user_input:
        raw_input = user_input.strip()

        # Built-in shortcut
        if raw_input.lower() == "summary":
            raw_input = (
                "Create a 60 second professional summary matching my resume and projects. "
                "Highlight key tools, measurable outcomes, and industries."
            )

        # Add user message to UI history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get model response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = chat.send_message(raw_input)
                    answer = response.text
                except Exception as e:
                    answer = f"Gemini encountered an error: {e}"

            st.markdown(answer)

        # Save assistant reply for future display
        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()







# # # career_bot.py
# import os
# import textwrap
# from dotenv import load_dotenv
# import google.generativeai as genai

# # Optional: PDF text extraction
# # pip install PyPDF2
# from PyPDF2 import PdfReader

# # --------- Config: update these filenames/links ----------
# RESUME_PDF = "docs/Jayavardhan_Reddy_Samidi_Resume.pdf"
# PROJECT1_PDF = "docs/Project_1.pdf"
# PROJECT2_PDF = "docs/Project_2.pdf"

# # Links are just included as reference text (the model won't fetch them automatically)
# LINKEDIN_URL = "https://www.linkedin.com/in/jayavardhan-s"
# POWERBI_URL  = "https://app.powerbi.com/view?r=eyJrIjoiYjcyOTJhOTgtY2MzMi00NjY0LTkwNGEtNzUyMTFhMGU5Y2ZkIiwidCI6ImFjNzllNWE4LWUwZTQtNDM0Yi1hMjkyLTJjODliNWMyODM2NiIsImMiOjF9"

# MODEL_NAME = "gemini-2.0-flash"
# # ---------------------------------------------------------

# # Load environment variable from the .env file
# load_dotenv()

# # Configure the Gemini API with the key from .env file
# try:
#     genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# except AttributeError:
#     print("Error! The GEMINI_API_KEY was not found.")
#     raise SystemExit(1)

# def read_pdf_text(path: str) -> str:
#     """Extract plain text from a PDF. Returns empty string if file missing or unreadable."""
#     if not os.path.exists(path):
#         return ""
#     try:
#         reader = PdfReader(path)
#         pages = []
#         for p in reader.pages:
#             t = p.extract_text() or ""
#             pages.append(t)
#         return "\n".join(pages)
#     except Exception as e:
#         print(f"[warn] Could not read {path}: {e}")
#         return ""

# def build_system_context() -> str:
#     """Build a concise system instruction from your resume and project PDFs plus link refs."""
#     resume_txt  = read_pdf_text(RESUME_PDF)
#     proj1_txt   = read_pdf_text(PROJECT1_PDF)
#     proj2_txt   = read_pdf_text(PROJECT2_PDF)

#     # Keep context size reasonable
#     def trim(txt, limit=16000):
#         return txt[:limit]

#     resume_txt = trim(resume_txt, 10000)
#     proj1_txt  = trim(proj1_txt, 7000)
#     proj2_txt  = trim(proj2_txt, 7000)

#     context = f"""
# You are a career assistant grounded strictly in the following sources.

# Resume
# {resume_txt}

# Project 1
# {proj1_txt}

# Project 2
# {proj2_txt}

# Reference Links
# LinkedIn {LINKEDIN_URL}
# Power BI {POWERBI_URL}

# Instructions
# 1. Answer using only the resume and project details above. If something is not supported by these sources, say you are unsure.
# 2. Prefer concrete skills, tools, metrics, and outcomes that appear in the sources.
# 3. Keep responses concise and professional.
# """
#     # Collapse whitespace a bit
#     return textwrap.dedent(context).strip()

# # Create the Generative Model with a system instruction built from your PDFs
# system_context = build_system_context()
# model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_context)

# # Start a chat session with no prior turns (the system context is already attached to the model)
# chat = model.start_chat(history=[])

# # Main Chat Loop
# print("Gemini Career Chatbot ready on 2.0 Flash. Type 'quit' to exit.")
# print("=" * 50)
# print("Shortcuts: type 'summary' for a 60-sec professional intro based on your files.\n")

# while True:
#     user_input = input("You : ")

#     if not user_input.strip():
#         print("Please enter a question or prompt.")
#         continue

#     # Built-in shortcut for a quick test output
#     if user_input.lower().strip() == "summary":
#         user_input = (
#             "Create a 60 second professional summary matching my resume and projects. "
#             "Highlight key tools, measurable outcomes, and industries."
#         )

#     # Check if the user wants to exit the chatbot
#     if user_input.lower() == "quit":
#         print("\nGoodbye and thanks for chatting with Gemini 2.0 Flash")
#         break

#     try:
#         # Send user input to the LLM (streaming response)
#         response = chat.send_message(user_input, stream=True)

#         # Print the LLM's response
#         print("Gemini : ", end="")
#         for chunk in response:
#             print(chunk.text, end="")
#         print("\n")

#     except Exception as e:
#         print(f"Gemini encountered an error while generating a response: {e}\n")
