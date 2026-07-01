"""Compare a Bloom filter against a plain Python set on memory usage
and false-positive behavior, and compare a Count-Min Sketch against an
exact Counter on memory usage and estimation error.

Run with:
    python benchmark.py
"""
import random
import string
import sys
from collections import Counter

from pds import BloomFilter, CountMinSketch


def random_word(length=10):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def bloom_vs_set(n=100_000, false_positive_rate=0.01):
    words = [random_word() for _ in range(n)]

    exact = set(words)
    bloom = BloomFilter(expected_items=n, false_positive_rate=false_positive_rate)
    for word in words:
        bloom.add(word)

    exact_bytes = sys.getsizeof(exact) + sum(sys.getsizeof(w) for w in exact)
    bloom_bytes = sys.getsizeof(bloom.bits)

    probes = [random_word() for _ in range(20_000)]
    false_positives = sum(1 for w in probes if w not in exact and w in bloom)

    print("=== Bloom Filter vs set() ===")
    print(f"items inserted:        {n:,}")
    print(f"set() memory:          {exact_bytes:,} bytes")
    print(f"BloomFilter memory:    {bloom_bytes:,} bytes")
    print(f"memory ratio:          {exact_bytes / bloom_bytes:,.1f}x smaller")
    print(f"target FP rate:        {false_positive_rate:.2%}")
    print(f"observed FP rate:      {false_positives / len(probes):.2%}")
    print()


def cms_vs_counter(n=100_000, vocab=500):
    stream = [f"word-{random.randint(0, vocab - 1)}" for _ in range(n)]

    exact = Counter(stream)
    cms = CountMinSketch(error_rate=0.01, confidence=0.99)
    for word in stream:
        cms.add(word)

    exact_bytes = sys.getsizeof(exact) + sum(sys.getsizeof(k) for k in exact)
    cms_bytes = sum(sys.getsizeof(row) for row in cms.table)

    errors = [cms.estimate(word) - count for word, count in exact.items()]
    max_error = max(errors)
    avg_error = sum(errors) / len(errors)

    print("=== Count-Min Sketch vs Counter ===")
    print(f"stream length:         {n:,}")
    print(f"distinct items:        {len(exact):,}")
    print(f"Counter memory:        {exact_bytes:,} bytes")
    print(f"CountMinSketch memory: {cms_bytes:,} bytes")
    print(f"memory ratio:          {exact_bytes / cms_bytes:,.1f}x smaller")
    print(f"max overcount error:   {max_error}")
    print(f"avg overcount error:   {avg_error:.3f}")


if __name__ == "__main__":
    random.seed(0)
    bloom_vs_set()
    cms_vs_counter()
