from collections import defaultdict, deque
from enum import Enum, auto
from typing import TextIO

Point = tuple[int, int, int]


class Axis(Enum):
    X = auto()
    Y = auto()
    Z = auto()


def part1(inp: TextIO) -> int:
    is_surface: dict[tuple[Point, Axis], bool] = defaultdict(bool)
    for line in inp:
        # Every time we add a new cube, the state of its faces are 'flipped'. If it is
        # not already part of the surface, adding that cube makes it part of the
        # surface. If it is, then adding that cube makes that face internal to the
        # droplet.
        x, y, z = (int(s) for s in line.split(","))

        for face in [
            ((x, y, z), Axis.X),
            ((x + 1, y, z), Axis.X),
            ((x, y, z), Axis.Y),
            ((x, y + 1, z), Axis.Y),
            ((x, y, z), Axis.Z),
            ((x, y, z + 1), Axis.Z),
        ]:
            is_surface[face] = not is_surface[face]

    return sum(1 for val in is_surface.values() if val)


def part2(inp: TextIO) -> int:
    points: set[Point] = {tuple(int(s) for s in line.split(",")) for line in inp}

    # Floodfill the region containing the droplets from the outside, marking each time
    # we run into an exposed face
    x_min = min(x for x, _, _ in points)
    x_max = max(x for x, _, _ in points)
    y_min = min(y for _, y, _ in points)
    y_max = max(y for _, y, _ in points)
    z_min = min(z for _, _, z in points)
    z_max = max(z for _, _, z in points)

    num_faces = 0
    start_point = (x_min - 1, y_min - 1, z_min - 1)
    visited = {start_point}
    to_visit = deque((start_point,))
    while to_visit:
        x, y, z = to_visit.popleft()

        for dx, dy, dz in [
            (-1, 0, 0),
            (1, 0, 0),
            (0, -1, 0),
            (0, 1, 0),
            (0, 0, -1),
            (0, 0, 1),
        ]:
            next_point = (x + dx, y + dy, z + dz)
            nx, ny, nz = next_point
            if not (
                x_min - 1 <= nx <= x_max + 1
                and y_min - 1 <= ny <= y_max + 1
                and z_min - 1 <= nz <= z_max + 1
            ):
                continue
            elif next_point in visited:
                continue
            elif next_point in points:
                num_faces += 1
            else:
                visited.add(next_point)
                to_visit.append(next_point)

    return num_faces
