import os
import requests

# ---------------- CONFIGURAÇÃO ----------------
api_key = 'K83625664488957'      # coloque sua chave do OCR.space
pasta_imagens = 'imagens/'      # pasta onde estão suas imagens
lingua = 'por'                  # 'por' para português
# ------------------------------------------------

url = 'https://api.ocr.space/parse/image'

# Listar arquivos da pasta
arquivos = [f for f in os.listdir(pasta_imagens) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

for arquivo in arquivos:
    caminho = os.path.join(pasta_imagens, arquivo)
    with open(caminho, 'rb') as f:
        payload = {
            'apikey': api_key,
            'language': lingua,
        }
        files = {'file': f}
        response = requests.post(url, data=payload, files=files)

    resultado = response.json()
    
    if not resultado['IsErroredOnProcessing']:
        texto = resultado['ParsedResults'][0]['ParsedText']
        print(f'------ {arquivo} ------')
        print(texto)
        print()
    else:
        print(f'Erro ao processar {arquivo}:', resultado.get('ErrorMessage'))
