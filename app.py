import streamlit as st
import google.generativeai as genai
import random

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Google AI Article Generator", layout="wide")

st.title("🤖 Google AI Humanized Article Creator")
st.markdown("Uses Gemini 1.5 Pro to create 1000-2000 word SEO articles.")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("API Settings")
    google_api_key = st.text_input("Enter Google AI Studio API Key", type="password")
    
    st.header("Article Details")
    keyword = st.text_input("Main Keyword", "CHEFMAN AIR FRYER")
    brand = st.text_input("Brand Name", "CHEFMAN")
    country = st.selectbox("Target Country", ["United States", "United Kingdom", "Canada"])
    language = st.selectbox("Language", ["English", "Spanish", "French"])
    
    st.header("Extra Instructions")
    extra_info = st.text_area("Paste links or specific features here...")

# --- ARTICLE GENERATION LOGIC ---
def generate_article_with_gemini(api_key, kw, br, info):
    genai.configure(api_key=api_key)
    
    # Configuration for Gemini
    generation_config = {
        "temperature": 0.9, # Higher temperature for more human-like variety
        "top_p": 1,
        "max_output_tokens": 8192, # Allows for very long articles
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    )

    # Detailed Prompt to hit 2000 words and 100% human score
    prompt = f"""
    Write a comprehensive, professional, and human-sounding SEO blog post about {kw}.
    Brand: {br}
    Target Audience: Home cooks in {country}.
    Additional Data to Include: {info}

    WORD COUNT REQUIREMENT: Minimum 1500 words, Maximum 2000 words. 
    You MUST be extremely descriptive.

    STYLE REQUIREMENTS:
    1. TONE: Helpful, enthusiastic, and conversational. Use "you" and "we". 
    2. STRUCTURE: 
       - Meta Title and Meta Description (SEO Optimized).
       - H1 Headline.
       - Introduction (Focus on benefits, not just features).
       - H2: Detailed features breakdown (Capacity, Technology like TurboFry).
       - H2: Health benefits (The "98% less oil" concept).
       - H2: Practical Tips for "Crispy Perfection".
       - H2: Cleaning and Maintenance.
       - H3: Comparison with traditional frying.
       - FAQ Section (5 detailed questions).
       - Key Features Summary (Bulleted list).
    3. HUMANIZATION: Avoid AI clichés like "In conclusion," "Unleash," "In the fast-paced world," or "Dive into." Write like a real product reviewer who has used the item.
    4. SEO: Use LSI keywords naturally throughout.
    """

    response = model.generate_content(prompt)
    return response.text

# --- IMAGE GENERATION ---
def get_image(kw):
    # Using a high-quality free image source that works via URL
    seed = random.randint(1, 1000)
    img_url = f"https://pollinations.ai/p/{kw.replace(' ', '_')}_modern_kitchen_appliance_cinematic_lighting?width=1024&height=768&seed={seed}"
    return img_url

# --- MAIN APP INTERFACE ---
if st.button("Generate Article & Images Now"):
    if not google_api_key:
        st.error("Please enter your Google API Key!")
    else:
        try:
            with st.spinner("Gemini is researching and writing your 2000-word article..."):
                # 1. Show the Image
                image_url = get_image(keyword)
                st.image(image_url, caption=f"Generated Image for {keyword}")
                
                # 2. Generate and Display Content
                article_content = generate_article_with_gemini(google_api_key, keyword, brand, extra_info)
                
                st.markdown("---")
                st.markdown(article_content)
                
                # 3. Download Button
                st.download_button(
                    label="Download Article as Text",
                    data=article_content,
                    file_name=f"{keyword.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")
