import google.generativeai as genai

# 🌟 PASTE YOUR KEY HERE
GOOG_API_KEY = "AIzaSyCDIB12k84JmdNfiWzd19JHO8em8FiaMmE" 

genai.configure(api_key=GOOG_API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        # Only show models that can generate text (chatbots)
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")

    