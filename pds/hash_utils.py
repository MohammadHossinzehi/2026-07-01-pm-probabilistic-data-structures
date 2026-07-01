"""Hash utilities for generating multiple independent-ish hash functions
from just two real hash computations.
"""
import hashlib


def _hash_to_int(data: bytes, seed: int) -> int:
    h = hashlib.sha256(seed.to_bytes(4, "little", signed=False) + data).digest()
    return int.from_bytes(h[:8], "little")


def double_hash(item: str, num_hashes: int, size: int):
    """Yield `num_hashes` independent-ish hash values of `item` modulo `size`.

    Uses the standard g_i(x) = h1(x) + i * h2(x) mod m construction
    (Kirsch & Mitzenmacher, 2006) so we only need two real hash
    computations no matter how many hash functions the caller wants.
    """
    data = item.encode("utf-8")
    h1 = _hash_to_int(data, 0)
    h2 = _hash_to_int(data, 1)
    for i in range(num_hashes):
        yield (h1 + i * h2) % size
