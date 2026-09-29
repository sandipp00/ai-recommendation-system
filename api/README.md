# FastAPI Service

## Run locally

From the repository root:

```bash
uvicorn api.main:app --reload
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

The production wiring for the real hybrid + RAG service will be added after the API contract is validated.

## Endpoints

### Health

`GET /health`

### Recommendations

`POST /recommend`

Example request:

```json
{
  "query": "I want a dark science-fiction movie",
  "top_k": 5
}
```
