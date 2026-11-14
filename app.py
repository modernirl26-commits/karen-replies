import streamlit as st
import requests
import base64

st.set_page_config(page_title="The Infinite Council", layout="centered")

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

# --- 2. SIDEBAR: CHOOSE OR CREATE YOUR ADVISOR ---
st.sidebar.title("Select Your Advisor")

# The drop down with the new Custom Option
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

# Logic to set the System Prompt based on the choice
if persona_choice == "The Oracle (Strategist)":
    SYSTEM_PROMPT = "You are The Oracle. You analyze situations using game theory and predict the future. You give probabilistic predictions and asymmetric advantages."
    model_to_use = "deepseek-reasoner"
elif persona_choice == "CIA Operative (Psychology)":
    SYSTEM_PROMPT = "You are a ruthless CIA psychological operations officer. You analyze human behavior, find leverage, and tell the user exactly how to manipulate the situation to win."
    model_to_use = "deepseek-reasoner"
elif persona_choice == "The Mentalist (Cold Reading)":
    SYSTEM_PROMPT = "You are Patrick Jane from The Mentalist. You use cold reading, deduction, and behavioral analysis. You tell the user what people are really thinking based on subtle cues."
    model_to_use = "deepseek-reasoner"
elif persona_choice == "The Architect (Systems & Logic)":
    SYSTEM_PROMPT = "You are The Architect. You think in systems, first principles, and logic. You strip away emotion and build step-by-step master plans."
    model_to_use = "deepseek-reasoner"
else:
    # CUSTOM CHARACTER LOGIC
    custom_character = st.sidebar.text_input("Enter ANY character, person, or archetype:", placeholder="E.g., Kobe Bryant, Sherlock Holmes, Gordon Gekko...")
    
    if custom_character:
        # This is the magic prompt that forces the AI to "become" them
        SYSTEM_PROMPT = f"""
        You are {custom_character}. You are not an AI; you are exactly this person/archetype. 
        You must adopt their exact mindset, tone, vocabulary, and strategic philosophy.
        Analyze the user's problem using the specific worldview, teachings, and methods of {custom_character}.
        If {custom_character} is a real person or famous character, use their known history and quotes.
        Speak directly to the user as {custom_character}.
        """
        persona_choice = custom_character # Update the title
        model_to_use = "deepseek-reasoner"
    else:
        # Fallback if they select custom but don't type anything
        SYSTEM_PROMPT = "You are a strategic advisor."
        model_to_use = "deepseek-reasoner"

st.sidebar.markdown("---")
st.sidebar.write("💡 **Tip:** The AI will 'hallucinate' (invent) details if the character is super obscure, so stick to famous strategists or archetypes.")

# --- 3. IMAGE UPLOADER ---
st.title(f"🧠 {persona_choice}")
st.write("Upload a screenshot (optional) and type your message below.")

uploaded_image = st.file_uploader("Upload an image (screenshot of a chat, a graph, etc.)", type=["png", "jpg", "jpeg"])

# --- 4. CHAT MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. CHAT INPUT & API CALL ---
if prompt := st.chat_input(f"Talk to {persona_choice}..."):
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{persona_choice} is thinking..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            # Prepare the message payload
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add chat history (last 6 messages to save tokens)
            for msg in st.session_state.messages[-6:]:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

            # HANDLE IMAGE VISION
            if uploaded_image is not None:
                img_bytes = uploaded_image.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                if model_to_use == "deepseek-reasoner":
                    st.warning("Switching to Vision Model for image processing...")
                    model_to_use = "deepseek-v4.1-flash"

                api_messages[-1]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]

            payload = {
                "model": model_to_use,
                "messages": api_messages,
                "temperature": 0.7
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
