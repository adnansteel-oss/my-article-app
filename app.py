def generate_article_with_gemini(api_key, kw, br, info):
    genai.configure(api_key=api_key)
    
    # We switch to 'gemini-1.5-flash' which has much higher availability
    # and still supports a massive 1-million-token context window.
    model_name = "gemini-1.5-flash" 
    
    generation_config = {
        "temperature": 1.0, 
        "top_p": 0.95,
        "max_output_tokens": 8192, 
    }

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
        )

        prompt = f"""
        Write a high-quality, HUMAN-LIKE SEO article about {kw}.
        Brand: {br}
        
        INSTRUCTIONS:
        - Total Length: 1500 to 2000 words.
        - Tone: Expert, conversational, and helpful.
        - Avoid AI language: DO NOT use words like 'unleash', 'delve', 'testament', or 'in today's digital age'.
        - Include: Meta Title, Meta Description, H1, H2 sections, FAQ, and a Conclusion.
        - Data to use: {info}
        
        Make the article extremely detailed. Describe every feature, benefit, and use-case for {kw} to ensure the word count reaches 2000 words.
        """

        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # If Flash also fails, this will show you exactly which models you ARE allowed to use
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return f"Error with model. Your available models are: {available_models}. Error details: {str(e)}"
