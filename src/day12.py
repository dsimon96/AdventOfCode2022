from collections import deque
from dataclasses import dataclass
from typing import Callable, TextIO


@dataclass(frozen=True)
class Vec2:
    x: int
    y: int

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)


@dataclass
class Map:
    data: list[list[int]]
    start: Vec2
    end: Vec2

    @property
    def height(self) -> int:
        return len(self.data)

    @property
    def width(self) -> int:
        return len(self.data[0])

    def __getitem__(self, coords: Vec2) -> int:
        return self.data[coords.y][coords.x]

    def __contains__(self, coords: Vec2) -> bool:
        return (
            0 <= coords.x
            and coords.x < self.width
            and 0 <= coords.y
            and coords.y < self.height
        )


def elev(c: str) -> int:
    "Encode elevations from a=0 to z=25"
    if c == "S":
        return 0
    elif c == "E":
        return 25
    else:
        return ord(c) - ord("a")


def get_map(inp: TextIO) -> Map:
    data: list[list[int]] = []
    start = None
    end = None
    for y, line in enumerate(inp):
        row: list[int] = []
        for x, c in enumerate(line.rstrip()):
            row.append(elev(c))
            if c == "S":
                start = Vec2(x, y)
            elif c == "E":
                end = Vec2(x, y)

        data.append(row)

    assert start
    assert end

    return Map(data, start, end)


@dataclass
class SearchNode:
    dist: int
    coords: Vec2


POSSIBLE_STEPS = [Vec2(-1, 0), Vec2(1, 0), Vec2(0, -1), Vec2(0, 1)]


def bfs_reverse_dist(
    map: Map,
    start_pred: Callable[[Map, Vec2], bool],
) -> int:
    """
    Breadth-first-search backwards from `map.end` until finding coords that satisfy the
    given predicate, then return the path distance
    """
    q: deque[SearchNode] = deque()
    q.append(SearchNode(0, map.end))

    visited: set[Vec2] = {map.end}
    while q:
        cur = q.popleft()

        for step in POSSIBLE_STEPS:
            prev = cur.coords + step
            if prev in visited:
                continue
            elif prev not in map:
                continue
            elif map[cur.coords] > map[prev] + 1:
                continue
            elif start_pred(map, prev):
                return cur.dist + 1

            visited.add(prev)
            q.append(SearchNode(cur.dist + 1, prev))

    return -1


def part1(inp: TextIO) -> int:
    map = get_map(inp)
    return bfs_reverse_dist(map, lambda map, coords: coords == map.end)


def part2(inp: TextIO) -> int:
    map = get_map(inp)
    return bfs_reverse_dist(map, lambda map, coords: map[coords] == 0)
