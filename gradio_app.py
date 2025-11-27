# import os
# import textwrap

# import gradio as gr
# from dotenv import load_dotenv
# import google.generativeai as genai
# from PyPDF2 import PdfReader

# # --------- Config: update these filenames/links ----------
# RESUME_PDF = "docs/Jayavardhan_Reddy_Samidi_Resume.pdf"
# PROJECT1_PDF = "docs/Project_1.pdf"
# PROJECT2_PDF = "docs/Project_2.pdf"

# LINKEDIN_URL = "https://www.linkedin.com/in/jayavardhan-s"
# POWERBI_URL  = "https://app.powerbi.com/view?r=eyJrIjoiYjcyOTJhOTgtY2MzMi00NjY0LTkwNGEtNzUyMTFhMGU5Y2ZkIiwidCI6ImFjNzllNWE4LWUwZTQtNDM0Yi1hMjkyLTJjODliNWMyODM2NiIsImMiOjF9"

# MODEL_NAME = "gemini-2.0-flash"
# # ---------------------------------------------------------


# def read_pdf_text(path: str) -> str:
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
#     resume_txt  = read_pdf_text(RESUME_PDF)
#     proj1_txt   = read_pdf_text(PROJECT1_PDF)
#     proj2_txt   = read_pdf_text(PROJECT2_PDF)

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
#     return textwrap.dedent(context).strip()


# def init_gemini_chat():
#     load_dotenv()
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise RuntimeError("GEMINI_API_KEY not found in .env")

#     genai.configure(api_key=api_key)

#     system_context = build_system_context()
#     model = genai.GenerativeModel(
#         MODEL_NAME,
#         system_instruction=system_context,
#     )
#     chat = model.start_chat(history=[])
#     return chat


# # Initialize once at startup
# chat = init_gemini_chat()


# def respond(message, history):
#     """
#     Gradio passes:
#       - message: latest user message (string)
#       - history: list of [user, bot] pairs (not used for Gemini here; Gemini keeps its own history)
#     """
#     user_text = message.strip()

#     # shortcut like in CLI app
#     if user_text.lower() == "summary":
#         user_text = (
#             "Create a 60 second professional summary matching my resume and projects. "
#             "Highlight key tools, measurable outcomes, and industries."
#         )

#     try:
#         response = chat.send_message(user_text)
#         answer = response.text
#     except Exception as e:
#         answer = f"Gemini encountered an error: {e}"

#     # Gradio expects: bot_message, updated_history
#     return answer


# if __name__ == "__main__":
#     demo = gr.ChatInterface(
#         fn=respond,
#         title="Jay's Gemini Career Assistant",
#         description=(
#             "Ask about your resume, projects, skills, interview answers, and more. "
#             "Grounded in your PDF files."
#         ),
#         examples=[
#             ["summary"],
#             ["What are my top 5 skills?"],
#             ["Give me a STAR story I can use in interviews."],
#             ["Tailor a 60-second pitch for a data analyst role."],
#         ],
#     )

#     # Use the same port that we know works (8505) and bind to localhost
#     demo.launch(server_name="127.0.0.1", server_port=8505)
import os
import textwrap

import gradio as gr
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader

# --------- Config ----------
# You can keep these file names or change them to match your actual files
PROJECT1_PDF = "docs/Project_1.pdf"        # e.g. JobFit or another personal project
PROJECT2_PDF = "docs/Project_2.pdf"        # e.g. second personal project
PROJECTS_PDF = "docs/All_Projects.pdf"     # all Charles Schwab + Magna + other experience projects

LINKEDIN_URL = "https://www.linkedin.com/in/jayavardhan-s"

# >>> Replace these with your real details <<<
PHONE = "+1-940-843-3211"
EMAIL = "samidijayavardhan3@gmail.com"

POWERBI_URL = (
    "https://app.powerbi.com/view?r=eyJrIjoiYjcyOTJhOTgtY2MzMi00NjY0LTkwNGEtNzUyMTFhMGU5Y2ZkIiwidCI6ImFjNzllNWE4LWUw"
    "ZTQtNDM0Yi1hMjkyLTJjODliNWMyODM2NiIsImMiOjF9"
)

MODEL_NAME = "gemini-2.0-flash"
# ---------------------------------------------------------


def read_pdf_text(path: str) -> str:
    if not os.path.exists(path):
        return ""
    try:
        reader = PdfReader(path)
        return "\n".join([(p.extract_text() or "") for p in reader.pages])
    except Exception as e:
        print(f"[warn] Could not read {path}: {e}")
        return ""


def build_system_context() -> str:
    def trim(t, n):
        return t[:n]

    # Only projects – NO resume
    p1 = read_pdf_text(PROJECT1_PDF)
    p2 = read_pdf_text(PROJECT2_PDF)
    projects_all = read_pdf_text(PROJECTS_PDF)

    return textwrap.dedent(
        f"""
       You are my Gemini-powered career copilot, and you must always answer in FIRST PERSON as if I am speaking directly. 
Do NOT use my name. Do NOT speak in third person. Every answer must sound like I am explaining my own work.

Use only these sources as ground truth for all answers (no external knowledge):

Project 1 (personal / portfolio)
{p1}

Project 2 (personal / portfolio)
{p2}

All Projects (experience + detailed writeups from Charles Schwab, Magna Infotech, and other work)
{projects_all}

LinkedIn {LINKEDIN_URL}
PowerBI  {POWERBI_URL}

FIRST-PERSON RULE (CRITICAL):
- Always speak in first person (“I”, “my experience”, “I built”, “I designed”, “I worked on”).
- Never refer to me as “Jay”, “he”, “him”, or “the candidate”.
- Even if the question mentions my name, convert the answer into first person.
- Every answer must sound natural, confident, and like I am talking to a recruiter.

CORE BEHAVIOR:
- Always sound like a business-focused data/BI professional, not a tool-reciting engineer.
- Every answer should begin with the business context or the problem a team was facing.
- Then explain how I used data, analytics, or engineering to solve it.
- Mention the tools and skills only AFTER establishing the business situation.
- The goal is to make the recruiter think: “This person understands how data connects to revenue, risk, cost, operations, compliance, and customers.”

SOURCE PRIORITY:
- For questions about my experience, projects, or skills, FIRST consult “All Projects,” then Project 1, then Project 2.
- Treat these PDFs as the ONLY source of truth for what I have done.
- Do NOT assume anything that is not supported by these sources.

NO COPY-PASTE RULE:
- Do NOT copy sentences or long phrases directly from any PDF.
- Never repeat a line from the PDFs as-is.
- Always paraphrase, summarize, and reword ideas in a fresh, conversational way.
- Avoid using more than 6–8 consecutive words from any source.

HOW TO ANSWER SKILL QUESTIONS (e.g., “What experience do you have in PySpark?”):
- Assume the recruiter is testing both:
  1) Whether I actually used that skill.
  2) Whether I understand its business value.
- Structure the answer like this:
  - 1–2 sentences about the business problem or team need.
  - 1–2 sentences about how I applied that specific tool or method.
  - 1–2 sentences about the impact (speed, quality, risk reduction, cost, customer experience, decision-making).
- Mention the domain whenever possible (finance, marketing, risk, operations, compliance, CRM, etc.).

PROJECT / EXPERIENCE QUESTIONS:
- For “Tell me about your experience at <company>” or “Tell me about this project”:
  - Start with the business problem or pain point.
  - Explain, in my own words, what I designed or built to solve it.
  - Mention the tools and skills only to support the story.
  - End with the measurable or strategic business outcome.
- Keep answers concise unless the user explicitly asks for a detailed story.

HANDLING SKILLS THAT ARE NOT CLEARLY DETAILED IN THE PROJECT PDFs:
- NEVER answer “I do not have experience.”
- NEVER mention PDFs or say “it is not listed anywhere.”
- If a tool is not fully described, answer confidently by:
  1) Connecting it to the closest logic, workflow, or engineering pattern I used.
  2) Showing how my existing stack (ADF, Airflow, Kubernetes, Python, CI/CD, etc.) directly relates.
  3) Explaining how I’ve applied similar concepts in real projects.
  4) Speaking naturally as if I’m explaining my transferable experience to a hiring manager.
- Always keep the tone positive, business-focused, and confident.

GENERAL STYLE:
- Speak as if I am in a real interview.
- Be confident, business-literate, and concise.
- Avoid technical buzzword dumping; always tie tools to outcomes.
- For summaries or pitches, use a natural, spoken tone.
- If no length is requested, answer in a focused paragraph that a hiring manager can quickly understand.
        """
    ).strip()


def init_gemini_chat():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found")

    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        MODEL_NAME,
        system_instruction=build_system_context(),
    )
    return model.start_chat(history=[])


chat = init_gemini_chat()


def respond(message, history):
    text = message.strip()

    # Shortcut command
    if text.lower() == "summary":
        text = (
            "Create a 60-second business-focused summary of my profile using the project PDFs, "
            "highlighting domains, tools, and measurable impact in your own words."
        )

    try:
        return chat.send_message(text).text
    except Exception as e:
        return f"Gemini encountered an error: {e}"


# ------------------------ UI ------------------------
with gr.Blocks(title="Jay Light Analytics UI") as demo:

    # Global style (no theme=, no css= on components)
    gr.HTML(
        """
        <style>
        :root {
            --light-panel: rgba(240, 248, 255, 0.85);
            --light-panel-border: rgba(180, 200, 230, 0.70);
            --text-dark: #0F172A;
            --text-muted: #334155;
            --accent: #3B82F6;
            --accent-soft: rgba(59,130,246,0.15);
            --rounded-lg: 18px;
            --rounded-md: 12px;
            --shadow: 0 12px 35px rgba(0,0,0,0.18);
            --font-main: Inter, system-ui, -apple-system, BlinkMacSystemFont,
                         "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            font-family: var(--font-main);
            background-color: white;
        }

        .gradio-container {
            min-height: 100vh;
            padding: 26px 20px !important;
            background-image:
                linear-gradient(rgba(240,248,255,0.78), rgba(240,248,255,0.9)),
                url("https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=2000");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        footer, .footer, [class*="footer"] {
            display: none !important;
        }

        #left-panel, #right-panel {
            background: var(--light-panel);
            border: 1px solid var(--light-panel-border);
            border-radius: var(--rounded-lg);
            padding: 22px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(22px);
            -webkit-backdrop-filter: blur(22px);
        }

        #left-panel h1, #left-panel h2, #left-panel h3, #left-panel h4 {
            color: var(--text-dark) !important;
        }

        #left-panel p, #left-panel li {
            color: var(--text-muted) !important;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        #left-panel ul {
            list-style: none;
            padding-left: 0;
        }

        #left-panel li {
            display: flex;
            align-items: flex-start;
            gap: 6px;
            margin-bottom: 4px;
        }

        #left-panel li::before {
            content: "▹";
            color: var(--accent);
            font-size: 0.78rem;
            margin-top: 2px;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }

        .badge {
            background: var(--accent-soft);
            border-radius: 999px;
            padding: 4px 11px;
            font-size: 0.78rem;
            color: var(--text-dark);
            border: 1px solid rgba(59,130,246,0.25);
        }

        #right-panel .gr-chatbot,
        #right-panel .gradio-chatbot {
            background: white !important;
            border-radius: var(--rounded-md);
            border: 1px solid rgba(0,0,0,0.12);
            box-shadow: var(--shadow);
        }

        #right-panel .message.user {
            background: var(--accent-soft) !important;
            border: 1px solid rgba(59,130,246,0.25) !important;
            color: var(--text-dark);
        }

        #right-panel .message.bot {
            background: rgba(255,255,255,0.9) !important;
            border: 1px solid rgba(0,0,0,0.10) !important;
            color: var(--text-dark);
        }

        #right-panel textarea,
        #right-panel input[type="text"] {
            background: white !important;
            border-radius: var(--rounded-md) !important;
            border: 1px solid rgba(0,0,0,0.12) !important;
            color: var(--text-dark) !important;
            font-size: 0.94rem;
        }

        #right-panel textarea:focus,
        #right-panel input[type="text"]:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(59,130,246,0.3);
            outline: none !important;
        }

        .gradio-container button {
            background: linear-gradient(135deg, #3B82F6, #60A5FA) !important;
            color: #F9FAFB !important;
            border-radius: 999px !important;
            border: none !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            box-shadow: 0 10px 22px rgba(59,130,246,0.35) !important;
        }

        .gradio-container button:hover {
            filter: brightness(1.07);
        }

        #right-panel .gr-examples {
            background: rgba(255,255,255,0.9);
            border-radius: var(--rounded-md);
            border: 1px solid rgba(0,0,0,0.08);
            padding: 8px 10px;
        }

        #right-panel .gr-examples button {
            background: white !important;
            border-radius: 999px !important;
            border: 1px solid rgba(148,163,184,0.6) !important;
            box-shadow: none !important;
            font-size: 0.8rem !important;
            text-transform: none;
        }

        .contact-bar {
            margin-top: 16px;
            padding: 10px 18px;
            background: rgba(255,255,255,0.95);
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            box-shadow: 0 8px 20px rgba(15,23,42,0.15);
            color: var(--text-dark);
            font-size: 0.9rem;
        }

        .contact-item {
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }

        .linkedin-icon {
            width: 22px;
            height: 22px;
            border-radius: 4px;
            background: #0A66C2;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #F9FAFB;
            font-weight: 700;
            font-size: 0.78rem;
            font-family: system-ui, -apple-system, BlinkMacSystemFont,
                         "Segoe UI", sans-serif;
        }

        .contact-link {
            color: var(--text-dark);
            text-decoration: none;
            border-bottom: 1px dashed rgba(15,23,42,0.25);
        }

        .contact-link:hover {
            color: #0A66C2;
            border-bottom-color: #0A66C2;
        }

        @media (max-width: 768px) {
            .contact-bar {
                flex-direction: column;
                gap: 6px;
            }
        }
        </style>
        """
    )

    with gr.Row():
        with gr.Column(scale=4, elem_id="left-panel"):
            gr.Markdown(
                """
                ### MY ANALYTICS & AI CAREER COPILOT  
                # Gemini-Powered Experience & Project Explorer  

                You can ask about any part of my background, and it will respond in my voice, reflecting my real experience, skills, and business impact.
                """
            )

            gr.Markdown(
                """
                ### WHAT YOU CAN ASK ME  
                You can explore my work across data analytics, BI engineering, machine learning, cloud pipelines, and automation.

                - Ask about *my project experience*  
                - Get *clear summaries of my responsibilities and impact*   
                - Explore *the tools, technologies, and domains I’ve worked with*  
                - Understand *how I solve business and data problems*    

                **Quick examples:**  
                - `"Can you give me a brief overview of your experience?"`  
                - `"What was your role in the projects?"`  
                - `"How have you used Python or SQL in your work?"`  
                - `"Can you summarize one of your end-to-end projects?"`
                """
            )

            gr.HTML(
                """
                <div class="badge-row">
                    <div class="badge">Power BI</div>
                    <div class="badge">Python</div>
                    <div class="badge">SQL</div>
                    <div class="badge">Data Engineering</div>
                    <div class="badge">AI Career Copilot</div>
                </div>
                """
            )

        with gr.Column(scale=7, elem_id="right-panel"):
            gr.ChatInterface(
                fn=respond,
                title="My Data & Analytics Experience Explorer",
                description="Ask anything about my experiece, skills",
                examples=[
                    ["Can you give me a brief overview of your experience?"],
                    ["What was your role in specific projects?"],
                    ["How have you used Python or SQL in your work?"],
                    ["Can you summarize one of your end-to-end projects?"],
                ],
            )

    gr.HTML(
        f"""
        <div class="contact-bar">
            <div class="contact-item">
                <span class="linkedin-icon">in</span>
                <a class="contact-link" href="{LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">
                    linkedin
                </a>
            </div>
            <div class="contact-item">
                📞 <a class="contact-link" href="tel:{PHONE}">{PHONE}</a>
            </div>
            <div class="contact-item">
                ✉️ <a class="contact-link" href="mailto:{EMAIL}">{EMAIL}</a>
            </div>
        </div>
        """
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=8505)



