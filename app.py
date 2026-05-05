import streamlit as st
import google.generativeai as genai
import random
import urllib.parse

# --- CONFIG ---
st.set_page_config(page_title="Humanized Article Factory", layout="wide")

st.title("🚀 Professional Humanized Article Generator")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 API Credentials")
    api_key = st.text_input("Enter Google API Key", type="password")
    
    st.header("📝 Article Settings")
    keyword = st.text_input("Main Keyword", "CHEFMAN AIR FRYER")
    brand = st.text_input("Brand Name", "CHEFMAN")
    extra_info = st.text_area("Extra Info (Links or Details)")

# --- CORE FUNCTIONS ---
def get_best_model(key):
    try:
        genai.configure(api_key=key)
        all_models = genai.list_models()
        model_names = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        for name in model_names:
            if "gemini-1.5-flash" in name: return name
        for name in model_names:
            if "gemini-1.5-pro" in name: return name
        return model_names[0] if model_names else None
    except: return None

def generate_article(key, model_name, kw, br, extra):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Write a high-quality, human-sounding SEO article about {kw}.
        Brand: {br}
        Details: {extra}

        REQUIREMENTS:
        - LENGTH: Minimum 1500 words.
        - STYLE: 100% Human-like. Avoid: delve, unlock, tapestry, in conclusion, unleash.
        - STRUCTURE: Meta Title, Meta Description, Catchy H1, Long Introduction, 5 H2 Sections, 6 FAQs, and a Feature Summary list.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"ERROR: {str(e)}"

# --- INTERFACE ---
if st.button("Generate Article & Image"):
    if not api_key:
        st.error("Please enter your API Key!")
    else:
        # --- NEW ROBUST IMAGE LOGIC ---
        # 1. Clean the keyword for a URL
        clean_kw = urllib.parse.quote(f"{keyword} modern kitchen appliance product photography")
        seed = random.randint(1, 100000)
        img_url = f"https://pollinations.ai/p/{clean_kw}?width=1024&height=768&seed={seed}&nologo=true"
        
        # 2. Create a placeholder for the image so it shows up immediately
        image_container = st.container()
        with image_container:
            st.image(img_url, caption=f"AI Generated Image for {keyword}", use_container_width=True)
            st.info("🎨 Image generated. Writing the 2000-word article now... please wait.")

        # --- ARTICLE GENERATION ---
        with st.spinner("Writing article..."):
            best_model_name = get_best_model(api_key)
            if not best_model_name:
                st.error("Model Error: Check your API key.")
            else:
                final_article = generate_article(api_key, best_model_name, keyword, brand, extra_info)
                
                if "ERROR" in final_article:
                    st.error(final_article)
                else:
                    word_count = len(final_article.split())
                    st.success(f"Generation Complete! (~{word_count} words)")
                    
                    st.markdown("---")
                    st.markdown(final_article)
                    
                    st.download_button(
                        label="📥 Download Article",
                        data=final_article,
                        file_name=f"{keyword.replace(' ', '_')}.txt"
                    )
