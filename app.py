import streamlit as st
import google.generativeai as genai
import random
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(page_title="Simple SEO Article Creator", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stSelectbox, .stTextArea, .stTextInput { background-color: #ffffff; border-radius: 8px; }
    .stButton>button { background: #FF9900; color: white; font-weight: bold; width: 100%; border: none; height: 3em; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛍️ Smart & Simple Affiliate Article Generator")
st.write("Generate easy-to-read, high-value product reviews for your visitors.")

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
    extra_info = st.text_area("Product Features (Paste specs or main points here)")

    st.header("🖼️ Image Settings")
    image_prompt = st.text_area("Describe the Image", "Professional product photo of the item in a clean, bright setting")

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
if st.button("🚀 Generate Simple & Knowledgeable Article"):
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
                You are a Helpful Product Reviewer for a popular shopping blog. 
                Your goal is to explain {keyword} ({brand}) in SIMPLE, EASY language.
                Current Section: Phase {i+1} of {steps}. Target word count for this part: {words_per_step} words.

                RULES:
                1. NO HTML: For Meta Title and Description, use ONLY plain text. No <meta> tags.
                2. LANGUAGE: Use simple, clear sentences. Do not go too deep into science or chemistry. 
                3. FOCUS: Talk about why the product is good, how it feels to use, and the main features people care about.
                4. KNOWLEDGE: Even though the language is simple, show that you know the product well. Mention quality, comfort, and real-life benefits.
                5. NO AI WORDS: Do not use "delve", "unlock", "tapestry", "unleash", "in conclusion".
                6. STRUCTURE: 
                   - Phase 1: Clear Meta Title, Simple Meta Description, H1, and an inviting Intro.
                   - Phase 2/3: The Main Points of the product, why it's better than others, and Pros/Cons.
                   - Final Phase: Who should buy this, 6 common Buyer FAQs, and a final simple summary.

                Product Data: {extra_info}
                """
                
                section_text = write_section(api_key, best_model, step_prompt)
                full_content += section_text + "\n\n"

            status.update(label="✅ Review Ready!", state="complete")

            # --- DISPLAY ---
            st.markdown("---")
            st.markdown(full_content)
            
            final_count = len(full_content.split())
            st.info(f"Final Count: {final_count} words.")
            
            st.download_button(
                label=f"📥 Download Review",
                data=full_content,
                file_name=f"{keyword.replace(' ', '_')}.txt"
            )
