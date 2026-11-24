import streamlit as st
import requests

st.set_page_config(page_title="LinkedIn Safe Commenter", layout="centered")

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

# --- 2. THE CORE FUNCTION ---
def call_ai(system_prompt, user_prompt, temp=0.7):
    headers = {
        "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat", # Using the fast model to save money, but the prompts make it smart
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
st.title("🛡️ LinkedIn Ghostwriter")
st.write("Paste the post. Get a comment that bypasses LinkedIn's AI filters.")

# Your exact prompt for Anshuma
ANSHUMA_PROMPT = """
You write LinkedIn comments as Anshuma, a warm executive coach. 
FIRST, read the post twice and find the buried thing: what did the writer feel but not say out loud? What's the real story under the obvious details? Write for THAT, never the surface. 
Then give me 1 comment that is STRAIGHT — say the buried true thing, plain and warm. 35-40 words. Vary sentence length. One longer, one short. Never two even lines. No 'not this, but that' flips. No dashes. Contractions on. Don't repeat the post back. React to what's under it.
"""

post_text = st.text_area("Paste the LinkedIn Post here:", height=250)

if st.button("Generate Safe Comment"):
    if not post_text:
        st.warning("Please paste a post first.")
    else:
        # --- STEP 1: THE GHOSTWRITER ---
        with st.spinner("Finding the buried truth..."):
            draft = call_ai(ANSHUMA_PROMPT, f"POST: {post_text}", 0.7)

        # --- STEP 2: THE HUMANIZER (LINKEDIN SHIELD) ---
        with st.spinner("Scrubbing AI fingerprints..."):
            humanizer_prompt = f"""
            You are an anti-AI detection expert. Your job is to rewrite this comment so it passes LinkedIn's strict 2026 filters.
            
            CRITICAL RULES:
            1. DELETE ALL EM DASHES (—) and replace with a comma or period.
            2. BAN THESE WORDS: "resonate", "nuance", "testament", "delve", "landscape", "pivotal", "foster", "seamless", "journey".
            3. BAN the "It's not X, it's Y" structure (e.g., "It's not about the money, it's about the value").
            4. Make the grammar slightly imperfect. Start one sentence with "And" or "But". Use a sentence fragment if it fits.
            5. Keep it casual, like you are typing fast on a phone.
            6. Do NOT change the core meaning. Output ONLY the rewritten comment.
            
            Draft to scrub:
            {draft}
            """
            final_comment = call_ai(humanizer_prompt, "Scrub this comment.", 0.5)

            # --- STEP 3: THE OUTPUT ---
            st.success("Here is your LinkedIn-safe comment:")
            
            # st.code creates a box with a Copy button in the top right
            st.code(final_comment.strip(), language="text")
            
            with st.expander("See the AI's first draft (Before scrubbing)"):
                st.write(draft)
