import streamlit as st
import google.generativeai as genai
import random
import urllib.parse
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="LUMINA SEO Factory", layout="wide")

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
        st.markdown("### Login")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Log In"):
            if email and pwd:
                st.session_state['logged_in'] = True
                st.rerun()
    with col2:
        st.info("To keep this tool free, get your own API Key from [Google AI Studio](https://aistudio.google.com/app/apikey)")

# --- THE 404 FIX: AGGRESSIVE DISCOVERY ---
def get_verified_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # We look through all models to find the exact name Google wants
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority 1: Search for 'gemini-1.5-flash'
        for m in models:
            if "gemini-1.5-flash" in m:
                return m
        # Priority 2: Any 1.5 model
        for m in models:
            if "1.5" in m:
                return m
        # Priority 3: Fallback to the first available model
        return models[0]
    except Exception as e:
        return f"MODEL_DISCOVERY_ERROR: {str(e)}"

# --- SECURE GENERATION ENGINE ---
def safe_generate(model_name, api_key, prompt):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name=model_name)
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "quota" in err_msg.lower():
                wait = 30 * (attempt + 1)
                st.warning(f"⚠️ Limit reached. Auto-retry in {wait}s...")
                time.sleep(wait)
            else:
                return f"ERROR_STOP: {err_msg}"
    return "ERROR_STOP: Maximum retries reached for quota."

# --- MAIN APP ---
def main_app():
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Amazon Affiliate SEO Factory")

    with st.sidebar:
        st.header("🔑 Your API Key")
        u_key = st.text_input("Paste Google API Key", type="password")
        
        st.header("📏 Word Count")
        wc_opt = st.selectbox("Options:", ["1000 Words", "1500 Words", "2000 Words"])
        target_wc = int(wc_opt.split()[0])
        
        st.header("📦 Product Details")
        kw = st.text_input("Product Name")
        br = st.text_input("Brand Name")
        info = st.text_area("Features")
        
        st.header("🖼️ Image")
        img_p = st.text_area("Image Prompt", "Professional product photo")

    if st.button("🚀 Generate SEO Article"):
        if not u_key or not kw:
            st.error("Please provide API Key and Product Name.")
        else:
            # 1. Image
            clean_p = urllib.parse.quote(img_p)
            img_url = f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=768&nologo=true&seed={random.randint(1,9999)}"
            st.image(img_url, use_container_width=True)

            # 2. Find Correct Model (Stops 404)
            m_name = get_verified_model(u_key)
            if "ERROR" in m_name:
                st.error(f"Could not connect to Google: {m_name}")
            else:
                st.info(f"Connected to: {m_name}")
                
                # 3. Write Article in Phases
                full_art = ""
                steps = 2 if target_wc == 1000 else (3 if target_wc == 1500 else 4)
                words_per_step = target_wc // steps
                
                status = st.status(f"Writing your {target_wc} word expert review...")
                
                for i in range(steps):
                    status.write(f"✍️ Phase {i+1} of {steps}...")
                    
                    # 15s Sleep between phases to prevent 429
                    if i > 0:
                        time.sleep(15)

                    prompt = f"""
                    Role: Experienced Amazon Product Reviewer. Topic: {kw} ({br}).
                    Goal: Matured, simple, and knowledgeable article. 
                    Length: {words_per_step} words for this section.
                    
                    SEO & FORMATTING RULES:
                    1. HEADING BEFORE EVERY PARAGRAPH: Start every paragraph with a new H2 or H3 heading.
                    2. KEYWORD HEADINGS: Headings must use "{kw}" or related LSI terms.
                    3. SIMPLE LANGUAGE: Easy to read, focusing on main benefits.
                    4. PLAIN TEXT META: No HTML tags like <meta>.
                    5. NO AI WORDS: Avoid delve, unlock, tapestry, unleash.
                    
                    Section {i+1} Focus: {'Meta Data & Intro' if i==0 else 'Main features/usage' if i < steps-1 else 'FAQ & Verdict'}
                    Data: {info}
                    """
                    
                    chunk = safe_generate(m_name, u_key, prompt)
                    if "ERROR_STOP" in chunk:
                        st.error(chunk)
                        break
                    else:
                        full_art += chunk + "\n\n"

                if full_art and "ERROR_STOP" not in full_art:
                    status.update(label="✅ Article Generated!", state="complete")
                    st.markdown("---")
                    st.markdown(full_art)
                    st.download_button("Download Review", full_art, file_name=f"{kw}.txt")

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
