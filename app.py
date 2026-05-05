import streamlit as st
import google.generativeai as genai
import time
import urllib.parse
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="SEO Article SaaS", layout="wide")

# ------------------ SESSION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ STYLE ------------------
st.markdown("""
<style>
.stButton>button {
    background: #FF9900;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    height: 3em;
}
</style>
""", unsafe_allow_html=True)

# ------------------ LOGIN PAGE ------------------
def login_page():
    st.title("🔒 Login to SEO Article Generator")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if not email or not password:
                st.warning("Please fill all fields")
            elif email == "admin@email.com" and password == "1234":
                st.session_state.logged_in = True
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid email or password")

# ------------------ MODEL DETECTION ------------------
@st.cache_data
def get_model(api_key):
    genai.configure(api_key=api_key)
    models = genai.list_models()

    for m in models:
        if "generateContent" in m.supported_generation_methods:
            return m.name

    return "models/gemini-1.5-flash"

# ------------------ GENERATION FUNCTION ------------------
def generate_article(api_key, model_name, keyword, brand, info, word_count):

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={"temperature": 0.7}
    )

    prompt = f"""
    Write a COMPLETE SEO optimized Amazon affiliate article.

    KEYWORD: {keyword}
    BRAND: {brand}

    STRICT STRUCTURE:
    - SEO Title
    - Meta Description
    - Introduction
    - Features & Benefits
    - Pros & Cons
    - FAQs
    - Final Verdict

    RULES:
    - Use simple English
    - Use headings for each section
    - No AI words like: delve, unlock, unleash
    - Write approx {word_count} words
    - Focus on buyer intent

    PRODUCT INFO:
    {info}
    """

    for i in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            time.sleep(5)

    return "ERROR: Failed to generate content"

# ------------------ MAIN APP ------------------
def main_app():

    st.title("🛍️ SEO Article Generator")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    with st.sidebar:
        st.header("Settings")

        api_key = st.text_input("Google API Key", type="password")
        word_count = st.selectbox("Word Count", [1000, 1500, 2000])

        keyword = st.text_input("Product Name")
        brand = st.text_input("Brand Name")

        info = st.text_area("Product Features / Details")

        img_prompt = st.text_area(
            "Image Prompt",
            "product photography, ultra realistic, 4k, studio lighting"
        )

    if st.button("🚀 Generate Article"):

        if not api_key.startswith("AIza"):
            st.error("Enter valid Google API Key")
            return

        if not keyword:
            st.error("Enter product name")
            return

        # -------- IMAGE --------
        clean_prompt = urllib.parse.quote(img_prompt)
        img_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=768&seed={random.randint(1,9999)}"
        st.image(img_url, use_container_width=True)

        # -------- MODEL --------
        model_name = get_model(api_key)
        st.info(f"Using model: {model_name}")

        # -------- GENERATE --------
        with st.spinner("Writing SEO article..."):
            article = generate_article(api_key, model_name, keyword, brand, info, word_count)

        if "ERROR" in article:
            st.error(article)
        else:
            st.success("Article Generated!")

            st.markdown("---")
            st.markdown(article)

            st.download_button(
                "📥 Download Article",
                article,
                file_name=f"{keyword}.txt"
            )

            st.code(article)

# ------------------ APP FLOW ------------------
if st.session_state.logged_in:
    main_app()
else:
    login_page()
