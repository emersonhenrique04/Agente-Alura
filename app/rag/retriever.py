"""
Camada de Recuperação (Etapa 4).

Busca semântica + filtro por metadados + threshold de confiança.
O reranker foi deixado como ponto de extensão (ver comentário abaixo) para
manter o MVP simples sem perder a possibilidade de evoluir a precisão depois.
"""
from typing import List, Dict, Optional

from app.config import TOP_K, SIMILARITY_THRESHOLD
from app.rag.vectorstore import VectorStore


class Retriever:
    def __init__(self, vectorstore: VectorStore):
        self.vectorstore = vectorstore

    def recuperar(self, pergunta: str, categoria: Optional[str] = None) -> List[Dict]:
        """Retorna os trechos mais relevantes para a pergunta, já filtrados por
        confiança mínima (similaridade). Se nada passar do threshold, retorna
        lista vazia — sinal para a camada de geração acionar o fallback."""
        candidatos = self.vectorstore.buscar(pergunta, top_k=TOP_K, categoria=categoria)
        relevantes = [c for c in candidatos if c["similaridade"] >= SIMILARITY_THRESHOLD]

        # Ponto de extensão: aqui entraria um reranker (ex: Cohere Rerank via OCI
        # Generative AI) recebendo `candidatos` e reordenando por relevância real
        # antes de aplicar o corte final. Deixado fora do MVP por simplicidade.

        return relevantes

    def montar_contexto(self, trechos: List[Dict]) -> str:
        """Formata os trechos recuperados em um bloco de texto com citação de fonte,
        pronto para ser inserido no prompt do LLM."""
        blocos = []
        for t in trechos:
            m = t["metadados"]
            fonte = f"[Fonte: {m['arquivo_origem']} | Categoria: {m['categoria']}]"
            blocos.append(f"{fonte}\n{t['texto']}")
        return "\n\n---\n\n".join(blocos)
