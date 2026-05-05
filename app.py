import streamlit as st
import google.generativeai as genai
import random
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="Amazon Affiliate Article Creator", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stSelectbox, .stTextArea, .stTextInput { background-color: #ffffff; border-radius: 8px; }
    .stButton>button { background: #FF9900; color: white; font-weight: bold; width: 100%; border: none; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛒 Amazon Affiliate Article Factory")
st.write("Create humanized, attractive, and knowledgeable product reviews.")

# --- SIDEBAR / OPTIONS ---
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Google AI API Key", type="password")
    
    st.header("📏 Length Control")
    word_count_option = st.selectbox(
        "Select Word Count:",
        ["1000 Words", "1500 Words", "2000 Words"]
    )
    target_words = int(word_count_option.split()[0])

    st.header("📦 Product Details")
    keyword = st.text_input("Product Name", "e.g., House of Sillage Whispers of Truth")
    brand = st.text_input("Brand Name", "e.g., House of Sillage")
    extra_info = st.text_area("Supplemental Data (Specs, Links, Ingredients)")

    st.header("🖼️ Image Customization")
    image_prompt = st.text_area("Image Prompt", "e.g., A luxury perfume bottle on a marble table with soft golden lighting, 4k, professional photography")

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
if st.button("🚀 Create Expert Review"):
    if not api_key:
        st.error("Please enter your API Key!")
    else:
        # 1. GENERATE IMAGE BASED ON USER PROMPT
        st.subheader("🖼️ Product Visual")
        clean_img_prompt = urllib.parse.quote(image_prompt)
        seed = random.randint(1, 99999)
        img_url = f"https://image.pollinations.ai/prompt/{clean_img_prompt}?width=1024&height=768&nologo=true&seed={seed}"
        st.image(img_url, use_container_width=True)

        # 2. START ARTICLE GENERATION
        best_model = get_best_model(api_key)
        if not best_model:
            st.error("API Error. Check your key.")
        else:
            full_content = ""
            status = st.status(f"Writing your {target_words} word expert article...")
            
            # Divide work into sections to control word count strictly
            # 1000 = 2 phases | 1500 = 3 phases | 2000 = 4 phases
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            for i in range(steps):
                status.write(f"Generating Phase {i+1} of {steps}...")
                
                step_prompt = f"""
                You are an Experienced Lifestyle & Tech Reviewer writing for an Amazon Affiliate site. 
                Your goal is to provide 'Expert Knowledge' that is easy to understand but very high-value.
                Topic: {keyword} ({brand}).
                Current Section: Phase {i+1} of {steps}.
                
                CONTENT RULES:
                1. FORMAT: DO NOT use HTML tags like <meta>. Use plain text headers.
                2. LENGTH: Write exactly {words_per_step} words for this section. DO NOT go over.
                3. STYLE: Mature, attractive, and knowledgeable. Give 'insider info' (e.g., if it's a perfume, talk about the chemistry of the dry-down; if it's a gadget, talk about the build quality or user interface).
                4. NO AI CLICHES: Avoid 'delve', 'unlock', 'tapestry', 'unleash', 'in conclusion'.
                5. FOCUS: 
                   - Phase 1: Meta Title (Text), Meta Description (Text), H1, and an attractive introduction.
                   - Middle Phases: Deep technical analysis, hidden benefits, and competitive comparison.
                   - Final Phase: Maintenance, 6 Detailed FAQs, and a final expert verdict.
                
                Product Info: {extra_info}
                """
                
                section_text = write_section(api_key, best_model, step_prompt)
                full_content += section_text + "\n\n"

            status.update(label="✅ Article Complete!", state="complete")

            # --- DISPLAY ---
            st.markdown("---")
            st.markdown(full_content)
            
            final_count = len(full_content.split())
            st.info(f"Final Word Count: {final_count} words.")
            
            st.download_button(
                label=f"📥 Download {target_words} Word Review",
                data=full_content,
                file_name=f"{keyword.replace(' ', '_')}.txt"
            )
