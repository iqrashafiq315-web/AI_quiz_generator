import streamlit as st
from groq import Groq
import json
import re

# Configure Groq API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
# Page config
st.set_page_config(page_title="Iqra & Imsal's AI Quiz Generator")

# Title
st.title("AI Quiz Generator")
st.subheader("Created by: Iqra & Imsal")
st.write("Enter any topic and I will generate a quiz for you!")

# Initialize session state
if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "current" not in st.session_state:
    st.session_state.current = 0
if "answered" not in st.session_state:
    st.session_state.answered = False

# Topic input
topic = st.text_input("Enter a topic:", placeholder="e.g. Solar System, Pakistan History, Python")

if st.button("Generate Quiz"):
    if topic:
        with st.spinner("Generating your quiz..."):
            try:
                prompt = f"""Create a quiz with 5 multiple choice questions about: {topic}
                Return ONLY a JSON array like this:
                [
                  {{
                    "question": "Question here?",
                    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                    "answer": "A) option1"
                  }}
                ]
                Return only the JSON, nothing else."""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.choices[0].message.content.strip()
                text = re.sub(r"```json|```", "", text).strip()
                st.session_state.quiz = json.loads(text)
                st.session_state.score = 0
                st.session_state.current = 0
                st.session_state.answered = False
            except Exception as e:
                error_msg = str(e)
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    st.warning("Daily limit reached! Please try again tomorrow.")
                elif "auth" in error_msg.lower() or "401" in error_msg:
                    st.error("API key issue. Please contact the developer.")
                else:
                    st.error("Something went wrong. Please try again!")

# Show quiz
if st.session_state.quiz:
    quiz = st.session_state.quiz
    idx = st.session_state.current

    if idx < len(quiz):
        q = quiz[idx]
        st.markdown(f"### Question {idx+1} of {len(quiz)}")
        st.markdown(f"**{q['question']}**")

        choice = st.radio("Choose your answer:", q["options"], key=f"q{idx}")

        if not st.session_state.answered:
            if st.button("Submit Answer"):
                st.session_state.answered = True
                if choice == q["answer"]:
                    st.success("Correct!")
                    st.session_state.score += 1
                else:
                    st.error(f"Wrong! Correct answer: {q['answer']}")

        if st.session_state.answered:
            if st.button("Next Question"):
                st.session_state.current += 1
                st.session_state.answered = False
                st.rerun()
    else:
        st.balloons()
        st.success(f"Quiz Complete! Your score: {st.session_state.score}/{len(quiz)}")
        if st.button("Try Another Topic"):
            st.session_state.quiz = None
            st.rerun()