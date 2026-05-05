import streamlit as st
import google.generativeai as genai
import random
import urllib.parse
import time # This is the secret to fixing the 429 error

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
    st.write("Welcome! Please enter your details to access the tool.")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### User Login")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        if st.button("Log In"):
            if email and password:
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Please enter both email and password.")
    with col2:
        st.markdown("### 📢 Important Note")
        st.info("""
        **Free Access Guide:**
        To keep this tool free, please use your own Google API Key. 
        [👉 Get Your Free Google API Key Here](https://aistudio.google.com/app/apikey)
        """)

# --- MAIN APP ---
def main_app():
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Amazon Affiliate SEO Article Factory")
    st.write("Generate matured, simple, and high-ranking product reviews.")

    with st.sidebar:
        st.header("🔑 Your API Credentials")
        user_api_key = st.text_input("Paste Your Google API Key", type="password")
        
        st.header("📏 Article Length")
        word_count_option = st.selectbox("Select Word Count:", ["1000 Words", "1500 Words", "2000 Words"])
        target_words = int(word_count_option.split()[0])

        st.header("📦 Product Information")
        keyword = st.text_input("Product Name")
        brand = st.text_input("Brand Name")
        extra_info = st.text_area("Main Features")

        st.header("🖼️ Image Settings")
        image_prompt_input = st.text_area("Describe Image", "Professional product photo")

    # --- CORE LOGIC ---
    def write_section(key, model_name, prompt):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"QUOTA_ERROR: {str(e)}"

    if st.button("🚀 Generate SEO Article Now"):
        if not user_api_key:
            st.error("Please enter your API Key!")
        else:
            # 1. IMAGE
            st.subheader("🖼️ Product Visual")
            clean_img = urllib.parse.quote(image_prompt_input)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img}?width=1024&height=768&nologo=true&seed={random.randint(1,9999)}"
            st.image(img_url, use_container_width=True)

            # 2. CONTENT
            full_content = ""
            status = st.status(f"Creating your {target_words} word review...")
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            # Using Gemini 1.5 Flash - It is the most stable for free keys
            model_to_use = "gemini-1.5-flash"

            for i in range(steps):
                status.write(f"Writing Phase {i+1} of {steps}...")
                
                # THE 429 FIX: Wait 12 seconds between requests to reset the Google limit
                if i > 0:
                    status.write("⏱️ Waiting 12 seconds (Cool-down to prevent Quota Error)...")
                    time.sleep(12) 

                step_prompt = f"""
                Persona: Helpful Reviewer. Product: {keyword} ({brand}). Length: {words_per_step} words.
                RULES: 
                - Start EVERY paragraph with an H2 or H3 heading using "{keyword}" or LSI terms.
                - Use SIMPLE language.
                - Meta Title/Desc in PLAIN TEXT. No HTML.
                - Avoid: delve, unlock, tapestry, unleash.
                Phase {i+1}: {'Meta/Intro' if i==0 else 'Main features' if i<steps-1 else 'FAQ/Verdict'}
                Data: {extra_info}
                """
                
                section_text = write_section(user_api_key, model_to_use, step_prompt)
                
                if "QUOTA_ERROR" in section_text:
                    st.error("Google's limit is very tight right now. Please wait 1 minute and click generate again.")
                    break
                else:
                    full_content += section_text + "\n\n"

            if full_content:
                status.update(label="✅ Finished!", state="complete")
                st.markdown("---")
                st.markdown(full_content)
                st.download_button("Download Review", full_content, file_name="review.txt")

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
