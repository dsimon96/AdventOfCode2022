from dataclasses import dataclass
from enum import Enum
from typing import Generator, TextIO


@dataclass(frozen=True)
class Vec2:
    x: int
    y: int

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    @property
    def magnitude(self) -> int:
        return max(abs(self.x), abs(self.y))


class Direction(Enum):
    U = Vec2(0, -1)
    D = Vec2(0, 1)
    L = Vec2(-1, 0)
    R = Vec2(1, 0)


@dataclass(frozen=True)
class Move:
    direction: Direction
    steps: int


Rope = list[Vec2]


def update_coord(h: int, t: int) -> int:
    return t + max(-1, min(h - t, 1))


def do_step(r: Rope, d: Direction) -> None:
    r[0] += d.value
    for i in range(1, len(r)):
        h = r[i - 1]
        t = r[i]
        if (h - t).magnitude <= 1:
            # this knot doesn't move, and neither does any following
            break
        r[i] = Vec2(update_coord(h.x, t.x), update_coord(h.y, t.y))


def get_moves(inp: TextIO) -> Generator[Move, None, None]:
    for line in inp:
        ds, ss = line.rstrip().split()
        yield Move(Direction[ds], int(ss))  # type: ignore


def do_sim(inp: TextIO, length: int) -> int:
    """
    Simulate the sequence of moves specified by the input on a rope with the specified
    length. Return the number of positions occupied by the tail of the rope
    """
    rope: Rope = [Vec2(0, 0)] * length
    tail_positions: set[Vec2] = {rope[length - 1]}
    for move in get_moves(inp):
        for _ in range(move.steps):
            do_step(rope, move.direction)
            tail_positions.add(rope[length - 1])

    return len(tail_positions)


def part1(inp: TextIO) -> int:
    return do_sim(inp, 2)


def part2(inp: TextIO) -> int:
    return do_sim(inp, 10)
