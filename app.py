import streamlit as st
import google.generativeai as genai
import random
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="SEO Heading-Rich Article Creator", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stSelectbox, .stTextArea, .stTextInput { background-color: #ffffff; border-radius: 8px; }
    .stButton>button { background: #FF9900; color: white; font-weight: bold; width: 100%; border: none; height: 3em; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 SEO Heading-Rich Article Factory")
st.write("Generate simple, attractive articles with keyword-rich headings for every paragraph.")

# --- SIDEBAR / OPTIONS ---
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Google AI API Key", type="password")
    
    st.header("📏 Article Length")
    word_count_option = st.selectbox(
        "Select Target Length:",
        ["1000 Words", "1500 Words", "2000 Words"]
    )
    target_words = int(word_count_option.split()[0])

    st.header("📦 Product Info")
    keyword = st.text_input("Product Name", placeholder="e.g. Sony WH-1000XM5")
    brand = st.text_input("Brand Name", placeholder="e.g. Sony")
    extra_info = st.text_area("Main Features / Points")

    st.header("🖼️ Image Settings")
    image_prompt = st.text_area("Describe the Image", "High-quality lifestyle product photo")

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

def write_section(key, model_name, prompt):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"Error: {str(e)}"

# --- MAIN APP LOGIC ---
if st.button("🚀 Generate SEO Article Now"):
    if not api_key:
        st.error("Please enter your API Key!")
    else:
        # 1. GENERATE IMAGE
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
            status = st.status(f"Creating your {target_words} word review...")
            
            # Divide work to control word count
            steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
            words_per_step = target_words // steps

            for i in range(steps):
                status.write(f"Writing Part {i+1}...")
                
                step_prompt = f"""
                You are a Helpful Product Reviewer and SEO Expert. 
                Topic: {keyword} ({brand}).
                Section: Phase {i+1} of {steps}. Target: {words_per_step} words.

                STRICT FORMATTING RULES:
                1. HEADING AFTER EVERY PARAGRAPH: You must start a new H2 or H3 heading before EVERY single paragraph of text. 
                2. SEO HEADINGS: Every heading MUST contain the main keyword "{keyword}" or related LSI (Latent Semantic Indexing) keywords.
                3. NO HTML: Use plain text for Meta Title and Meta Description.
                4. SIMPLE LANGUAGE: Use clear, easy-to-understand language. Focus on the main points and buyer benefits.
                5. HUMANIZED: Write like a real person who loves the product. Do not use AI words like "delve", "unlock", "tapestry", "unleash".
                6. KNOWLEDGEABLE: Provide attractive and useful information for a visitor who wants to buy this.

                Phase 1: Meta Title, Meta Description, H1, and Intro.
                Middle Phases: Detailed features, pros/cons, and real-life usage.
                Final Phase: FAQ (6 questions), Maintenance, and Conclusion.

                Product Features to mention: {extra_info}
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
                label=f"📥 Download SEO Review",
                data=full_content,
                file_name=f"{keyword.replace(' ', '_')}_SEO.txt"
            )
