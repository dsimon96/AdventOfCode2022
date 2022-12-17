from collections import deque
from dataclasses import dataclass
from itertools import cycle
from typing import Iterator, Optional, TextIO

import numpy as np
from more_itertools import peekable
from numpy.typing import NDArray

MAP_WIDTH = 7
ROCK_INITIAL_X = 2
ROCK_INITIAL_HEIGHT_OFFSET = 3

Shape = NDArray[np.bool_]


@dataclass
class Piece:
    data: Shape
    x: int
    y: int

    @property
    def width(self):
        return self.data.shape[1]

    @property
    def height(self):
        return self.data.shape[0]


@dataclass
class Map:
    floor_level = 0
    occupied = np.zeros((MAP_WIDTH, 0), dtype=bool)

    def tower_height(self) -> int:
        return (
            1
            + self.floor_level
            + max(col.nonzero()[0].max(initial=-1) for col in self.occupied)
        )

    def _extend_occupied(self, height: int):
        "Extend the underlying NDArray to accommodate a tower of the requested height"
        top_level = self.occupied.shape[1] + self.floor_level
        if height > top_level:
            self.occupied = np.pad(self.occupied, ((0, 0), (0, height - top_level)))

    def _check_collision(self, piece: Piece, dx: int, dy: int):
        "Check if the piece would collide with anything if moved."
        start_x = piece.x + dx
        start_y = piece.y + dy - self.floor_level
        return piece.data.flatten().dot(
            self.occupied[
                start_x : start_x + piece.width,
                start_y : start_y + piece.height,
            ]
            .transpose()
            .flatten()
        )

    def _try_shift(self, piece: Piece, dx: int, dy: int) -> bool:
        "Move the piece if no collision prevents the move. Return whether successful."
        new_piece_x = piece.x + dx
        new_piece_y = piece.y + dy
        if (
            0 <= new_piece_x
            and new_piece_x + piece.width <= MAP_WIDTH
            and self.floor_level <= new_piece_y
            and not self._check_collision(piece, dx, dy)
        ):
            piece.x += dx
            piece.y += dy
            return True
        else:
            return False

    def _effective_floor(self) -> int:
        """
        Determine the effective floor, i.e. the highest row in the map which is
        unreachable by falling pieces
        """
        reachability = np.zeros_like(self.occupied)
        visited = set[tuple[int, int]]()
        to_visit = deque[tuple[int, int]](
            (i, self.occupied.shape[1] - 1) for i in range(MAP_WIDTH)
        )

        while to_visit:
            cur_x, cur_y = to_visit.popleft()
            reachability[cur_x, cur_y] = True

            for nxt in ((cur_x - 1, cur_y), (cur_x + 1, cur_y), (cur_x, cur_y - 1)):
                if (
                    nxt not in visited
                    and 0 <= nxt[0] < MAP_WIDTH
                    and 0 <= nxt[1]
                    and not self.occupied[nxt]
                ):
                    visited.add(nxt)
                    to_visit.append(nxt)

        return min(col.nonzero()[0][0] for col in reachability)

    def _finalize_piece(self, piece: Piece):
        """
        Mark the locations as occupied in the map which the piece currently occupies.
        Also truncates the map if reachability has changed.
        """
        start_y = piece.y - self.floor_level
        self.occupied[
            piece.x : piece.x + piece.width,
            start_y : start_y + piece.height,
        ] |= piece.data.transpose()
        if (effective_floor := self._effective_floor()) > 0:
            self.floor_level += effective_floor
            self.occupied = self.occupied[:, effective_floor:]

    def drop_piece(self, shape: Shape, jet_seq: Iterator[tuple[int, str]]):
        piece = Piece(
            shape, ROCK_INITIAL_X, self.tower_height() + ROCK_INITIAL_HEIGHT_OFFSET
        )
        self._extend_occupied(piece.y + piece.height)

        while True:
            _, jet_direction = next(jet_seq)
            if jet_direction == "<":
                self._try_shift(piece, -1, 0)
            elif jet_direction == ">":
                self._try_shift(piece, 1, 0)

            if not self._try_shift(piece, 0, -1):
                self._finalize_piece(piece)
                break

    def digest(self) -> int:
        "Hash that summarizes the structure of the reachable portion of the tower"
        return hash(
            tuple(
                sum(1 << i if val else 0 for i, val in enumerate(col))
                for col in self.occupied
            )
        )

    def pretty_print(self, piece: Optional[Piece] = None):
        n = len(str(self.tower_height()))
        s = ""
        for r_inv, row in enumerate(reversed(self.occupied.transpose())):
            r = self.occupied.shape[1] - 1 - r_inv + self.floor_level
            s += f"{r:n} |"
            for c, val in enumerate(row):
                if (
                    piece is not None
                    and piece.x <= c < piece.x + piece.width
                    and piece.y <= r < piece.y + piece.height
                    and piece.data[r - piece.y][c - piece.x]
                ):
                    s += "@"
                elif val:
                    s += "#"
                else:
                    s += "."

            s += "|\n"
        s += f"{self.floor_level:n} +{'-' * MAP_WIDTH}+"

        print(s)


SHAPE_SEQ = [
    np.array([[True, True, True, True]]),
    np.array([[False, True, False], [True, True, True], [False, True, False]]),
    np.array([[True, True, True], [False, False, True], [False, False, True]]),
    np.array([[True], [True], [True], [True]]),
    np.array([[True, True], [True, True]]),
]


def part1(inp: TextIO) -> int:
    shape_seq = cycle(SHAPE_SEQ)
    jet_seq = cycle(enumerate(inp.readline().rstrip()))
    map = Map()
    for _ in range(2022):
        map.drop_piece(next(shape_seq), jet_seq)

    return map.tower_height()


def part2(inp: TextIO) -> int:
    TOTAL_STEPS = 1000000000000

    shape_seq = peekable(cycle(enumerate(SHAPE_SEQ)))
    jet_seq = peekable(cycle(enumerate(inp.readline().rstrip())))
    map = Map()

    # For each encountered state, remember when it was encountered and the tower height
    # when it was encountered. This allows us to discover repetitions and fast-forward.
    seen = dict[tuple[int, int, int], tuple[int, int]]()
    for steps_completed in range(TOTAL_STEPS):
        i, _ = shape_seq.peek()
        j, _ = jet_seq.peek()
        state = (i, j, map.digest())
        if state in seen:
            break
        else:
            seen[state] = (steps_completed, map.tower_height())

        _, shape = next(shape_seq)
        map.drop_piece(shape, jet_seq)
    else:
        # Should not get here without first encountering a repetition
        raise RuntimeError

    # skip over as many repetitions as possible
    prev_steps_completed, prev_tower_height = seen[state]
    period = steps_completed - prev_steps_completed
    periods_skipped = (TOTAL_STEPS - steps_completed) // period
    map.floor_level += (map.tower_height() - prev_tower_height) * periods_skipped
    steps_completed += periods_skipped * period

    # resume simulating the remaining steps
    for _ in range(steps_completed, TOTAL_STEPS):
        _, shape = next(shape_seq)
        map.drop_piece(shape, jet_seq)

    return map.tower_height()
