from dataclasses import dataclass
from functools import cached_property
from typing import Collection, Generator, Optional, TextIO
from progress.bar import Bar  # typing: ignore


@dataclass(frozen=True)
class Vec2:
    x: int
    y: int

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    @cached_property
    def magnitude(self) -> int:
        "Taxicab distance"
        return abs(self.x) + abs(self.y)


@dataclass(frozen=True)
class Range:
    lower_incl: int
    upper_incl: int

    def contains(self, other: int) -> bool:
        return self.lower_incl <= other and other <= self.upper_incl

    def mergeable(self, other: "Range") -> bool:
        "Two ranges are mergeable if they are not separated by a gap of at least 1"
        return not (
            other.upper_incl < self.lower_incl - 1
            or self.upper_incl < other.lower_incl - 1
        )

    def merge(self, other: "Range") -> "Range":
        "Merge two ranges, assuming they arge mergeable"
        return Range(
            min(self.lower_incl, other.lower_incl),
            max(self.upper_incl, other.upper_incl),
        )

    @property
    def num_points(self) -> int:
        return 1 + self.upper_incl - self.lower_incl


@dataclass(frozen=True, order=True)
class ExclusionZone:
    sensor: Vec2
    beacon: Vec2

    def contains(self, other: Vec2) -> bool:
        return (other - self.sensor).magnitude <= self.radius

    def intersect_y(self, y: int) -> Optional[Range]:
        remaining = self.radius - abs(y - self.sensor.y)
        if remaining < 0:
            return None
        else:
            return Range(self.sensor.x - remaining, self.sensor.x + remaining)

    @cached_property
    def radius(self):
        return (self.beacon - self.sensor).magnitude


def get_exclusion_zones(inp: TextIO) -> Generator[ExclusionZone, None, None]:
    for line in inp:
        tokens = line.split()
        sensor_x = int(tokens[2][2:-1])
        sensor_y = int(tokens[3][2:-1])
        beacon_x = int(tokens[8][2:-1])
        beacon_y = int(tokens[9][2:])

        yield ExclusionZone(Vec2(sensor_x, sensor_y), Vec2(beacon_x, beacon_y))


def calc_y_projection(
    excl_zones: Collection[ExclusionZone], target_y: int
) -> set[Range]:
    ranges: set[Range] = set()
    for excl_zone in excl_zones:
        new_range = excl_zone.intersect_y(target_y)  # 2000000)
        if new_range is None:
            continue

        # consolidate this range with overlapping ones
        to_merge: set[Range] = set()
        new_ranges: set[Range] = set()
        for range in ranges:
            if new_range.mergeable(range):
                to_merge.add(range)
            else:
                new_ranges.add(range)

        for range in to_merge:
            new_range = new_range.merge(range)
        new_ranges.add(new_range)

        ranges = new_ranges

    return ranges


def part1(inp: TextIO) -> int:
    TARGET_Y = 2000000

    excl_zones = list(get_exclusion_zones(inp))
    on_target_line: set[int] = set(
        excl_zone.beacon.x for excl_zone in excl_zones if excl_zone.beacon.y == TARGET_Y
    )
    excl_ranges = calc_y_projection(excl_zones, TARGET_Y)

    total_points = sum(range.num_points for range in excl_ranges)
    occupied_by_beacons = sum(
        1
        for beacon_x in on_target_line
        if any(range.contains(beacon_x) for range in excl_ranges)
    )

    return total_points - occupied_by_beacons


def find_sensor_pos_on_line(
    excl_zones: Collection[ExclusionZone], y: int
) -> Optional[Vec2]:
    TARGET_X_RANGE = Range(0, 4000000)

    x = TARGET_X_RANGE.lower_incl
    while x <= TARGET_X_RANGE.upper_incl:
        for excl_zone in excl_zones:
            excl_range = excl_zone.intersect_y(y)
            if excl_range is not None and excl_range.contains(x):
                x = excl_range.upper_incl + 1
                break
        else:
            # if we got here, x was not within any range
            return Vec2(x, y)


def part2(inp: TextIO) -> int:
    TARGET_Y_RANGE = Range(0, 4000000)
    excl_zones = list(get_exclusion_zones(inp))
    with Bar("Searching", max=TARGET_Y_RANGE.num_points) as bar:
        for y in range(TARGET_Y_RANGE.lower_incl, TARGET_Y_RANGE.upper_incl + 1):
            if (pos := find_sensor_pos_on_line(excl_zones, y)) is not None:
                return 4000000 * pos.x + pos.y
            bar.next()

    return -1
