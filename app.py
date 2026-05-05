import streamlit as st
import google.generativeai as genai
import random

# --- CONFIG ---
st.set_page_config(page_title="Humanized Article Factory", layout="wide")

st.title("🚀 Professional Humanized Article Generator")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 API Credentials")
    api_key = st.text_input("Enter New Google API Key", type="password")
    st.info("Get a fresh key at aistudio.google.com")
    
    st.header("📝 Article Settings")
    keyword = st.text_input("Main Keyword", "CHEFMAN AIR FRYER")
    brand = st.text_input("Brand Name", "CHEFMAN")
    extra_info = st.text_area("Extra Info (Links or Details)")

# --- CORE FUNCTIONS ---
def get_best_model(key):
    """Automatically finds the correct model name to avoid 404 errors."""
    try:
        genai.configure(api_key=key)
        all_models = genai.list_models()
        # Look for 1.5 Flash first, then 1.5 Pro, then 1.0 Pro
        model_names = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        for name in model_names:
            if "gemini-1.5-flash" in name:
                return name
        for name in model_names:
            if "gemini-1.5-pro" in name:
                return name
        return model_names[0] if model_names else None
    except:
        return None

def generate_article(key, model_name, kw, br, extra):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        
        # PROMPT ENGINEERED FOR 1500-2000 WORDS
        prompt = f"""
        Write a high-quality, human-sounding SEO article about {kw}.
        Brand: {br}
        Details: {extra}

        REQUIREMENTS:
        - LENGTH: Minimum 1500 words. Be very descriptive.
        - STYLE: 100% Human-like. Avoid "AI-speak" (don't use: delve, unlock, tapestry, in conclusion, unleash).
        - STRUCTURE: Meta Title, Meta Description, Catchy H1, Long Introduction, 5 H2 Sections, 6 FAQs, and a Feature Summary list.
        - TONE: Conversational, expert, and helpful.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- INTERFACE ---
if st.button("Generate 2000-Word Article"):
    if not api_key:
        st.error("Please enter your API Key!")
    else:
        # Generate high-quality kitchen image
        seed = random.randint(1, 9999)
        img_url = f"https://pollinations.ai/p/{keyword.replace(' ', '_')}_modern_kitchen_lifestyle_photography?width=1024&height=768&seed={seed}"
        st.image(img_url, caption=f"SEO Image for {keyword}")

        with st.spinner("Finding available model and writing article..."):
            best_model_name = get_best_model(api_key)
            
            if not best_model_name:
                st.error("Model Error: Your API key might be restricted or the Generative Language API is not enabled.")
            else:
                st.info(f"Writing with model: {best_model_name}")
                final_article = generate_article(api_key, best_model_name, keyword, brand, extra_info)
                
                if "ERROR" in final_article:
                    st.error(final_article)
                else:
                    word_count = len(final_article.split())
                    st.success(f"Generation Complete! (~{word_count} words)")
                    st.markdown("---")
                    st.markdown(final_article)
                    
                    st.download_button(
                        label="📥 Download Article (.txt)",
                        data=final_article,
                        file_name=f"{keyword.replace(' ', '_')}.txt"
                    )
