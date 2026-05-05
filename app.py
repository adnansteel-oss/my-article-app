import streamlit as st
import google.generativeai as genai
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro Humanized Article AI", layout="wide")

# --- CUSTOM CSS FOR BETTER LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 High-Length Humanized Article Generator")
st.write("Generating SEO-optimized articles (1500-2000 words) using Google Gemini AI.")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("🔑 API Configuration")
    google_api_key = st.text_input("Google AI Studio API Key", type="password")
    st.info("Get your key at: aistudio.google.com")
    
    st.header("📝 Article Settings")
    keyword = st.text_input("Main Keyword", "CHEFMAN AIR FRYER")
    brand = st.text_input("Brand Name", "CHEFMAN")
    language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
    
    st.header("⚙️ Advanced")
    extra_data = st.text_area("Supplemental Content / Links", help="Paste specific product details or website links here.")

# --- IMAGE GENERATOR FUNCTION ---
def get_image(kw):
    seed = random.randint(1, 9999)
    # Using Pollinations AI for high-quality, free AI images
    img_url = f"https://pollinations.ai/p/{kw.replace(' ', '_')}_professional_product_photography_modern_kitchen_high_resolution?width=1024&height=768&seed={seed}&nologo=true"
    return img_url

# --- ARTICLE GENERATOR FUNCTION ---
def generate_long_article(api_key, kw, br, extra):
    try:
        genai.configure(api_key=api_key)
        
        # Using gemini-1.5-flash for maximum speed and stability
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # PROMPT DESIGNED FOR 2000 WORDS AND HUMAN TONE
        prompt = f"""
        You are a senior SEO Copywriter. Write a 2000-word deep-dive article about {kw}.
        Brand: {br}
        Supplemental Info: {extra}

        STRUCTURE REQUIREMENTS:
        1. Meta Title & Description: Optimized for Google Search Console.
        2. H1 Headline: Catchy and human.
        3. Introduction: Start with a relatable story or problem. 400 words.
        4. Detailed H2 Sections: 
           - Technology & Innovation (TurboFry, etc.)
           - Capacity & Family Use (8-Quart vs others)
           - Health Benefits (Detailed talk about 98% less oil)
           - Cooking Tips (How to get food crispy)
           - Durability & Maintenance (Stainless steel, cleaning)
        5. Detailed FAQ: 6 unique questions.
        6. Conclusion & Key Features: Bulleted list summary.

        HUMANIZATION RULES (CRITICAL):
        - Do NOT use: "In conclusion", "Unlock", "Delve", "Tapestry", "Harness", "Think of it as".
        - Use "burstiness": mix short, punchy sentences with longer, descriptive ones.
        - Write at a 8th-grade reading level.
        - Be extremely descriptive. Instead of saying "it is easy to clean," describe the non-stick coating and the dishwasher experience.
        - Ensure total word count is between 1500 and 2000 words.
        """

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- MAIN APP LOGIC ---
if st.button("Create Humanized Article"):
    if not google_api_key:
        st.warning("Please enter your API Key in the sidebar!")
    else:
        # Step 1: Generate Image
        img_url = get_image(keyword)
        st.image(img_url, caption=f"SEO Optimized Image for {keyword}")

        # Step 2: Generate Content
        with st.spinner("Writing high-length article... Please wait (takes ~30 seconds)"):
            article_text = generate_long_article(google_api_key, keyword, brand, extra_data)
            
            if "ERROR" in article_text:
                st.error(article_text)
            else:
                st.success("Article Generated Successfully!")
                
                # Word Count Check
                words = len(article_text.split())
                st.info(f"Approximate Word Count: {words} words")
                
                st.markdown("---")
                st.markdown(article_text)
                
                # Step 3: Download Button
                st.download_button(
                    label="📥 Download Article (.txt)",
                    data=article_text,
                    file_name=f"{keyword.replace(' ', '_')}_article.txt",
                    mime="text/plain"
                )

st.markdown("---")
st.caption("Powered by Google Gemini 1.5 & Pollinations AI")
