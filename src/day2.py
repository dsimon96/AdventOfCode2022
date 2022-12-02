import logging
from enum import Enum
from typing import Callable, Generator, TextIO, Tuple

logger = logging.getLogger(__file__)


class Outcome(Enum):
    LOSS = -1
    DRAW = 0
    WIN = 1

    def score(self) -> int:
        return 3 * (self.value + 1)


class Shape(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

    def score(self) -> int:
        return self.value + 1

    def __gt__(self, other: "Shape") -> bool:
        return (self.value - other.value) % 3 == 1

    def __add__(self, other: Outcome) -> "Shape":
        return Shape((self.value + other.value) % 3)


Round = Tuple[Shape, Outcome]
RoundFunc = Callable[[Shape, str], Round]

OPP_CODE = {"A": Shape.ROCK, "B": Shape.PAPER, "C": Shape.SCISSORS}
P1_CODE = {"X": Shape.ROCK, "Y": Shape.PAPER, "Z": Shape.SCISSORS}
P2_CODE = {"X": Outcome.LOSS, "Y": Outcome.DRAW, "Z": Outcome.WIN}


def get_outcome(opp_shape: Shape, my_shape: Shape) -> Outcome:
    if my_shape > opp_shape:
        return Outcome.WIN
    elif my_shape == opp_shape:
        return Outcome.DRAW
    else:
        return Outcome.LOSS


def p1_round_func(opp_shape: Shape, code: str) -> Round:
    shape = P1_CODE[code]
    return (shape, get_outcome(opp_shape, shape))


def p2_round_func(opp_shape: Shape, code: str) -> Round:
    outcome = P2_CODE[code]
    return (opp_shape + outcome, outcome)


def get_scores(inp: TextIO, round_fn: RoundFunc) -> Generator[int, None, None]:
    for line in inp:
        first, second = line.rstrip().split()
        shape, outcome = round_fn(OPP_CODE[first], second)
        yield shape.score() + outcome.score()


def get_total(inp: TextIO, round_fn: RoundFunc) -> int:
    return sum(get_scores(inp, round_fn))


def part1(inp: TextIO) -> int:
    return get_total(inp, p1_round_func)


def part2(inp: TextIO) -> int:
    return get_total(inp, p2_round_func)
