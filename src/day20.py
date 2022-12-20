from itertools import cycle, islice
from typing import Callable, Iterator, Optional, TextIO

from tqdm import tqdm


class Node:
    val: int
    next_orig_order: Optional["Node"]
    next_decoded: "Node"
    prev_decoded: "Node"

    def __init__(self, val: int, prev: Optional["Node"]):
        self.val = val
        self.next_orig_order = None

        if prev:
            prev.next_orig_order = self
            self.next_decoded = prev.next_decoded
            prev.next_decoded = self
            self.next_decoded.prev_decoded = self
            self.prev_decoded = prev

        else:
            self.next_decoded = self
            self.prev_decoded = self

    def swap(self, forward: bool):
        if forward:
            first = self
            second = self.next_decoded
        else:
            first = self.prev_decoded
            second = self

        first.prev_decoded.next_decoded = second
        second.next_decoded.prev_decoded = first

        first.next_decoded = second.next_decoded
        second.prev_decoded = first.prev_decoded

        first.prev_decoded = second
        second.next_decoded = first


class NodeIterator(Iterator[Node]):
    def __init__(
        self,
        first: Node,
        next_fn: Callable[[Node], Optional[Node]],
    ):
        self.cur = first
        self.next_fn = next_fn

    def __iter__(self):
        return self

    def __next__(self) -> Node:
        if self.cur is None:
            raise StopIteration

        node = self.cur
        self.cur = self.next_fn(node)
        return node


class List:
    _len: int = 0
    first: Optional[Node] = None
    last: Optional[Node] = None
    zero: Optional[Node] = None

    def __len__(self) -> int:
        return self._len

    def insert(self, val: int):
        "Insert the given value after the last node"
        self._len += 1
        node = Node(val, self.last)
        if not self.first:
            self.first = node
        if val == 0:
            self.zero = node
        self.last = node

    def orig_order(self) -> NodeIterator:
        assert self.first
        return NodeIterator(self.first, lambda node: node.next_orig_order)

    def zero_order(self) -> NodeIterator:
        assert self.zero
        return NodeIterator(self.zero, lambda node: node.next_decoded)


def decode(inp: TextIO, multiplier: int, num_rounds: int) -> int:
    ls = List()
    for line in inp:
        ls.insert(int(line) * multiplier)

    for cur in tqdm(
        islice(cycle(ls.orig_order()), len(ls) * num_rounds), total=len(ls) * num_rounds
    ):
        for _ in range(abs(cur.val) % (len(ls) - 1)):
            forward = cur.val > 0
            cur.swap(forward)

        cur = cur.next_orig_order

    return sum(cur.val for cur in islice(ls.zero_order(), None, 3001, 1000))


def part1(inp: TextIO) -> int:
    return decode(inp, 1, 1)


def part2(inp: TextIO) -> int:
    return decode(inp, 811589153, 10)
