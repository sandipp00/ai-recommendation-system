# Deployment Guide

## Container architecture

The application runs as two services:

- **API:** FastAPI recommendation backend on port 8000
- **UI:** Streamlit frontend on port 8501

The API owns the retrieval, ranking, RAG, and LLM pipeline. Streamlit communicates with it through HTTP.

## Local production-style run

Build and start the stack:

```bash
docker compose up --build
```

Check API health:

```text
http://localhost:8000/health
```

Open the application:

```text
http://localhost:8501
```

Stop:

```bash
docker compose down
```

## Model caching

Docker Compose creates a named `hf_cache` volume mounted at:

```text
/models/huggingface
```

This allows Hugging Face model files to persist across container recreation.

The cache is controlled through:

```text
HF_HOME=/models/huggingface
```

## Production considerations

Before public deployment:

1. Replace the sample dataset with an appropriately licensed production dataset.
2. Use a production-grade model-serving strategy if LLM inference becomes resource intensive.
3. Add authentication and rate limiting to the API.
4. Store secrets outside the image and repository.
5. Add structured logging and application metrics.
6. Configure persistent model storage or a managed model endpoint.
7. Put the API and Streamlit services behind HTTPS.
8. Restrict exposed ports according to the deployment environment.

## Health checks

FastAPI exposes:

```text
GET /health
```

Docker uses this endpoint to determine whether the API is ready before starting the Streamlit dependency chain.
