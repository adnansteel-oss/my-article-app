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
    .stButton>button { background: #FF9900; color: white; font-weight: bold; width: 100%; border: none; height: 3em; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE FOR LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- LOGIN PAGE ---
def login_page():
    st.title("🔒 SEO Article Factory Access")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### User Login")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        if st.button("Log In"):
            if email and password:
                st.session_state['logged_in'] = True
                st.rerun()
    with col2:
        st.info("**Free Access Guide:** Use your own Google API Key to keep this tool free. [Get Key Here](https://aistudio.google.com/app/apikey)")

# --- DYNAMIC MODEL FINDER (The 404 Fix) ---
def find_working_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # We ask Google to list all models available to your specific key
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # We prioritize 1.5 Flash as it is the most stable for free users
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        # Fallback if the specific string isn't found
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

# --- SECURE GENERATOR (The 429 Fix) ---
def safe_generate(model_instance, prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = 35 * (attempt + 1)
                st.warning(f"⚠️ Google Limit hit. Waiting {wait} seconds...")
                time.sleep(wait)
            else:
                return f"ERROR: {str(e)}"
    return "QUOTA_ERROR"

# --- MAIN APP ---
def main_app():
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Amazon Affiliate SEO Article Factory")

    with st.sidebar:
        st.header("🔑 API Credentials")
        user_api_key = st.text_input("Paste Your Google API Key", type="password")
        
        st.header("📏 Article Length")
        word_count_option = st.selectbox("Select Word Count:", ["1000 Words", "1500 Words", "2000 Words"])
        target_words = int(word_count_option.split()[0])
        
        st.header("📦 Product Info")
        keyword = st.text_input("Product Name")
        brand = st.text_input("Brand Name")
        extra_info = st.text_area("Main Features / Specs")
        
        st.header("🖼️ Image Settings")
        image_prompt_input = st.text_area("Describe Image", "Professional product photography")

    if st.button("🚀 Generate SEO Article Now"):
        if not user_api_key or not keyword:
            st.error("Please ensure API Key and Product Name are filled!")
        else:
            # 1. IMAGE GENERATION
            st.subheader("🖼️ Product Visual")
            clean_img = urllib.parse.quote(image_prompt_input)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img}?width=1024&height=768&nologo=true&seed={random.randint(1,9999)}"
            st.image(img_url, use_container_width=True)

            # 2. AUTO-DETECT MODEL
            model_name = find_working_model(user_api_key)
            st.info(f"System: Connected via {model_name}")

            # 3. CONTENT GENERATION
            full_content = ""
            status = st.status(f"Writing your {target_words} word expert review...")
            
            # Logic: 1000=2 phases, 1500=3 phases, 2000=4 phases
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            model_obj = genai.GenerativeModel(model_name)

            for i in range(steps):
                status.write(f"Generating Part {i+1} of {steps}...")
                
                # Critical 15-second sleep to prevent 429 Errors
                if i > 0:
                    status.write("⏱️ Cool-down period (15s) to stay under Google's limit...")
                    time.sleep(15)

                prompt = f"""
                Persona: Helpful Consumer Expert. Topic: {keyword} ({brand}).
                Current Section: Phase {i+1} of {steps}. Length: {words_per_step} words.

                RULES:
                1. HEADING BEFORE EVERY PARAGRAPH: Every single paragraph must be preceded by a new H2 or H3 heading.
                2. HEADINGS MUST USE "{keyword}" or related LSI terms.
                3. LANGUAGE: Simple, matured, and attractive. Focus on main points.
                4. NO HTML: Provide Meta Title and Description in plain text.
                5. NO AI WORDS: Avoid delve, unlock, tapestry, unleash, in conclusion.
                
                Focus: {'Meta Data & Introduction' if i==0 else 'Main features & performance' if i<steps-1 else 'FAQ & Final Verdict'}
                Product Specs: {extra_info}
                """
                
                chunk = safe_generate(model_obj, prompt)
                
                if "ERROR" in chunk or "QUOTA_ERROR" in chunk:
                    st.error(chunk)
                    break
                else:
                    full_content += chunk + "\n\n"

            if full_content and "ERROR" not in full_content:
                status.update(label="✅ Article Fully Generated!", state="complete")
                st.markdown("---")
                st.markdown(full_content)
                st.download_button("Download Review", full_content, file_name=f"{keyword}.txt")

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
