# Arquitetura da Solução

```
 Documentos (PDF, DOCX, XLSX, PPTX, MD, CSV, JSON, HTML)
         │
         ▼
 [1] Coleta e Organização  →  data/documents/<categoria>/ + OWNERS.md
         │
         ▼
 [2] Processamento e Extração  →  app/ingestion/loaders.py
         │   (extração por formato → limpeza → chunking → metadados)
         ▼
 [3] Indexação Vetorial  →  app/rag/embeddings.py + app/rag/vectorstore.py
         │   (OCI Generative AI embeddings → Chroma persistente)
         ▼
 [4] Recuperação (Retrieval)  →  app/rag/retriever.py
         │   (busca semântica top-K + filtro por categoria + threshold)
         ▼
 [5] Geração de Resposta  →  app/rag/generator.py
         │   (prompt anti-alucinação + OCI Generative AI LLM + fallback)
         ▼
 [6] Interface  →  app/main.py (Streamlit)
         │
         ▼
 [7] Logging  →  app/utils/logging.py (JSON Lines, feedback 👍/👎)
```

## Por que essas escolhas

- **Chroma** como banco vetorial: roda embutido no próprio container, sem
  infraestrutura extra — prioriza simplicidade para o escopo do challenge.
  Alternativa documentada: migrar para Oracle 23ai (Autonomous Database) com
  Vector Search nativo, que também resolveria o requisito OCI sozinho.
- **OCI Generative AI** para embeddings e LLM: cumpre o requisito de uso de
  serviço OCI diretamente no núcleo do pipeline de IA, não apenas na infra.
- **Streamlit**: interface simples e funcional, como recomendado no desafio,
  sem necessidade de front-end profissional.
- **Threshold de similaridade** em vez de reranker: reduz alucinação com baixo
  custo de implementação; o reranker fica documentado como ponto de evolução.

## Serviços OCI utilizados

| Serviço | Papel |
|---|---|
| OCI Generative AI | Embeddings (Cohere multilingual) e geração de respostas (Command R+) |
| OCI Container Registry (OCIR) | Armazenamento da imagem Docker da aplicação |
| OCI Container Instances | Execução do container em produção |
| OCI Object Storage | Armazenamento dos documentos originais e backup de logs |
| OCI Vault | Armazenamento seguro de credenciais e segredos |

## Estrutura do repositório

```
agente-corporativo/
├── app/
│   ├── main.py                # Interface Streamlit
│   ├── config.py               # Configurações centrais
│   ├── ingestion/
│   │   ├── loaders.py          # Extração por formato de arquivo
│   │   └── chunking.py         # Divisão em chunks + metadados
│   ├── rag/
│   │   ├── embeddings.py       # Geração de embeddings (OCI/local)
│   │   ├── vectorstore.py      # Wrapper do Chroma
│   │   ├── retriever.py        # Busca semântica + filtro + threshold
│   │   └── generator.py        # Prompt + chamada ao LLM + fallback
│   └── utils/
│       ├── logging.py          # Log estruturado de interações
│       └── storage.py          # Integração com OCI Object Storage
├── data/documents/<categoria>/ # Documentos fonte, organizados por categoria
├── scripts/ingest.py           # Pipeline de ingestão/reindexação
├── docs/                       # Documentação estendida (este arquivo, deploy)
├── logs/interacoes.jsonl       # Log de execução (gerado em runtime)
├── Dockerfile
├── requirements.txt
└── .github/workflows/deploy.yml
```
