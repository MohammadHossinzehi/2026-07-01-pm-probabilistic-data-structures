"""Count-Min Sketch: a probabilistic frequency table that estimates how
many times an item has been seen in a stream using sub-linear space,
trading a small, one-sided overestimation error for that space savings.
"""
import hashlib
import math


class CountMinSketch:
    def __init__(self, width: int = None, depth: int = None, error_rate: float = 0.01, confidence: float = 0.99):
        if width is None:
            width = max(1, math.ceil(math.e / error_rate))
        if depth is None:
            depth = max(1, math.ceil(math.log(1 / (1 - confidence))))

        self.width = width
        self.depth = depth
        self.error_rate = error_rate
        self.confidence = confidence
        self.table = [[0] * width for _ in range(depth)]
        self.total = 0

    def _index(self, item: str, row: int) -> int:
        data = item.encode("utf-8")
        h = hashlib.sha256(row.to_bytes(4, "little") + data).digest()
        return int.from_bytes(h[:8], "little") % self.width

    def add(self, item: str, count: int = 1) -> None:
        for row in range(self.depth):
            col = self._index(item, row)
            self.table[row][col] += count
        self.total += count

    def estimate(self, item: str) -> int:
        return min(self.table[row][self._index(item, row)] for row in range(self.depth))

    def __len__(self) -> int:
        return self.total
