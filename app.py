import streamlit as st
import google.generativeai as genai
import time
import urllib.parse
import random

# ------------------ CONFIG ------------------
st.set_page_config(page_title="SEO Article SaaS", layout="wide")

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

# ------------------ SESSION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ LOGIN ------------------
def login():
    st.title("🔐 Login to SEO SaaS")

    email = st.text_input("Email")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if email == "admin@email.com" and pwd == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# ------------------ MODEL DETECTION ------------------
@st.cache_data
def get_model(api_key):
    genai.configure(api_key=api_key)
    models = genai.list_models()

    for m in models:
        if "gemini" in m.name and "generateContent" in m.supported_generation_methods:
            return m.name

    return "models/gemini-1.5-flash"

# ------------------ GENERATOR ------------------
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
    - Features & Benefits (with headings)
    - Pros & Cons
    - FAQs
    - Final Verdict

    RULES:
    - Use simple English
    - Every section must have headings
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

    return "ERROR: Failed after retries"

# ------------------ MAIN APP ------------------
def app():

    st.title("🛍️ SEO Article Generator (SaaS Version)")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    with st.sidebar:
        st.header("Settings")

        api_key = st.text_input("Google API Key", type="password")

        word_count = st.selectbox("Word Count", [1000, 1500, 2000])

        keyword = st.text_input("Product Name")
        brand = st.text_input("Brand")

        info = st.text_area("Features / Details")

        img_prompt = st.text_area("Image Prompt", "product photography, 4k, studio lighting")

    if st.button("🚀 Generate Article"):

        if not api_key.startswith("AIza"):
            st.error("Invalid API Key")
            return

        if not keyword:
            st.error("Enter product name")
            return

        # IMAGE
        clean = urllib.parse.quote(img_prompt)
        img_url = f"https://image.pollinations.ai/prompt/{clean}?width=1024&height=768&seed={random.randint(1,9999)}"

        st.image(img_url, use_container_width=True)

        # MODEL
        model_name = get_model(api_key)
        st.info(f"Using model: {model_name}")

        with st.spinner("Writing article..."):
            article = generate_article(api_key, model_name, keyword, brand, info, word_count)

        if "ERROR" in article:
            st.error(article)
        else:
            st.success("Article generated!")

            st.markdown("---")
            st.markdown(article)

            st.download_button("Download", article, file_name=f"{keyword}.txt")

            st.code(article)  # easy copy

# ------------------ FLOW ------------------
if st.session_state.logged_in:
    app()
else:
    login()
