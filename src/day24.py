from collections import defaultdict, deque
from dataclasses import dataclass
from typing import TextIO

Blizzards = dict[int, set[int]]
State = tuple[int, int, int, int, int]  # row, col, h_offset, v_offset, dest_idx


@dataclass
class Map:
    rows: int
    cols: int
    start_col: int
    end_col: int
    left_blizzards: Blizzards
    right_blizzards: Blizzards
    up_blizzards: Blizzards
    down_blizzards: Blizzards


MOVES = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))


def find_shortest_path(
    map: Map,
    waypoints: list[tuple[int, int]],
) -> int:
    init_state = (waypoints[0][0], waypoints[0][1], 1, 1, 1)
    visited = set[State]((init_state,))
    queue = deque[tuple[State, int]](((init_state, 1),))
    while queue:
        (r, c, h_offset, v_offset, dest_idx), minute = queue.popleft()

        next_h_offset = (h_offset + 1) % (map.cols - 2)
        next_v_offset = (v_offset + 1) % (map.rows - 2)

        for (dr, dc) in MOVES:
            next_r = r + dr
            next_c = c + dc
            if waypoints[dest_idx][0] == next_r and waypoints[dest_idx][1] == next_c:
                dest_idx += 1
                if dest_idx == len(waypoints):
                    return minute
            elif next_r < -1:
                continue
            elif next_r == -1 and next_c != map.start_col:
                continue
            elif next_r > map.rows - 2:
                continue
            elif next_r == map.rows - 2 and next_c != map.end_col:
                continue
            elif next_c < 0 or next_c > map.cols - 2:
                continue
            elif (next_c + h_offset) % (map.cols - 2) in map.left_blizzards[next_r]:
                continue
            elif (next_c - h_offset) % (map.cols - 2) in map.right_blizzards[next_r]:
                continue
            elif (next_r + v_offset) % (map.rows - 2) in map.up_blizzards[next_c]:
                continue
            elif (next_r - v_offset) % (map.rows - 2) in map.down_blizzards[next_c]:
                continue
            elif (next_r, next_c, next_h_offset, next_v_offset, dest_idx) in visited:
                continue

            next_state = (next_r, next_c, next_h_offset, next_v_offset, dest_idx)
            visited.add(next_state)
            queue.append((next_state, minute + 1))

    raise ValueError


def get_map(inp: TextIO) -> Map:
    "To simplify math later on, indexes are from [-1, width/col - 1)"
    s = [line.rstrip() for line in inp.readlines()]
    rows = len(s)
    cols = len(s[0])
    start_col = s[0].index(".") - 1
    end_col = s[-1].index(".") - 1

    left_blizzards: Blizzards = defaultdict(set)
    right_blizzards: Blizzards = defaultdict(set)
    up_blizzards: Blizzards = defaultdict(set)
    down_blizzards: Blizzards = defaultdict(set)
    for r in range(rows - 2):
        for c in range(cols - 2):
            match s[1 + r][1 + c]:
                case "<":
                    left_blizzards[r].add(c)
                case ">":
                    right_blizzards[r].add(c)
                case "^":
                    up_blizzards[c].add(r)
                case "v":
                    down_blizzards[c].add(r)
                case _:
                    continue

    return Map(
        rows,
        cols,
        start_col,
        end_col,
        left_blizzards,
        right_blizzards,
        up_blizzards,
        down_blizzards,
    )


def part1(inp: TextIO) -> int:
    map = get_map(inp)
    return find_shortest_path(map, [(-1, map.start_col), (map.rows - 2, map.end_col)])


def part2(inp: TextIO) -> int:
    map = get_map(inp)
    start = (-1, map.start_col)
    end = (map.rows - 2, map.end_col)
    return find_shortest_path(map, [start, end, start, end])
