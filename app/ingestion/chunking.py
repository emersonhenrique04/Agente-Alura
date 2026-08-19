"""
Divisão do texto extraído em chunks + atribuição de metadados (Etapa 2, parte final).
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_SIZE, CHUNK_OVERLAP

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def gerar_chunks(texto: str, caminho: Path, categoria: str, responsavel: str = "não definido") -> List[Dict]:
    """Divide o texto em pedaços menores e anexa metadados de origem a cada um.

    Metadados seguem o que foi definido na etapa de coleta/organização de documentos:
    categoria de negócio, arquivo de origem, data de processamento e responsável.
    """
    pedacos = _splitter.split_text(texto)
    agora = datetime.now(timezone.utc).isoformat()

    chunks = []
    for i, pedaco in enumerate(pedacos):
        chunks.append(
            {
                "texto": pedaco,
                "metadados": {
                    "categoria": categoria,
                    "arquivo_origem": caminho.name,
                    "chunk_index": i,
                    "total_chunks": len(pedacos),
                    "data_processamento": agora,
                    "responsavel": responsavel,
                },
            }
        )
    return chunks
