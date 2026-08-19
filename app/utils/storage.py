"""
Integração com OCI Object Storage.

Usado para:
1) Guardar os documentos originais (fonte "oficial", em vez de depender só do
   disco local do container);
2) Fazer backup periódico dos logs de interação.

Este módulo é opcional para rodar o projeto localmente (a aplicação funciona
lendo de data/documents/ direto do disco), mas é usado no processo de deploy
para sincronizar com a nuvem.
"""
from pathlib import Path

from app.config import OCI_CONFIG_PROFILE, OCI_OBJECT_STORAGE_NAMESPACE, OCI_OBJECT_STORAGE_BUCKET


def _get_client():
    import oci

    config = oci.config.from_file(profile_name=OCI_CONFIG_PROFILE)
    return oci.object_storage.ObjectStorageClient(config)


def upload_arquivo(caminho_local: Path, nome_objeto: str, bucket: str = None):
    """Envia um arquivo para o OCI Object Storage."""
    client = _get_client()
    bucket = bucket or OCI_OBJECT_STORAGE_BUCKET
    with open(caminho_local, "rb") as f:
        client.put_object(
            namespace_name=OCI_OBJECT_STORAGE_NAMESPACE,
            bucket_name=bucket,
            object_name=nome_objeto,
            put_object_body=f,
        )


def listar_arquivos(bucket: str = None, prefixo: str = ""):
    """Lista os objetos disponíveis em um bucket (usado para sincronizar novos documentos)."""
    client = _get_client()
    bucket = bucket or OCI_OBJECT_STORAGE_BUCKET
    resposta = client.list_objects(
        namespace_name=OCI_OBJECT_STORAGE_NAMESPACE,
        bucket_name=bucket,
        prefix=prefixo,
    )
    return [obj.name for obj in resposta.data.objects]


def baixar_arquivo(nome_objeto: str, destino_local: Path, bucket: str = None):
    """Baixa um objeto do Object Storage para o disco local."""
    client = _get_client()
    bucket = bucket or OCI_OBJECT_STORAGE_BUCKET
    resposta = client.get_object(
        namespace_name=OCI_OBJECT_STORAGE_NAMESPACE,
        bucket_name=bucket,
        object_name=nome_objeto,
    )
    destino_local.parent.mkdir(parents=True, exist_ok=True)
    with open(destino_local, "wb") as f:
        for chunk in resposta.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)
