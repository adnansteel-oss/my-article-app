import streamlit as st
import google.generativeai as genai
import random
import urllib.parse
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Professional SEO Article Factory", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stSelectbox, .stTextArea, .stTextInput { background-color: #ffffff; border-radius: 8px; }
    .stButton>button { background: #FF9900; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- LOGIN PAGE ---
def login_page():
    st.title("🔒 Access SEO Article Factory")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### User Login")
        email = st.text_input("Email Address")
        pwd = st.text_input("Password", type="password")
        if st.button("Log In"):
            if email and pwd:
                st.session_state['logged_in'] = True
                st.rerun()
    with col2:
        st.info("To keep this tool free, get your own API Key from [Google AI Studio](https://aistudio.google.com/app/apikey)")

# --- THE 404 FIX: STABLE MODEL SELECTION ---
def get_verified_model(api_key):
    try:
        genai.configure(api_key=api_key)
        all_models = genai.list_models()
        
        # We look for the STABLE production name first
        stable_names = ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest"]
        
        # Get list of all model names allowed for your key
        allowed_names = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        # 1. Check if stable names exist in allowed names
        for name in stable_names:
            if name in allowed_names:
                return name
        
        # 2. Otherwise, find any flash model that is NOT 'robotics' or 'preview'
        for name in allowed_names:
            if "gemini-1.5-flash" in name and "robotics" not in name and "preview" not in name:
                return name
                
        return "models/gemini-1.5-flash" # Absolute fallback
    except:
        return "models/gemini-1.5-flash"

# --- SECURE GENERATION ENGINE ---
def safe_generate(model_name, api_key, prompt):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR_STOP: {str(e)}"

# --- MAIN APP ---
def main_app():
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Amazon Affiliate SEO Article Factory")

    with st.sidebar:
        st.header("🔑 Your API Key")
        u_key = st.text_input("Paste Google API Key", type="password")
        
        st.header("📏 Word Count")
        wc_opt = st.selectbox("Options:", ["1000 Words", "1500 Words", "2000 Words"])
        target_wc = int(wc_opt.split()[0])
        
        st.header("📦 Product Details")
        kw = st.text_input("Product Name")
        br = st.text_input("Brand Name")
        info = st.text_area("Features / Main Points")
        
        st.header("🖼️ Image Setting")
        img_p = st.text_area("Describe Image", "Professional product photography")

    if st.button("🚀 Generate SEO Article Now"):
        if not u_key or not kw:
            st.error("Please provide API Key and Product Name.")
        else:
            # 1. Image
            clean_p = urllib.parse.quote(img_p)
            img_url = f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=768&nologo=true&seed={random.randint(1,9999)}"
            st.image(img_url, use_container_width=True)

            # 2. Find Correct Stable Model (Stops the Robotics 404)
            m_name = get_verified_model(u_key)
            st.info(f"System: Connected via {m_name}")
                
            # 3. Write Article in Phases
            full_art = ""
            steps = 2 if target_wc == 1000 else (3 if target_wc == 1500 else 4)
            words_per_step = target_wc // steps
            
            status = st.status(f"Writing your {target_wc} word expert review...")
            
            for i in range(steps):
                status.write(f"✍️ Writing Phase {i+1} of {steps}...")
                
                # 15s Sleep between phases to prevent 429 Limit
                if i > 0:
                    time.sleep(15)

                prompt = f"""
                Persona: Helpful Consumer Expert Reviewer. Topic: {kw} ({br}).
                Goal: Write a simple, matured, and knowledgeable Amazon affiliate article. 
                Section: Phase {i+1} of {steps}. Length: {words_per_step} words.
                
                SEO & FORMATTING RULES:
                1. HEADING BEFORE EVERY PARAGRAPH: You MUST start every new paragraph with a new H2 or H3 heading.
                2. KEYWORD HEADINGS: Headings must use "{kw}" or related LSI terms.
                3. SIMPLE LANGUAGE: Easy to read English focusing on main points and benefits.
                4. PLAIN TEXT META: No HTML tags.
                5. NO AI WORDS: Avoid delve, unlock, tapestry, unleash, in conclusion.
                
                Section {i+1} Focus: {'Meta Data & Attractive Introduction' if i==0 else 'Key features and usage analysis' if i < steps-1 else 'FAQ & Final Expert Verdict'}
                Data: {info}
                """
                
                chunk = safe_generate(m_name, u_key, prompt)
                if "ERROR_STOP" in chunk:
                    st.error(f"Google Limit/Error: {chunk}. Please wait 1 minute and click generate again.")
                    break
                else:
                    full_art += chunk + "\n\n"

            if full_art and "ERROR_STOP" not in full_art:
                status.update(label="✅ Article Fully Generated!", state="complete")
                st.markdown("---")
                st.markdown(full_art)
                st.download_button("Download Review", full_art, file_name=f"{kw}.txt")

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
