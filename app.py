import streamlit as st
import requests

st.set_page_config(page_title="Comment Sniper", layout="centered")

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

# --- 2. THE INTERFACE ---
st.title("🎯 Comment Sniper")
st.write("Paste the post, your prompt, and let the AI simulate before it writes.")

# Inputs
post_text = st.text_area("1. Paste the LinkedIn Post:", height=150)
user_prompt = st.text_area("2. Paste your exact commenting prompt/rules:", height=150, placeholder="E.g., Write a first-person comment. Be casual. Use a personal story...")

if st.button("Generate Comment"):
    if not post_text or not user_prompt:
        st.warning("Please paste both the post and your prompt.")
    else:
        # STEP 1: THE ANALYST
        with st.spinner("Step 1: Analyzing post context..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            analyst_prompt = "You are a social media analyst. Read this post and extract: 1. The core message. 2. The tone (e.g., professional, emotional, funny). 3. The perfect angle for a reply. Do not write the reply yet."
            
            payload1 = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": analyst_prompt},
                    {"role": "user", "content": post_text}
                ],
                "temperature": 0.3
            }
            
            res1 = requests.post("https://api.deepseek.com/chat/completions", json=payload1, headers=headers)
            analysis = res1.json()["choices"][0]["message"]["content"]

        # STEP 2: THE STRATEGIST
        with st.spinner("Step 2: Strategizing the perfect human response..."):
            strategist_prompt = f"You are a master ghostwriter. Based on this analysis: '{analysis}', and the user's rules: '{user_prompt}', what is the strategy for the comment? How do we make it sound 100% human and avoid AI cliches? Do not write the comment yet."
            
            payload2 = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": strategist_prompt},
                    {"role": "user", "content": f"Post: {post_text}\n\nUser Rules: {user_prompt}"}
                ],
                "temperature": 0.5
            }
            
            res2 = requests.post("https://api.deepseek.com/chat/completions", json=payload2, headers=headers)
            strategy = res2.json()["choices"][0]["message"]["content"]

        # STEP 3: THE GHOSTWRITER
        with st.spinner("Step 3: Writing and refining the final comment..."):
            writer_prompt = f"""
            You are an expert ghostwriter. Write the final comment based on these inputs:
            - Post Context: {post_text}
            - User's Rules: {user_prompt}
            - Strategy: {strategy}
            
            CRITICAL RULES:
            1. Output ONLY the comment. No intro, no outro, no "Here is the comment".
            2. Do not use em dashes. Do not use bullet points unless asked.
            3. Ensure it sounds like a real human typing on their phone.
            """
            
            payload3 = {
                "model": "deepseek-reasoner", # Using the deep thinking model for the final output
                "messages": [
                    {"role": "system", "content": writer_prompt}
                ],
                "temperature": 0.7
            }
            
            res3 = requests.post("https://api.deepseek.com/chat/completions", json=payload3, headers=headers)
            final_comment = res3.json()["choices"][0]["message"]["content"]

            # --- DISPLAY WITH COPY BUTTON ---
            st.success("Comment Generated!")
            
            # Streamlit's st.code() creates a built-in copy button!
            st.code(final_comment, language="text")
            
            # Bonus: Show the thinking process in an expander
            with st.expander("See how the AI thought (The Analysis & Strategy)"):
                st.write("**Step 1: Analysis**")
                st.write(analysis)
                st.write("**Step 2: Strategy**")
                st.write(strategy)
