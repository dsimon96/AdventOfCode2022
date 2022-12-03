from typing import Callable, Generator, Iterator, Set, TextIO, Tuple, TypeVar

Rucksack = str

T = TypeVar("T")

RucksackTupleGen = Generator[Tuple[Rucksack, ...], None, None]

GetRucksacksFunc = Callable[[TextIO], RucksackTupleGen]


def common(rucksacks: Tuple[Rucksack, ...]) -> str:
    res: Set[str] = set.intersection(*(set(rs) for rs in rucksacks))  # type: ignore
    assert len(res) == 1
    return res.pop()


def score(badge: str) -> int:
    if badge.islower():
        return 1 + ord(badge) - ord("a")
    else:
        return 27 + ord(badge) - ord("A")


def get_total_score(inp: TextIO, get_rucksacks_fn: GetRucksacksFunc) -> int:
    return sum(score(common(tup)) for tup in get_rucksacks_fn(inp))


def get_rucksacks_p1(inp: TextIO) -> RucksackTupleGen:
    for line in inp:
        line = line.rstrip()

        demarcation = len(line) // 2
        yield (line[:demarcation], line[demarcation:])


def part1(inp: TextIO) -> int:
    return get_total_score(inp, get_rucksacks_p1)


def yield3(iter: Iterator[T]) -> Generator[Tuple[T, T, T], None, None]:
    """
    Yield tuples of three items at a time from the given iterator. If the length of the
    iterator is not a multiple of three, the final one or two items will be omitted
    """
    try:
        while True:
            yield (next(iter), next(iter), next(iter))
    except StopIteration:
        pass


def get_rucksacks_p2(inp: TextIO) -> RucksackTupleGen:
    return yield3(line.rstrip() for line in inp)


def part2(inp: TextIO) -> int:
    return get_total_score(inp, get_rucksacks_p2)
