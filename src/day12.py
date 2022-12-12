from collections import deque
from dataclasses import dataclass
from typing import Annotated, Callable, TextIO


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

EndConditionFunc = Callable[[Map, Vec2], bool]

TraversabilityFunc = Annotated[
    Callable[[int, int], bool],
    """
    f(cur, next) == True iff search should proceed from a node of height `cur` to a node
    of height `next`
    """,
]


def map_bfs_dist(
    map: Map,
    start: Vec2,
    can_traverse: TraversabilityFunc,
    is_end: EndConditionFunc,
) -> int:
    q: deque[SearchNode] = deque()
    q.append(SearchNode(0, start))

    visited: set[Vec2] = {start}
    while q:
        cur = q.popleft()
        cur_elev = map.data[cur.coords.y][cur.coords.x]

        for step in POSSIBLE_STEPS:
            next = cur.coords + step

            if not (
                0 <= next.x
                and next.x < map.width
                and 0 <= next.y
                and next.y < map.height
            ):
                continue

            if not can_traverse(cur_elev, map.data[next.y][next.x]):
                continue

            if is_end(map, next):
                return cur.dist + 1
            elif next in visited:
                continue

            visited.add(next)
            q.append(SearchNode(cur.dist + 1, next))

    return -1


def part1(inp: TextIO) -> int:
    map = get_map(inp)
    can_climb: TraversabilityFunc = lambda cur, next: next <= cur + 1
    is_end_coords: EndConditionFunc = lambda map, coords: map.end == coords

    return map_bfs_dist(map, map.start, can_climb, is_end_coords)


def part2(inp: TextIO) -> int:
    map = get_map(inp)
    can_climb_in_reverse: TraversabilityFunc = lambda cur, next: cur <= next + 1
    is_zero_elev: EndConditionFunc = (
        lambda map, coords: map.data[coords.y][coords.x] == 0
    )

    return map_bfs_dist(map, map.end, can_climb_in_reverse, is_zero_elev)
