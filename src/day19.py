from collections import UserDict
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from enum import IntEnum
from itertools import islice
from math import prod
from typing import Generator, TextIO

from tqdm import tqdm


class Resource(IntEnum):
    ORE = 0
    CLAY = 1
    OBSIDIAN = 2
    GEODE = 3


class ResourceCount(UserDict[Resource, int]):
    def __getitem__(self, key: Resource) -> int:
        return self.data.get(key, 0)

    def __hash__(self) -> int:
        return hash(tuple(self[resource] for resource in Resource))


@dataclass
class Blueprint:
    id: int
    robots: dict[Resource, ResourceCount]

    def cost_bound(self) -> ResourceCount:
        return ResourceCount(
            {
                resource: max(
                    cost[resource] for cost in self.robots.values() if resource in cost
                )
                for resource in Resource
                if resource != Resource.GEODE
            }
        )


def ceil_div(x: int, y: int) -> int:
    return -(x // -y)


@dataclass(frozen=True)
class State:
    minutes: int
    robots: ResourceCount
    resources: ResourceCount


def max_geodes(bp: Blueprint, init_minutes: int) -> int:
    init_state = State(init_minutes, ResourceCount({Resource.ORE: 1}), ResourceCount())

    cost_bound = bp.cost_bound()

    visited = set((init_state,))
    queue = [init_state]
    best_seen = 0
    while queue:
        state = queue.pop()
        best_seen = max(
            best_seen,
            state.resources[Resource.GEODE]
            + state.robots[Resource.GEODE] * state.minutes,
        )

        upper_bound = (
            state.robots[Resource.GEODE] * state.minutes
            + (state.minutes + 1) * state.minutes // 2
        )
        if state.resources[Resource.GEODE] + upper_bound <= best_seen:
            continue

        # what if we choose not to build another robot?
        new_state = State(
            0,
            state.robots,
            ResourceCount(
                {
                    resource: state.resources[resource]
                    + state.minutes * state.robots[resource]
                    for resource in Resource
                }
            ),
        )
        visited.add(new_state)
        queue.append(new_state)

        for robot_type, cost in bp.robots.items():
            if (
                robot_type != Resource.GEODE
                and state.robots[robot_type] >= cost_bound[robot_type]
            ):
                # don't need to build more robots of this type
                continue

            if any(
                state.robots[resource] == 0
                for resource, needed in cost.items()
                if needed > 0
            ):
                # Don't have the robots needed to produce requisite materials
                continue

            wait_time = max(
                (
                    ceil_div(
                        (needed - state.resources[resource]), state.robots[resource]
                    )
                    for resource, needed in cost.items()
                    if state.resources[resource] < needed
                ),
                default=0,
            )
            if wait_time >= state.minutes:
                # won't get to use this robot's output anyway
                continue

            new_resources = ResourceCount(
                {
                    resource: state.resources[resource]
                    + (state.robots[resource] * (wait_time + 1))
                    - cost[resource]
                    for resource in Resource
                }
            )

            new_robots = state.robots.copy()
            new_robots[robot_type] += 1

            new_state = State(state.minutes - wait_time - 1, new_robots, new_resources)
            if new_state not in visited:
                visited.add(new_state)
                queue.append(new_state)

    return best_seen


def parse_blueprint(s: str) -> Blueprint:
    tokens = s.split()
    id = int(tokens[1][:-1])
    robots = dict[Resource, ResourceCount]()
    robots[Resource.ORE] = ResourceCount({Resource.ORE: int(tokens[6])})
    robots[Resource.CLAY] = ResourceCount({Resource.ORE: int(tokens[12])})
    robots[Resource.OBSIDIAN] = ResourceCount(
        {
            Resource.ORE: int(tokens[18]),
            Resource.CLAY: int(tokens[21]),
        }
    )
    robots[Resource.GEODE] = ResourceCount(
        {
            Resource.ORE: int(tokens[27]),
            Resource.OBSIDIAN: int(tokens[30]),
        }
    )
    return Blueprint(id, robots)


def get_blueprints(inp: TextIO) -> Generator[Blueprint, None, None]:
    for line in inp:
        yield parse_blueprint(line)


def get_quality_score(bp: Blueprint) -> int:
    return bp.id * max_geodes(bp, 24)


def part1(inp: TextIO) -> int:
    fs = list[Future[int]]()
    with ProcessPoolExecutor() as ex:
        for bp in get_blueprints(inp):
            fs.append(ex.submit(get_quality_score, bp))

        return sum(f.result() for f in tqdm(as_completed(fs), total=len(fs)))


def part2(inp: TextIO) -> int:
    fs = list[Future[int]]()
    with ProcessPoolExecutor() as ex:
        for bp in islice(get_blueprints(inp), 3):
            fs.append(ex.submit(max_geodes, bp, 32))

        return prod(f.result() for f in tqdm(as_completed(fs), total=len(fs)))
