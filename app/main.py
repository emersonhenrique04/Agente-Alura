"""
Interface do Agente Corporativo (Etapa: Interface).

Chat web simples em Streamlit com:
- Aviso de que é um agente de IA
- Histórico de conversa da sessão
- Exibição das fontes citadas em cada resposta
- Botões de feedback (👍/👎)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.config import CATEGORIAS
from app.rag.vectorstore import VectorStore
from app.rag.retriever import Retriever
from app.rag.generator import gerar_resposta
from app.utils.logging import registrar_interacao, registrar_feedback

st.set_page_config(page_title="Agente Corporativo", page_icon="🤖", layout="centered")


@st.cache_resource
def carregar_pipeline():
    vectorstore = VectorStore()
    retriever = Retriever(vectorstore)
    return vectorstore, retriever


vectorstore, retriever = carregar_pipeline()

st.title("🤖 Agente Corporativo")
st.caption(
    "Você está conversando com um **agente de inteligência artificial**, não uma "
    "pessoa. As respostas são baseadas nos documentos internos da empresa."
)

with st.sidebar:
    st.header("Filtros")
    categoria_selecionada = st.selectbox(
        "Restringir busca a uma categoria (opcional)",
        ["Todas"] + CATEGORIAS,
    )
    st.divider()
    st.metric("Chunks indexados", vectorstore.total_chunks())
    st.caption("Rode `python scripts/ingest.py` para (re)indexar os documentos.")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

for i, msg in enumerate(st.session_state.mensagens):
    with st.chat_message(msg["role"]):
        st.markdown(msg["conteudo"])
        if msg["role"] == "assistant" and msg.get("fontes"):
            with st.expander("📄 Fontes utilizadas"):
                for fonte in msg["fontes"]:
                    st.markdown(
                        f"- **{fonte['arquivo']}** (categoria: {fonte['categoria']}, "
                        f"relevância: {fonte['similaridade']})"
                    )
        if msg["role"] == "assistant" and not msg.get("feedback_enviado"):
            col1, col2, _ = st.columns([1, 1, 8])
            if col1.button("👍", key=f"up_{i}"):
                registrar_feedback(msg["interacao_id"], "positivo")
                st.session_state.mensagens[i]["feedback_enviado"] = True
                st.rerun()
            if col2.button("👎", key=f"down_{i}"):
                registrar_feedback(msg["interacao_id"], "negativo")
                st.session_state.mensagens[i]["feedback_enviado"] = True
                st.rerun()

pergunta = st.chat_input("Digite sua pergunta sobre políticas, processos, RH, financeiro...")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "conteudo": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    categoria_filtro = None if categoria_selecionada == "Todas" else categoria_selecionada

    with st.chat_message("assistant"):
        with st.spinner("Buscando nos documentos..."):
            inicio = time.time()
            trechos = retriever.recuperar(pergunta, categoria=categoria_filtro)
            contexto = retriever.montar_contexto(trechos)
            resultado = gerar_resposta(pergunta, trechos, contexto, categoria=categoria_filtro)
            tempo_ms = int((time.time() - inicio) * 1000)

            interacao_id = registrar_interacao(
                pergunta=pergunta,
                resposta=resultado["resposta"],
                fontes=resultado["fontes"],
                tempo_resposta_ms=tempo_ms,
                categoria=categoria_filtro,
                usou_fallback=resultado["usou_fallback"],
            )

        st.markdown(resultado["resposta"])
        if resultado["fontes"]:
            with st.expander("📄 Fontes utilizadas"):
                for fonte in resultado["fontes"]:
                    st.markdown(
                        f"- **{fonte['arquivo']}** (categoria: {fonte['categoria']}, "
                        f"relevância: {fonte['similaridade']})"
                    )

    st.session_state.mensagens.append(
        {
            "role": "assistant",
            "conteudo": resultado["resposta"],
            "fontes": resultado["fontes"],
            "interacao_id": interacao_id,
            "feedback_enviado": False,
        }
    )
    st.rerun()
