import streamlit as st
import google.generativeai as genai
import random
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="Expert SEO Article App", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stSelectbox, .stRadio { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #ddd; }
    .stButton>button { background: linear-gradient(to right, #007bff, #0056b3); color: white; border: none; padding: 10px 20px; font-size: 18px; border-radius: 5px; cursor: pointer; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Mature SEO Article Factory")
st.write("Generate high-authority, humanized articles with specific word count targets.")

# --- SIDEBAR / OPTIONS ---
with st.sidebar:
    st.header("🔑 API Key")
    api_key = st.text_input("Google AI Studio API Key", type="password")
    
    st.header("📦 Article Length Option")
    # This is the "Box" with the 3 options you requested
    word_count_option = st.selectbox(
        "Select Article Length:",
        ["1000 Words Article", "1500 Words Article", "2000 Words Article"]
    )
    
    # Extract the number from the selection
    target_words = int(word_count_option.split()[0])

    st.header("📝 Topic Details")
    keyword = st.text_input("Main Keyword", "CHEFMAN AIR FRYER")
    brand = st.text_input("Brand Name", "CHEFMAN")
    extra_info = st.text_area("Supplemental Data (Links/Specs)")

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

# --- MAIN APP LOGIC ---
if st.button("🚀 Generate Mature Article"):
    if not api_key:
        st.error("Please enter your API Key!")
    else:
        # 1. NEW IMAGE GENERATION METHOD
        st.subheader("🖼️ Article Visual")
        clean_kw = urllib.parse.quote(f"high-end professional kitchen photography of {keyword} lifestyle")
        seed = random.randint(1, 99999)
        img_url = f"https://image.pollinations.ai/prompt/{clean_kw}?width=1024&height=768&nologo=true&seed={seed}"
        
        # Displaying image with a fallback link
        st.image(img_url, use_container_width=True)
        st.markdown(f"*[Link to Image if not loading]({img_url})*")

        # 2. START ARTICLE GENERATION
        best_model = get_best_model(api_key)
        if not best_model:
            st.error("API Error. Check your key.")
        else:
            full_content = ""
            status = st.status(f"Writing your {target_words} word article...")
            
            # Divide work into sections to ensure word count and quality
            # 1000 words = 2 steps | 1500 words = 3 steps | 2000 words = 4 steps
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            for i in range(steps):
                status.write(f"Generating Phase {i+1} of {steps}...")
                
                step_prompt = f"""
                You are a Mature Culinary Industry Expert and SEO Strategist. 
                Write a section for a deep-dive article about {keyword} ({brand}).
                
                Phase {i+1} focus: 
                - If Phase 1: Meta Data, H1, and an expert-level technical introduction.
                - If Phase 2: Deep feature analysis, thermodynamic efficiency of the {brand} technology.
                - If Phase 3: Comparative industry analysis and maintenance for long-term durability.
                - If Phase 4: Mature FAQ, Search Console optimization, and Pro-tips.

                STRICT RULES:
                1. WORD COUNT: This specific section MUST be at least {words_per_step} words.
                2. MATURITY: Do not use generic blogger language. Provide new, attractive, and knowledgeable insights. 
                3. HUMANIZATION: Do NOT use: delve, unlock, tapestry, unleash, in conclusion. 
                4. VALUE: Give the reader knowledge they cannot find on common websites.
                5. DATA: Incorporate this: {extra_info}.
                """
                
                section_text = write_section(api_key, best_model, step_prompt)
                full_content += section_text + "\n\n"

            status.update(label="✅ Article Complete!", state="complete")

            # --- DISPLAY ---
            st.markdown("---")
            st.markdown(full_content)
            
            final_count = len(full_content.split())
            st.info(f"Verified Word Count: {final_count} words.")
            
            st.download_button(
                label=f"📥 Download {target_words} Word Article",
                data=full_content,
                file_name=f"{keyword}_expert_article.txt"
            )
