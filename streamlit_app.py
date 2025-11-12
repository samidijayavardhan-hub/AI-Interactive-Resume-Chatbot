# import os
# import io
# import textwrap
# import streamlit as st
# import google.generativeai as genai
# from PyPDF2 import PdfReader
# from glob import glob

# MODEL_NAME = "gemini-2.0-flash"

# # ---------- EDIT THESE ----------
# DOC_DIR = "docs"  # folder inside your repo that contains your PDFs
# DOC_FILES = [
#     "Jay_Samidi_Resume.pdf",
#     "Project_1.pdf",
#     "Project_2.pdf",
# ]
# LINKEDIN_URL_DEFAULT = "https://www.linkedin.com/in/jayavardhan-s"
# POWERBI_URL_DEFAULT = ""  # put public URL if you have one
# # --------------------------------

# def read_pdf_text(path: str) -> str:
#     try:
#         with open(path, "rb") as f:
#             reader = PdfReader(io.BytesIO(f.read()))
#         pages = []
#         for p in reader.pages:
#             t = p.extract_text() or ""
#             pages.append(t)
#         return "\n".join(pages)
#     except Exception as e:
#         return f"[warn] Could not read {os.path.basename(path)}. {e}"

# def trim(txt: str, limit: int) -> str:
#     return txt[:limit] if txt else ""

# def build_system_context(texts: list[str], filenames: list[str],
#                          linkedin_url: str, powerbi_url: str) -> str:
#     # basic trimming to keep token size in check
#     trimmed = [trim(t, 9000 if i == 0 else 6500) for i, t in enumerate(texts)]
#     blocks = []
#     for name, content in zip(filenames, trimmed):
#         blocks.append(f"{name}\n{content}\n")
#     ctx = f"""
# You are a career assistant grounded strictly in the following sources.

# {'\n'.join(blocks)}

# Reference Links
# LinkedIn {linkedin_url}
# Power BI {powerbi_url}

# Instructions
# 1. Answer using only the resume and project details above or the given links.
# 2. Prefer concrete skills, tools, metrics, and outcomes found in the sources.
# 3. If something is not supported by these sources, say you are unsure.
# """
#     return textwrap.dedent(ctx).strip()

# def get_model(system_instruction: str):
#     api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         st.error("Missing GEMINI_API_KEY in Streamlit secrets")
#         st.stop()
#     genai.configure(api_key=api_key)
#     return genai.GenerativeModel(MODEL_NAME, system_instruction=system_instruction)

# st.set_page_config(page_title="Career Chatbot", layout="wide")
# st.title("Career Chatbot")

# with st.sidebar:
#     st.subheader("Source folder")
#     st.caption(f"Reading PDFs from ./{DOC_DIR}")
#     linkedin_url = st.text_input("LinkedIn URL", value=LINKEDIN_URL_DEFAULT)
#     powerbi_url = st.text_input("Power BI public URL", value=POWERBI_URL_DEFAULT)
#     build_clicked = st.button("Build context")

# # Load local PDFs
# available = {os.path.basename(p): p for p in glob(os.path.join(DOC_DIR, "*.pdf"))}
# missing = [f for f in DOC_FILES if f not in available]

# st.write("### Files")
# for f in DOC_FILES:
#     if f in available:
#         st.success(f"Found {f}")
#     else:
#         st.error(f"Missing {f} in ./{DOC_DIR}")

# if build_clicked:
#     if missing:
#         st.error("Some files are missing. Fix the red items above and click Build context again.")
#         st.stop()

#     texts = [read_pdf_text(available[f]) for f in DOC_FILES]
#     st.session_state["system_ctx"] = build_system_context(texts, DOC_FILES, linkedin_url, powerbi_url)
#     st.session_state["chat_history"] = []
#     st.session_state["model"] = get_model(st.session_state["system_ctx"])
#     st.session_state["chat"] = st.session_state["model"].start_chat(history=[])
#     st.success("Context built. Start chatting below.")

# if "chat" not in st.session_state:
#     st.info("Put your PDFs in the docs folder, confirm they show as Found, then click Build context.")
#     st.stop()

# for role, text in st.session_state.get("chat_history", []):
#     with st.chat_message(role):
#         st.markdown(text)

# prompt = st.chat_input("Ask about your experience, projects, or create a summary")
# if prompt:
#     st.session_state["chat_history"].append(("user", prompt))
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     try:
#         response = st.session_state["chat"].send_message(prompt, stream=True)
#         acc = ""
#         with st.chat_message("assistant"):
#             placeholder = st.empty()
#             for ch in response:
#                 piece = getattr(ch, "text", "")
#                 acc += piece
#                 placeholder.markdown(acc)
#         st.session_state["chat_history"].append(("assistant", acc))
#     except Exception as e:
#         st.error(f"Error from model. {e}")






# # career_bot.py
import os
import textwrap
from dotenv import load_dotenv
import google.generativeai as genai

# Optional: PDF text extraction
# pip install PyPDF2
from PyPDF2 import PdfReader

# --------- Config: update these filenames/links ----------
RESUME_PDF = "docs/Jayavardhan_Reddy_Samidi_Resume.pdf"
PROJECT1_PDF = "docs/Project_1.pdf"
PROJECT2_PDF = "docs/Project_2.pdf"

# Links are just included as reference text (the model won't fetch them automatically)
LINKEDIN_URL = "https://www.linkedin.com/in/jayavardhan-s"
POWERBI_URL  = "https://app.powerbi.com/view?r=eyJrIjoiYjcyOTJhOTgtY2MzMi00NjY0LTkwNGEtNzUyMTFhMGU5Y2ZkIiwidCI6ImFjNzllNWE4LWUwZTQtNDM0Yi1hMjkyLTJjODliNWMyODM2NiIsImMiOjF9"

MODEL_NAME = "gemini-2.0-flash"
# ---------------------------------------------------------

# Load environment variable from the .env file
load_dotenv()

# Configure the Gemini API with the key from .env file
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except AttributeError:
    print("Error! The GEMINI_API_KEY was not found.")
    raise SystemExit(1)

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

def build_system_context() -> str:
    """Build a concise system instruction from your resume and project PDFs plus link refs."""
    resume_txt  = read_pdf_text(RESUME_PDF)
    proj1_txt   = read_pdf_text(PROJECT1_PDF)
    proj2_txt   = read_pdf_text(PROJECT2_PDF)

    # Keep context size reasonable
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
    # Collapse whitespace a bit
    return textwrap.dedent(context).strip()

# Create the Generative Model with a system instruction built from your PDFs
system_context = build_system_context()
model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_context)

# Start a chat session with no prior turns (the system context is already attached to the model)
chat = model.start_chat(history=[])

# Main Chat Loop
print("Gemini Career Chatbot ready on 2.0 Flash. Type 'quit' to exit.")
print("=" * 50)
print("Shortcuts: type 'summary' for a 60-sec professional intro based on your files.\n")

while True:
    user_input = input("You : ")

    if not user_input.strip():
        print("Please enter a question or prompt.")
        continue

    # Built-in shortcut for a quick test output
    if user_input.lower().strip() == "summary":
        user_input = (
            "Create a 60 second professional summary matching my resume and projects. "
            "Highlight key tools, measurable outcomes, and industries."
        )

    # Check if the user wants to exit the chatbot
    if user_input.lower() == "quit":
        print("\nGoodbye and thanks for chatting with Gemini 2.0 Flash")
        break

    try:
        # Send user input to the LLM (streaming response)
        response = chat.send_message(user_input, stream=True)

        # Print the LLM's response
        print("Gemini : ", end="")
        for chunk in response:
            print(chunk.text, end="")
        print("\n")

    except Exception as e:
        print(f"Gemini encountered an error while generating a response: {e}\n")
