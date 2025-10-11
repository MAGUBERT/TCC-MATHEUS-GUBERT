import google.generativeai as genai
from PIL import Image

genai.configure(api_key="SUA_AAIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0PI_KEY_AQUI")

model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

imagem = Image.open("/home/magubert/Documentos/TCC-MATHEUS-GUBERT/imagens/teste1.png")

prompt = "Descreva o conteúdo desta imagem e extraia quaisquer códigos visuais, números ou texto legível."

response = model.generate_content([prompt, imagem])

print(response.text)
