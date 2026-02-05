# Retrieval Augmented Generation (RAG)

> [!WARNING]
> **Status: PLANNED**

RAG allows Zero to answer questions based on your local files, documentation, and personal notes, rather than just the LLM's training data.

## 1. Ingestion Pipelines

### Local Files
We need a `FileWatcher` to index specific folders (e.g., `~/Documents/Projects`).
*   **Loader:** Unstructured or built-in text loaders.
*   **Chunking:** Recursive character splitter (overlap: 200, chunk: 1000).

### Browser History (Context)
*   Zero already monitors usage. It should index the content of pages visited (using accessibility API or browser extensions) to allow "chat with browsing history".

## 2. Vector Store
We will use a **local-first** vector store to maintain privacy. Data never leaves the device for indexing if we use local embedding models.

*   **Embedding Model:** `Ollama` (nomic-embed-text) or `HuggingFace` (all-MiniLM-L6-v2) running via CoreML.
*   **Database:** `ChromaDB` (persistent local) or `LanceDB` (serverless, file-based).

## 3. Retrieval Strategy

### Hybrid Search
Combine **Semantic Search** (Vectors) with **Keyword Search** (BM25) for precision.

### Contextual Re-ranking
1.  Retrieve top-K (e.g., 20) documents.
2.  Use a Cross-Encoder (local small model) to re-rank them based on relevance to the query.
3.  Feed top-N (e.g., 5) to the LLM.

## 4. Feature: "Project Awareness"

Users should be able to "pin" a folder to the conversation context.
*   *Config:* `.zero/config.json` in a project root.
*   *Action:* When `ContextMonitor` detects a file in that folder is open, Zero automatically loads the vector index for that project.
