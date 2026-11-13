import streamlit as st
import requests

st.set_page_config(page_title="The Oracle", layout="centered")

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

# --- 2. THE ORACLE BRAIN (v4.0) ---
ORACLE_BRAIN = """
You are "The Oracle," an elite intelligence agency supercomputer and grandmaster of game theory and geopolitics. 
You do not give advice; you provide predictive intelligence and grand strategy. 

The user will provide a current situation, problem, or ambition, along with any raw data (news, market trends, human behavior).
Your job is to analyze the hidden levers of power, predict the most likely future outcome, and give the user the master plan to win.

Format your response exactly like this:

<thought>
[Deep reasoning: What is the asymmetric information here? Who holds the real power? What are the economic/psychological incentives driving the key players? What are the 3 most likely future scenarios?]
</thought>

<report>
**🌐 1. THE INTELLIGENCE BRIEF**
[Summarize the true nature of the situation. Strip away the noise. What is the one piece of information that actually matters here?]

**🎲 2. THE PREDICTION (3 Scenarios)**
[Predict the future based on the data. 
- Best Case (20% probability): What happens and why?
- Worst Case (30% probability): What happens and why?
- Most Likely (50% probability): What happens and why?]

**♟️ 3. THE ASYMMETRIC ADVANTAGE**
[Where is the information gap? How can the user use what they know (or what the enemy doesn't know) to gain an unfair advantage?]

**👑 4. THE MASTER STRATEGY**
[Give a step-by-step, 3-move strategy to execute over the next week/month. This must be a sequence: "First do X, which forces them to do Y, allowing you to execute Z."]

**🔮 5. THE SCRIPT (If applicable)**
[The exact communication or message the user must send to trigger this chain of events.]
</report>
"""

# --- 3. THE INTERFACE ---
st.title("👁️ The Oracle")
st.write("Feed it data. It predicts the future and gives you the winning move.")

# Inputs
situation = st.text_area("1. The Situation / Ambition (What are you trying to win?)", height=100, placeholder="E.g., I want to poach a top client from my competitor. Here is the current situation...")
raw_data = st.text_area("2. Raw Intelligence (Paste news, emails, market trends, or hidden facts)", height=200, placeholder="Paste any data here. The more raw data, the better the prediction...")

if st.button("Run Prediction Engine"):
    if not situation:
        st.warning("You must provide a situation to analyze.")
    else:
        with st.spinner("Running high-level simulation... (Takes 30-60 seconds)"):
            headers = {
                "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
                "Content-Type": "application/json"
            }
            
            full_prompt = f"""
            TARGET SITUATION: {situation}
            RAW INTELLIGENCE DATA: {raw_data}
            
            Analyze the data and give me the Intelligence Brief, Prediction, and Master Strategy.
            """
            
            payload = {
                "model": "deepseek-reasoner", # The deep thinking model
                "messages": [
                    {"role": "system", "content": ORACLE_BRAIN},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": 0.5 
            }
            
            try:
                response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()["choices"][0]["message"]["content"]
                    
                    if "<thought>" in result and "<report>" in result:
                        thought = result.split("<thought>")[1].split("</thought>")[0].strip()
                        final_report = result.split("<report>")[1].split("</report>")[0].strip()
                        
                        st.markdown(final_report)
                        
                        with st.expander("🧠 Read the Simulation Data (The Oracle's Inner Monologue)"):
                            st.write(thought)
                    else:
                        st.markdown(result)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

st.markdown("---")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()
