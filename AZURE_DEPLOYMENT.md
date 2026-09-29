# Azure Container Apps Deployment

This guide prepares the project for deployment to Azure Container Apps using the existing Docker images.

## Architecture

GitHub -> Docker -> Azure Container Registry -> Azure Container Apps

Run the FastAPI API and Streamlit UI as separate Container Apps.

## Prerequisites

Install Azure CLI and authenticate:

```bash
az login
az account show
az account set --subscription "<SUBSCRIPTION_ID>"
```

## Create resources

```bash
az group create --name rg-ai-recommendation --location centralindia

az acr create --resource-group rg-ai-recommendation --name <UNIQUE_ACR_NAME> --sku Basic

az containerapp env create --name cae-ai-recommendation --resource-group rg-ai-recommendation --location centralindia
```

## Build and push images

```bash
az acr build --registry <UNIQUE_ACR_NAME> --image ai-recommendation-api:latest --file Dockerfile .
az acr build --registry <UNIQUE_ACR_NAME> --image ai-recommendation-ui:latest --file Dockerfile.streamlit .
```

## Deploy the API

```bash
az containerapp create \
  --name ca-ai-recommendation-api \
  --resource-group rg-ai-recommendation \
  --environment cae-ai-recommendation \
  --image <UNIQUE_ACR_NAME>.azurecr.io/ai-recommendation-api:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server <UNIQUE_ACR_NAME>.azurecr.io \
  --cpu 2.0 \
  --memory 4Gi \
  --env-vars RECOMMENDATION_DATASET=data/raw/sample_movies.csv SEMANTIC_MODEL=all-MiniLM-L6-v2 LLM_MODEL=EleutherAI/gpt-neo-125M
```

Get the API hostname:

```bash
az containerapp show --name ca-ai-recommendation-api --resource-group rg-ai-recommendation --query properties.configuration.ingress.fqdn --output tsv
```

Verify `/health` on the resulting HTTPS hostname.

## Deploy Streamlit

Set `API_URL` to the deployed API HTTPS URL:

```bash
az containerapp create \
  --name ca-ai-recommendation-ui \
  --resource-group rg-ai-recommendation \
  --environment cae-ai-recommendation \
  --image <UNIQUE_ACR_NAME>.azurecr.io/ai-recommendation-ui:latest \
  --target-port 8501 \
  --ingress external \
  --registry-server <UNIQUE_ACR_NAME>.azurecr.io \
  --cpu 1.0 \
  --memory 2Gi \
  --env-vars API_URL=https://<API_FQDN>
```

Get the UI hostname:

```bash
az containerapp show --name ca-ai-recommendation-ui --resource-group rg-ai-recommendation --query properties.configuration.ingress.fqdn --output tsv
```

## Production notes

- Never commit Azure credentials, API keys, or registry credentials.
- Prefer managed identities and Azure secret storage for production secrets.
- Replace the sample dataset with a properly licensed production dataset.
- The current LLM is lightweight for a portfolio/demo deployment; larger models require more compute.
- Configure scaling and resource limits from observed traffic.
- Protect public API endpoints with authentication/rate limiting before exposing them to untrusted clients.
- Consider persistent or managed model storage if cold-start latency becomes significant.

## CI/CD

The existing GitHub Actions workflow runs the test suite. A later deployment workflow can authenticate to Azure using GitHub Actions OpenID Connect and deploy new Container App revisions only after CI succeeds.