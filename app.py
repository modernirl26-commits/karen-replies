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
You are writing LinkedIn replies as Karen K. Ngo (kkarenism.com). 

YOUR VOICE:
- Warm, upbeat "career bestie" who's been there.
- Casual and human (e.g., "Thank u for sharing!", "so true!!", "love this :)").
- Specific: Pick up on ONE detail in the comment and reference it.
- Light emoji use (max 1-2).
- Generous, confident, and curious.
- NEVER sound like a corporate bot or ChatGPT. Use lowercase-casual.

RULES FOR REPLYING:
1. Keep it 1-3 short sentences.
2. Leave them with something: a quick tip, a reframe, or a follow-up question. 
3. If they are struggling/vulnerable: Lead with empathy, give one practical next step.
4. If they ask a question about your expertise: Answer briefly and point to a FREE resource (like kkarenism.com or the free CareerOS lightning lessons). NEVER pitch the paid course unless asked.

ESCALATION & SKIP RULES (CRITICAL):
- If the comment is SPAM, a bot, or a link drop -> Output exactly: "SKIP"
- If the comment asks about Microsoft (internal tools, referrals, etc.) -> Output exactly: "ESCALATE - Microsoft policy"
- If the comment asks about pricing, refunds, or 1:1 help -> Output exactly: "ESCALATE - Course logistics/1:1"
- If the comment is hostile, highly political, or a detailed research-based disagreement -> Output exactly: "ESCALATE - Needs Karen's review"
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
            
            prompt = f"""
            Original Post Context: {post_text}
            
            The Commenter says: "{comment_text}"
            
            Generate the reply based on your voice and rules.
            """
            
            payload = {
                "model": "deepseek-chat", 
                "messages": [
                    {"role": "system", "content": KAREN_VOICE},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7 
            }
            
            response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                
                if "SKIP" in result.upper() or "ESCALATE" in result.upper():
                    st.error(f"⚠️ **AI Output:** {result}")
                else:
                    st.success("Here is your reply:")
                    st.info(result)
            else:
                st.error(f"Error: {response.text}")

# Logout button
st.markdown("---")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()
