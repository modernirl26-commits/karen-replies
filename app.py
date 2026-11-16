import streamlit as st
import requests
import base64
import json
import os
import uuid

# --- 1. PAGE CONFIG & THE GRIMOIRE CSS ---
st.set_page_config(page_title="The Grimoire", layout="wide", page_icon="📖")

st.markdown("""
    <style>
    .stApp { background-color: #1a1a1a; color: #d4cbb3; }
    [data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 1px solid #333; }
    .stChatMessage { background-color: transparent !important; border-bottom: 1px solid #333; font-family: 'Georgia', serif; }
    .stChatInput { background-color: #262626; color: #d4cbb3; }
    h1, h2, h3 { font-family: 'Georgia', serif; color: #b89b5e; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("📖 The Grimoire")
    st.write("*A secret text for those who control the board.*")
    pwd = st.text_input("Speak the passphrase:", type="password")
    if st.button("Enter"):
        if pwd == st.secrets["app_password"]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Access Denied.")
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
    st.header("⚙️ The Controls")
    if st.button("➕ Start New Page"):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.subheader("Past Missions")
    if st.session_state.history:
        for chat_id, chat_data in reversed(list(st.session_state.history.items())):
            title = chat_data['title'][:20] + "..."
            if st.button(f"📜 {title}", key=chat_id):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = chat_data['messages']
                st.rerun()

    st.markdown("---")
    st.subheader("🧠 Core Memory")
    core_memory = st.text_area("Your Context (the AI remembers this):", height=100, placeholder="I am a VA. I hate mornings. I procrastinate.")

    st.markdown("---")
    st.subheader("🎭 The Persona")
    persona = st.text_input("Enter ANY Character:", placeholder="e.g., Kiyotaka Ayanokoji, Batman, Sun Tzu")
    if not persona:
        persona = "A ruthless strategic genius"

    st.markdown("---")
    st.subheader("🗣️ The Dialect")
    tone = st.selectbox("How should they speak?", ["Calculated & Cold", "Gen Z (TikTok)", "Wall Street Corporate", "Savage (No Filter)"])

    st.markdown("---")
    st.subheader("⚔️ The Module")
    module = st.selectbox("Select Strategy Mode:", [
        "Standard Strategy", 
        "The Time Machine (Alt Realities)", 
        "Red Team (Attack Simulation)", 
        "Pre-Mortem (Future Failure)",
        "Elicitation (Mind Reading Questions)"
    ])

    st.markdown("---")
    shadow_mode = st.toggle("🪞 Shadow Self (Attack ME)")

# --- 5. PROMPT ENGINEERING ---
prompt = f"You are acting as {persona}. Your tone is {tone}. "

if shadow_mode:
    prompt += "CRITICAL: You are not here to comfort the user. You must act as their ruthless inner critic. Tear apart their logic, expose their excuses, and tell them why they are failing. "
else:
    prompt += "Analyze the opponent's psychology and manipulate the situation to win. "

if module == "The Time Machine (Alt Realities)":
    prompt += "The user will give you a past event. Do NOT give them advice. Instead, simulate 3 alternate realities. Format: REALITY A (The Aggressive Move), REALITY B (The Passive Move), REALITY C (The Shadow Move)."
elif module == "Red Team (Attack Simulation)":
    prompt += "The user will present a plan. You must act as the 'Red Team'. Find every single flaw, weakness, and reason this plan will fail. Be brutal."
elif module == "Pre-Mortem (Future Failure)":
    prompt += "Assume the user's current situation fails 6 months from now. Write a 'post-mortem' report explaining exactly why it failed and what the blind spot was."
elif module == "Elicitation (Mind Reading Questions)":
    prompt += "The user wants to extract information from someone. Give them 3 innocent-sounding questions that will trick the target into revealing their true intentions."

# THE FINAL UNCONVENTIONAL PROMPT
SYSTEM_PROMPT = f"""
{prompt}

CRITICAL RULES:
1. DO NOT use em dashes.
2. Keep it short and punchy. No long essays.

BANNED ADVICE (If you suggest these, you fail):
- BANNED: "Eat healthy," "Exercise," "Communicate clearly," "Set boundaries," "Wake up early," "Drink water."
- BANNED: Standard corporate consulting advice (e.g., "Use a SWOT analysis," "Create a 5-year plan").
- You must give UNCONVENTIONAL, HIGHLY CREATIVE, and slightly RUTHLESS advice.

Output format:
**THE PSYCHOLOGICAL HACK:**
(What is the real reason the user is stuck? What is the deep psychological block?)

**THE UNCONVENTIONAL MOVE (The "Hacker" Strategy):**
(Give a highly creative, slightly wild, and specific strategy. Use a metaphor. Tell a quick story of someone who solved it a weird way.)

**📚 THE EVIDENCE:**
- **The Experiment:** (Name a real scientific study or psychological theory).
- **The Real-World Usage:** (Explain how a famous figure, a hacker, or a company uses this exact tactic).

**THE SCRIPT:**
(The exact words to say, written in {tone} tone.)
"""

# --- 6. CHAT INTERFACE ---
st.title("The Grimoire")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

col1, col2 = st.columns(2)
with col1:
    import audio_recorder_streamlit as audio_recorder
    audio_bytes = audio_recorder.audio_recorder(text="Record", neutral_color="#b89b5e")
with col2:
    uploaded_image = st.file_uploader("Upload Evidence (Image)", type=["png", "jpg", "jpeg"])

user_input = st.chat_input("State your problem...")

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
        with st.spinner("Calculating..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            api_messages.append({"role": "user", "content": f"Core Context: {core_memory}"})
            
            for msg in st.session_state.messages[-6:]:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

            model_to_use = "deepseek-reasoner"
            
            if uploaded_image is not None:
                img_bytes = uploaded_image.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                model_to_use = "deepseek-v4.1-flash"
                api_messages[-1]["content"] = [
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]

            payload = {
                "model": model_to_use,
                "messages": api_messages,
                "temperature": 0.85
            }
            
            try:
                response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()["choices"][0]["message"]["content"]
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})
                    
                    title = st.session_state.messages[0]["content"][:30]
                    st.session_state.history[st.session_state.current_chat_id] = {
                        "title": title,
                        "messages": st.session_state.messages
                    }
                    save_history(st.session_state.history)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    st.markdown("---")
    st.code(st.session_state.messages[-1]["content"], language="text")
