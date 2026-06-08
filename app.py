import streamlit as st
from groq import Groq

# ── Groq client ──────────────────────────────────────
import os
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Page config ──────────────────────────────────────
st.set_page_config(
    page_title="EduBot - AI Study Assistant",
    page_icon="🎓",
    layout="wide"
)

# ── System prompt ─────────────────────────────────────
SYSTEM_PROMPT = """You are EduBot, a friendly and smart study assistant.
Your job is to:
1. Explain any topic in simple, clear language with examples
2. When asked to quiz, generate 1 MCQ question with 4 options (A, B, C, D)
3. When user answers, tell them if correct or wrong and explain why
4. Keep explanations beginner-friendly with bullet points
5. Always be encouraging and patient.
When generating a quiz question, always end with: CORRECT_ANSWER: [letter]"""

# ── Session state setup ───────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0

# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.title("🎓 EduBot")
    st.markdown("### Your AI Study Assistant")
    st.divider()

    st.markdown("### 📊 Quiz Score")
    if st.session_state.total > 0:
        percentage = int((st.session_state.score / st.session_state.total) * 100)
        st.metric("Score", f"{st.session_state.score}/{st.session_state.total}")
        st.progress(percentage / 100)
        st.caption(f"{percentage}% correct")
    else:
        st.info("No quizzes attempted yet")

    st.divider()

    st.markdown("### 💡 Quick Topics")
    topics = [
        "Python Lists", "Recursion", "OOP Concepts",
        "Sorting Algorithms", "SQL Basics",
        "Machine Learning", "Binary Search", "Big O Notation"
    ]
    for topic in topics:
        if st.button(f"📚 {topic}", use_container_width=True):
            st.session_state.pending_topic = topic

    st.divider()

    st.markdown("### 🧠 Quiz Me On")
    quiz_topics = ["Python", "DSA", "ML Concepts", "SQL"]
    for qt in quiz_topics:
        if st.button(f"❓ {qt}", use_container_width=True):
            st.session_state.pending_quiz = qt

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.score = 0
        st.session_state.total = 0
        st.rerun()

    st.divider()
    st.caption("Built by Tankala Samba Siva Mani")
    st.caption("Powered by Groq · Llama 3.3 · Streamlit")

# ── Main chat area ────────────────────────────────────
st.title("🎓 EduBot — AI Study Assistant")
st.caption("Ask me anything! I explain concepts, give examples, and quiz you.")
st.divider()

# ── Welcome message ───────────────────────────────────
if len(st.session_state.messages) == 0:
    st.markdown("""
    ### 👋 Welcome! Here's what I can do:

    | Feature | Example |
    |--------|---------|
    | 📖 Explain concepts | "Explain recursion in simple terms" |
    | 🧠 Quiz you | "Quiz me on Python lists" |
    | 💡 Give examples | "Give me an example of OOP" |
    | ✅ Check your answers | Answer any quiz question |

    **👈 Click a topic from the sidebar or type below to get started!**
    """)

# Handle topic button clicks
if "pending_topic" in st.session_state:
    topic = st.session_state.pending_topic
    del st.session_state.pending_topic
    prompt = f"Explain {topic} in simple terms with examples"
    st.session_state.messages.append({"role": "user", "content": prompt})

# Handle quiz button clicks
if "pending_quiz" in st.session_state:
    quiz = st.session_state.pending_quiz
    del st.session_state.pending_quiz
    prompt = f"Quiz me on {quiz} with one MCQ question"
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a question or type 'Quiz me on Python'..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                messages=api_messages,
                model="llama-3.3-70b-versatile",
            )
            reply = response.choices[0].message.content

            if "CORRECT_ANSWER:" in reply:
                st.session_state.total += 1

            if any(word in reply.lower() for word in ["correct!", "that's right", "well done", "excellent"]):
                st.session_state.score += 1

            display_reply = "\n".join(
                line for line in reply.split("\n")
                if "CORRECT_ANSWER:" not in line
            )
            st.markdown(display_reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()