# Guia de Deploy na OCI (Oracle Cloud Infrastructure)

Este guia assume que você já tem uma conta OCI (o [Always Free Tier](https://www.oracle.com/cloud/free/)
é suficiente para este projeto) e o [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm) instalado.

## 1. Criar o Compartment (opcional, mas recomendado)

Organize os recursos do projeto em um compartment dedicado pelo console OCI:
`Identity & Security → Compartments → Create Compartment`.

## 2. Criar o bucket no Object Storage

```bash
oci os bucket create \
  --compartment-id <SEU_COMPARTMENT_OCID> \
  --name agente-corporativo-docs

oci os bucket create \
  --compartment-id <SEU_COMPARTMENT_OCID> \
  --name agente-corporativo-logs
```

Envie os documentos de exemplo (opcional, a aplicação também lê do disco local
dentro do container):

```bash
oci os object bulk-upload \
  --bucket-name agente-corporativo-docs \
  --src-dir data/documents
```

## 3. Habilitar o OCI Generative AI

No console: `Analytics & AI → Generative AI`. Confirme que o serviço está
disponível na sua região (ex: `sa-saopaulo-1`) e anote o `compartment OCID`
que será usado nas variáveis de ambiente.

## 4. Criar o repositório no OCI Container Registry (OCIR)

```bash
# Não é necessário criar o repo manualmente — o primeiro push já cria.
docker login <regiao-key>.ocir.io -u '<namespace>/<usuario_oci>'
# Senha = Auth Token gerado em Identity → Users → Auth Tokens
```

Build e push da imagem:

```bash
docker build -t <regiao-key>.ocir.io/<namespace>/agente-corporativo:latest .
docker push <regiao-key>.ocir.io/<namespace>/agente-corporativo:latest
```

## 5. Guardar segredos no OCI Vault

```bash
oci vault create --compartment-id <OCID> --display-name agente-corporativo-vault \
  --vault-type DEFAULT

oci kms key create --compartment-id <OCID> --display-name agente-corporativo-key \
  --key-shape '{"algorithm":"AES","length":32}' --endpoint <management-endpoint>
```

Guarde no Vault as variáveis sensíveis (compartment OCID, credenciais etc.) e
referencie-as no deploy do Container Instance.

## 6. Deploy no OCI Container Instances

Pelo console: `Developer Services → Container Instances → Create Container Instance`.

- Imagem: `<regiao-key>.ocir.io/<namespace>/agente-corporativo:latest`
- Porta: `8501`
- Variáveis de ambiente: copie do `.env.example`, com `USE_LOCAL_FALLBACK=false`
  e os valores reais de compartment, endpoint e buckets.
- Shape sugerido: `CI.Standard.E4.Flex` com 1 OCPU / 4 GB (suficiente para o MVP).

Ou via CLI:

```bash
oci container-instances container-instance create \
  --compartment-id <OCID> \
  --display-name agente-corporativo \
  --availability-domain <AD> \
  --shape "CI.Standard.E4.Flex" \
  --shape-config '{"ocpus": 1, "memoryInGBs": 4}' \
  --containers '[{"displayName":"agente-corporativo","imageUrl":"<regiao-key>.ocir.io/<namespace>/agente-corporativo:latest"}]' \
  --vnics '[{"subnetId":"<SUBNET_OCID>","isPublicIpAssigned":true}]'
```

## 7. Rede (VCN)

Se ainda não tiver uma VCN, use o assistente `Networking → Virtual Cloud Networks
→ Start VCN Wizard → Create VCN with Internet Connectivity`, que já cria subnet
pública, internet gateway e route table automaticamente.

## 8. Validar

Após o deploy, o Container Instance recebe um IP público. Acesse
`http://<IP_PUBLICO>:8501` para confirmar que o agente está no ar.

## 9. CI/CD (opcional)

O workflow em `.github/workflows/deploy.yml` builda e envia a imagem para o
OCIR a cada push na branch `main`. Configure os seguintes secrets no GitHub
(`Settings → Secrets and variables → Actions`):

- `OCI_REGION_KEY` (ex: `gru` para São Paulo)
- `OCI_TENANCY_NAMESPACE`
- `OCI_USERNAME`
- `OCI_AUTH_TOKEN`

## 10. Evidência para o README

Depois do deploy funcionando, tire um print (ou grave um vídeo curto) da tela
do Streamlit rodando no IP público, mostrando uma pergunta sendo feita e
respondida com as fontes citadas. Salve em `docs/evidencias/` e referencie no
`README.md` principal.
