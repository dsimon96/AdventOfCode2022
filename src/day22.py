from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterator, Optional, TextIO, Type


class Heading(IntEnum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

    def rotate(self, dir: str) -> "Heading":
        delta = 1 if dir == "R" else -1
        return Heading((self.value + delta) % len(Heading))


@dataclass
class State:
    x: int
    y: int
    hdg: Heading


@dataclass
class Map:
    data: list[list[Optional[bool]]]
    leftmost: list[int] = field(init=False)
    y_rng: list[tuple[int, int]] = field(init=False)
    width: int = field(init=False)

    def __post_init__(self):
        self.leftmost = [
            next((i for i, val in enumerate(row) if val is not None))
            for row in self.data
        ]
        self.width = max(len(row) for row in self.data)
        self.y_rng = [
            (
                next(
                    (
                        i
                        for i, row in enumerate(self.data)
                        if col < len(row) and row[col] is not None
                    )
                ),
                next(
                    (
                        len(self.data) - 1 - i
                        for i, row in enumerate(reversed(self.data))
                        if col < len(row) and row[col] is not None
                    )
                ),
            )
            for col in range(self.width)
        ]

    def get_next(self, s: State) -> State:
        match s.hdg:
            case Heading.UP:
                if s.y > 0 and self.data[s.y - 1][s.x] is not None:
                    return State(s.x, s.y - 1, s.hdg)
                else:
                    return State(s.x, self.y_rng[s.x][1], s.hdg)
            case Heading.LEFT:
                if s.x > 0 and self.data[s.y][s.x - 1] is not None:
                    return State(s.x - 1, s.y, s.hdg)
                else:
                    return State(len(self.data[s.y]) - 1, s.y, s.hdg)
            case Heading.DOWN:
                if s.y < len(self.data) - 1 and s.x < len(self.data[s.y + 1]):
                    return State(s.x, s.y + 1, s.hdg)
                else:
                    return State(s.x, self.y_rng[s.x][0], s.hdg)
            case Heading.RIGHT:
                if s.x < len(self.data[s.y]) - 1:
                    return State(s.x + 1, s.y, s.hdg)
                else:
                    return State(self.leftmost[s.y], s.y, s.hdg)


def parse_char(c: str) -> Optional[bool]:
    match c:
        case " ":
            return None
        case ".":
            return False
        case "#":
            return True
        case _:
            raise ValueError(c)


Move = int | str


def iter_moves(s: str) -> Iterator[Move]:
    buf = ""
    for c in s:
        if c.isdigit():
            buf += c
        else:
            yield int(buf)
            yield c
            buf = ""

    if buf:
        yield int(buf)


def parse_inp(inp: TextIO, map_type: Type[Map]) -> tuple[Map, Iterator[Move]]:
    m = list[list[Optional[bool]]]()
    for line in inp:
        line = line.rstrip()
        if not line:
            break

        m.append([parse_char(c) for c in line])

    return (map_type(m), iter_moves(inp.readline().rstrip()))


def do_move(m: Map, move: Move, state: State) -> State:
    if isinstance(move, str):
        state.hdg = state.hdg.rotate(move)
        return state

    for _ in range(move):
        new_s = m.get_next(state)
        if m.data[new_s.y][new_s.x]:
            return state

        state = new_s

    return state


def navigate(m: Map, moves: Iterator[Move]) -> int:
    s = State(m.leftmost[0], 0, Heading.RIGHT)
    for move in moves:
        s = do_move(m, move, s)

    return 1000 * (1 + s.y) + 4 * (1 + s.x) + s.hdg.value


def part1(inp: TextIO) -> int:
    m, moves = parse_inp(inp, Map)

    return navigate(m, moves)


class HardcodedCubeMap(Map):
    def get_next(self, s: State) -> State:
        match s.hdg:
            case Heading.UP:
                if s.y > 0 and self.data[s.y - 1][s.x] is not None:
                    return State(s.x, s.y - 1, s.hdg)
                elif s.x < 50:
                    return State(50, 50 + s.x, Heading.RIGHT)
                elif s.x < 100:
                    return State(0, 150 + s.x - 50, Heading.RIGHT)
                else:
                    return State(s.x - 100, 199, Heading.UP)
            case Heading.LEFT:
                if s.x > 0 and self.data[s.y][s.x - 1] is not None:
                    return State(s.x - 1, s.y, s.hdg)
                elif s.y < 50:
                    return State(0, 149 - s.y, Heading.RIGHT)
                elif s.y < 100:
                    return State(s.y - 50, 100, Heading.DOWN)
                elif s.y < 150:
                    return State(50, 49 - (s.y - 100), Heading.RIGHT)
                else:
                    return State(50 + (s.y - 150), 0, Heading.DOWN)
            case Heading.DOWN:
                if s.y < len(self.data) - 1 and s.x < len(self.data[s.y + 1]):
                    return State(s.x, s.y + 1, s.hdg)
                elif s.x < 50:
                    return State(100 + s.x, 0, Heading.DOWN)
                elif s.x < 100:
                    return State(49, 150 + (s.x - 50), Heading.LEFT)
                else:
                    return State(99, 50 + (s.x - 100), Heading.LEFT)
            case Heading.RIGHT:
                if s.x < len(self.data[s.y]) - 1:
                    return State(s.x + 1, s.y, s.hdg)
                elif s.y < 50:
                    return State(99, 149 - s.y, Heading.LEFT)
                elif s.y < 100:
                    return State(100 + (s.y - 50), 49, Heading.UP)
                elif s.y < 150:
                    return State(149, 49 - (s.y - 100), Heading.LEFT)
                else:
                    return State(50 + (s.y - 150), 149, Heading.UP)


def part2(inp: TextIO) -> int:
    m, moves = parse_inp(inp, HardcodedCubeMap)

    return navigate(m, moves)
