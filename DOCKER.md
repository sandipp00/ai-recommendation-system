# Docker Deployment

## Prerequisites

Install Docker Desktop with Docker Compose support.

## Build and start

From the repository root:

```powershell
docker compose up --build
```

Services:

- FastAPI: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Streamlit: http://localhost:8501

Stop the stack:

```powershell
docker compose down
```

## Configuration

The API container supports:

- `RECOMMENDATION_DATASET`
- `SEMANTIC_MODEL`
- `LLM_MODEL`

The Streamlit application reads its API URL from the `API_URL` environment variable.

## Notes

The first recommendation request can take longer because the Sentence Transformer and Hugging Face model may need to be downloaded and loaded.

For production deployment, use persistent model caching or a dedicated model-serving layer rather than downloading models on every new container instance.
