"""
Registro de Execução (Etapa: Logging/Observabilidade).

Grava cada interação em formato JSON Lines, incluindo pergunta, fontes usadas,
resposta, timestamp, tempo de resposta e feedback do colaborador.
Os logs ficam em /logs localmente; em produção na OCI, o mesmo arquivo pode ser
sincronizado periodicamente para o OCI Object Storage (ver app/utils/storage.py).
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import LOGS_DIR

LOG_FILE = LOGS_DIR / "interacoes.jsonl"


def registrar_interacao(pergunta: str, resposta: str, fontes: list,
                         tempo_resposta_ms: int, categoria: str = None,
                         usou_fallback: bool = False) -> str:
    """Grava uma interação no log e retorna o id gerado (usado para associar feedback depois)."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    interacao_id = str(uuid.uuid4())
    registro = {
        "id": interacao_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pergunta": pergunta,
        "categoria_detectada": categoria,
        "fontes": fontes,
        "resposta": resposta,
        "tempo_resposta_ms": tempo_resposta_ms,
        "usou_fallback": usou_fallback,
        "feedback": None,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return interacao_id


def registrar_feedback(interacao_id: str, feedback: str):
    """Atualiza o registro de uma interação com o feedback (positivo/negativo).

    Implementação simples por reescrita do arquivo — adequada ao volume de um
    MVP. Para alto volume, trocar por um banco de dados (ex: SQLite ou tabela
    dedicada no Autonomous Database).
    """
    if not LOG_FILE.exists():
        return
    linhas = LOG_FILE.read_text(encoding="utf-8").splitlines()
    novas_linhas = []
    for linha in linhas:
        registro = json.loads(linha)
        if registro["id"] == interacao_id:
            registro["feedback"] = feedback
        novas_linhas.append(json.dumps(registro, ensure_ascii=False))
    LOG_FILE.write_text("\n".join(novas_linhas) + "\n", encoding="utf-8")
