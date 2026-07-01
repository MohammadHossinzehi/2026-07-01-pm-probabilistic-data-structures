"""A Counting Bloom filter: like a standard Bloom filter but each slot is
a small counter instead of a single bit, which makes deletion possible
at the cost of extra memory.
"""
import math

from .hash_utils import double_hash


class CountingBloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01, counter_bits: int = 4):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < false_positive_rate < 1:
            raise ValueError("false_positive_rate must be in (0, 1)")

        self.expected_items = expected_items
        self.false_positive_rate = false_positive_rate
        self.size = self._optimal_size(expected_items, false_positive_rate)
        self.num_hashes = self._optimal_num_hashes(self.size, expected_items)
        self.max_count = (1 << counter_bits) - 1
        self.counters = [0] * self.size
        self.count = 0

    @staticmethod
    def _optimal_size(n: int, p: float) -> int:
        return max(1, math.ceil(-(n * math.log(p)) / (math.log(2) ** 2)))

    @staticmethod
    def _optimal_num_hashes(m: int, n: int) -> int:
        return max(1, round((m / n) * math.log(2)))

    def add(self, item: str) -> None:
        for index in double_hash(item, self.num_hashes, self.size):
            if self.counters[index] < self.max_count:
                self.counters[index] += 1
        self.count += 1

    def remove(self, item: str) -> None:
        """Remove an item. Only safe to call on items that were actually
        added; removing an item that was never added can introduce false
        negatives for other items sharing its slots."""
        if item not in self:
            return
        for index in double_hash(item, self.num_hashes, self.size):
            if self.counters[index] > 0:
                self.counters[index] -= 1
        self.count -= 1

    def __contains__(self, item: str) -> bool:
        return all(self.counters[i] > 0 for i in double_hash(item, self.num_hashes, self.size))

    def __len__(self) -> int:
        return self.count
