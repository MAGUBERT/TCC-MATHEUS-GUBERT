import google.generativeai as genai

genai.configure(api_key="AIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0")

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)
