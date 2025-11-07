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
    """Envia as imagens para o Gemini e processa a resposta JSON."""
    
    contents_parts = []
    
    for file in uploaded_files:
        contents_parts.append(
            types.Part.from_bytes(
                data=file.getvalue(),
                mime_type=file.type,
            )
        )
    
    prompt_final = f"""
    Analise detalhadamente as {len(uploaded_files)} imagens da peça automotiva.

    Instruções Cruciais:
    1.  **CÓDIGO DE PEÇA:** Procure o número de peça nos rótulos, etiquetas ou gravado na própria peça. Use este código como a principal fonte de identificação, mesmo que não seja o 8631A437.
    2.  **EXTRAÇÃO DE DADOS:** Descreva a peça e sua função (Item 1).
    3.  **COMPATIBILIDADE:** Liste modelos e anos de carro compatíveis APENAS se houver alta confiança, citando a fonte (se for pela imagem ou por conhecimento geral).
    4.  **FORMATO:** Retorne a resposta ESTRITAMENTE no formato JSON, seguindo o esquema definido.

    Foco: Garanta que o código de peça e os modelos listados sejam os mais precisos possíveis com base na evidência visual.
    """
    contents_parts.append(prompt_final)

    with st.spinner("🧠 Analisando imagens com Gemini..."):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents_parts,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AnalisePeca,
                )
            )
            json_string = response.text
            
            analise_data = AnalisePeca.model_validate_json(json_string)
            
            db_success = insert_analysis_data(analise_data)
            
            return analise_data, db_success

        except Exception as e:
            st.error(f"❌ Erro durante a análise ou processamento: {e}")
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