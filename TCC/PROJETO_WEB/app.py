import streamlit as st
from google import genai
from google.genai import types
from core.config import SETTINGS
from core.models import AnalisePeca
from core.database import insert_analysis_data, supabase_client

supabase_enabled = True if supabase_client else False

if not SETTINGS.GEMINI_API_KEY:
    st.error("🚨 ERRO: A chave GEMINI_API_KEY não está configurada no arquivo .env.")
    st.stop()

client = genai.Client(api_key=SETTINGS.GEMINI_API_KEY)


def display_results(analise_data: AnalisePeca, supabase_success: bool):
    """Exibe os resultados da análise na página."""
    st.subheader("✅ Análise Concluída")
    
    st.markdown("---")
    st.info(f"**Descrição e Função da Peça:**\n{analise_data.descricao_peca}")

    st.markdown("#### Tabela de Compatibilidade e Códigos")
    
    data_for_table = [item.model_dump() for item in analise_data.compatibilidade_lista]
    st.dataframe(data_for_table, use_container_width=True)

    if supabase_success:
        st.success(f"Dados inseridos com sucesso na tabela '{SETTINGS.SUPABASE_TABLE}' do Supabase!")
    elif supabase_enabled:
        st.warning("⚠️ Dados não foram inseridos no Supabase. Verifique logs e permissões de RLS.")
    else:
        st.info("A inserção no Supabase está desativada (falha na conexão ou configuração).")


def run_gemini_analysis(uploaded_files):
    """Executa a análise em duas etapas: Busca na Web (PRO) e Estruturação JSON (PRO)."""
    
    contents_parts_busca = [] 
    contents_parts_json = []  

    for file in uploaded_files:
        part = types.Part.from_bytes(data=file.getvalue(), mime_type=file.type)
        contents_parts_busca.append(part)
        contents_parts_json.append(part)
        
    prompt_busca = f"""
    Analise as {len(uploaded_files)} imagens para identificar o código de peça automotiva (olhe rótulos ou gravações). 
    Em seguida, **USE A FERRAMENTA DE BUSCA** com o código EXATO que você encontrou para pesquisar a lista MAIS PRECISA de modelos e anos de carro compatíveis e a descrição detalhada da peça. 
    Retorne o resultado COMPLETO como **TEXTO LIVRE e DETALHADO**. Inclua explicitamente o código de peça, a descrição e a lista de compatibilidade que encontrou. Não use o formato JSON nesta etapa.
    """
    contents_parts_busca.append(prompt_busca)

    st.info("🧠 Etapa 1/2: Analisando imagens com Gemini-Pro e pesquisando compatibilidade na Web...")
    try:
        response_busca = client.models.generate_content(
            model='gemini-2.5-pro', 
            contents=contents_parts_busca,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}], 
            )
        )
        busca_result_text = response_busca.text
        
        # Opcional: Mostrar o resultado da busca para debug
        # st.markdown("##### Resultado Bruto da Busca:")
        # st.code(busca_result_text, language='markdown') 
        
    except Exception as e:
        st.error(f"❌ Erro na Etapa 1 (Busca na Web). Verifique se as imagens são claras e se a API Key está correta: {e}")
        return None, False


    prompt_json = f"""
    Com base na seguinte análise detalhada e resultados de pesquisa obtidos (que estão abaixo da linha):
    
    --- INFORMAÇÕES BRUTAS DA BUSCA ---
    {busca_result_text}
    --- FIM DAS INFORMAÇÕES BRUTAS ---
    
    Converta estas informações em um objeto ESTRITAMENTE no formato JSON, seguindo o esquema Pydantic (AnalisePeca).
    A descrição da peça deve ser o campo 'descricao_peca'.
    A lista de compatibilidade e códigos deve ser o campo 'compatibilidade_lista'.
    NÃO use a ferramenta de busca e NUNCA adicione texto fora do JSON.
    """
    contents_parts_json.append(prompt_json)

    st.info("⚙️ Etapa 2/2: Estruturando o resultado (com Gemini-Pro) para o formato JSON...")
    try:
        response_json = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=contents_parts_json,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalisePeca,
            )
        )
        json_string = response_json.text

        analise_data = AnalisePeca.model_validate_json(json_string)
        db_success = insert_analysis_data(analise_data)

        return analise_data, db_success

    except Exception as e:
        st.error(f"❌ Erro na Etapa 2 (Estruturação JSON). O JSON retornado pelo modelo PRO pode ser inválido: {e}")
        st.code(f"JSON retornado (verifique o formato): {json_string}", language='json')
        return None, False
st.set_page_config(
    page_title="AutoPart Analyzer com Gemini e Supabase",
    layout="wide"
)

st.title("🔩 AutoPart Analyzer (AI)")
st.markdown("Use a IA do Gemini para analisar imagens de peças, extrair dados estruturados e salvar no banco de dados.")

uploaded_files = st.file_uploader(
    "📤 Faça upload de uma ou mais fotos da peça (JPG/PNG)", 
    type=SETTINGS.ALLOWED_EXTENSIONS, 
    accept_multiple_files=True
)

if uploaded_files:
    
    st.markdown(f"**Imagens Carregadas ({len(uploaded_files)}):**")
    cols = st.columns(min(len(uploaded_files), 5)) 
    for i, file in enumerate(uploaded_files):
        cols[i % 5].image(file, caption=file.name, use_column_width=True)
    
    st.divider()
    
    if st.button("Analisar Peça e Salvar Dados", type="primary"):
        
        analysis_result, db_success = run_gemini_analysis(uploaded_files)
        
        if analysis_result:
            display_results(analysis_result, db_success)