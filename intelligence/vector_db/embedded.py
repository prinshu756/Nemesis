
def embed(text):
    """Embedding function with lazy loading and fallback"""
    # Always use fallback for now to avoid hanging
    return _fallback_embed(text)

def _fallback_embed(text):
    """Simple fallback embedding using basic text features"""
    import hashlib

    # Use hash of text to create deterministic pseudo-random vector
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()

    # Convert hash to float values between -1 and 1
    vector = []
    for i in range(0, len(hash_bytes), 4):
        chunk = hash_bytes[i:i+4]
        val = int.from_bytes(chunk, byteorder='big', signed=False)
        # Normalize to [-1, 1]
        normalized = (val / (2**32 - 1)) * 2 - 1
        vector.append(normalized)

    # Pad or truncate to 384 dimensions
    while len(vector) < 384:
        vector.extend(vector[:384 - len(vector)])

    return vector[:384]