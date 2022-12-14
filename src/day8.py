from dataclasses import dataclass
from typing import Generator, Iterator, TextIO

Coords = tuple[int, int]


@dataclass
class HeightMap:
    grid: list[list[int]]

    @property
    def height(self) -> int:
        return len(self.grid)

    @property
    def width(self) -> int:
        return len(self.grid[0])

    def __getitem__(self, coords: Coords) -> int:
        return self.grid[coords[0]][coords[1]]


def parse_heightmap(inp: TextIO) -> HeightMap:
    grid: list[list[int]] = []
    for line in inp:
        line = line.rstrip()

        grid.append(list(int(c) for c in line))

    return HeightMap(grid)


def scan_for_visible(
    heightmap: HeightMap, coords_it: Iterator[Coords]
) -> Generator[Coords, None, None]:
    max_height = -1
    for coords in coords_it:
        if (height := heightmap[coords]) > max_height:
            max_height = height
            yield coords


def part1(inp: TextIO):
    heightmap = parse_heightmap(inp)

    visible_coords: set[tuple[int, int]] = set()

    for r in range(heightmap.height):
        # scan row left to right
        visible_coords.update(
            scan_for_visible(heightmap, ((r, c) for c in range(heightmap.width)))
        )
        # right to left
        visible_coords.update(
            scan_for_visible(
                heightmap, ((r, c) for c in range(heightmap.width - 1, -1, -1))
            )
        )

    for c in range(heightmap.width):
        # scan col top to bottom
        visible_coords.update(
            scan_for_visible(heightmap, ((r, c) for r in range(heightmap.height)))
        )
        # bottom to top
        visible_coords.update(
            scan_for_visible(
                heightmap, ((r, c) for r in range(heightmap.height - 1, -1, -1))
            )
        )

    return len(visible_coords)


def get_blockage_dist(
    heightmap: HeightMap, height: int, coord_it: Iterator[Coords]
) -> int:
    n = 0
    for coord in coord_it:
        n += 1
        if heightmap[coord] >= height:
            break

    return n


def part2(inp: TextIO):
    heightmap = parse_heightmap(inp)

    max_score = 0
    for r in range(heightmap.height):
        for c in range(heightmap.width):
            height = heightmap[(r, c)]
            score = (
                get_blockage_dist(
                    heightmap, height, ((r, c) for r in range(r - 1, -1, -1))
                )
                * get_blockage_dist(
                    heightmap, height, ((r, c) for r in range(r + 1, heightmap.height))
                )
                * get_blockage_dist(
                    heightmap, height, ((r, c) for c in range(c - 1, -1, -1))
                )
                * get_blockage_dist(
                    heightmap, height, ((r, c) for c in range(c + 1, heightmap.width))
                )
            )

            max_score = max(max_score, score)

    return max_score
