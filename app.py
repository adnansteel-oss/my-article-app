import streamlit as st
import google.generativeai as genai
import random
import urllib.parse
import time  # NEW: Required for delays

# --- PAGE CONFIG ---
st.set_page_config(page_title="Safe SEO Article Factory", layout="wide")

# --- LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login_page():
    st.title("🔒 Login to Article Factory")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        if email and password:
            st.session_state['logged_in'] = True
            st.rerun()

def main_app():
    with st.sidebar:
        st.header("🔑 Your API Key")
        user_api_key = st.text_input("Paste Google API Key", type="password")
        
        st.header("📏 Length")
        word_count_option = st.selectbox("Word Count:", ["1000 Words", "1500 Words", "2000 Words"])
        target_words = int(word_count_option.split()[0])

        st.header("📦 Product")
        keyword = st.text_input("Product Name")
        brand = st.text_input("Brand Name")
        extra_info = st.text_area("Features")

        st.header("🖼️ Image")
        image_prompt = st.text_area("Image Description")

    if st.button("🚀 Generate Article (Safe Mode)"):
        if not user_api_key:
            st.error("Enter your API Key.")
        else:
            # 1. IMAGE
            st.subheader("🖼️ Visual")
            clean_img = urllib.parse.quote(image_prompt)
            img_url = f"https://image.pollinations.ai/prompt/{clean_img}?width=1024&height=768&seed={random.randint(1,9999)}"
            st.image(img_url)

            # 2. CONTENT GENERATION
            try:
                genai.configure(api_key=user_api_key)
                # FORCE GEMINI 1.5 FLASH (Most stable)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                full_content = ""
                steps = 2 if target_words == 1000 else (3 if target_words == 1500 else 4)
                
                status = st.status("Writing article... Please wait for cool-down periods.")
                
                for i in range(steps):
                    status.write(f"Writing Phase {i+1} of {steps}...")
                    
                    step_prompt = f"""
                    Reviewer: Helpful Consumer Expert. Product: {keyword}. 
                    Write {target_words // steps} words. 
                    Simple language, SEO headings for every paragraph.
                    Phase {i+1}: {'Intro/Meta' if i==0 else 'Main points' if i<steps-1 else 'FAQ/Verdict'}
                    """
                    
                    # --- THE FIX: TIME DELAY ---
                    if i > 0:
                        status.write("⏱️ Sleeping for 10 seconds to avoid Google Rate Limit...")
                        time.sleep(10) # Pause for 10 seconds between requests
                    
                    response = model.generate_content(step_prompt)
                    full_content += response.text + "\n\n"
                
                status.update(label="✅ Article Complete!", state="complete")
                st.markdown(full_content)
                st.download_button("Download", full_content, file_name="review.txt")
                
            except Exception as e:
                st.error(f"Google Limit Reached: {str(e)}")
                st.info("TIP: Wait 60 seconds, then click generate again. Or, create a NEW Project in AI Studio.")

# --- APP FLOW ---
if st.session_state['logged_in']:
    main_app()
else:
    login_page()
