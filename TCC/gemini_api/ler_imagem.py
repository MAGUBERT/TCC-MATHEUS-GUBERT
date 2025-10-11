import os
import json
from google import genai
from google.genai import types

# 1. Configuração da API
# INSERIR SUA CHAVE DE API AQUI (Ex: "AIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0E_AQUI")
# É altamente recomendado usar variáveis de ambiente, mas para teste, você pode inserir a chave aqui.
API_KEY = "AIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0" 

try:
    # O cliente será inicializado com a chave fornecida ou tentará usar a variável de ambiente GEMINI_API_KEY
    client = genai.Client(api_key=API_KEY if API_KEY != "AIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0" else None)
    
    # Se a chave não for fornecida e não estiver na variável de ambiente,
    # a inicialização falhará e o bloco 'except' será executado.
    if not client._client._api_key:
        raise ValueError("Chave de API não configurada.")
        
except Exception as e:
    print("-------------------------------------------------------------------------------------------------")
    print("ERRO DE CONFIGURAÇÃO: Certifique-se de que a variável 'API_KEY' no script está correta ou que a ")
    print("variável de ambiente GEMINI_API_KEY está configurada.")
    print(f"Detalhes do erro: {e}")
    print("-------------------------------------------------------------------------------------------------")
    exit()

# 2. Caminhos dos arquivos de imagem
# Certifique-se de que esses arquivos (peca2.jpeg e peca2baixo.jpeg) estão no mesmo diretório do script.
IMAGE_PATH_1 = "peca2.jpeg"
IMAGE_PATH_2 = "peca2baixo.jpeg"

# 4. Estrutura de Resposta (Schema JSON) - Definida GLOBALMENTE, FORA das funções
# Usamos a tipagem padrão do Python para definir o esquema.
class ModuloPeca(types.Type):
    """Define a estrutura de dados para uma peça do módulo ABS."""
    nome_peca: str
    numeros_peca: list[str]
    codigo_qr: str
    pump_data: str

class ResultadoExtracao(types.Type):
    """A estrutura de nível superior para a resposta, contendo a lista de módulos."""
    modulos: list[ModuloPeca]


def processar_imagens():
    """
    Carrega as imagens, define o prompt, chama a API Gemini e processa a resposta.
    """
    
    # 3. Função auxiliar para carregar arquivos em bytes
    def load_image_bytes(path, mime_type):
        """Carrega um arquivo de imagem em bytes para a API Gemini."""
        try:
            with open(path, "rb") as f:
                return types.Part.from_bytes(data=f.read(), mime_type=mime_type)
        except FileNotFoundError:
            # Lança um erro customizado para avisar o usuário que o arquivo não existe
            raise FileNotFoundError(f"Erro: Arquivo não encontrado em {path}. Verifique se a imagem está no mesmo diretório.")

    # Carregar as imagens (usando 'image/jpeg' como tipo MIME)
    try:
        image_part_1 = load_image_bytes(IMAGE_PATH_1, 'image/jpeg')
        image_part_2 = load_image_bytes(IMAGE_PATH_2, 'image/jpeg')
    except FileNotFoundError as e:
        print(e)
        return

    # Prompt Inteligente
    prompt_text = (
        "Analise as duas imagens de módulos de freio ABS/peças automotivas. "
        "Extraia todos os números de peça, códigos de dados da bomba e o código QR de cada módulo. "
        "Formate a resposta EXCLUSIVAMENTE como um objeto JSON que segue o esquema 'ResultadoExtracao'. "
        "Garanta que todos os campos estejam preenchidos com os dados extraídos das imagens. "
        "Tente adivinhar o 'nome_peca' com base no texto encontrado (ex: 'ATE Controller', 'Bloco de Válvulas')."
    )

    # 5. Envio para a API
    print(f"Enviando {IMAGE_PATH_1} e {IMAGE_PATH_2} para a API Gemini...")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Modelo rápido e eficiente para tarefas de visão
        contents=[
            image_part_1,  # Primeira imagem
            image_part_2,  # Segunda imagem
            prompt_text    # O prompt de instrução
        ],
        config=types.GenerateContentConfig(
            # Esta configuração força a saída a ser um JSON válido
            response_mime_type="application/json",
            response_schema=ResultadoExtracao,
        ),
    )

    # 6. Processamento da Resposta
    print("\n--- Resultado da Extração (JSON) ---\n")
    try:
        # A resposta de texto é uma string JSON, a carregamos como um objeto Python
        dados_json = json.loads(response.text)
        print(json.dumps(dados_json, indent=4, ensure_ascii=False))
        
        # Exemplo de acesso aos dados extraídos
        if dados_json.get("modulos"):
            print("\n--- Resumo dos Números de Peça ---\n")
            for modulo in dados_json["modulos"]:
                print(f"PEÇA: {modulo.get('nome_peca', 'Não especificado')}")
                print(f"Números: {', '.join(modulo.get('numeros_peca', ['Nenhum']))}")
                if modulo.get('codigo_qr'):
                    print(f"Cód. QR: {modulo.get('codigo_qr')}")
                if modulo.get('pump_data'):
                    print(f"Pump Data: {modulo.get('pump_data')}")
                print("-" * 20)
                
    except json.JSONDecodeError:
        print("-------------------------------------------------------------------------------------------------")
        print("ERRO DE PROCESSAMENTO: A API não retornou um JSON válido. Isso pode ser um erro temporário.")
        print(f"Resposta bruta (para inspeção): {response.text}")
        print("-------------------------------------------------------------------------------------------------")
    except Exception as e:
        print(f"Ocorreu um erro inesperado no processamento dos dados: {e}")

if __name__ == "__main__":
    processar_imagens()
