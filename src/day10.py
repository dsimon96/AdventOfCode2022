from typing import Callable, Generator, TextIO


State = int
Args = list[int]

InstructionFn = Callable[[State, Args], tuple[State, int]]


def noop(s: State, _: Args) -> tuple[State, int]:
    return (s, 1)


def addx(s: State, a: Args) -> tuple[State, int]:
    return (s + int(a[0]), 2)


def gen_states(inp: TextIO) -> Generator[State, None, None]:
    "Yield the sequence of states at the beginning of each cycle"
    state = 1
    for line in inp:
        tokens = line.rstrip().split()
        inst = tokens[0]

        next_state, num_cycles = globals()[inst](state, tokens[1:])
        for _ in range(num_cycles):
            yield state
        state = next_state

    yield state


def part1(inp: TextIO) -> int:
    return sum(
        cycle_num * state
        for cycle_num, state in enumerate(gen_states(inp), start=1)
        if (cycle_num - 20) % 40 == 0
    )


CRT_WIDTH = 40
CRT_HEIGHT = 6


def part2(inp: TextIO) -> int:
    crt = ["."] * CRT_HEIGHT * CRT_WIDTH
    for cycle_num, x in enumerate(gen_states(inp), start=1):
        # which pixel in the crt is being drawn
        crt_idx = (cycle_num - 1) % (CRT_WIDTH * CRT_HEIGHT)

        # determine the appropriate value depending on the position of the sprite
        crt_col = (cycle_num - 1) % CRT_WIDTH
        sprite_col = x - 1
        crt[crt_idx] = (
            "#" if sprite_col <= crt_col and crt_col < sprite_col + 3 else "."
        )

    # pretty print the crt
    for row in range(CRT_HEIGHT):
        row_start = row * CRT_WIDTH
        row_end = (row + 1) * CRT_WIDTH
        print("".join(crt[row_start:row_end]))

    return 0
