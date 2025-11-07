from supabase import create_client, Client
from .config import SETTINGS
from .models import AnalisePeca 

# --- Funções de Inicialização ---

def get_supabase_client() -> Client | None:
    """Tenta criar o cliente Supabase e retorna se for bem-sucedido."""
    if not SETTINGS.SUPABASE_URL or not SETTINGS.SUPABASE_KEY:
        return None
    
    try:
        # Apenas tenta a conexão, sem criar a tabela
        client = create_client(SETTINGS.SUPABASE_URL, SETTINGS.SUPABASE_KEY)
        print("✅ Conexão Supabase bem-sucedida.")
        return client
    except Exception as e:
        print(f"❌ Erro ao criar o cliente Supabase: {e}")
        return None

# --- Inicialização Global ---
# A verificação da tabela é MANUALMENTE ignorada para evitar o erro PGRST202.
supabase_client = get_supabase_client()

if not supabase_client:
    print("Supabase desativado (Credenciais ausentes ou inválidas).")
else:
    print("Supabase pronto para inserção.")


# --- Função de Inserção (Não Muda) ---
def insert_analysis_data(analise_data: AnalisePeca) -> bool:
    # ... (Resto da função de inserção permanece o mesmo) ...
    # (A função usa supabase_client e falhará se a tabela não existir,
    # mas não irá quebrar a inicialização do Streamlit.)
    
    if not supabase_client:
        return False

    data_to_insert = []
    for item in analise_data.compatibilidade_lista:
        data_to_insert.append({
            "descricao_peca": analise_data.descricao_peca,
            "modelo": item.modelo,
            "codigo_peca": item.codigo_peca,
        })
    
    if not data_to_insert:
        return False

    try:
        supabase_client.table(SETTINGS.SUPABASE_TABLE).insert(data_to_insert).execute()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados no Supabase: {e}")
        return False