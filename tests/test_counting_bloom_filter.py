import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pds import CountingBloomFilter


def test_add_and_contains():
    cbf = CountingBloomFilter(expected_items=100)
    cbf.add("apple")
    cbf.add("banana")
    assert "apple" in cbf
    assert "banana" in cbf
    assert "cherry" not in cbf


def test_remove_makes_item_absent():
    cbf = CountingBloomFilter(expected_items=100)
    cbf.add("apple")
    assert "apple" in cbf
    cbf.remove("apple")
    assert "apple" not in cbf
    assert len(cbf) == 0


def test_remove_nonexistent_item_is_a_noop():
    cbf = CountingBloomFilter(expected_items=100)
    cbf.add("apple")
    cbf.remove("banana")
    assert "apple" in cbf
    assert len(cbf) == 1


def test_shared_slots_survive_partial_removal():
    cbf = CountingBloomFilter(expected_items=100)
    cbf.add("apple")
    cbf.add("apple")
    cbf.remove("apple")
    assert "apple" in cbf
