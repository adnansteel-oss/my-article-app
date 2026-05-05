import streamlit as st
import google.generativeai as genai
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="SEO Article App", layout="wide")

st.title("✍️ Professional SEO Article Generator")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 API Setup")
    # I have added a fallback so you can try different model names if one fails
    google_api_key = st.text_input("Enter New Google API Key", type="password")
    
    model_name = st.selectbox("Select Model (Try Flash first)", 
                               ["models/gemini-1.5-flash", 
                                "models/gemini-1.5-pro", 
                                "gemini-1.5-flash"])
    
    st.header("📝 Content Settings")
    keyword = st.text_input("Main Keyword", "CHEFMAN AIR FRYER")
    brand = st.text_input("Brand Name", "CHEFMAN")
    extra_data = st.text_area("Supplemental Content / Links")

# --- IMAGE GEN ---
def get_image(kw):
    seed = random.randint(1, 9999)
    return f"https://pollinations.ai/p/{kw.replace(' ', '_')}_kitchen_appliance?width=1024&height=768&seed={seed}"

# --- CONTENT GEN ---
def generate_article(api_key, model_choice, kw, br, extra):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_choice)
        
        prompt = f"""
        Write a 1500-2000 word humanized SEO article about {kw}.
        Brand Name: {br}
        Additional Data: {extra}

        Guidelines:
        - Use a conversational, human tone.
        - Avoid AI words like 'delve', 'unleash', 'tapestry'.
        - Format with H1, H2, and H3 headers.
        - Include a Meta Title, Meta Description, and 6 FAQs.
        - Make it extremely detailed to hit the 2000 word goal.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- BUTTON ---
if st.button("Generate My Article"):
    if not google_api_key:
        st.error("Please enter your API Key!")
    else:
        # Show Image
        st.image(get_image(keyword), caption=keyword)
        
        with st.spinner(f"Using {model_name} to write your article..."):
            result = generate_article(google_api_key, model_name, keyword, brand, extra_data)
            
            if "ERROR" in result:
                st.error(result)
                st.info("TIP: If you see a 404 error, try changing the 'Select Model' dropdown in the sidebar to a different version.")
            else:
                st.success("Article Created!")
                st.markdown(result)
                st.download_button("Download Article", result, file_name="article.txt")
