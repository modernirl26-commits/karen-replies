import streamlit as st
import requests
import json
import os
import uuid

st.set_page_config(page_title="Neural Core", layout="wide", page_icon="🧠")

# --- CSS FOR DARK HACKER VIBE ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ffcc; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #00ffcc; }
    .stChatMessage { background-color: #0a0a0a; border: 1px solid #222; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.title("🧠 NEURAL CORE")
    pwd = st.text_input("ACCESS CODE:", type="password")
    if st.button("INITIALIZE"):
        if pwd == st.secrets["app_password"]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("ACCESS DENIED.")
    st.stop()

# --- DATA STORAGE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("SYSTEM PARAMETERS")
    if st.button("CLEAR MEMORY"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    persona = st.text_input("TARGET PERSONA:", placeholder="e.g., Kiyotaka Ayanokoji, CIA Operative")
    if not persona: persona = "A ruthless, emotionless supercomputer"
    
    st.markdown("---")
    st.write("**THE 4-AGENT PROTOCOL IS ALWAYS ACTIVE.**")

# --- THE 4-AGENT ENGINE ---
def call_deepseek(system_prompt, user_prompt, temp=0.7):
    headers = {
        "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat", # Using fast model for the internal agents
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temp
    }
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

# --- INTERFACE ---
st.title("NEURAL CORE")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("INPUT PROBLEM DATA...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("EXECUTING 4-AGENT PROTOCOL..."):
            
            # AGENT 1: The Profiler
            profiler_prompt = "You are a cold, emotionless psychological profiler. Analyze the hidden weaknesses, fears, and predictable moves of the people in this situation. Do not hold back. Be brutal. Do not use em dashes."
            profile = call_deepseek(profiler_prompt, user_input, 0.4)
            
            # AGENT 2: The Strategist
            strategist_prompt = f"You are a master of asymmetric warfare. You are {persona}. Based on this psychological profile: '{profile}', give a highly unconventional, slightly ruthless move. Use metaphors. No lists. No em dashes."
            strategy = call_deepseek(strategist_prompt, user_input, 0.8)
            
            # AGENT 3: The Scientist
            scientist_prompt = "You are a data scientist and historian. What real-world experiment (e.g., Pavlov, Asch, Milgram) or famous historical figure (e.g., Elon Musk, Machiavelli, Steve Jobs) uses the exact tactic described here? Provide one single, hard-hitting citation."
            evidence = call_deepseek(scientist_prompt, strategy, 0.3)
            
            # AGENT 4: The Final Editor (Creates the final output)
            editor_prompt = f"""
            You are the final voice of a supercomputer. You must combine these three inputs into one cohesive, chilling, and brilliant response. 
            Speak with zero emotion. Short sentences. No lists. No bullet points. No em dashes. 
            
            Format EXACTLY like this:
            
            **THE ANALYSIS:**
            (Summarize the brutal truth of the situation based on the profiler)
            
            **THE EXECUTION:**
            (Give the strategist's unconventional move. Make it sound like a chess play.)
            
            **📚 THE EVIDENCE:**
            (Insert the scientist's citation naturally into a sentence.)
            
            **THE SCRIPT:**
            (Write the exact words the user should say, in the voice of {persona}.)
            """
            
            final_input = f"User Problem: {user_input}\n\nProfile: {profile}\n\nStrategy: {strategy}\n\nEvidence: {evidence}"
            
            final_result = call_deepseek(editor_prompt, final_input, 0.7)
            
            st.markdown(final_result)
            st.session_state.messages.append({"role": "assistant", "content": final_result})

    st.markdown("---")
    st.code(st.session_state.messages[-1]["content"], language="text")
