# B3 Scrapper AWS Lambda

## Descrição

Sistema automatizado para coleta diária de dados do índice IBOVESPA da B3 (Brasil, Bolsa, Balcão), utilizando AWS Lambda, S3 e EventBridge. Os dados são extraídos via API da B3, processados com pandas e armazenados em formato Parquet no S3.

## Funcionalidades

- 📊 **Extração de dados**: Coleta dados do IBOVESPA via API da B3
- 🔄 **Processamento**: Converte dados para DataFrame pandas
- 💾 **Armazenamento**: Salva em formato Parquet no S3
- ⏰ **Agendamento**: Execução automática diária às 19:00 BRT
- 🏗️ **Infraestrutura como código**: Provisionamento via Terraform
- 📦 **Build automatizado**: Script Python para empacotamento

## Estrutura do Projeto

```
├── src/                        # Código fonte da Lambda
│   ├── lambda_handler.py       # Handler principal da Lambda
│   ├── extractor.py           # Classe principal de extração
│   ├── scrapper.py            # Cliente da API B3
│   └── base64_decoder.py      # Utilitário para codificação Base64
├── build/                      # Arquivos de build (gerados)
│   ├── build.py               # Script de build automatizado
│   ├── lambda.zip             # Código da Lambda empacotado
│   └── layers/                # Lambda Layers
│       ├── layer_pandas.zip   # Layer do pandas (~38MB)
│       ├── layer_pyarrow.zip  # Layer do pyarrow (~26MB)
│       └── layer_requests.zip # Layer do requests (~1MB)
├── infra/                      # Terraform
│   ├── lambda/                # Infraestrutura da Lambda
│   │   ├── main.tf            # Recursos principais
│   │   ├── variables.tf       # Variáveis configuráveis
│   │   └── outputs.tf         # Outputs do Terraform
│   └── s3/                    # Infraestrutura do S3
│       ├── main.tf            # Bucket S3
│       ├── variables.tf       # Variáveis do S3
│       └── outputs.tf         # Outputs do S3
├── requirements.txt            # Dependências Python
└── README.md                  # Este arquivo
```

## Dependências

### Python
- `pandas`: Manipulação de dados
- `pyarrow`: Engine para formato Parquet
- `requests`: Cliente HTTP para API da B3
- `boto3`: SDK AWS (já disponível no runtime da Lambda)

### AWS
- Lambda (Python 3.12)
- S3
- EventBridge (CloudWatch Events)
- IAM

## Configuração

### Variáveis de Ambiente

A Lambda utiliza as seguintes variáveis de ambiente:

- `BUCKET_NAME`: Nome do bucket S3 para armazenamento
- `B3_API_URL`: URL da API da B3 (padrão: `https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/`)

### Variáveis do Terraform

#### infra/lambda/variables.tf
- `region`: Região AWS (padrão: `us-east-1`)
- `bucket_name`: Nome do bucket S3 (padrão: `861115334572-raw`)
- `B3_URL`: URL da API B3

#### infra/s3/variables.tf
- `bucket_name`: Nome do bucket S3

## Provisionamento

### 1. Build Automatizado

Execute o script de build para empacotar o código e criar as layers:

```bash
python build/build.py
```

O script irá:
- Criar uma layer separada para cada dependência do `requirements.txt`
- Ignorar dependências já disponíveis no runtime da Lambda (boto3, etc.)
- Gerar `build/lambda.zip` com o código da Lambda
- Gerar layers em `build/layers/`

### 2. Provisionar o S3

```bash
cd infra/s3
terraform init
terraform apply -var="bucket_name=seu-bucket-name"
```

### 3. Provisionar a Lambda

```bash
cd infra/lambda
terraform init
terraform apply -var="bucket_name=seu-bucket-name"
```

## Execução

### Execução Automática
- A Lambda é executada diariamente às 19:00 BRT (22:00 UTC)
- Configurada via EventBridge (CloudWatch Events)

### Execução Manual
```bash
# Teste local
cd src
python lambda_handler.py

# Via AWS CLI
aws lambda invoke --function-name b3_scrapper output.json
```

## Formato dos Dados

### Entrada (API B3)
- Payload: `{"language":"pt-br","index":"IBOV","segment":"1"}`
- Codificação: Base64
- Endpoint: GET com payload codificado na URL

### Saída (S3)
- Formato: Parquet
- Estrutura: `s3://bucket/{YYYY-MM-DD}/b3_{YYYY-MM-DD}.parquet`
- Engine: pyarrow

## Monitoramento

### CloudWatch Logs
- Grupo: `/aws/lambda/b3_scrapper`
- Logs de execução, erros e métricas

### Códigos de Retorno
- `200`: Sucesso na extração e armazenamento
- `500`: Erro na extração de dados

## Desprovisionar

```bash
# Remover Lambda e recursos relacionados
cd infra/lambda
terraform destroy

# Remover S3 (cuidado: dados serão perdidos)
cd infra/s3
terraform destroy
```

## Desenvolvimento

### Estrutura do Código

1. **`lambda_handler.py`**: Ponto de entrada da Lambda
2. **`extractor.py`**: Orquestra extração, processamento e armazenamento
3. **`scrapper.py`**: Cliente da API B3 com codificação Base64
4. **`base64_decoder.py`**: Utilitário para codificação/decodificação

### Adicionando Dependências

1. Adicione a dependência no `requirements.txt`
2. Execute `python build/build.py`
3. Atualize o Terraform em `infra/lambda/main.tf` se necessário

### Logs e Debug

```bash
# Visualizar logs
aws logs tail /aws/lambda/b3_scrapper --follow

# Testar função localmente
cd src && python lambda_handler.py
```

## Custos Estimados

- **Lambda**: ~$0.20/mês (execução diária)
- **S3**: ~$0.023/GB/mês para armazenamento
- **EventBridge**: Gratuito (até 1M eventos/mês)
- **CloudWatch Logs**: ~$0.50/GB para retenção

## Troubleshooting

### Erro 500 na Lambda
- Verifique logs no CloudWatch
- Confirme se a API da B3 está respondendo
- Verifique permissões do S3

### Build falhando
- Confirme se tem Python 3.12+ instalado
- Execute `pip install -r requirements.txt` localmente primeiro
- Verifique se o diretório `build/` tem permissões de escrita

### Terraform apply falhando
- Confirme se as credenciais AWS estão configuradas
- Execute `python build/build.py` antes do terraform apply
- Verifique se o bucket S3 já existe (se estiver usando um existente) 