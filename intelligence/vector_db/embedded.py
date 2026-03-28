"""
Text embedding utilities for Nemesis
"""

import logging

logger = logging.getLogger('nemesis')


def embed(text: str):
    """Embed text for vector database"""
    try:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.encode(text)
        except Exception as e:
            logger.warning(f"Sentence transformer failed: {e}, using fallback")
            # Fallback: simple hash-based embedding
            import hashlib
            hash_val = hashlib.sha256(text.encode()).hexdigest()
            return [float(ord(c)) / 255.0 for c in hash_val[:384]]
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return [0.0] * 384
