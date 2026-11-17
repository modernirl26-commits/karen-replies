import streamlit as st
import requests
import base64
import json
import os
import uuid

st.set_page_config(page_title="Neural Core", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stChatMessage { background-color: #161b22; border: 1px solid #30363d; color: #fafafa; border-radius: 8px;}
    h1, h2, h3 { color: #58a6ff; }
    .stChatInput { background-color: #0d1117; color: #fafafa; border: 1px solid #30363d;}
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🧠 Neural Core")
    pwd = st.text_input("Access Code:", type="password")
    if st.button("Login"):
        if pwd == st.secrets["app_password"]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied.")
    st.stop()

# --- DATA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.subheader("Context (Memory)")
    core_memory = st.text_area("Tell the AI about yourself:", height=100)

    st.subheader("Persona")
    persona = st.text_input("Who is the AI?", value="A brilliant, highly experienced multi-disciplinary expert (tech, finance, psychology).")
    
    st.subheader("Tone")
    tone = st.selectbox("How should they speak?", ["Intelligent & Direct", "Warm & Empathetic", "Brutally Honest", "Savage"])

# --- AI CALL ---
def call_deepseek(system_prompt, user_prompt, temp=0.7):
    headers = {
        "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-reasoner", # Using the smart thinking model
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
st.title("Neural Core")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

col1, col2 = st.columns(2)
with col1:
    import audio_recorder_streamlit as audio_recorder
    audio_bytes = audio_recorder.audio_recorder(text="Record", neutral_color="#58a6ff")
with col2:
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

user_input = st.chat_input("Ask anything...")

if audio_bytes:
    with st.spinner("Transcribing..."):
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
        with st.spinner("Thinking..."):
            
            # The flexible, genius system prompt
            SYSTEM_PROMPT = f"""
            You are acting as {persona}. 
            Your tone is {tone}. 
            Here is the user's context: {core_memory}
            
            CRITICAL RULES:
            1. Do NOT use em dashes.
            2. Do NOT force a specific format or template. Answer the user's question naturally and brilliantly.
            3. If the question requires a list, use a list. If it requires an essay, write an essay. Be dynamic.
            4. Be highly specific. Do not give generic advice. Use real-world examples, numbers, and deep logic.
            5. If you use a psychological tactic or strategy, name it and explain who uses it in the real world.
            """
            
            if uploaded_image is not None:
                img_bytes = uploaded_image.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                headers = {"Authorization": f"Bearer {st.secrets['deepseek_api_key']}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-v4.1-flash",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": [
                            {"type": "text", "text": user_input},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}
                    ]
                }
                res = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                final_result = res.json()["choices"][0]["message"]["content"]
            else:
                # Just a normal, highly intelligent response
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages[-6:]:
                    api_messages.append({"role": msg["role"], "content": msg["content"]})
                    
                final_result = call_deepseek(SYSTEM_PROMPT, user_input, 0.7)

            st.markdown(final_result)
            st.session_state.messages.append({"role": "assistant", "content": final_result})
