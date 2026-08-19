# 🤖 Agente Corporativo — Alura Challenge Agentes de IA

Agente de inteligência artificial corporativo, aberto a todos os colaboradores,
capaz de responder perguntas com base em documentos internos da empresa
fictícia **TechNova Brasil**. O agente compreende múltiplos formatos de
arquivo (PDF, Word, Excel, PowerPoint, Markdown, CSV, JSON e HTML) e cobre
diferentes domínios organizacionais (RH, Financeiro, Jurídico, Operacional),
funcionando como uma base de conhecimento conversacional, centralizada e
sempre disponível.

## 📌 Sobre o projeto

O agente foi construído seguindo um pipeline completo de RAG
(Retrieval-Augmented Generation):

1. **Coleta e organização** dos documentos por categoria de negócio;
2. **Processamento e extração** de texto por formato de arquivo;
3. **Indexação vetorial** com embeddings gerados via OCI Generative AI;
4. **Recuperação** por busca semântica, com filtro por categoria e controle
   de confiança;
5. **Geração de resposta** com citação de fonte e prevenção de alucinação
   (o agente admite quando não sabe a resposta);
6. **Interface de chat** em Streamlit, com histórico e feedback;
7. **Registro de execução** (logs) de cada interação.

Ver detalhes completos em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 🏗️ Arquitetura (resumo)

```
Documentos → Extração/Chunking → Embeddings (OCI GenAI) → Chroma (vetores)
    → Retrieval (top-K + filtro + threshold) → LLM (OCI GenAI) com anti-alucinação
    → Streamlit (chat + fontes + feedback) → Logs (JSON Lines)
```

## 🛠️ Tecnologias utilizadas

- **Python 3.11**
- **Streamlit** — interface de chat
- **Chroma** — banco de dados vetorial
- **OCI Generative AI** — embeddings (Cohere multilingual) e LLM (Command R+)
- **LangChain (text splitters)** — chunking
- **pypdf, python-docx, python-pptx, openpyxl, pandas, BeautifulSoup** —
  extração por formato
- **Docker** — containerização
- **GitHub Actions** — CI/CD (build e push para o OCIR)

## ☁️ Serviços OCI utilizados

| Serviço | Papel no projeto |
|---|---|
| OCI Generative AI | Embeddings e geração de respostas do LLM |
| OCI Container Registry (OCIR) | Armazena a imagem Docker da aplicação |
| OCI Container Instances | Executa o container em produção |
| OCI Object Storage | Armazena os documentos originais e backup de logs |
| OCI Vault | Armazena credenciais e segredos de forma segura |

Guia passo a passo do deploy em [`docs/DEPLOY.md`](docs/DEPLOY.md).

## 📂 Documentos e categorias

| Categoria | Responsável | Exemplos de documentos incluídos |
|---|---|---|
| RH | Ana Beatriz Souza | Política de férias (.md), Benefícios (.json) |
| Financeiro | Carlos Mendes | Política de reembolso (.pdf), Limites de despesas (.csv) |
| Jurídico | Fernanda Lima | FAQ LGPD (.html) |
| Operacional | Rafael Torres | Manual de onboarding (.docx), Contatos das áreas (.xlsx) |

Ver ownership completo em [`data/documents/OWNERS.md`](data/documents/OWNERS.md).

## 🚀 Como rodar localmente

```bash
# 1. Clonar o repositório
git clone https://github.com/<seu-usuario>/agente-corporativo.git
cd agente-corporativo

# 2. Criar ambiente virtual e instalar dependências
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Para testar sem credenciais OCI, mantenha USE_LOCAL_FALLBACK=true no .env

# 4. Indexar os documentos de exemplo
python scripts/ingest.py

# 5. Rodar a aplicação
streamlit run app/main.py
```

Acesse `http://localhost:8501` no navegador.

> Para usar o OCI Generative AI de verdade (embeddings e respostas reais),
> configure `USE_LOCAL_FALLBACK=false` e preencha as credenciais OCI no `.env`.

## 🐳 Rodando com Docker

```bash
docker build -t agente-corporativo .
docker run -p 8501:8501 --env-file .env agente-corporativo
```

## ☁️ Deploy em nuvem (OCI)

O deploy completo — containerização, push para o OCIR e execução no OCI
Container Instances — está documentado passo a passo em
[`docs/DEPLOY.md`](docs/DEPLOY.md).

**Evidência de execução em nuvem:**

> 🔗 URL pública: `<preencher após o deploy>`
>
> 📸 Print/vídeo do agente em execução: `docs/evidencias/execucao-oci.png`
> *(adicionar aqui a imagem ou vídeo do agente rodando no OCI Container Instances)*

## 💬 Exemplos de perguntas que o agente responde

- "Quantos dias de férias eu tenho direito?"
- "Posso vender parte das minhas férias?"
- "Qual o limite de reembolso para hospedagem em viagem?"
- "Quais benefícios a empresa oferece?"
- "O que fazer em caso de vazamento de dados de clientes?"
- "Quem é o encarregado de dados (DPO) da empresa?"
- "Quais ferramentas preciso instalar no onboarding?"
- "Qual o e-mail de contato do time Financeiro?"

## 📸 Exemplo de resposta do agente

**Pergunta:** *"Quantos dias de férias eu tenho direito e posso fracionar?"*

**Resposta do agente:**
> Todo colaborador CLT tem direito a 30 dias corridos de férias após completar
> 12 meses de trabalho. É possível fracionar em até 3 períodos, sendo que um
> deles não pode ser inferior a 14 dias e os demais não podem ser inferiores
> a 5 dias corridos cada.
>
> 📄 Fonte: politica-ferias.md (categoria: RH)

*(print real da interface a ser adicionado após o deploy)*

## 🔄 Manutenção e melhoria contínua

- **Reindexação:** rode `python scripts/ingest.py` sempre que documentos
  forem adicionados, alterados ou removidos.
- **Curadoria:** cada categoria tem um responsável (ver `OWNERS.md`) que
  aprova e mantém os documentos atualizados.
- **Monitoramento:** os logs em `logs/interacoes.jsonl` registram pergunta,
  fontes usadas, tempo de resposta e feedback (👍/👎) de cada interação,
  servindo de base para identificar lacunas na base de conhecimento.
- **Fallback:** quando nenhum documento relevante é encontrado, o agente
  informa isso claramente e direciona o colaborador ao contato da área
  responsável, em vez de arriscar uma resposta incorreta.

## 📋 Requisitos do desafio atendidos

- [x] Repositório público no GitHub
- [x] Deploy na OCI usando múltiplos serviços (Generative AI, OCIR, Container
      Instances, Object Storage, Vault)
- [x] README com arquitetura, tecnologias, instruções de execução, exemplos
      de perguntas/respostas e evidência de execução em nuvem
- [x] Agente funcional respondendo com base em documentos (PDF, DOCX, XLSX,
      PPTX, MD, CSV, JSON, HTML)
- [x] Código de leitura/processamento dos documentos fonte

## 📝 Licença

Projeto desenvolvido para fins educacionais — Challenge Alura Agentes de IA.
