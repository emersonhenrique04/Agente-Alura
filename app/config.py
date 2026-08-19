"""
Configurações centrais do Agente Corporativo.
Todas as credenciais sensíveis vêm de variáveis de ambiente (nunca hardcoded).
Em produção na OCI, recomenda-se popular essas variáveis via OCI Vault.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Diretórios ---
BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
VECTOR_DB_DIR = BASE_DIR / "data" / "vectorstore"
LOGS_DIR = BASE_DIR / "logs"

# --- Categorias de negócio suportadas ---
CATEGORIAS = ["RH", "Financeiro", "Juridico", "Operacional"]

# --- Contatos por área (usado no fallback quando o agente não encontra resposta) ---
CONTATOS_AREAS = {
    "RH": "rh@empresa.com.br",
    "Financeiro": "financeiro@empresa.com.br",
    "Juridico": "juridico@empresa.com.br",
    "Operacional": "operacoes@empresa.com.br",
}

# --- Chunking ---
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# --- Recuperação (retrieval) ---
TOP_K = 5
SIMILARITY_THRESHOLD = 0.35  # abaixo disso, o agente assume que não sabe a resposta

# --- OCI Generative AI (LLM + Embeddings) ---
OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID", "")
OCI_GENAI_ENDPOINT = os.getenv(
    "OCI_GENAI_ENDPOINT",
    "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com",
)
OCI_EMBED_MODEL_ID = os.getenv("OCI_EMBED_MODEL_ID", "cohere.embed-multilingual-v3.0")
OCI_LLM_MODEL_ID = os.getenv("OCI_LLM_MODEL_ID", "cohere.command-r-plus")

# --- Modo local (fallback sem OCI, útil para desenvolvimento/testes) ---
# Se USE_LOCAL_FALLBACK=true, usa sentence-transformers localmente em vez da OCI.
# Isso NÃO substitui o requisito de usar OCI no deploy final, é só para dev.
USE_LOCAL_FALLBACK = os.getenv("USE_LOCAL_FALLBACK", "false").lower() == "true"
LOCAL_EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# --- OCI Object Storage (armazenamento dos documentos originais) ---
OCI_OBJECT_STORAGE_NAMESPACE = os.getenv("OCI_OBJECT_STORAGE_NAMESPACE", "")
OCI_OBJECT_STORAGE_BUCKET = os.getenv("OCI_OBJECT_STORAGE_BUCKET", "agente-corporativo-docs")
OCI_OBJECT_STORAGE_LOGS_BUCKET = os.getenv("OCI_OBJECT_STORAGE_LOGS_BUCKET", "agente-corporativo-logs")
