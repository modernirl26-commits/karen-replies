import streamlit as st
import requests

st.set_page_config(page_title="Deep Thinker", page_icon="🧠", layout="wide")

# --- 1. PREMIUM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #d1d5db; font-family: 'Inter', sans-serif; }
    .stChatMessage { background-color: transparent; border: none; padding: 1.5rem; max-width: 800px; margin: 0 auto; }
    .stChatMessage[data-testid="stChatMessageUser"] { background-color: #11151c; border-radius: 12px; }
    .stChatInput { background-color: #1f2937; color: #f9fafb; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIN ---
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

# --- 3. THE COGNITIVE ENGINE ---
def call_thinker(user_prompt):
    headers = {
        "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
        "Content-Type": "application/json"
    }
    
    # The "NoteGPT" System Prompt forces deep reasoning
    system_prompt = """
    You are an elite, highly intelligent AI assistant (like Claude 3.5 Sonnet or NoteGPT). 
    You do not give shallow answers. You think deeply before you speak.

    Here is your cognitive process:
    1. First, analyze the user's underlying intent. What are they ACTUALLY asking for?
    2. Then, structure your thoughts. Break the problem down logically.
    3. Finally, deliver the answer in a clear, incredibly smart, and nuanced way.

    Rules:
    - Do NOT use em dashes (—).
    - Do NOT use AI filler words (delve, testament, landscape).
    - Be direct, warm, and profound.
    """
    
    api_messages = [{"role": "system", "content": system_prompt}]
    # Include chat history for memory
    for msg in st.session_state.messages[-6:]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})
        
    payload = {
        "model": "deepseek-reasoner", # <--- THE SMART MODEL
        "messages": api_messages,
        "temperature": 0.7
    }
    
    try:
        res = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
        data = res.json()["choices"][0]["message"]
        
        # deepseek-reasoner returns a "reasoning_content" (the thoughts) and "content" (the answer)
        thoughts = data.get("reasoning_content", "")
        final_answer = data.get("content", "")
        return thoughts, final_answer
    except Exception as e:
        return "", f"Error: {e}"

# --- 4. THE INTERFACE ---
st.title("🧠 Deep Thinker")
st.write("This AI uses the `deepseek-reasoner` model. It thinks deeply before answering.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a deep question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking deeply... (This takes 15-20 seconds)"):
            thoughts, response = call_thinker(prompt)
            
            # Show the final answer
            st.markdown(response)
            
            # Put the "Brain" (thought process) in an expander
            if thoughts:
                with st.expander("🧠 See the AI's thought process"):
                    st.write(thoughts)
                    
            st.session_state.messages.append({"role": "assistant", "content": response})
