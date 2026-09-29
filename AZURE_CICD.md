# Azure CI/CD Setup

The GitHub Actions workflow has three stages:

1. **test** — installs dependencies and runs the test suite.
2. **docker-build** — builds both container images after tests pass.
3. **azure-deploy** — optionally pushes images to Azure Container Registry and updates Azure Container Apps.

Azure deployment is disabled by default.

## Required GitHub Actions variables

- `AZURE_DEPLOY_ENABLED=true`
- `AZURE_CONTAINER_REGISTRY=<registry-name>`
- `AZURE_RESOURCE_GROUP=rg-ai-recommendation`
- `AZURE_API_APP_NAME=ca-ai-recommendation-api`
- `AZURE_UI_APP_NAME=ca-ai-recommendation-ui`

## Required GitHub Actions secrets

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

These values should correspond to an Azure Entra ID application configured for GitHub Actions federation.

## OIDC security model

The deployment job requests the GitHub Actions `id-token: write` permission and uses `azure/login@v2`. No long-lived Azure client secret is stored in the repository.

Before enabling deployment, configure an Azure federated identity credential that trusts this repository and the intended GitHub branch or environment.

## Deployment behavior

Pull requests run tests only.

A push to `main` runs tests and builds both Docker images. Azure deployment runs only when `AZURE_DEPLOY_ENABLED` is exactly `true`.

Images are tagged with the immutable Git commit SHA so each deployment can be traced to a specific source revision.
