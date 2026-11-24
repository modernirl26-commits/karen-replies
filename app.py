import streamlit as st
import requests

st.set_page_config(page_title="LinkedIn Sentinel", layout="centered")

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

# --- 2. THE AUDITOR BRAIN ---
def call_ai(system_prompt, user_prompt, temp=0.3):
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

# --- 3. THE INTERFACE ---
st.title("🛡️ LinkedIn Sentinel")
st.write("Paste a comment below. The AI will audit it against LinkedIn's 2026 AI-detection filters.")

comment_to_test = st.text_area("Paste the Comment:", height=200)

if st.button("Audit Comment"):
    if not comment_to_test:
        st.warning("Please paste a comment first.")
    else:
        with st.spinner("Running risk analysis..."):
            
            auditor_prompt = """
            You are a ruthless LinkedIn risk-control auditor. Your job is to analyze a draft comment and predict if LinkedIn's 2026 algorithm will flag it as "AI-generated slop" and hide it in the "Most Recent" tab.

            Here are the rules of the 2026 LinkedIn algorithm:
            1. It HATES em dashes (—).
            2. It HATES perfect grammar. It wants human messiness (lowercase, fragments, casual fillers like 'fr', 'lol', 'honestly').
            3. It flags "AI words" (delve, testament, nuance, underneath, journey).
            4. It penalizes comments that just validate the post without adding a concrete, specific detail.
            5. It flags the "It's not X, it's Y" structure.

            Analyze the comment provided by the user. Output EXACTLY in this format:

            **RISK SCORE:** [Give a score from 1 to 10. 10 means it will absolutely pass and be seen. 1 means it will be hidden instantly.]

            **THE RED FLAGS:**
            [List the exact words, punctuation, or structures in the comment that will trigger the algorithm. If there are none, say "None".]

            **THE VERDICT:**
            [A 2-sentence explanation of why it will pass or fail.]

            **THE FIX:**
            [If the score is below 8, rewrite the comment to be 100% safe. Make it messy, lowercase, human, and remove all AI tells. If it's already an 8+, just say "No changes needed."]
            """
            
            result = call_ai(auditor_prompt, f"Here is the comment to audit:\n\n{comment_to_test}", 0.3)
            
            st.markdown(result)

st.markdown("---")
st.write('💡 **Tip:** If the score is below 8, copy the text from the "THE FIX" section and use that instead.')
