import os
import random
import string
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pds import BloomFilter


def random_word(length=8):
    return "".join(random.choices(string.ascii_lowercase, k=length))


def test_no_false_negatives():
    words = [random_word() for _ in range(500)]
    bf = BloomFilter(expected_items=500, false_positive_rate=0.01)
    for word in words:
        bf.add(word)
    for word in words:
        assert word in bf


def test_false_positive_rate_is_reasonable():
    random.seed(42)
    inserted = [random_word() for _ in range(2000)]
    bf = BloomFilter(expected_items=2000, false_positive_rate=0.01)
    for word in inserted:
        bf.add(word)

    inserted_set = set(inserted)
    probes = [random_word() for _ in range(20000)]
    false_positives = sum(1 for word in probes if word not in inserted_set and word in bf)
    observed_rate = false_positives / len(probes)

    # Generous headroom over the 1% target since this is a randomized
    # test; a correct implementation should still land well under 3%.
    assert observed_rate < 0.03


def test_empty_filter_rejects_everything():
    bf = BloomFilter(expected_items=100)
    assert "anything" not in bf
    assert len(bf) == 0


def test_len_tracks_insertions():
    bf = BloomFilter(expected_items=10)
    for i in range(5):
        bf.add(f"item-{i}")
    assert len(bf) == 5
