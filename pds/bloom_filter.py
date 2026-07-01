"""A classic Bloom filter: a space-efficient probabilistic set that
supports fast membership testing with no false negatives and a
tunable false positive rate.
"""
import math

from .hash_utils import double_hash


class BloomFilter:
    def __init__(self, expected_items: int, false_positive_rate: float = 0.01):
        if expected_items <= 0:
            raise ValueError("expected_items must be positive")
        if not 0 < false_positive_rate < 1:
            raise ValueError("false_positive_rate must be in (0, 1)")

        self.expected_items = expected_items
        self.false_positive_rate = false_positive_rate
        self.size = self._optimal_size(expected_items, false_positive_rate)
        self.num_hashes = self._optimal_num_hashes(self.size, expected_items)
        self.bits = bytearray((self.size + 7) // 8)
        self.count = 0

    @staticmethod
    def _optimal_size(n: int, p: float) -> int:
        return max(1, math.ceil(-(n * math.log(p)) / (math.log(2) ** 2)))

    @staticmethod
    def _optimal_num_hashes(m: int, n: int) -> int:
        return max(1, round((m / n) * math.log(2)))

    def _set_bit(self, index: int) -> None:
        self.bits[index // 8] |= 1 << (index % 8)

    def _get_bit(self, index: int) -> int:
        return (self.bits[index // 8] >> (index % 8)) & 1

    def add(self, item: str) -> None:
        for index in double_hash(item, self.num_hashes, self.size):
            self._set_bit(index)
        self.count += 1

    def __contains__(self, item: str) -> bool:
        return all(self._get_bit(i) for i in double_hash(item, self.num_hashes, self.size))

    def current_false_positive_rate(self) -> float:
        """Estimate of the current false positive rate given how full the
        filter actually is (as opposed to the design-time target)."""
        if self.size == 0:
            return 0.0
        fraction_set = sum(bin(byte).count("1") for byte in self.bits) / self.size
        return fraction_set ** self.num_hashes

    def __len__(self) -> int:
        return self.count
