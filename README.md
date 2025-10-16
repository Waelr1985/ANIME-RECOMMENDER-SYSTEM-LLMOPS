# ANIME-RECOMMENDER-SYSTEM-LLMOPS

A retrieval‑augmented, LLM‑powered Anime recommender built with LangChain, Chroma vector store, and Groq’s Llama 3.1 models. The app exposes a simple Streamlit UI: you enter your preferences (e.g., “light‑hearted anime with school settings”), and it returns structured recommendations grounded in a curated dataset.

## Why this project?
Many recommendation systems are black boxes. This project demonstrates a transparent, RAG‑style approach:
- Curate and preprocess an anime dataset into concise, searchable text chunks.
- Embed and persist those chunks in a local vector database (Chroma).
- Retrieve the most relevant context for a user’s query.
- Use a strong LLM (Groq) with a domain‑specific prompt to generate well‑structured, grounded recommendations.

## Key Features
- Streamlit web UI for interactive queries.
- RAG pipeline with Chroma and sentence‑transformer embeddings.
- Groq LLM integration via `langchain_groq.ChatGroq`.
- Clear prompt template that enforces three recommendations with rationale.
- Simple, reproducible pipeline scripts for preprocessing and vector DB building.

## Project Structure
```
.
├── app/
│   └── app.py                 # Streamlit UI (entrypoint: streamlit run app/app.py)
├── pipeline/
│   ├── pipeline.py            # Orchestrates vector store + recommender runtime
│   └── build_pipeline.py      # One‑time (or periodic) build of Chroma vector store
├── src/
│   ├── data_loader.py         # Loads CSV, validates columns, builds combined text
│   ├── vector_store.py        # Creates/loads Chroma with HuggingFace embeddings
│   ├── recommender.py         # LangChain RetrievalQA with ChatGroq LLM
│   └── prompt_template.py     # Domain prompt enforcing structure & grounding
├── config/
│   └── config.py              # Loads env vars (.env + Streamlit secrets fallback)
├── utils/
│   ├── custom_exception.py    # Friendly exceptions with file/line context
│   └── logger.py              # Basic logger helper
├── data/                      # Raw and processed CSVs (ignored if large)
├── chroma_db/                 # Persisted local vector DB (generated)
├── requirements.txt
├── Dockerfile
└── llmops-k8s.yaml            # Example Kubernetes manifest
```

## How It Works
1. Data preprocessing (`src/data_loader.py`)
   - Expects a CSV with columns: `Name`, `Genres`, `sypnopsis`.
   - Creates a single `combined_info` column: Title + Overview + Genres.
   - Outputs a slim CSV with `combined_info` for efficient chunking.

2. Vector store build (`src/vector_store.py`, `pipeline/build_pipeline.py`)
   - Splits `combined_info` into chunks (via `CharacterTextSplitter`).
   - Embeds with `all-MiniLM-L6-v2` (HuggingFace sentence transformer).
   - Persists to `chroma_db/` for fast later retrieval.

3. Recommendation runtime (`pipeline/pipeline.py`, `src/recommender.py`)
   - Loads the persisted Chroma store and creates a retriever.
   - Uses `ChatGroq` (Groq LLM) with a prompt that enforces:
     - Exactly three anime titles
     - 2–3 sentence plot and a reason it matches user preferences
   - Returns a clean, numbered list back to the Streamlit UI.

## Prerequisites
- Python 3.10+
- A Groq API key for LLM inference
- Optionally a Hugging Face token if your environment requires it for model download

## Setup
1. Create and activate a virtual environment
   - Windows (PowerShell):
     - `python -m venv venv`
     - `venv\\Scripts\\Activate.ps1`
   - macOS/Linux:
     - `python -m venv venv`
     - `source venv/bin/activate`

2. Install dependencies
   - `pip install -r requirements.txt`

3. Create a `.env` file in the project root (recommended)
   - Example:
     ```env
     GROQ_API_KEY=your_groq_api_key
     MODEL_NAME=llama-3.1-8b-instant
     HUGGINGFACEHUB_API_TOKEN=your_hf_token_optional
     ```
   - Note: The project also supports a fallback `.env` at `venv/.env`, but root `.env` is standard.

## Build the Vector Database (one‑time or when data changes)
- Place your source dataset at `data/anime_with_synopsis.csv` with columns: `Name`, `Genres`, `sypnopsis`.
- Run the build script:
  - `python pipeline/build_pipeline.py`
- This will create `data/anime_updated.csv` and a persisted vector DB at `chroma_db/`.

## Run the App
- Start Streamlit:
  - `streamlit run app/app.py`
- Enter your preferences in the text box (e.g., “Cozy slice‑of‑life with school setting”).
- The app will:
  - Load the retriever from `chroma_db/`
  - Query the Groq LLM with relevant context
  - Return three structured recommendations

## Configuration
- `config/config.py` loads environment variables in this order:
  - Root `.env` (via `python-dotenv`)
  - Streamlit secrets (if running on Streamlit Cloud)
  - Fallback to `venv/.env` if `GROQ_API_KEY` is still unset
- Key variables:
  - `GROQ_API_KEY` (required)
  - `MODEL_NAME` (default: `llama-3.1-8b-instant`)
  - `HUGGINGFACEHUB_API_TOKEN` (optional; needed in some environments to download embeddings)

## Troubleshooting
- Error: “The api_key client option must be set…GROQ_API_KEY”
  - Ensure your `.env` (root) contains `GROQ_API_KEY`.
  - Or set it for your shell: Windows PowerShell → `$env:GROQ_API_KEY="..."`, macOS/Linux → `export GROQ_API_KEY=...`.
  - A fallback to `venv/.env` is supported if root `.env` is missing.

- Missing embeddings/model download
  - If `all-MiniLM-L6-v2` fails to download, set `HUGGINGFACEHUB_API_TOKEN` in `.env`.

- Chroma DB not found or empty
  - Run the build step: `python pipeline/build_pipeline.py`.
  - Confirm `chroma_db/` exists and contains index files.

## Docker (optional)
- Build image: `docker build -t anime-recommender:latest .`
- Run container (example):
  - `docker run -e GROQ_API_KEY=your_key -p 8501:8501 anime-recommender:latest`
- For persistence, mount `chroma_db/` into the container and run the build step inside once, or bake it into the image during build.

## Kubernetes (optional)
- A sample manifest is provided at `llmops-k8s.yaml`.
- Typical steps:
  - Create a secret for `GROQ_API_KEY` (and optionally HF token).
  - Apply the manifest.
  - Expose the service via port‑forward or an ingress.
- See `FULL_DOCUMENTATION.md` for a more detailed, step‑by‑step cluster walkthrough (Minikube/Grafana).

## Development Notes
- Logging and exceptions are centralized in `utils/`.
- The pipeline class `AnimeRecommendationPipeline` encapsulates the runtime wiring (vector store + recommender) and exposes a simple `recommend(query: str) -> str` interface.
- The Streamlit app caches the pipeline (`@st.cache_resource`) for better performance.

## Tech Stack
- LangChain, Chroma, HuggingFace sentence transformers
- Groq LLMs via `langchain_groq`
- Streamlit UI
- Python 3.10+

## License
This project is provided as‑is. Add your preferred OSS license if you plan to open source it.

