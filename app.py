import streamlit as st
import google.generativeai as genai
import random
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="Free SEO Article Factory", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stButton>button { background: #FF9900; color: white; font-weight: bold; width: 100%; border-radius: 5px; }
    .login-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE FOR LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- LOGIN PAGE ---
def login_page():
    st.title("🔒 Access the Article Factory")
    st.write("Please log in to start creating 100% humanized SEO articles.")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### User Login")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            if st.button("Log In"):
                if email and password: # You can add specific password check here
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Please enter both email and password.")
        
        with col2:
            st.markdown("### 📢 Important Note")
            st.info("""
            **Why do I need a Google API Key?**
            To keep this service **FREE for everyone**, every user uses their own dedicated power from Google. 
            
            1. It takes 30 seconds to get one.
            2. It is **100% Free**.
            3. Your articles will generate faster.
            
            [👉 Click Here to Get Your Free Key](https://aistudio.google.com/app/apikey)
            """)

# --- ARTICLE GENERATOR PAGE ---
def main_app():
    # Logout button in sidebar
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Smart SEO Article Factory")
    st.write("Create high-quality Amazon Affiliate reviews in seconds.")

    # --- SIDEBAR OPTIONS ---
    with st.sidebar:
        st.header("🔑 Your API Key")
        user_api_key = st.text_input("Paste Your Google API Key Here", type="password")
        
        st.header("📏 Article Length")
        word_count_option = st.selectbox("Word Count:", ["1000 Words", "1500 Words", "2000 Words"])
        target_words = int(word_count_option.split()[0])

        st.header("📦 Product Info")
        keyword = st.text_input("Product Name")
        brand = st.text_input("Brand Name")
        extra_info = st.text_area("Features / Main Points")

        st.header("🖼️ Image Settings")
        image_prompt = st.text_area("Describe the Image", "High quality product photo on a clean background")

    # --- CORE FUNCTIONS ---
    def get_best_model(key):
        try:
            genai.configure(api_key=key)
            model_names = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return next((n for n in model_names if "gemini-1.5-flash" in n), model_names[0])
        except: return None

    def write_section(key, model_name, prompt):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            return model.generate_content(prompt).text
        except Exception as e: return f"Error: {str(e)}"

    # --- ACTION ---
    if st.button("🚀 Generate SEO Article Now"):
        if not user_api_key:
            st.error("You must enter your own Google API Key to use this tool.")
        elif not keyword:
            st.error("Please enter a Product Name.")
        else:
            # 1. IMAGE
            st.subheader("🖼️ Product Visual")
            clean_img = urllib.parse.quote(image_prompt)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img}?width=1024&height=768&nologo=true&seed={random.randint(1,9999)}"
            st.image(img_url, use_container_width=True)

            # 2. CONTENT
            best_model = get_best_model(user_api_key)
            if not best_model:
                st.error("Invalid API Key. Please check your Google AI Studio Key.")
            else:
                full_content = ""
                status = st.status("Writing article...")
                steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
                
                for i in range(steps):
                    status.write(f"Writing Phase {i+1}...")
                    step_prompt = f"""
                    Reviewer Persona: Helpful Consumer Expert.
                    Product: {keyword} ({brand}).
                    Length: {target_words // steps} words for this section.
                    
                    SEO RULES:
                    - Use simple language.
                    - Start every new paragraph with a new H2 or H3 Heading.
                    - Use "{keyword}" or related LSI terms in every heading.
                    - No HTML tags.
                    - Avoid: delve, unlock, tapestry, unleash.
                    
                    Phase {i+1} Focus: 
                    {'Meta Title/Desc/H1 and Intro' if i==0 else 'Main points and usage' if i < steps-1 else 'FAQs and Final Verdict'}
                    Data: {extra_info}
                    """
                    full_content += write_section(user_api_key, best_model, step_prompt) + "\n\n"
                
                status.update(label="✅ Finished!", state="complete")
                st.markdown("---")
                st.markdown(full_content)
                st.download_button("Download Review", full_content, file_name="review.txt")

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
