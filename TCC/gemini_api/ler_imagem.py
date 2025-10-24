from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0")

with open('peca2.jpg', 'rb') as f:
    image_bytes = f.read()

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
      ),
      'Descreva esta imagem em detalhes usando o Português do Brasil. Quais modelos de carro sao compativel?'
    ]
)

print(response.text)