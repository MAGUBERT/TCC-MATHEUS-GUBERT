import os
import requests
import re
from PIL import Image, ImageEnhance, ImageFilter

api_key = 'K83625664488957'      
pasta_imagens = 'imagens/'       
pasta_saida = 'txt_codigos/'   
pasta_processadas = 'pecas_processadas/'  
lingua = 'por'        
fator_redimensionamento = 2            

url = 'https://api.ocr.space/parse/image'

for pasta in [pasta_saida, pasta_processadas]:
    if not os.path.exists(pasta):
        os.makedirs(pasta)

arquivos = [f for f in os.listdir(pasta_imagens) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

for arquivo in arquivos:
    caminho = os.path.join(pasta_imagens, arquivo)

    img = Image.open(caminho)
    #img = img.convert('L')  
    img = img.filter(ImageFilter.MedianFilter()) 
    largura, altura = img.size
    img = img.resize((largura * fator_redimensionamento, altura * fator_redimensionamento), Image.LANCZOS)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)  
    #enhancer = ImageEnhance.Sharpness(img)
    #img = enhancer.enhance(2)  
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(2)

    caminho_proc = os.path.join(pasta_processadas, arquivo)
    img.save(caminho_proc)
    print(f"Imagem foi salvada em: {caminho_proc}")

    with open(caminho_proc, 'rb') as f:
        payload = {
            'apikey': api_key,
            'language': lingua,
            'OCREngine': 2,
            'isOverlayRequired': False
        }
        files = {'file': f}
        response = requests.post(url, data=payload, files=files)

    resultado = response.json()
    
    if not resultado['IsErroredOnProcessing']:
        texto_ocr = resultado['ParsedResults'][0]['ParsedText'].strip().upper()
        codigos = re.findall(r'\b[A-Z0-9\-]{5,15}\b', texto_ocr)

        texto = "\n".join(codigos)

        nome_txt = os.path.splitext(arquivo)[0] + '.txt'
        caminho_txt = os.path.join(pasta_saida, nome_txt)
        with open(caminho_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.write(texto)
        print(f'Código da imagem {arquivo} salvo em {nome_txt}')
    else:
        print(f'Erro ao processar {arquivo}:', resultado.get('ErrorMessage'))
