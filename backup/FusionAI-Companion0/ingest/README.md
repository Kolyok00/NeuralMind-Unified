# Ingest & Embed - Web Crawling and Embedding Services

This directory contains the web crawling and document embedding components.

## Setup Instructions

1. Add the mcp-crawl4ai-rag submodule:
```bash
git submodule add https://github.com/coleam00/mcp-crawl4ai-rag ingest
```

2. The Crawl4AI service is automatically started via Docker Compose

## Components

### Crawl4AI
- Web crawling and content extraction
- Smart content parsing and cleaning
- Support for JavaScript-rendered pages
- Rate limiting and politeness policies

### Embedding Pipeline
- Document chunking strategies
- Vector embedding generation
- Integration with Supabase pgvector
- Metadata extraction and storage

### Search Integration
- SearXNG for web search
- Hybrid search (vector + keyword)
- Result ranking and filtering

## Configuration

Key environment variables:
- `CRAWL4AI_API_URL`: Crawl4AI service endpoint
- `SEARXNG_URL`: SearXNG search service
- `SUPABASE_URL`: Vector database connection
- `OPENAI_API_KEY`: For embedding generation

## Usage Examples

### Web Crawling
```python
import requests

# Crawl a webpage
response = requests.post("http://localhost:8000/crawl", json={
    "url": "https://example.com",
    "extraction_strategy": "content"
})
```

### Document Embedding
```python
# Embed documents into vector database
response = requests.post("http://localhost:8000/embed", json={
    "text": "Document content to embed",
    "metadata": {"source": "example.com"}
})
```

## API Endpoints

- `POST /crawl` - Crawl a webpage
- `POST /embed` - Generate embeddings
- `GET /search` - Search embedded content
- `POST /bulk-crawl` - Bulk crawling operations
