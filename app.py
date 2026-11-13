import streamlit as st
import requests

st.set_page_config(page_title="The War Room", layout="centered")

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

# --- 2. THE STRATEGIST BRAIN ---
STRATEGIST_BRAIN = """
You are a ruthless, elite strategic consultant. You do not give fluffy, emotional advice. You solve problems using logic, game theory, economics, and business frameworks.

The user will present a personal or professional problem.
You must analyze it and provide a structured solution using the following format:

**1. The Core Issue (First Principles):**
Strip away the emotion. What is the actual bottleneck or root cause of this problem? 

**2. The Data/Framework:**
Apply a specific, real-world framework to solve this. For example, use the Pareto Principle (80/20 rule), Game Theory, SWOT Analysis, or Cost-Benefit Analysis. Use numbers and logic to justify the strategy.

**3. The Brutal Truth:**
What is the user doing wrong? What uncomfortable truth are they avoiding? 

**4. The Action Plan (Step-by-Step):**
Give 3 specific, measurable actions the user must take immediately to solve this. If it requires a script to send to a client or boss, write the exact script.
"""

# --- 3. THE INTERFACE ---
st.title("🧠 The War Room")
st.write("Paste your problem. Get a logical, strategic solution.")

problem = st.text_area("What is the problem?", height=200, placeholder="E.g., My client keeps adding extra work without paying me, but I'm scared to lose the income...")

if st.button("Formulate Strategy"):
    if not problem:
        st.warning("Please describe the problem.")
    else:
        with st.spinner("Applying strategic frameworks..."):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-reasoner", # Using the smart thinking model
                "messages": [
                    {"role": "system", "content": STRATEGIST_BRAIN},
                    {"role": "user", "content": problem}
                ],
                "temperature": 0.4 # Lower temperature for cold, hard logic
            }
            
            try:
                response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()["choices"][0]["message"]["content"]
                    st.markdown(result)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

st.markdown("---")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()
