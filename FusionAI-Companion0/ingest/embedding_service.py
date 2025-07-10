"""
Embedding Service - Handles document embedding and vector search
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Manages document embedding and vector search operations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model", "nomic-embed-text")
        self.chunk_size = config.get("chunk_size", 1000)
        self.chunk_overlap = config.get("chunk_overlap", 200)

        # Service endpoints
        self.ollama_url = "http://localhost:11434"
        self.supabase_url = config.get("supabase_url")
        self.crawl4ai_url = "http://localhost:8000"

        # HTTP client
        self.http_client = None

        # Cache for embeddings
        self.embedding_cache = {}
        self.is_initialized = False

    async def initialize(self):
        """Initialize the embedding service"""
        try:
            logger.info("Initializing EmbeddingService...")

            # Create HTTP client
            self.http_client = httpx.AsyncClient(timeout=60.0)

            # Check services
            await self._check_services()

            # Initialize vector database
            await self._init_vector_db()

            self.is_initialized = True
            logger.info("EmbeddingService initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing EmbeddingService: {e}")
            raise

    async def start(self):
        """Start the embedding service"""
        if not self.is_initialized:
            await self.initialize()
        logger.info("EmbeddingService started")

    async def stop(self):
        """Stop the embedding service"""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("EmbeddingService stopped")

    async def health_check(self) -> bool:
        """Check if embedding service is healthy"""
        try:
            if not self.http_client:
                return False

            # Check Ollama embedding model
            response = await self.http_client.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.model, "prompt": "test"},
            )
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def _check_services(self):
        """Check if required services are available"""
        try:
            # Check Ollama
            response = await self.http_client.get(f"{self.ollama_url}/api/tags")
            if response.status_code != 200:
                raise Exception("Ollama service not available")

            # Check if embedding model is available
            models = response.json()
            model_names = [model["name"] for model in models.get("models", [])]
            if self.model not in model_names:
                logger.warning(f"Embedding model {self.model} not found")

            logger.info("Embedding services are available")

        except Exception as e:
            logger.error(f"Service check failed: {e}")
            raise

    async def _init_vector_db(self):
        """Initialize vector database schema"""
        try:
            # For now, we'll use in-memory storage
            # In production, this would connect to Supabase/pgvector
            logger.info("Vector database initialized (in-memory mode)")

        except Exception as e:
            logger.error(f"Vector DB initialization error: {e}")
            raise

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            # Check cache first
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self.embedding_cache:
                return self.embedding_cache[text_hash]

            # Generate embedding
            response = await self.http_client.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )

            response.raise_for_status()
            result = response.json()

            embedding = result.get("embedding", [])

            # Cache the result
            self.embedding_cache[text_hash] = embedding

            return embedding

        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise

    async def embed_document(
        self, content: str, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Embed a document with chunking"""
        try:
            # Split document into chunks
            chunks = self._chunk_text(content)

            # Generate embeddings for each chunk
            chunk_embeddings = []
            for i, chunk in enumerate(chunks):
                embedding = await self.embed_text(chunk)

                chunk_data = {
                    "chunk_id": i,
                    "content": chunk,
                    "embedding": embedding,
                    "metadata": metadata or {},
                }

                chunk_embeddings.append(chunk_data)

            result = {
                "success": True,
                "total_chunks": len(chunks),
                "chunks": chunk_embeddings,
                "metadata": metadata or {},
            }

            return result

        except Exception as e:
            logger.error(f"Document embedding error: {e}")
            return {"success": False, "error": str(e), "chunks": []}

    async def crawl_and_embed(
        self, url: str, metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Crawl a webpage and embed its content"""
        try:
            # Crawl the webpage
            crawl_response = await self.http_client.post(
                f"{self.crawl4ai_url}/crawl",
                json={"url": url, "extraction_strategy": "content"},
            )

            crawl_response.raise_for_status()
            crawl_data = crawl_response.json()

            content = crawl_data.get("content", "")
            if not content:
                raise Exception("No content extracted from webpage")

            # Add URL to metadata
            if metadata is None:
                metadata = {}
            metadata.update(
                {
                    "url": url,
                    "crawled_at": datetime.now().isoformat(),
                    "title": crawl_data.get("title", ""),
                    "description": crawl_data.get("description", ""),
                }
            )

            # Embed the content
            result = await self.embed_document(content, metadata)

            if result["success"]:
                logger.info(
                    f"Successfully crawled and embedded: {url} "
                    f"({result['total_chunks']} chunks)"
                )

            return result

        except Exception as e:
            logger.error(f"Crawl and embed error for {url}: {e}")
            return {"success": False, "error": str(e), "chunks": []}

    async def search_similar(
        self, query: str, limit: int = 10, threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar content using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = await self.embed_text(query)

            # For now, return mock results
            # In production, this would query the vector database
            mock_results = [
                {
                    "content": "Example similar content...",
                    "similarity": 0.85,
                    "metadata": {"source": "example.com"},
                }
            ]

            return mock_results

        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # If this is not the last chunk, try to break at a sentence
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(end - 100, start)
                sentence_end = max(
                    text.rfind(". ", search_start, end),
                    text.rfind("! ", search_start, end),
                    text.rfind("? ", search_start, end),
                )

                if sentence_end > start:
                    end = sentence_end + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - self.chunk_overlap

            # Prevent infinite loop
            if start >= end:
                start = end

        return chunks

    def _calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0

    async def bulk_embed_urls(self, urls: List[str]) -> Dict[str, Any]:
        """Embed multiple URLs in parallel"""
        try:
            tasks = []
            for url in urls:
                task = self.crawl_and_embed(url)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = 0
            error_count = 0
            all_chunks = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing {urls[i]}: {result}")
                    error_count += 1
                elif result.get("success", False):
                    success_count += 1
                    all_chunks.extend(result.get("chunks", []))
                else:
                    error_count += 1

            return {
                "success": True,
                "total_urls": len(urls),
                "successful": success_count,
                "failed": error_count,
                "total_chunks": len(all_chunks),
                "chunks": all_chunks,
            }

        except Exception as e:
            logger.error(f"Bulk embedding error: {e}")
            return {"success": False, "error": str(e)}

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        return {
            "cache_size": len(self.embedding_cache),
            "model": self.model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "is_initialized": self.is_initialized,
        }
