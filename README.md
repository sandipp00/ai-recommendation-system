# AI-Powered Personalized Recommendation System

An end-to-end movie recommendation platform that combines **content-based retrieval, semantic embeddings, hybrid ranking, Retrieval-Augmented Generation (RAG), and a local Hugging Face LLM** to generate personalized recommendations from natural-language preferences.

## Project Overview

Traditional recommendation systems often rely on ratings or item similarity alone. This project combines multiple signals:

- **TF-IDF content similarity** for interpretable lexical matching
- **Sentence Transformer embeddings** for semantic retrieval
- **Hybrid ranking** combining content, semantic, and popularity signals
- **RAG** to ground the language model in retrieved movie candidates
- **Hugging Face LLM** for natural-language explanations
- **FastAPI** for a programmatic backend
- **Streamlit** for an interactive user interface
- **Pytest + GitHub Actions** for automated validation

The architecture is intentionally modular so individual components can be replaced or improved independently.

## Architecture

```text
                    User
                     │
                     ▼
             Streamlit Frontend
                     │
                     ▼
              FastAPI /recommend
                     │
                     ▼
          Hybrid Recommendation Engine
             ┌───────┴────────┐
             ▼                ▼
        TF-IDF Content   Semantic Embeddings
          Retrieval          Retrieval
             └───────┬────────┘
                     ▼
              Hybrid Ranking
                     │
                     ▼
             Top-K Candidates
                     │
                     ▼
              RAG Context Builder
                     │
                     ▼
             Grounded Prompt
                     │
                     ▼
             Hugging Face LLM
                     │
                     ▼
        Recommendations + Explanation
```

## Repository Structure

```text
ai-recommendation-system/
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── README.md
├── data/
│   └── raw/
│       └── sample_movies.csv
├── src/
│   ├── content_recommender.py
│   ├── data_loader.py
│   ├── embedding_store.py
│   ├── hybrid_recommender.py
│   ├── llm_client.py
│   ├── pipeline.py
│   ├── preprocessing.py
│   ├── prompt_builder.py
│   ├── rag_context.py
│   ├── rag_recommender.py
│   ├── recommendation_pipeline.py
│   └── semantic_recommender.py
├── tests/
│   ├── test_api.py
│   ├── test_content_recommender.py
│   ├── test_data_loader.py
│   ├── test_embedding_store.py
│   ├── test_hybrid_recommender.py
│   ├── test_pipeline.py
│   ├── test_preprocessing.py
│   ├── test_rag.py
│   ├── test_recommendation_pipeline.py
│   └── test_semantic_recommender.py
├── ui/
│   └── README.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── app.py
├── DATA_CARD.md
├── requirements.txt
└── README.md
```

## Recommendation Pipeline

### 1. Data preparation

Movie metadata is loaded and normalized before recommendation.

The development dataset contains:

- title
- genres
- keywords
- overview
- cast
- director
- release year
- rating
- vote count

The preprocessing layer removes duplicate titles, normalizes text, and handles numeric fields.

### 2. Content-based retrieval

Movie profiles are constructed from textual metadata.

TF-IDF with unigram/bigram features provides a lightweight lexical retrieval signal.

### 3. Semantic retrieval

Movie profiles are embedded using:

```text
all-MiniLM-L6-v2
```

Normalized embeddings allow cosine-style similarity search for semantically related queries.

### 4. Hybrid ranking

The default ranking combines:

```text
Final Score =
0.35 × Content Score
+ 0.50 × Semantic Score
+ 0.15 × Popularity Score
```

The weights are configurable in the hybrid recommender.

### 5. RAG

Only retrieved movie candidates are placed into the LLM context.

The prompt explicitly instructs the model to:

- use only the supplied movies
- avoid inventing movie titles or facts
- explain why each recommendation matches
- acknowledge when no strong match exists

This grounds the generated explanation in the retrieval results.

### 6. LLM generation

The development configuration uses:

```text
EleutherAI/gpt-neo-125M
```

The model is loaded lazily by the API, avoiding model initialization during application import.

The model can be changed through the `LLM_MODEL` environment variable.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sandipp00/ai-recommendation-system.git
cd ai-recommendation-system
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the API

Start FastAPI:

```powershell
uvicorn api.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Recommendation request

```http
POST /recommend
```

Example:

```json
{
  "query": "I want a dark science-fiction movie about artificial intelligence",
  "top_k": 5
}
```

The response includes structured recommendation scores and the generated explanation.

## Run the Streamlit App

Start the API first:

```powershell
uvicorn api.main:app --reload
```

Then open another terminal and run:

```powershell
streamlit run app.py
```

The Streamlit interface allows users to enter natural-language movie preferences and view:

- recommended movies
- hybrid scores
- semantic scores
- content scores
- popularity scores
- genres
- movie overviews
- AI-generated explanations

## Configuration

The API supports environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `RECOMMENDATION_DATASET` | `data/raw/sample_movies.csv` | Movie dataset |
| `SEMANTIC_MODEL` | `all-MiniLM-L6-v2` | Sentence Transformer model |
| `LLM_MODEL` | `EleutherAI/gpt-neo-125M` | Hugging Face causal language model |
| `TMDB_ENABLED` | `false` | Enable live TMDB movie recommendations |
| `TMDB_ACCESS_TOKEN` | unset | TMDB v4 API Read Access Token |
| `TMDB_API_KEY` | unset | TMDB v3 API key alternative |
| `TMDB_PAGES` | `3` | High-rated candidate pages to retrieve |
| `TMDB_MINIMUM_VOTES` | `300` | Minimum TMDB votes for the high-rated pool |

Example:

```powershell
$env:LLM_MODEL="EleutherAI/gpt-neo-125M"
$env:SEMANTIC_MODEL="all-MiniLM-L6-v2"
uvicorn api.main:app --reload
```

## Live TMDB Recommendation Mode

The application can use TMDB as a live movie source for stronger recommendations. TMDB's developer API exposes movie metadata, ratings, vote counts, popularity, and discovery filters. The live provider is designed for Render Free: it retrieves a small candidate pool over HTTP and ranks it locally with TF-IDF rather than loading a large movie catalog or embedding model.

Ranking in live mode:

~~~text
Final Score =
0.55 × Query Relevance
+ 0.30 × Bayesian TMDB Rating
+ 0.15 × Current TMDB Popularity
~~~

Enable it with TMDB_ENABLED=true plus TMDB_ACCESS_TOKEN or TMDB_API_KEY. Credentials are never stored in the repository. See TMDB.md.

TMDB data displayed by the application must include the attribution required by TMDB, and the project is intended for non-commercial use under TMDB's developer API terms.

## Recommendation Evaluation

The repository includes ranking metrics in `src/evaluation.py`: Precision@K, Recall@K, Hit Rate@K, and NDCG@K. See [EVALUATION.md](EVALUATION.md) for the benchmark methodology and the distinction between synthetic development labels and production ground truth.
## Testing

Run the complete test suite:

```powershell
python -m pytest -q
```

The tests cover:

- data loading
- preprocessing
- TF-IDF recommendations
- semantic retrieval
- embedding search
- hybrid ranking
- RAG context and prompting
- recommendation pipeline
- FastAPI endpoints

Semantic and LLM-heavy components use test doubles where appropriate, so unit tests do not need to download large models.

## Continuous Integration

GitHub Actions automatically runs the test suite for:

- pushes to `main`
- pull requests targeting `main`

Workflow:

```text
Checkout
   ↓
Python 3.11
   ↓
Install dependencies
   ↓
pytest -q
```

## Dataset

The repository includes a small synthetic/reproducible movie dataset for development and testing.

For a larger production experiment, the architecture can be connected to the **TMDB 5000 Movie Dataset**. The full external dataset is intentionally kept outside the repository to avoid unnecessary redistribution and repository bloat.

See [DATA_CARD.md](DATA_CARD.md) for dataset details and limitations.

## Cinematic Discovery Experience

The Streamlit frontend now provides two complementary discovery modes:

- **AI Discovery** — natural-language recommendations powered by the retrieval + RAG pipeline.
- **Live TMDB collections** — Trending, Top Rated, New Releases, and Hidden Gems.
- **Mood signals** — optional mood preference can be combined with a natural-language request.
- **Quick Vibes** — one-click prompts for common viewing moods.
- **More Like This** — live TMDB recommendations from a selected movie.
- **Poster-first cards** — ratings, release years, genres, and concise overviews.
- **Live-data caching** — discovery collections are cached briefly in the Streamlit layer to reduce repeated API calls.

TMDB's Discover API supports filtering and sorting by ratings, vote counts, release dates, and other movie attributes; CineMind uses those capabilities for the live collection views. citeturn1search2

## Engineering Highlights

This project demonstrates:

- modular ML architecture
- NLP-based information retrieval
- semantic search
- hybrid recommendation systems
- vector similarity
- RAG architecture
- LLM integration
- prompt grounding
- FastAPI REST APIs
- Streamlit application development
- dependency injection for testing
- lazy model initialization
- unit testing
- GitHub Actions CI/CD foundations
- configurable model and dataset paths

## Future Improvements

Planned production-level extensions include:

- TMDB 5000 production dataset integration
- persistent vector database
- user-profile and interaction-based personalization
- collaborative filtering
- re-ranking model
- recommendation evaluation metrics
- structured LLM output
- response caching
- API authentication and rate limiting
- Docker containerization
- cloud deployment
- experiment tracking
- monitoring and observability

## License

This repository is intended as a portfolio and educational project.
