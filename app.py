import streamlit as st
import google.generativeai as genai
import random
import urllib.parse
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Professional SEO Article Factory", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    .stSelectbox, .stTextArea, .stTextInput { background-color: #ffffff; border-radius: 8px; }
    .stButton>button { background: #FF9900; color: white; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; }
    .footer { text-align: center; color: #666; padding: 20px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE FOR LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- LOGIN PAGE ---
def login_page():
    st.title("🔒 SEO Article Factory Access")
    st.write("Please enter your details to access the professional generator.")
    
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
        st.markdown("### 📢 Why do I need a Key?")
        st.info("""
        To keep this service **FREE**, every user uses their own Google API Power. 
        - It is 100% Free.
        - Takes 30 seconds to get.
        - Keeps your data private.
        
        [👉 Click here to get your Free Google API Key](https://aistudio.google.com/app/apikey)
        """)

# --- CORE FUNCTIONS ---

def get_verified_model_name(api_key):
    """Detects the correct model name for the user's specific account (Fixes 404)."""
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

def safe_generate_content(model_instance, prompt):
    """Handles the actual generation with retry logic for quota issues (Fixes 429)."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait_time = 30 * (attempt + 1)
                st.warning(f"⚠️ Google limit reached. Auto-waiting {wait_time}s and retrying...")
                time.sleep(wait_time)
            else:
                return f"ERROR_STOP: {str(e)}"
    return "ERROR_STOP: Quota exceeded after retries."

# --- MAIN APPLICATION ---
def main_app():
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Amazon Affiliate SEO Article Factory")
    st.write("Generate matured, simple, and high-ranking product reviews with SEO headings.")

    with st.sidebar:
        st.header("🔑 Your API Credentials")
        user_key = st.text_input("Paste Your Google API Key", type="password")
        
        st.header("📏 Article Length")
        word_count_option = st.selectbox("Select Word Count:", ["1000 Words", "1500 Words", "2000 Words"])
        target_words = int(word_count_option.split()[0])
        
        st.header("📦 Product Info")
        keyword = st.text_input("Product Name (e.g. Sony Headphones)")
        brand = st.text_input("Brand Name")
        extra_info = st.text_area("Features / Main Points")
        
        st.header("🖼️ Image Settings")
        image_prompt_input = st.text_area("Describe the Image", "Professional lifestyle photography of the product")

    # --- EXECUTION ---
    if st.button("🚀 Generate High-Quality Article"):
        if not user_key or not keyword:
            st.error("Please provide both your API Key and Product Name.")
        else:
            # 1. Image Generation
            st.subheader("🖼️ Product Visual")
            clean_img = urllib.parse.quote(image_prompt_input)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img}?width=1024&height=768&nologo=true&seed={random.randint(1,99999)}"
            st.image(img_url, use_container_width=True)

            # 2. Setup Model
            model_name = get_verified_model_name(user_key)
            st.info(f"System: Connected via {model_name}")
            model_obj = genai.GenerativeModel(model_name)

            # 3. Generate Article in Phases
            full_article = ""
            status = st.status(f"Writing your {target_words} word expert review...")
            
            # Divide target into 500-word chunks (Phases)
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            for i in range(steps):
                status.write(f"✍️ Writing Phase {i+1} of {steps}...")
                
                # --- The 429 Prevention: 15-second pause between requests ---
                if i > 0:
                    time.sleep(15)

                prompt = f"""
                Persona: Helpful Consumer Expert & Amazon Reviewer.
                Topic: {keyword} ({brand}).
                Section: Phase {i+1} of {steps}. Length: {words_per_step} words.

                STRICT FORMATTING & CONTENT RULES:
                1. NEW HEADING BEFORE EVERY PARAGRAPH: You MUST start a new H2 or H3 heading before EVERY single paragraph of text.
                2. SEO HEADINGS: Every heading must use the keyword "{keyword}" or related LSI terms.
                3. SIMPLE LANGUAGE: Use clear, matured, and attractive English. Focus on the main points and benefits. Do not use hard technical science.
                4. PLAIN TEXT META: Provide Meta Title and Meta Description in PLAIN TEXT only. DO NOT use <meta> or HTML tags.
                5. NO AI CLICHES: Do not use: delve, unlock, tapestry, unleash, in conclusion.
                6. VALUE: Provide knowledgeable insights about build quality, real-life usage, and consumer benefits.

                Phase {i+1} Focus: 
                {'Meta Title, Meta Description, H1, and Attractive Introduction' if i==0 else 'Key features, performance, and daily usage' if i < steps-1 else 'Maintenance tips, 6 Buyer FAQs, and Final Expert Verdict'}
                
                Data to use: {extra_info}
                """
                
                chunk = safe_generate_content(model_obj, prompt)
                
                if "ERROR_STOP" in chunk:
                    st.error(chunk)
                    break
                else:
                    full_article += chunk + "\n\n"

            if full_article and "ERROR_STOP" not in full_article:
                status.update(label="✅ Article Fully Generated!", state="complete")
                st.markdown("---")
                st.markdown(full_content := full_article)
                
                st.download_button(
                    label=f"📥 Download {target_words} Word Review",
                    data=full_content,
                    file_name=f"{keyword.replace(' ', '_')}.txt"
                )

    st.markdown('<div class="footer">© 2024 Article Factory | Powered by Google Gemini 1.5 Flash</div>', unsafe_allow_html=True)

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
