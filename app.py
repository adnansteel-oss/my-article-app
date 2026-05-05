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
    .login-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE FOR LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- LOGIN PAGE FUNCTION ---
def login_page():
    st.title("🔒 SEO Article Factory Access")
    st.write("Welcome! Please enter your details to access the professional article generator.")
    
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
        To keep this tool free for the community, you must use your own Google API Key. 
        
        1. It takes 30 seconds to get.
        2. It is **100% Free**.
        3. No credit card required.
        
        [👉 Get Your Free Google API Key Here](https://aistudio.google.com/app/apikey)
        """)

# --- MAIN APP FUNCTION ---
def main_app():
    # Logout button in sidebar
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("🛍️ Amazon Affiliate SEO Article Factory")
    st.write("Generate matured, simple, and high-ranking product reviews.")

    # --- SIDEBAR OPTIONS ---
    with st.sidebar:
        st.header("🔑 Your API Credentials")
        user_api_key = st.text_input("Paste Your Google API Key", type="password")
        
        st.header("📏 Article Length")
        word_count_option = st.selectbox(
            "Select Article Word Count:",
            ["1000 Words", "1500 Words", "2000 Words"]
        )
        target_words = int(word_count_option.split()[0])

        st.header("📦 Product Information")
        keyword = st.text_input("Product Name", placeholder="e.g. House of Sillage Whispers of Truth")
        brand = st.text_input("Brand Name", placeholder="e.g. House of Sillage")
        extra_info = st.text_area("Main Features / Supplemental Data")

        st.header("🖼️ Image Settings")
        image_prompt_input = st.text_area("Describe the Image", "Professional lifestyle photography of the product on a clean background")

    # --- MODEL LOADER ---
    def get_best_model(key):
        try:
            genai.configure(api_key=key)
            all_models = genai.list_models()
            model_names = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
            for name in model_names:
                if "gemini-1.5-flash" in name: return name
            return model_names[0] if model_names else None
        except: return None

    # --- GENERATOR ENGINE ---
    def write_section(key, model_name, prompt):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e: return f"Error: {str(e)}"

    # --- ACTION ---
    if st.button("🚀 Generate SEO Article Now"):
        if not user_api_key:
            st.error("Please enter your own Google API Key in the sidebar.")
        elif not keyword:
            st.error("Please enter a Product Name.")
        else:
            # 1. IMAGE GENERATION
            st.subheader("🖼️ Product Visual")
            clean_img_prompt = urllib.parse.quote(image_prompt_input)
            seed = random.randint(1, 99999)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img_prompt}?width=1024&height=768&nologo=true&seed={seed}"
            st.image(img_url, use_container_width=True)

            # 2. START ARTICLE GENERATION
            best_model = get_best_model(user_api_key)
            if not best_model:
                st.error("API Key Error. Please ensure your key is active in Google AI Studio.")
            else:
                full_content = ""
                status = st.status(f"Creating your {target_words} word expert review...")
                
                # Logic to control word count strictly via sections
                steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
                words_per_step = target_words // steps

                for i in range(steps):
                    status.write(f"Writing Phase {i+1} of {steps}...")
                    
                    step_prompt = f"""
                    Role: Experienced Consumer Product Reviewer. 
                    Goal: Write a simple, mature, and knowledgeable article about {keyword} ({brand}).
                    Target Word Count for this section: {words_per_step} words.

                    STRICT FORMATTING & SEO RULES:
                    1. NEW HEADING AFTER EVERY PARAGRAPH: You MUST start a new H2 or H3 heading before every single paragraph.
                    2. KEYWORD HEADINGS: Every heading must include the keyword "{keyword}" or related LSI (Latent Semantic Indexing) terms.
                    3. PLAIN TEXT META: Provide Meta Title and Meta Description in PLAIN TEXT only. DO NOT use <meta> or HTML tags.
                    4. SIMPLE LANGUAGE: Use clear, attractive, and easy-to-read language. Focus on the main points and benefits.
                    5. NO AI WORDS: Avoid 'delve', 'unlock', 'tapestry', 'unleash', 'in conclusion'.
                    6. KNOWLEDGE: Give visitor-friendly info that shows deep familiarity with the product.

                    Phase {i+1} Focus: 
                    - If Phase 1: Meta Title, Meta Description, H1, and engaging Introduction.
                    - If Middle Phase: Main features, performance analysis, and real-world usage.
                    - If Final Phase: 6 Detailed FAQs, Buyer's Guide summary, and Final Verdict.

                    Product Data to use: {extra_info}
                    """
                    
                    section_text = write_section(user_api_key, best_model, step_prompt)
                    full_content += section_text + "\n\n"
                    # Small 2-second pause to prevent minor quota flickers
                    time.sleep(2)

                status.update(label="✅ Article Fully Generated!", state="complete")

                # --- DISPLAY ---
                st.markdown("---")
                st.markdown(full_content)
                
                final_count = len(full_content.split())
                st.info(f"Final Word Count: {final_count} words.")
                
                st.download_button(
                    label=f"📥 Download {target_words} Word SEO Review",
                    data=full_content,
                    file_name=f"{keyword.replace(' ', '_')}_SEO.txt"
                )

# --- APP FLOW CONTROL ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
