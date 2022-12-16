from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from typing import Generator, Iterable, Iterator, TextIO, TypeVar
from itertools import chain, combinations
from tqdm import tqdm
import numpy as np

Node = int
ValveGraph = dict[Node, tuple[int, set[Node]]]
NodeDistances = dict[tuple[Node, Node], int]


class BitSet:
    @staticmethod
    def contains(bv: int, node: int) -> bool:
        return (bv >> node) & 1 == 1

    @staticmethod
    def add(bv: int, node: int) -> int:
        return bv | (1 << node)


def parse_line(line: str) -> tuple[str, int, set[str]]:
    tokens = line.split()
    node_name = tokens[1]
    flow_rate = int(tokens[4][5:-1])
    next_nodes = set(node.rstrip(",") for node in tokens[9:])
    return (node_name, flow_rate, next_nodes)


class NodeAssignmentHelper:
    _mapping = dict[str, Node]()
    _next = 0

    def get(self, node: str) -> Node:
        if (val := self._mapping.get(node)) is not None:
            return val

        res = self._next
        self._mapping[node] = res
        self._next += 1
        return res


def get_graph(inp: TextIO) -> tuple[NodeAssignmentHelper, ValveGraph]:
    helper = NodeAssignmentHelper()
    graph = ValveGraph()
    for line in inp:
        node_name, flow_rate, next_nodes = parse_line(line)

        graph[helper.get(node_name)] = (
            flow_rate,
            {helper.get(next_node) for next_node in next_nodes},
        )

    return helper, graph


def get_distances(graph: ValveGraph) -> NodeDistances:
    distances = NodeDistances()

    # Initialize with self-edges and neighbors
    for i, v in graph.items():
        distances[(i, i)] = 0
        for j in v[1]:
            distances[(i, j)] = 1

    # Floyd Warshall
    for k in graph.keys():
        for i in graph.keys():
            for j in graph.keys():
                if (dist_ik := distances.get((i, k))) is None or (
                    dist_kj := distances.get((k, j))
                ) is None:
                    continue

                dist_via_k = dist_ik + dist_kj
                if (i, j) not in distances or distances[(i, j)] > dist_via_k:
                    distances[(i, j)] = dist_via_k

    return distances


def max_flow(
    graph: ValveGraph,
    distances: NodeDistances,
    to_open: set[Node],
    start_node: Node,
    time: int,
) -> int:
    mapping = {node: i for i, node in enumerate(to_open)}
    table = np.full((len(graph), time + 1, 1 << len(to_open)), -1, dtype=np.int32)

    def max_flow_recursive(cur_node: int, time_left: int, open_valves: int = 0) -> int:
        """
        The max total flow that can be achieved by opening more valves, given current
        conditions.
        """
        if time_left <= 0:
            return 0
        elif (res := table[cur_node, time_left, open_valves]) >= 0:
            return res

        flow_rate, _ = graph[cur_node]
        total_flow = 0
        if flow_rate > 0:
            total_flow = flow_rate * (time_left - 1)
            time_left -= 1
            open_valves = BitSet.add(open_valves, mapping[cur_node])

        total_flow += max(
            (
                max_flow_recursive(
                    next_node, time_left - distances[(cur_node, next_node)], open_valves
                )
                for next_node in to_open
                if not BitSet.contains(open_valves, mapping[next_node])
            ),
            default=0,
        )

        table[cur_node, time_left, open_valves] = total_flow
        return total_flow

    return max_flow_recursive(start_node, time)


def part1(inp: TextIO) -> int:
    assignments, graph = get_graph(inp)
    distances = get_distances(graph)
    nonzero_nodes = {k for k, v in graph.items() if v[0] > 0}
    return max_flow(graph, distances, nonzero_nodes, assignments.get("AA"), 30)


T = TypeVar("T")


def powerset(iterable: Iterable[T]) -> Iterator[Iterable[T]]:
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def all_set_partitions(
    orig: set[str],
) -> Generator[tuple[set[str], set[str]], None, None]:
    for my_nodes in powerset(orig):
        yield set(my_nodes), orig.difference(my_nodes)


def max_flow_partitioned(
    graph: ValveGraph,
    distances: NodeDistances,
    my_set: set[Node],
    eleph_set: set[Node],
    start_node: Node,
    time: int,
) -> int:
    return max_flow(graph, distances, my_set, start_node, time) + max_flow(
        graph, distances, eleph_set, start_node, time
    )


def part2(inp: TextIO) -> int:
    assignments, graph = get_graph(inp)
    distances = get_distances(graph)
    nonzero_nodes = {k for k, v in graph.items() if v[0] > 0}
    aa = assignments.get("AA")

    with ProcessPoolExecutor() as ex:
        fs: list[Future[int]] = []
        pset = list(powerset(nonzero_nodes))
        for my_nodes in pset[: len(pset) // 2]:
            my_set = set(my_nodes)
            eleph_set = nonzero_nodes.difference(my_nodes)
            fs.append(
                ex.submit(
                    max_flow_partitioned,
                    graph,
                    distances,
                    my_set,
                    eleph_set,
                    aa,
                    26,
                )
            )

        return max(f.result() for f in tqdm(as_completed(fs), total=len(pset) // 2))
