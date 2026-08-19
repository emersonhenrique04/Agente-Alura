"""
Banco vetorial (Etapa 3: Indexação Vetorial).

Usa Chroma com persistência em disco. A escolha do Chroma prioriza simplicidade
e portabilidade: o índice roda dentro do próprio container da aplicação, sem
depender de um serviço de banco de dados externo. Os documentos originais e os
backups do índice são versionados no OCI Object Storage (ver app/utils/storage.py),
o que cumpre o requisito de uso de um serviço OCI nessa camada.

Alternativa possível (mais robusta, 100% OCI): Oracle 23ai Autonomous Database
com Vector Search nativo — ver docs/ARCHITECTURE.md para instruções de migração.
"""
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings

from app.config import VECTOR_DB_DIR
from app.rag.embeddings import get_embedder

_COLLECTION_NAME = "documentos_corporativos"


class VectorStore:
    def __init__(self):
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedder = get_embedder()

    def indexar_chunks(self, chunks: List[Dict]):
        """Gera embeddings para uma lista de chunks e os adiciona ao índice."""
        if not chunks:
            return
        textos = [c["texto"] for c in chunks]
        vetores = self.embedder.embed(textos)
        ids = [
            f"{c['metadados']['arquivo_origem']}_{c['metadados']['chunk_index']}"
            for c in chunks
        ]
        self.collection.upsert(
            ids=ids,
            embeddings=vetores,
            documents=textos,
            metadatas=[c["metadados"] for c in chunks],
        )

    def buscar(self, pergunta: str, top_k: int = 5, categoria: Optional[str] = None) -> List[Dict]:
        """Busca semântica com filtro opcional por categoria (metadado)."""
        vetor_pergunta = self.embedder.embed([pergunta])[0]
        where = {"categoria": categoria} if categoria else None

        resultado = self.collection.query(
            query_embeddings=[vetor_pergunta],
            n_results=top_k,
            where=where,
        )

        candidatos = []
        for i in range(len(resultado["ids"][0])):
            distancia = resultado["distances"][0][i]
            similaridade = 1 - distancia  # Chroma retorna distância de cosseno
            candidatos.append(
                {
                    "texto": resultado["documents"][0][i],
                    "metadados": resultado["metadatas"][0][i],
                    "similaridade": similaridade,
                }
            )
        return candidatos

    def remover_documento(self, arquivo_origem: str):
        """Remove todos os chunks de um arquivo (usado na reindexação/atualização)."""
        self.collection.delete(where={"arquivo_origem": arquivo_origem})

    def total_chunks(self) -> int:
        return self.collection.count()
