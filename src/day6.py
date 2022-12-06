from collections import Counter
from typing import Generic, TextIO, TypeVar

T = TypeVar("T")


class CounterWithUniqueNonzero(Generic[T]):
    _counter: Counter[T] = Counter()
    num_unique: int = 0

    def __getitem__(self, c: T) -> int:
        return self._counter[c]

    def __setitem__(self, c: T, i: int) -> None:
        if i > 0 and self._counter[c] == 0:
            self.num_unique += 1
        elif i == 0 and self._counter[c] > 0:
            self.num_unique -= 1
        self._counter[c] = i


def find_marker(inp: TextIO, window_length: int) -> int:
    counter = CounterWithUniqueNonzero[str]()
    for line in inp:
        line = line.rstrip()

        for c in line[:window_length]:
            counter[c] += 1

        for i in range(window_length, len(line)):
            counter[line[i]] += 1
            counter[line[i - window_length]] -= 1

            if counter.num_unique == window_length:
                return i + 1

    raise ValueError("No marker position")


def part1(inp: TextIO) -> int:
    return find_marker(inp, 4)


def part2(inp: TextIO) -> int:
    return find_marker(inp, 14)
