"""
Geração de embeddings (Etapa 3: Indexação Vetorial).

Usa OCI Generative AI (modelo Cohere multilingual) por padrão.
Para desenvolvimento local sem credenciais OCI, defina USE_LOCAL_FALLBACK=true
no .env para usar sentence-transformers localmente (mesma interface).
"""
from typing import List

from app.config import (
    USE_LOCAL_FALLBACK,
    LOCAL_EMBED_MODEL,
    OCI_CONFIG_PROFILE,
    OCI_COMPARTMENT_ID,
    OCI_GENAI_ENDPOINT,
    OCI_EMBED_MODEL_ID,
)


class OCIEmbeddings:
    """Wrapper para o serviço de embeddings da OCI Generative AI."""

    def __init__(self):
        import oci

        config = oci.config.from_file(profile_name=OCI_CONFIG_PROFILE)
        self.client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=OCI_GENAI_ENDPOINT,
        )
        self._oci = oci

    def embed(self, textos: List[str]) -> List[List[float]]:
        detalhes = self._oci.generative_ai_inference.models.EmbedTextDetails(
            inputs=textos,
            serving_mode=self._oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=OCI_EMBED_MODEL_ID
            ),
            compartment_id=OCI_COMPARTMENT_ID,
            truncate="END",
        )
        resposta = self.client.embed_text(detalhes)
        return resposta.data.embeddings


class LocalEmbeddings:
    """Fallback local usando sentence-transformers — apenas para desenvolvimento/testes."""

    def __init__(self):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(LOCAL_EMBED_MODEL)

    def embed(self, textos: List[str]) -> List[List[float]]:
        return self.model.encode(textos, show_progress_bar=False).tolist()


def get_embedder():
    """Fábrica: retorna o embedder configurado (OCI por padrão, local em dev)."""
    if USE_LOCAL_FALLBACK:
        return LocalEmbeddings()
    return OCIEmbeddings()
