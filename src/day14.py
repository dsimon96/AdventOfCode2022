from dataclasses import dataclass
from typing import TextIO


@dataclass(frozen=True)
class Vec2:
    x: int
    y: int


def parse_vec2(s: str) -> Vec2:
    xs, ys = s.split(",")
    return Vec2(int(xs), int(ys))


def mark_line(occupied: set[Vec2], s: str):
    markers = s.split(" -> ")
    start_point = parse_vec2(markers[0])
    occupied.add(start_point)
    for end_point_s in markers[1:]:
        end_point = parse_vec2(end_point_s)
        if start_point.x == end_point.x:
            smaller_y, larger_y = sorted((start_point.y, end_point.y))
            occupied.update(
                Vec2(start_point.x, y) for y in range(smaller_y, larger_y + 1)
            )
        else:
            smaller_x, larger_x = sorted((start_point.x, end_point.x))
            occupied.update(
                Vec2(x, start_point.y) for x in range(smaller_x, larger_x + 1)
            )
        start_point = end_point


def sim(inp: TextIO, has_floor: bool) -> int:
    occupied: set[Vec2] = set()
    for line in inp:
        mark_line(occupied, line.rstrip())

    max_y = max(point.y for point in occupied)
    cur = Vec2(500, 0)
    num_placed = 0
    backtrack: list[Vec2] = []
    while has_floor or cur.y < max_y:
        if has_floor and cur.y + 1 == max_y + 2:
            num_placed += 1
            occupied.add(cur)
            cur = backtrack.pop()
        elif (next := Vec2(cur.x, cur.y + 1)) not in occupied:
            backtrack.append(cur)
            cur = next
        elif (next := Vec2(cur.x - 1, cur.y + 1)) not in occupied:
            backtrack.append(cur)
            cur = next
        elif (next := Vec2(cur.x + 1, cur.y + 1)) not in occupied:
            backtrack.append(cur)
            cur = next
        else:
            num_placed += 1
            occupied.add(cur)
            if not backtrack:
                break
            cur = backtrack.pop()

    return num_placed


def part1(inp: TextIO) -> int:
    return sim(inp, False)


def part2(inp: TextIO) -> int:
    return sim(inp, True)
