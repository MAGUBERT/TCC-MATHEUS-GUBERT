from google import genai
from google.genai import types
from pathlib import Path  
import os               

IMAGE_FOLDER = 'pecas_automotivas' 
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']

client = genai.Client(api_key="AIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0")

print(f"Buscando imagens dentro da pasta: {IMAGE_FOLDER}")

folder_path = Path(IMAGE_FOLDER)
contents_parts = []
image_count = 0

if not folder_path.is_dir():
    print(f"❌ Erro: A pasta '{IMAGE_FOLDER}' não foi encontrada.")
else:
    for file_path in folder_path.iterdir():
        
        file_suffix = file_path.suffix.lower()
        
        if file_suffix in ALLOWED_EXTENSIONS:
            try:
                with open(file_path, 'rb') as f:
                    image_bytes = f.read()
                
                if file_suffix in ['.jpg', '.jpeg']:
                    mime_type = 'image/jpeg'
                elif file_suffix == '.png':
                    mime_type = 'image/png'
                else:
                    mime_type = f'image/{file_suffix[1:]}' 
                
                contents_parts.append(
                    types.Part.from_bytes(
                        data=image_bytes, 
                        mime_type=mime_type, 
                    )
                )
                image_count += 1
                print(f"  ✅ Adicionada: {file_path.name}")

            except Exception as e:
                print(f"  ❌ Erro ao ler o arquivo {file_path.name}: {e}")

prompt = f"""
leia as {image_count} imagens que você recebeu. 
As imagens mostram diferentes ângulos e detalhes de uma peça automotiva. 
Com base na análise das peças em todas as imagens envidas, descreva a peça 
e liste os modelos de carro que são compatíveis seperados e com seus anos.
quais sao os codigos liste seperadamente eles.
Use o Português do Brasil para toda a resposta.
"""
contents_parts.append(prompt)

if image_count > 0:
    print("\nIniciando a análise com o modelo Gemini...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents_parts 
        )
        print("\n--- Resposta do Gemini ---\n")
        print(response.text)
    except Exception as e:
        print(f"\n❌ Erro na chamada da API: {e}")
else:
    print("\n❌ Nenhuma imagem compatível foi encontrada na pasta para enviar à API.")