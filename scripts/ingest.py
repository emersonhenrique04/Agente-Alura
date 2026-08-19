"""
Pipeline de ingestão inicial (Etapas 1 + 2 + 3): percorre data/documents/<categoria>/,
extrai o texto de cada arquivo suportado, gera chunks com metadados e indexa no
banco vetorial.

Uso:
    python scripts/ingest.py

Rode este script sempre que adicionar, remover ou atualizar documentos.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DOCUMENTS_DIR
from app.ingestion.loaders import extrair_texto, EXTRATORES
from app.ingestion.chunking import gerar_chunks
from app.rag.vectorstore import VectorStore


def main():
    print(f"Iniciando ingestão a partir de: {DOCUMENTS_DIR}")
    vectorstore = VectorStore()

    total_arquivos = 0
    total_chunks = 0

    for categoria_dir in sorted(DOCUMENTS_DIR.iterdir()):
        if not categoria_dir.is_dir():
            continue
        categoria = categoria_dir.name.capitalize()

        for arquivo in sorted(categoria_dir.iterdir()):
            if arquivo.suffix.lower() not in EXTRATORES:
                continue
            print(f"  Processando [{categoria}] {arquivo.name} ...", end=" ")
            try:
                texto = extrair_texto(arquivo)
                if not texto.strip():
                    print("vazio, ignorado.")
                    continue
                chunks = gerar_chunks(texto, arquivo, categoria)
                vectorstore.indexar_chunks(chunks)
                total_arquivos += 1
                total_chunks += len(chunks)
                print(f"OK ({len(chunks)} chunks)")
            except Exception as e:
                print(f"ERRO: {e}")

    print(f"\nIngestão concluída: {total_arquivos} arquivos, {total_chunks} chunks indexados.")
    print(f"Total no índice: {vectorstore.total_chunks()} chunks.")


if __name__ == "__main__":
    main()
