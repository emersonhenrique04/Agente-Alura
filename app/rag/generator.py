"""
Geração de Resposta (Etapa 5).

Monta o prompt com o contexto recuperado, chama o LLM (OCI Generative AI) e
aplica o fallback quando nenhum trecho relevante foi encontrado.
"""
from typing import List, Dict, Optional

from app.config import (
    USE_LOCAL_FALLBACK,
    OCI_CONFIG_PROFILE,
    OCI_COMPARTMENT_ID,
    OCI_GENAI_ENDPOINT,
    OCI_LLM_MODEL_ID,
    CONTATOS_AREAS,
)

PROMPT_SISTEMA = """Você é um assistente corporativo interno. Responda a pergunta do \
colaborador usando EXCLUSIVAMENTE as informações do contexto abaixo, extraído de \
documentos internos da empresa.

Regras obrigatórias:
- Responda apenas com base no contexto fornecido, nunca use conhecimento externo.
- Se a informação não estiver no contexto, diga claramente que não encontrou a \
resposta nos documentos disponíveis.
- Sempre cite a fonte (nome do arquivo e categoria) ao final da resposta.
- Seja objetivo e claro.

Contexto:
{contexto}

Pergunta do colaborador: {pergunta}

Resposta:"""


def _mensagem_fallback(categoria: Optional[str]) -> str:
    contato = CONTATOS_AREAS.get(categoria, "a área responsável pelo assunto")
    return (
        "Não encontrei essa informação nos documentos disponíveis. "
        f"Recomendo entrar em contato com {contato} para mais detalhes."
    )


class OCIGenerator:
    def __init__(self):
        import oci

        config = oci.config.from_file(profile_name=OCI_CONFIG_PROFILE)
        self.client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=OCI_GENAI_ENDPOINT,
        )
        self._oci = oci

    def gerar(self, prompt: str) -> str:
        chat_request = self._oci.generative_ai_inference.models.CohereChatRequest(
            message=prompt,
            max_tokens=800,
            temperature=0.2,
        )
        detalhes = self._oci.generative_ai_inference.models.ChatDetails(
            compartment_id=OCI_COMPARTMENT_ID,
            serving_mode=self._oci.generative_ai_inference.models.OnDemandServingMode(
                model_id=OCI_LLM_MODEL_ID
            ),
            chat_request=chat_request,
        )
        resposta = self.client.chat(detalhes)
        return resposta.data.chat_response.text


class LocalGenerator:
    """Fallback simples para desenvolvimento sem credenciais OCI: apenas devolve
    o contexto bruto, sem geração real. Substitua por outra API se preferir
    testar a lógica de prompt sem depender da OCI."""

    def gerar(self, prompt: str) -> str:
        return (
            "[MODO LOCAL - sem chamada real ao LLM]\n"
            "Configure USE_LOCAL_FALLBACK=false e as credenciais OCI para "
            "respostas geradas de verdade.\n\nPrompt que seria enviado:\n" + prompt
        )


def get_generator():
    if USE_LOCAL_FALLBACK:
        return LocalGenerator()
    return OCIGenerator()


def gerar_resposta(pergunta: str, trechos: List[Dict], contexto_formatado: str,
                    categoria: Optional[str] = None) -> Dict:
    """Orquestra a geração: aplica fallback se não há trechos, senão chama o LLM."""
    if not trechos:
        return {
            "resposta": _mensagem_fallback(categoria),
            "fontes": [],
            "usou_fallback": True,
        }

    prompt = PROMPT_SISTEMA.format(contexto=contexto_formatado, pergunta=pergunta)
    generator = get_generator()
    texto_resposta = generator.gerar(prompt)

    fontes = [
        {
            "arquivo": t["metadados"]["arquivo_origem"],
            "categoria": t["metadados"]["categoria"],
            "similaridade": round(t["similaridade"], 3),
        }
        for t in trechos
    ]

    return {"resposta": texto_resposta, "fontes": fontes, "usou_fallback": False}
