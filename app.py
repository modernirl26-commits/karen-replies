import streamlit as st
import requests
import base64

st.set_page_config(page_title="The Strategist", layout="centered")

# --- LOGIN ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.header("Context")
    core_memory = st.text_area("Tell the AI about yourself:", height=150, placeholder="I am a BBA grad in India. I am scared of AI. I want to buy bikes.")

# --- INTERFACE ---
st.title("🧠 The Strategist")
st.write("Ask a complex question. The AI will use DeepSeek's deepest reasoning model to answer.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

uploaded_image = st.file_uploader("Upload Image (Optional)", type=["png", "jpg", "jpeg"])
prompt = st.chat_input("Ask your question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking deeply..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            # The NEW, clean prompt. No templates. Just pure intelligence.
            SYSTEM_PROMPT = f"""
            You are an elite strategic thinker, combining the intelligence of a top-tier business consultant, a psychologist, and a tech expert.
            
            Here is the user's context: {core_memory}
            
            Your goal is to give the user a genuinely brilliant, highly creative, and deeply nuanced answer. 
            
            RULES:
            1. Do NOT use a template. Answer naturally.
            2. Do NOT use em dashes (—).
            3. Think outside the box. Do not give generic advice like "do an MBA" or "learn coding." Give them highly specific, unconventional paths they haven't thought of.
            4. If you are asked about the future or AI, be realistic but highly strategic.
            """
            
            model_to_use = "deepseek-reasoner"
            
            if uploaded_image is not None:
                img_bytes = uploaded_image.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                model_to_use = "deepseek-v4.1-flash"
                
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages[-4:]:
                    if msg["role"] != "assistant" or msg == st.session_state.messages[-1]:
                         api_messages.append({"role": msg["role"], "content": msg["content"]})
                         
                api_messages[-1]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            else:
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages[-4:]:
                    api_messages.append({"role": msg["role"], "content": msg["content"]})

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
