import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pds import CountMinSketch


def test_estimate_never_undercounts():
    random.seed(7)
    stream = [random.choice("abcdefghij") for _ in range(5000)]
    true_counts = Counter(stream)

    cms = CountMinSketch(error_rate=0.01, confidence=0.99)
    for item in stream:
        cms.add(item)

    for item, true_count in true_counts.items():
        assert cms.estimate(item) >= true_count


def test_estimate_is_reasonably_tight_for_heavy_hitters():
    random.seed(7)
    stream = ["hot"] * 3000 + [f"cold-{i % 200}" for i in range(3000)]
    random.shuffle(stream)

    cms = CountMinSketch(error_rate=0.005, confidence=0.99)
    for item in stream:
        cms.add(item)

    estimate = cms.estimate("hot")
    assert 3000 <= estimate <= 3100


def test_len_tracks_total_additions():
    cms = CountMinSketch()
    for i in range(10):
        cms.add(f"item-{i}", count=i + 1)
    assert len(cms) == sum(range(1, 11))
