import os
import requests

# ---------------- CONFIGURAÇÃO ----------------
api_key = 'K83625664488957'       # coloque sua chave do OCR.space
pasta_imagens = 'imagens/'       # pasta onde estão suas imagens
pasta_saida = 'txt_codigos/'     # pasta para salvar os txt
lingua = 'por'                   # 'por' para português
# ------------------------------------------------

url = 'https://api.ocr.space/parse/image'

# Criar pasta de saída se não existir
if not os.path.exists(pasta_saida):
    os.makedirs(pasta_saida)

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
        texto = resultado['ParsedResults'][0]['ParsedText'].strip()
        # Salvar em txt com mesmo nome da imagem
        nome_txt = os.path.splitext(arquivo)[0] + '.txt'
        caminho_txt = os.path.join(pasta_saida, nome_txt)
        with open(caminho_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.write(texto)
        print(f'Código da imagem {arquivo} salvo em {nome_txt}')
    else:
        print(f'Erro ao processar {arquivo}:', resultado.get('ErrorMessage'))
