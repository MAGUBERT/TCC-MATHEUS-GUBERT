import os
import json
from google import genai
from google.genai import types

# 1. Configuração da API
# O cliente busca automaticamente a chave GEMINI_API_KEY da variável de ambiente
try:
    client = genai.Client()
except Exception as e:
    print("Erro ao inicializar o cliente. Certifique-se de que a variável de ambiente GEMINI_API_KEY está configurada corretamente.")
    print(f"Detalhes do erro: {e}")
    exit()

# 2. Caminhos dos arquivos de imagem
IMAGE_PATH_1 = "peca2.jpeg"
IMAGE_PATH_2 = "peca2baixo.jpeg"

def processar_imagens():
    """
    Carrega as duas imagens, cria um prompt estruturado e chama a API Gemini.
    """
    
    # 3. Função auxiliar para carregar arquivos em bytes
    def load_image_bytes(path, mime_type):
        """Carrega um arquivo de imagem em bytes para a API Gemini."""
        try:
            with open(path, "rb") as f:
                return types.Part.from_bytes(data=f.read(), mime_type=mime_type)
        except FileNotFoundError:
            raise FileNotFoundError(f"Erro: Arquivo não encontrado em {path}")

    # Carregar as imagens (usando 'image/jpeg' como tipo MIME)
    try:
        image_part_1 = load_image_bytes(IMAGE_PATH_1, 'image/jpeg')
        image_part_2 = load_image_bytes(IMAGE_PATH_2, 'image/jpeg')
    except FileNotFoundError as e:
        print(e)
        return

    # 4. Prompt Inteligente e Estrutura de Resposta (Schema JSON)
    # O prompt instrui o modelo exatamente o que extrair e como
    
    prompt_text = (
        "Analise as duas imagens de módulos de freio ABS/peças automotivas. "
        "Extraia todos os números de peça, códigos de dados da bomba e o código QR. "
        "Formate a resposta EXCLUSIVAMENTE como um objeto JSON que segue o esquema."
    )
    
    # Definindo a estrutura JSON esperada (Schema Pydantic para tipagem em Python)
    class ModuloPeca(types.Type):
        """Define a estrutura de dados para uma peça do módulo."""
        nome_peca: str = "Nome da Peça (ex: ATE Controller, Módulo Inferior)"
        numeros_peca: list[str] = "Lista de todos os números de peça principais (ex: 06.2109-6146.3)"
        codigo_qr: str = "O número decodificado do código QR"
        pump_data: str = "O código 'PUMP DATA' ou similar (se presente)"
        
    class ResultadoExtracao(types.Type):
        """A estrutura de nível superior para a resposta."""
        modulos: list[ModuloPeca]

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
            print("\n--- Números de Peça Principais ---\n")
            for modulo in dados_json["modulos"]:
                print(f"Nome: {modulo.get('nome_peca')}")
                print(f"Códigos: {', '.join(modulo.get('numeros_peca', []))}")
                if modulo.get('codigo_qr'):
                    print(f"Código QR: {modulo.get('codigo_qr')}")
                if modulo.get('pump_data'):
                    print(f"Pump Data: {modulo.get('pump_data')}")
                print("-" * 20)
                
    except json.JSONDecodeError:
        print("Erro: A resposta da API não foi um JSON válido.")
        print(f"Resposta bruta: {response.text}")
    except Exception as e:
        print(f"Ocorreu um erro no processamento: {e}")

if __name__ == "__main__":
    processar_imagens()