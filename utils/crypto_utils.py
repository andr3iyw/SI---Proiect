import hashlib
import os

def calculate_sha256(filepath: str) -> str:
    """Calculeaza amprenta SHA-256 a unui fisier."""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(filepath, "rb") as f:
            # Citim in blocuri de 4K pentru eficienta
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None