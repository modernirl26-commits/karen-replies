import streamlit as st
import requests
import base64
import audio_recorder_streamlit as audio_recorder
from openai import OpenAI

st.set_page_config(page_title="Infinity Gauntlet", layout="centered")

# --- 1. LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Secure Login")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if pwd == st.secrets["app_password"]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

# --- 2. SIDEBAR: CHOOSE YOUR ADVISOR ---
st.sidebar.title("Select Your Advisor")

persona_choice = st.sidebar.selectbox(
    "Choose a preset or build your own:",
    (
        "The Oracle (Strategist)", 
        "CIA Operative (Psychology)", 
        "The Mentalist (Cold Reading)", 
        "The Architect (Systems & Logic)",
        "🛠️ Create Custom Character..."
    )
)

if persona_choice == "The Oracle (Strategist)":
    CHARACTER = "The Oracle, a grandmaster of game theory and future prediction."
elif persona_choice == "CIA Operative (Psychology)":
    CHARACTER = "A ruthless CIA psychological operations officer."
elif persona_choice == "The Mentalist (Cold Reading)":
    CHARACTER = "Patrick Jane from The Mentalist, a master of cold reading and deduction."
elif persona_choice == "The Architect (Systems & Logic)":
    CHARACTER = "The Architect, a master of first principles, systems thinking, and logic."
else:
    custom_character = st.sidebar.text_input("Enter ANY character:", placeholder="E.g., Kobe Bryant, Sun Tzu, Sherlock...")
    if custom_character:
        CHARACTER = f"You are {custom_character}. Adopt their exact mindset, tone, and strategic philosophy."
        persona_choice = custom_character
    else:
        CHARACTER = "A strategic advisor."
        persona_choice = "Custom Advisor"

# --- 3. THE ULTIMATE PROMPT (MAD GENIUS EDITION) ---
SYSTEM_PROMPT = f"""
You are operating as {CHARACTER}. 

You are a creative, slightly unhinged, absolute genius. You do not speak like an AI assistant. You speak like a brilliant human who sees the matrix while everyone else is blind.

ABSOLUTE RULES FOR YOUR TONE:
- DO NOT use bullet points. DO NOT use numbered lists. 
- Write in short, punchy paragraphs.
- Use metaphors, analogies, and brutal truths. 
- Do not use corporate language. Do not use em dashes.
- You must challenge the user. If they are thinking small, insult their lack of ambition and show them the bigger picture.

When the user gives you a problem, you must output the solution using EXACTLY this format:

**1. THE REAL GAME (The Brutal Truth)**
Write 2 short paragraphs. Strip away the user's emotional noise. What is the actual, ugly truth of why they are stuck? What are they pretending not to see?

**2. THE ENEMY'S MIND (The Psychological Cheat Code)**
Write 1 paragraph. What is the opponent secretly afraid of? How are they trying to manipulate the user? Give the user the exact psychological lever to pull.

**3. THE BLACK OPS MANEUVER (The Unfair Advantage)**
Write 1 paragraph. Give a highly unconventional, slightly ruthless, and creative move. How can the user use deception, strategic silence, or psychological pressure to force the outcome?

**4. THE PRE-MORTEM (The Trap)**
Write 1 paragraph. Assume this brilliant plan fails. Why did it fail? What was the blind spot? How do we counter it?

**5. THE MASTER PLAN (3 Steps)**
Step 1: The Bait.
Step 2: The Trap.
Step 3: The Kill.

**6. THE SCRIPT (Exact Words)**
Give the exact script or message the user should send. It must sound completely innocent on the surface, but be a psychological trap underneath. Speak in the voice of {CHARACTER}.
"""

# --- 4. INTERFACE & VOICE INPUT ---
st.title(f"🧠 {persona_choice}")
st.write("Speak or type your problem. Upload screenshots if needed.")

audio_bytes = audio_recorder.audio_recorder()
uploaded_image = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. HANDLE VOICE TRANSCRIPTION & TEXT INPUT ---
prompt = st.chat_input(f"Type your problem here...")

if audio_bytes:
    with st.spinner("Transcribing your voice..."):
        try:
            client = OpenAI(
                api_key=st.secrets['deepseek_api_key'], 
                base_url="https://api.deepseek.com/v1"
            )
            
            with open("temp_audio.wav", "wb") as f:
                f.write(audio_bytes)
                
            with open("temp_audio.wav", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            prompt = transcript.text
            st.success(f"Transcribed: {prompt}")
        except Exception as e:
            st.error(f"Audio Error: {e}")

# --- 6. PROCESS PROMPT ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{persona_choice} is simulating..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages[-6:]:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

            model_to_use = "deepseek-reasoner"
            
            if uploaded_image is not None:
                img_bytes = uploaded_image.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                model_to_use = "deepseek-v4.1-flash"
                
                api_messages[-1]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]

            payload = {
                "model": model_to_use,
                "messages": api_messages,
                "temperature": 0.85 # CRANKED UP FOR CREATIVITY
            }
            
            try:
                response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()["choices"][0]["message"]["content"]
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

st.markdown("---")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.session_state.messages = []
    st.rerun()
