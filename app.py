import streamlit as st
import google.generativeai as genai
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="Humanized Article AI", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("✍️ Auto-Detect Humanized Article AI")
st.write("This version automatically finds the correct Google Model to prevent 404 errors.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 API Setup")
    google_api_key = st.text_input("Google AI Studio API Key", type="password")
    st.info("Get your key at: aistudio.google.com")
    
    st.header("📝 Article Settings")
    keyword = st.text_input("Main Keyword", "CHEFMAN AIR FRYER")
    brand = st.text_input("Brand Name", "CHEFMAN")
    
    st.header("⚙️ Extra Instructions")
    extra_data = st.text_area("Supplemental Content / Links")

# --- AUTO-DETECT MODEL FUNCTION ---
def get_best_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # Get all models available to your API Key
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority: Flash first (fastest), then Pro, then anything available
        for model in available_models:
            if "gemini-1.5-flash" in model:
                return model
        for model in available_models:
            if "gemini-1.5-pro" in model:
                return model
        return available_models[0] # Just pick the first one if others aren't found
    except Exception as e:
        return None

# --- IMAGE GENERATOR ---
def get_image(kw):
    seed = random.randint(1, 9999)
    img_url = f"https://pollinations.ai/p/{kw.replace(' ', '_')}_modern_kitchen_appliance_professional_photography?width=1024&height=768&seed={seed}&nologo=true"
    return img_url

# --- CONTENT GENERATOR ---
def generate_long_article(api_key, model_name, kw, br, extra):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Write a professional, HUMAN-LIKE SEO article. 
        Length: 1500-2000 words.
        Keyword: {kw}
        Brand: {br}
        Details: {extra}

        STRUCTURE:
        - Meta Title & Description
        - Catchy H1
        - Intro (Relatable and long - 300 words)
        - 5-6 Detailed H2 Subheadings (Features, Health, Cleaning, Tips)
        - Detailed FAQ (6 Questions)
        - Summary of Key Features

        HUMANIZATION RULES:
        - Avoid AI words: "delve", "unlock", "tapestry", "in conclusion", "unleash".
        - Use simple, punchy language.
        - Be extremely descriptive to ensure high word count. Describe sounds, textures, and specific cooking results.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- MAIN APP ---
if st.button("Generate Article Now"):
    if not google_api_key:
        st.warning("Please enter your API Key!")
    else:
        with st.spinner("Finding best model for your account..."):
            best_model = get_best_model(google_api_key)
            
            if not best_model:
                st.error("Could not find any available Gemini models. Check your API key.")
            else:
                st.info(f"Using Model: {best_model}")
                
                # 1. Generate Image
                st.image(get_image(keyword), caption=f"AI Generated Image for {keyword}")

                # 2. Generate Content
                with st.spinner("Writing 2000-word article..."):
                    article_text = generate_long_article(google_api_key, best_model, keyword, brand, extra_data)
                    
                    if "ERROR" in article_text:
                        st.error(article_text)
                    else:
                        words = len(article_text.split())
                        st.success(f"Article Generated! Word Count: {words}")
                        st.markdown("---")
                        st.markdown(article_text)
                        
                        st.download_button(
                            label="📥 Download Article",
                            data=article_text,
                            file_name=f"{keyword.replace(' ', '_')}.txt"
                        )
