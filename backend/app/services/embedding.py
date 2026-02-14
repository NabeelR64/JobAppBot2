import logging
from typing import List

import numpy as np
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text using OpenAI's
    text-embedding-3-small model (1536 dimensions).

    Returns an empty list if the API key is missing or the call fails.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set — skipping embedding generation.")
        return []

    if not text or not text.strip():
        logger.warning("Empty text provided — skipping embedding generation.")
        return []

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text[:8000]  # Limit to ~8k chars to stay within token limits
        )
        embedding = response.data[0].embedding
        logger.info(f"Generated embedding vector with {len(embedding)} dimensions.")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return []


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    Returns a float between -1 and 1, or 0.0 if either vector is empty.
    """
    if not vec_a or not vec_b:
        return 0.0

    a = np.array(vec_a)
    b = np.array(vec_b)

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))
