import requests

api_key = 'K83625664488957'
url = 'https://api.ocr.space/parse/image'

# Abrir imagem
with open('peca.png', 'rb') as f:
    payload = {
        'apikey': api_key,
        'language': 'por',  # 'eng' para inglês
    }
    files = {'peca.png': f}
    response = requests.post(url, data=payload, files=files)

result = response.json()

# Mostrar o texto detectado
if result['IsErroredOnProcessing'] == False:
    text = result['ParsedResults'][0]['ParsedText']
    print(text)
else:
    print("Erro:", result['ErrorMessage'])
