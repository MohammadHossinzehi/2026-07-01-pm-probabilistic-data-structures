# probabilistic-data-structures

Three probabilistic data structures, implemented from scratch in pure Python (no dependencies beyond the standard library): a **Bloom filter**, a **Counting Bloom filter**, and a **Count-Min Sketch**. Each trades a small, well-understood error rate for dramatically less memory than the exact data structure it replaces.

## Why this exists

Exact set membership (`set()`) and exact frequency counting (`collections.Counter`) both scale linearly with the number of distinct items you store. That's fine until it isn't: a web crawler tracking billions of visited URLs, a database checking whether a key might exist before doing a disk read, or a stream processor counting event frequencies in real time all hit the point where storing every item exactly is too expensive. Probabilistic data structures solve this by hashing items into a fixed-size structure and accepting a small, controllable error rate in exchange for sub-linear (often constant) memory.

This repo implements the three you'll run into most often in real systems:

- **`BloomFilter`** — space-efficient set membership. No false negatives, tunable false positive rate. Used by things like Chrome's Safe Browsing list and Cassandra's SSTable lookups.
- **`CountingBloomFilter`** — a Bloom filter that supports deletion, at the cost of using small counters instead of single bits per slot.
- **`CountMinSketch`** — approximate frequency counting for streams. Never undercounts; overcounts by a bounded, tunable amount. Used for things like finding heavy hitters in network traffic or trending items.

## Install / run

No external dependencies are required to use the library itself; `pytest` is only needed to run the test suite.

```bash
git clone https://github.com/MohammadHossinzehi/2026-07-01-pm-probabilistic-data-structures.git
cd 2026-07-01-pm-probabilistic-data-structures
pip install -r requirements.txt   # only needed for running tests
```

Basic usage:

```python
from pds import BloomFilter, CountingBloomFilter, CountMinSketch

bf = BloomFilter(expected_items=10_000, false_positive_rate=0.01)
bf.add("alice@example.com")
"alice@example.com" in bf   # True
"bob@example.com" in bf     # almost certainly False

cbf = CountingBloomFilter(expected_items=10_000)
cbf.add("session-123")
cbf.remove("session-123")   # unlike a plain Bloom filter, this is supported
"session-123" in cbf        # False

cms = CountMinSketch(error_rate=0.001, confidence=0.99)
for event in ["login", "login", "logout", "login"]:
    cms.add(event)
cms.estimate("login")       # 3, or possibly a slight overcount
```

Run the benchmark script to see the memory/accuracy tradeoff for yourself:

```bash
python benchmark.py
```

Run the test suite:

```bash
pytest -v
```

## Design decisions

- **Hashing.** Rather than requiring `k` genuinely independent hash functions (expensive, and awkward without a C extension like `mmh3`), both Bloom filter variants use the "double hashing" technique from Kirsch & Mitzenmacher (2006): derive two hashes from SHA-256 and combine them as `g_i(x) = h1(x) + i * h2(x) mod m`. This is provably almost as good as truly independent hash functions and only costs two hash computations no matter how many are logically needed.
- **Sizing.** Bit array size and hash count are computed automatically from `expected_items` and a target `false_positive_rate` using the standard formulas (`m = -n*ln(p) / (ln 2)^2`, `k = (m/n)*ln 2`), so callers don't have to do that math themselves.
- **Counting Bloom filter counters** are stored as plain Python ints capped at a configurable bit width, rather than packed into a bitarray, favoring readability over the last bit of memory efficiency — this is a reference implementation meant to be read, not a production-grade C-optimized library.
- **Count-Min Sketch** defaults its `width`/`depth` from `error_rate`/`confidence` using the standard formulas (`width = ceil(e / error_rate)`, `depth = ceil(ln(1/(1-confidence)))`), matching the original Cormode & Muthukrishnan paper.

## Testing

The test suite (`pytest`) covers both correctness and probabilistic guarantees:

- **No false negatives** for the Bloom filter — anything added must always test as present.
- **False positive rate stays within a generous bound** of the configured target, checked empirically against thousands of random probes with a fixed random seed for reproducibility.
- **Counting Bloom filter deletion** — added items become absent after removal, removing a non-member is a no-op, and shared slots between duplicate insertions don't cause premature false negatives.
- **Count-Min Sketch never undercounts**, and stays tight (bounded overcount) for a skewed "heavy hitter" workload, which is the realistic use case for this structure.

`benchmark.py` is a separate, non-test script that prints actual memory usage and empirical error rates so you can see the tradeoff numerically rather than just trusting the math.

## Project layout

```
pds/
  __init__.py
  hash_utils.py          # shared double-hashing helper
  bloom_filter.py
  counting_bloom_filter.py
  count_min_sketch.py
tests/
  test_bloom_filter.py
  test_counting_bloom_filter.py
  test_count_min_sketch.py
benchmark.py
requirements.txt
```
