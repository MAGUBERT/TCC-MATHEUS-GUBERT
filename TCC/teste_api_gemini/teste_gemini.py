import os
from PIL import Image, ImageEnhance
import google.generativeai as genai

genai.configure(api_key="AIzaSyABD3_f04bb8Qu0dN-dJkMRJFY7R_s6cvo")
model = genai.GenerativeModel("gemini-1.5-flash")

IMAGENS_DIR = "imagens"
RESULTADOS_DIR = "resultados"
MELHORADAS_DIR = "melhoradas"

os.makedirs(RESULTADOS_DIR, exist_ok=True)
os.makedirs(MELHORADAS_DIR, exist_ok=True)

for arquivo in os.listdir(IMAGENS_DIR):
    if arquivo.lower().endswith((".png", ".jpg", ".jpeg")):
        caminho_original = os.path.join(IMAGENS_DIR, arquivo)
        caminho_melhorada = os.path.join(MELHORADAS_DIR, f"melhorada_{arquivo}")

        img = Image.open(caminho_original)
        img = ImageEnhance.Contrast(img).enhance(1.8)
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        img = ImageEnhance.Color(img).enhance(1.0)
        largura, altura = img.size
        img = img.resize((largura * 2, altura * 2))
        img.save(caminho_melhorada)

        with open(caminho_melhorada, "rb") as f:
            response = model.generate_content([
                "Extraia somente os códigos de peça visíveis nesta imagem. "
                "Retorne apenas os códigos, um por linha, sem nenhum texto adicional.",
                {"mime_type": "image/png", "data": f.read()}
            ])
        codigos = response.text.strip().upper()

        caminho_txt = os.path.join(RESULTADOS_DIR, f"{os.path.splitext(arquivo)[0]}.txt")
        with open(caminho_txt, "w") as f:
            f.write(codigos)

        print(f"✅ {arquivo} → códigos salvos em {caminho_txt}")
