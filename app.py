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
        st.info("**Free Access Guide:** Use your own Google API Key to keep this tool free. [Get Key Here](https://aistudio.google.com/app/apikey)")

# --- SMART GENERATOR WITH AUTO-RETRY ---
def write_section_safe(key, model_name, prompt):
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1) # Wait 30s, then 60s
                    st.warning(f"⚠️ Google Limit Reached. Retrying automatically in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    return f"QUOTA_ERROR: Google's daily/minute limit is full. Please try a different API Key or wait 1 hour."
            else:
                return f"ERROR: {str(e)}"
    return "ERROR: Unknown failure"

# --- MAIN APP ---
def main_app():
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Amazon Affiliate SEO Article Factory")

    with st.sidebar:
        st.header("🔑 API Credentials")
        user_api_key = st.text_input("Paste Your Google API Key", type="password")
        word_count_option = st.selectbox("Select Word Count:", ["1000 Words", "1500 Words", "2000 Words"])
        target_words = int(word_count_option.split()[0])
        keyword = st.text_input("Product Name")
        brand = st.text_input("Brand Name")
        extra_info = st.text_area("Main Features")
        image_prompt_input = st.text_area("Describe Image", "Professional product photography")

    if st.button("🚀 Generate SEO Article Now"):
        if not user_api_key:
            st.error("Please enter your API Key!")
        else:
            # 1. Image
            clean_img = urllib.parse.quote(image_prompt_input)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img}?width=1024&height=768&nologo=true&seed={random.randint(1,9999)}"
            st.image(img_url, use_container_width=True)

            # 2. Content
            full_content = ""
            status = st.status(f"Writing your {target_words} word review...")
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            for i in range(steps):
                status.write(f"Writing Phase {i+1} of {steps}...")
                
                # Pre-request delay to be extra safe
                if i > 0:
                    time.sleep(5) 

                step_prompt = f"""
                Persona: Helpful Consumer Expert. Product: {keyword} ({brand}). Length: {words_per_step} words.
                Phase {i+1} focus: {'Meta/Intro' if i==0 else 'Features/Usage' if i<steps-1 else 'FAQ/Verdict'}
                
                RULES: 
                - New H2/H3 Heading before EVERY paragraph using "{keyword}" or LSI terms.
                - Use SIMPLE language. NO HTML. No Meta tags.
                - Avoid: delve, unlock, tapestry, unleash.
                Data: {extra_info}
                """
                
                section_text = write_section_safe(user_api_key, "gemini-1.5-flash", step_prompt)
                
                if "QUOTA_ERROR" in section_text:
                    st.error(section_text)
                    break
                else:
                    full_content += section_text + "\n\n"

            if "QUOTA_ERROR" not in full_content and full_content:
                status.update(label="✅ Finished!", state="complete")
                st.markdown("---")
                st.markdown(full_content)
                st.download_button("Download Review", full_content, file_name=f"{keyword}.txt")

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
