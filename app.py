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

# --- SESSION STATE ---
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
        st.info("**Free Access Guide:** Use your own Google API Key. [Get Key Here](https://aistudio.google.com/app/apikey)")

# --- THE 404 FIX: DYNAMIC MODEL DISCOVERY ---
def get_verified_model_name(api_key):
    try:
        genai.configure(api_key=api_key)
        # We list all models and find the one that Google recognizes for your key
        available_models = genai.list_models()
        for m in available_models:
            # We look for the newest Flash model available to you
            if 'gemini-1.5-flash' in m.name and 'generateContent' in m.supported_generation_methods:
                return m.name
        # If the loop finds nothing, we try the most common stable name
        return "models/gemini-1.5-flash"
    except Exception as e:
        return "models/gemini-1.5-flash"

# --- THE 429 FIX: SECURE GENERATION ---
def safe_write(model_instance, prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = 30 * (attempt + 1)
                st.warning(f"⚠️ Limit hit. Cooling down for {wait}s...")
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
        user_key = st.text_input("Paste Your Google API Key", type="password")
        
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
        if not user_key or not keyword:
            st.error("Please provide your API Key and Product Name.")
        else:
            # 1. Image Generation
            st.subheader("🖼️ Product Visual")
            clean_img = urllib.parse.quote(image_prompt_input)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img}?width=1024&height=768&nologo=true&seed={random.randint(1,9999)}"
            st.image(img_url, use_container_width=True)

            # 2. Find Correct Model (FIXES 404)
            verified_name = get_verified_model_name(user_key)
            st.info(f"System: Connected to {verified_name}")

            # 3. Content Generation
            full_content = ""
            status = st.status(f"Writing your {target_words} word review...")
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            model_obj = genai.GenerativeModel(model_name=verified_name)

            for i in range(steps):
                status.write(f"Writing Phase {i+1} of {steps}...")
                
                # Sleep to stay under 429 Limit
                if i > 0:
                    time.sleep(15)

                prompt = f"""
                Persona: Helpful Consumer Expert. Topic: {keyword} ({brand}).
                Goal: Write a simple but knowledgeable Amazon affiliate review. 
                Section: Phase {i+1} of {steps}. Length: {words_per_step} words.

                SEO & STYLE RULES:
                1. EVERY single paragraph must start with a new H2 or H3 Heading.
                2. HEADINGS must include "{keyword}" or related LSI terms.
                3. LANGUAGE: Use simple, matured, and attractive English. Focus on main points.
                4. PLAIN TEXT ONLY: Provide Meta Title and Meta Description in plain text. No HTML.
                5. NO AI WORDS: Avoid delve, unlock, tapestry, unleash, in conclusion.

                Phase {i+1} Focus: {'Meta Data & Attractive Introduction' if i==0 else 'Key features, usage, and benefits' if i<steps-1 else 'FAQ (6 questions) and Expert Verdict'}
                Product Specs: {extra_info}
                """
                
                chunk = safe_write(model_obj, prompt)
                
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
