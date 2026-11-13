import streamlit as st
import requests

st.set_page_config(page_title="Shopping Sniper", layout="centered")

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

# --- 2. THE SHOPPING SNIPER INTERFACE ---
st.title("🛒 Shopping Sniper")
st.write("Search the live web for the best deals, quality analysis, and style advice.")

product = st.text_input("What do you want to buy? (e.g., 'Nike Revolution 7 running shoes')")

if st.button("Hunt for Deals"):
    if not product:
        st.warning("Please enter a product.")
    else:
        headers = {
            "Authorization": f"Bearer {st.secrets['deepseek_api_key']}",
            "Content-Type": "application/json"
        }
        
        # STEP 1: SEARCH THE WEB
        with st.spinner("Scanning the internet for live prices and reviews..."):
            search_payload = {
                "query": f"{product} best price review India",
                "count": 5, 
                "need_content": True 
            }
            
            search_response = requests.post("https://api.deepseek.com/v1/tools/search", json=search_payload, headers=headers)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                results = search_data.get("results", [])
                
                # Combine all the search results into a giant text block
                web_data = ""
                for r in results:
                    web_data += f"Title: {r['title']}\nURL: {r['url']}\nSummary: {r['summary']}\n\n"
                
                st.success("Web scan complete. Analyzing data...")
                
                # STEP 2: SEND TO AI FOR ANALYSIS
                with st.spinner("The AI is comparing prices, quality, and style..."):
                    AI_BRAIN = """
                    You are an elite, highly intelligent personal shopping assistant and fashion consultant. 
                    I will give you live web search results for a product.

                    Your job is to analyze the data and give me a brutal, honest breakdown:

                    1. **The Best Deal:** Find the lowest price mentioned in the text. Tell me which site (Amazon, Flipkart, etc.) it is on.
                    2. **Quality vs. Price:** Do the reviews say the cheaper option is garbage? Is the expensive option actually worth it? Tell me which one gives the best "value for money."
                    3. **Fashion/Style Advice:** Briefly tell me what this product pairs well with, or who it is best suited for.
                    4. **The "Wait or Buy" Strategy:** Based on the search results, are there any upcoming sales, or is this a good time to buy?

                    Be direct. Use bullet points. Do not fluff. If the search results don't have enough data on a specific point, tell me honestly.
                    """
                    
                    prompt = f"I want to buy: {product}\n\nHere are the latest search results:\n{web_data}\n\nWhat is the best deal and what should I buy?"
                    
                    payload = {
                        "model": "deepseek-reasoner", 
                        "messages": [
                            {"role": "system", "content": AI_BRAIN},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3 
                    }
                    
                    ai_response = requests.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers)
                    
                    if ai_response.status_code == 200:
                        final_result = ai_response.json()["choices"][0]["message"]["content"]
                        st.markdown(final_result)
                    else:
                        st.error(f"AI Error: {ai_response.text}")
            else:
                st.error(f"Search Error: {search_response.text}")

st.markdown("---")
if st.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()
