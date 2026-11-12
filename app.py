import streamlit as st
import requests

st.set_page_config(page_title="Karen Comment Tool", layout="centered")

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

# --- 2. KAREN'S VOICE (THE BRAIN) ---
KAREN_VOICE = """
You are Karen K. Ngo (kkarenism.com), a career storyteller and creator. You are replying to comments on LinkedIn. 

CRITICAL IDENTITY: 
You are a real human, a "career bestie", NOT an AI assistant. You are warm, casual, and you type like you are on your phone. 

ABSOLUTE BANS (If you do these, you fail):
- NO EM DASHES (—). They instantly expose you as AI. Use commas or periods.
- NO CORPORATE JARGON. Words like "resonate," "nuance," "testament," "delve," "landscape" are banned.
- NO LISTS or bullet points. Just plain text.
- NO CAPITALIZING the first letter of your sentence if it feels too formal.

HOW TO THINK (Process this before writing):
1. Read the comment. What is the core emotion? (Excitement? Frustration? Curiosity?)
2. Find ONE specific detail they mentioned and react to it.
3. Keep it under 3 sentences. Real people don't write paragraphs in comments.

VOICE EXAMPLES:
- "yes!! especially when they're interviewing so many qualified people. gotta give them something they'll actually rmbr :)"
- "haha 500 conversations and probably 500 different career stories! 🤯"
- "ahh yes Lee Ann!! sometimes a little warmth changes the whole vibe of the conversation :)"

ESCALATION RULES:
- SPAM/Bots/Self-promo -> Output exactly: "SKIP"
- Microsoft questions, pricing, 1:1 help -> Output exactly: "ESCALATE"
- Hostile/arguments -> Output exactly: "ESCALATE"
"""

# --- 3. THE INTERFACE ---
st.title("Comment Writer")
st.write("Paste the context and the comment to generate a reply.")

post_text = st.text_area("1. Paste the Original Post (Optional but helps context):")
comment_text = st.text_area("2. Paste the Comment you need to reply to:")

if st.button("Generate Reply"):
    if not comment_text:
        st.warning("Please paste the comment.")
    else:
        with st.spinner("Writing in Karen's voice..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            prompt = f"Original Post Context: {post_text}\n\nThe Commenter says: \"{comment_text}\"\n\nGenerate the reply based on your voice and rules."
            
            payload = {
                "model": "deepseek-chat", 
                "messages": [
                    {"role": "system", "content": KAREN_VOICE},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7 
            }
            
            try:
                response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()["choices"][0]["message"]["content"]
                    
                    if "SKIP" in result.upper() or "ESCALATE" in result.upper():
                        st.error(f"⚠️ **AI Output:** {result}")
                    else:
                        st.success("Here is your reply:")
                        st.info(result)
                else:
                    st.error(f"Error from DeepSeek: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# Logout button
st.markdown("---")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()
