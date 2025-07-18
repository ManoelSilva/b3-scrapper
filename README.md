[Versão em Português](README.pt-br.md)

# B3 Scrapper AWS Lambda

## Description

Automated system for daily collection of IBOVESPA index data from B3 (Brasil, Bolsa, Balcão), using AWS Lambda, S3, and EventBridge. Data is extracted via B3 API, processed with pandas, and stored in Parquet format on S3.

## Features

- 📊 **Data Extraction**: Collects IBOVESPA data via B3 API
- 🔄 **Processing**: Converts data to pandas DataFrame
- 💾 **Storage**: Saves in Parquet format on S3
- ⏰ **Scheduling**: Automatic daily execution at 19:00 BRT
- 🏗️ **Infrastructure as Code**: Provisioning via Terraform
- 📦 **Automated Build**: Python script for packaging

## Project Structure

```
├── src/                        # Lambda source code
│   ├── lambda_handler.py       # Main Lambda handler
│   ├── extractor.py           # Main extraction class
│   ├── scrapper.py            # B3 API client
│   └── base64_decoder.py      # Base64 utility
├── build/                      # Build files (generated)
│   ├── build.py               # Automated build script
│   ├── lambda.zip             # Packaged Lambda code
│   └── layers/                # Lambda Layers
│       ├── layer_pandas.zip   # pandas layer (~38MB)
│       ├── layer_pyarrow.zip  # pyarrow layer (~26MB)
│       └── layer_requests.zip # requests layer (~1MB)
├── infra/                      # Terraform
│   ├── lambda/                # Lambda infrastructure
│   │   ├── main.tf            # Main resources
│   │   ├── variables.tf       # Configurable variables
│   │   └── outputs.tf         # Terraform outputs
│   └── s3/                    # S3 infrastructure
│       ├── main.tf            # S3 bucket
│       ├── variables.tf       # S3 variables
│       └── outputs.tf         # S3 outputs
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## Dependencies

### Python
- `pandas`: Data manipulation
- `pyarrow`: Parquet format engine
- `requests`: HTTP client for B3 API
- `boto3`: AWS SDK (already available in Lambda runtime)

### AWS
- Lambda (Python 3.12)
- S3
- EventBridge (CloudWatch Events)
- IAM

## Configuration

### Environment Variables

The Lambda uses the following environment variables:

- `BUCKET_NAME`: S3 bucket name for storage
- `B3_API_URL`: B3 API URL (default: `https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/`)

### Terraform Variables

#### infra/lambda/variables.tf
- `region`: AWS region (default: `us-east-1`)
- `bucket_name`: S3 bucket name (default: `861115334572-raw`)
- `B3_URL`: B3 API URL

#### infra/s3/variables.tf
- `bucket_name`: S3 bucket name

## Provisioning

### 1. Automated Build

Run the build script to package the code and create the layers:

```bash
python build/build.py
```

The script will:
- Create a separate layer for each dependency in `requirements.txt`
- Ignore dependencies already available in the Lambda runtime (boto3, etc.)
- Generate `build/lambda.zip` with the Lambda code
- Generate layers in `build/layers/`

### 2. Provision S3

```bash
cd infra/s3
terraform init
terraform apply -var="bucket_name=your-bucket-name"
```

### 3. Provision Lambda

```bash
cd infra/lambda
terraform init
terraform apply -var="bucket_name=your-bucket-name"
```

## Execution

### Automatic Execution
- The Lambda runs daily at 19:00 BRT (22:00 UTC)
- Configured via EventBridge (CloudWatch Events)

### Manual Execution
```bash
# Local test
cd src
python lambda_handler.py

# Via AWS CLI
aws lambda invoke --function-name b3_scrapper output.json
```

## Data Format

### Input (B3 API)
- Payload: `{"language":"pt-br","index":"IBOV","segment":"1"}`
- Encoding: Base64
- Endpoint: GET with payload encoded in the URL

### Output (S3)
- Format: Parquet
- Structure: `s3://bucket/{YYYY-MM-DD}/b3_{YYYY-MM-DD}.parquet`
- Engine: pyarrow

## Monitoring

### CloudWatch Logs
- Group: `/aws/lambda/b3_scrapper`
- Execution logs, errors, and metrics

### Return Codes
- `200`: Successful extraction and storage
- `500`: Data extraction error

## Deprovisioning

```bash
# Remove Lambda and related resources
cd infra/lambda
terraform destroy

# Remove S3 (caution: data will be lost)
cd infra/s3
terraform destroy
```

## Development

### Code Structure

1. **`lambda_handler.py`**: Lambda entry point
2. **`extractor.py`**: Orchestrates extraction, processing, and storage
3. **`scrapper.py`**: B3 API client with Base64 encoding
4. **`base64_decoder.py`**: Encoding/decoding utility

### Adding Dependencies

1. Add the dependency to `requirements.txt`
2. Run `python build/build.py`
3. Update Terraform in `infra/lambda/main.tf` if necessary

### Logs and Debug

```bash
# View logs
aws logs tail /aws/lambda/b3_scrapper --follow

# Test function locally
cd src && python lambda_handler.py
```

## Estimated Costs

- **Lambda**: ~$0.20/month (daily execution)
- **S3**: ~$0.023/GB/month for storage
- **EventBridge**: Free (up to 1M events/month)
- **CloudWatch Logs**: ~$0.50/GB for retention

## Troubleshooting

### Lambda 500 Error
- Check logs in CloudWatch
- Confirm B3 API is responding
- Check S3 permissions

### Build Failing
- Make sure Python 3.12+ is installed
- Run `pip install -r requirements.txt` locally first
- Check if the `build/` directory has write permissions

### Terraform apply failing
- Make sure AWS credentials are configured
- Run `python build/build.py` before terraform apply
- Check if the S3 bucket already exists (if using an existing one) 