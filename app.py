import streamlit as st
from openai import OpenAI

# App Configuration
st.set_page_config(page_title="SEO Humanized Article Generator", layout="wide")

# --- UI Layout ---
st.title("✍️ Professional Humanized Article Creator")
st.markdown("Generates 1500-2000 word articles that pass AI detectors and rank on Google.")

# Sidebar for API Key and Settings
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    model_choice = "gpt-4o" # Best for human-like writing
    
    st.header("Article Parameters")
    main_keyword = st.text_input("Main Keyword", placeholder="e.g. CHEFMAN AIR FRYER")
    brand_name = st.text_input("Brand Name", placeholder="e.g. CHEFMAN")
    country = st.selectbox("Google Search Country", ["United States", "United Kingdom", "Canada"])
    language = st.selectbox("Language", ["English", "Spanish", "French"])
    extra_data = st.text_area("Supplemental Info (Paste links or extra info here)")

# Function to generate content in sections to ensure 2000 words
def generate_long_article(api_key, keyword, brand, extra):
    client = OpenAI(api_key=api_key)
    
    sections = [
        "Introduction and Meta Data (Include Meta Title, Description, and an engaging H1)",
        "In-depth Product Overview and Technology (Focus on TurboFry and Multifunctional aspects)",
        "Health Benefits and Comparison (Focus on 98% less oil and nutritional cooking)",
        "Mastering the Appliance: Tips, Tricks, and Recipe Ideas for Crispy Results",
        "Durability, Design, and Safety Features (Stainless steel, auto-shutoff, cleaning)",
        "Customer Reviews Summary and FAQ (Answer at least 5 common questions)",
        "Final Summary and Key Features Bullet Points"
    ]
    
    full_article = ""
    progress_bar = st.progress(0)
    
    for i, section in enumerate(sections):
        st.write(f"Generating {section}...")
        prompt = f"""
        Write a professional, humanized SEO section for an article about {keyword}.
        Brand Name: {brand}. 
        Specific Section to write: {section}.
        Context/Data: {extra}.
        
        Rules:
        1. Use a conversational, helpful, human tone (avoid 'AI-sounding' words like 'delve', 'tapestry', 'testament').
        2. Use LSI keywords related to {keyword}.
        3. Make this section very detailed. Write at least 300 words for this section alone.
        4. Use Bold text for key points.
        5. Structure with H2 or H3 headers.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are an expert SEO copywriter who writes 100% human-score content."},
                      {"role": "user", "content": prompt}],
            temperature=0.8
        )
        full_article += response.choices[0].message.content + "\n\n"
        progress_bar.progress((i + 1) / len(sections))
    
    return full_article

def generate_seo_image(api_key, keyword):
    client = OpenAI(api_key=api_key)
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Professional high-quality lifestyle photography of {keyword} in a modern kitchen. High resolution, bright lighting, 16:9 aspect ratio.",
        size="1024x1024"
    )
    return response.data[0].url

# --- Execution ---
if st.button("Generate 2000-Word Article & Image"):
    if not api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    else:
        with st.spinner("Writing article... This takes about 1-2 minutes to ensure high word count."):
            # Generate Image
            image_url = generate_seo_image(api_key, main_keyword)
            st.image(image_url, caption=f"SEO Image for {main_keyword}")
            
            # Generate Content
            final_content = generate_long_article(api_key, main_keyword, brand_name, extra_data)
            
            st.markdown("---")
            st.markdown(final_content)
            
            st.download_button("Download Article", final_content, file_name="article.md")
