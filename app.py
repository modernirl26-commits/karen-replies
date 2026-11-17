import streamlit as st
import requests
import base64
import json
import os
import uuid

# --- 1. PAGE CONFIG & HACKER CSS ---
st.set_page_config(page_title="Neural Core", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ffcc; font-family: 'Courier New', monospace; }
    [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #00ffcc; }
    .stChatMessage { background-color: #0a0a0a; border: 1px solid #222; color: #00ffcc; }
    h1, h2, h3 { color: #00ffcc; }
    .stChatInput { background-color: #111; color: #00ffcc; border: 1px solid #00ffcc;}
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🧠 NEURAL CORE")
    st.write("*Access restricted to strategic personnel.*")
    pwd = st.text_input("ACCESS CODE:", type="password")
    if st.button("INITIALIZE"):
        if pwd == st.secrets["app_password"]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("ACCESS DENIED.")
    st.stop()

# --- 3. DATA STORAGE ---
HISTORY_FILE = "chat_history.json"
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    return {}
def save_history(history):
    with open(HISTORY_FILE, "w") as f: json.dump(history, f)

if "history" not in st.session_state:
    st.session_state.history = load_history()
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.messages = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("SYSTEM PARAMETERS")
    
    if st.button("➕ NEW SESSION"):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.subheader("PAST SESSIONS")
    if st.session_state.history:
        for chat_id, chat_data in reversed(list(st.session_state.history.items())):
            title = chat_data['title'][:20] + "..."
            if st.button(f"📜 {title}", key=chat_id):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = chat_data['messages']
                st.rerun()

    st.markdown("---")
    st.subheader("🧠 CORE MEMORY")
    core_memory = st.text_area("Context to remember:", height=100, placeholder="I am a BBA IB grad in India. I fear AI. I want to buy bikes.")

    st.markdown("---")
    st.subheader("🎭 TARGET PERSONA")
    persona = st.text_input("Enter Character:", placeholder="e.g., Kiyotaka Ayanokoji, Tycoon")
    if not persona:
        persona = "A ruthless, emotionless supercomputer"

    st.markdown("---")
    st.subheader("🗣️ DIALECT")
    tone = st.selectbox("How should they speak?", ["Calculated & Cold", "Gen Z", "Wall Street Corporate", "Savage"])

# --- 5. THE 4-AGENT ENGINE ---
def call_deepseek(system_prompt, user_prompt, temp=0.7):
    headers = {
        "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
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

# --- 6. CHAT INTERFACE ---
st.title("NEURAL CORE")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Voice & Image
col1, col2 = st.columns(2)
with col1:
    import audio_recorder_streamlit as audio_recorder
    audio_bytes = audio_recorder.audio_recorder(text="Record", neutral_color="#00ffcc")
with col2:
    uploaded_image = st.file_uploader("Upload Evidence", type=["png", "jpg", "jpeg"])

user_input = st.chat_input("INPUT PROBLEM DATA...")

if audio_bytes:
    with st.spinner("Transcribing audio..."):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=st.secrets['deepseek_api_key'], base_url="https://api.deepseek.com/v1")
            with open("temp_audio.wav", "wb") as f: f.write(audio_bytes)
            with open("temp_audio.wav", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
            user_input = transcript.text
        except Exception as e:
            st.error(f"Audio Error: {e}")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("EXECUTING 4-AGENT PROTOCOL..."):
            
            # If an image is uploaded, we skip the 4-agent loop and just read the image
            if uploaded_image is not None:
                img_bytes = uploaded_image.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                headers = {"Authorization": f"Bearer {st.secrets['deepseek_api_key']}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-v4.1-flash",
                    "messages": [
                        {"role": "system", "content": f"You are {persona}. Tone: {tone}. Core Memory: {core_memory}. Analyze this image."},
                        {"role": "user", "content": [
                            {"type": "text", "text": user_input},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}
                    ]
                }
                res = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                final_result = res.json()["choices"][0]["message"]["content"]
            
            # If no image, run the 4-Agent Brain
            else:
                # Agent 1: Profiler
                profiler_prompt = f"You are a cold psychological profiler. Analyze the hidden weaknesses and fears in this situation. Core Memory: {core_memory}. No em dashes. Be brutal."
                profile = call_deepseek(profiler_prompt, user_input, 0.4)
                
                # Agent 2: Strategist
                strategist_prompt = f"You are a master of asymmetric warfare. You are {persona}. Based on this psychological profile: '{profile}', give a highly unconventional, slightly ruthless move. No lists. No em dashes. Tone: {tone}."
                strategy = call_deepseek(strategist_prompt, user_input, 0.8)
                
                # Agent 3: Scientist
                scientist_prompt = "You are a data scientist. What real-world experiment (e.g., Pavlov, Asch) or famous historical figure (e.g., Elon Musk, Machiavelli) uses the tactic described here? Provide one single, hard-hitting citation."
                evidence = call_deepseek(scientist_prompt, strategy, 0.3)
                
                # Agent 4: Final Editor
                editor_prompt = f"""
                You are the final voice of a supercomputer. Combine the profiler, strategist, and scientist inputs into one cohesive, chilling response. 
                Speak with zero emotion. Short sentences. No lists. No em dashes. Tone: {tone}.
                
                Format EXACTLY like this:
                **THE ANALYSIS:**
                (Summarize the brutal truth based on the profiler)
                
                **THE EXECUTION:**
                (Give the strategist's unconventional move)
                
                **📚 THE EVIDENCE:**
                (Insert the scientist's citation naturally)
                
                **THE SCRIPT:**
                (Exact words the user should say, in the voice of {persona}.)
                """
                final_input = f"User Problem: {user_input}\n\nProfile: {profile}\n\nStrategy: {strategy}\n\nEvidence: {evidence}"
                final_result = call_deepseek(editor_prompt, final_input, 0.7)

            st.markdown(final_result)
            st.session_state.messages.append({"role": "assistant", "content": final_result})
            
            # Save History
            title = st.session_state.messages[0]["content"][:30]
            st.session_state.history[st.session_state.current_chat_id] = {
                "title": title,
                "messages": st.session_state.messages
            }
            save_history(st.session_state.history)

    st.markdown("---")
    st.code(st.session_state.messages[-1]["content"], language="text")
