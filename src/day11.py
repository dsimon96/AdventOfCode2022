from collections import deque
from dataclasses import dataclass
import heapq
import math
import operator
from typing import Callable, Generator, TextIO


@dataclass
class Item:
    worry: int


Operation = Callable[[int], int]


@dataclass(frozen=True)
class Throw:
    target: int
    item: Item


@dataclass()
class Monkey:
    items: deque[Item]
    operation: Operation
    test_divisor: int
    true_target: int
    false_target: int
    inspect_count: int = 0

    def inspect_all(
        self, decrease_worry: bool, divisors_lcm: int
    ) -> Generator[Throw, None, None]:
        while self.items:
            item = self.items.popleft()
            self.inspect_count += 1
            item.worry = self.operation(item.worry)
            if decrease_worry:
                item.worry //= 3

            # each monkey cares only about worry modulo its test divisor. taking mod by
            # the lcm of all of the test divisors allows us to truncate worry without
            # distoring each monkey's check
            item.worry %= divisors_lcm

            target = (
                self.true_target
                if (item.worry % self.test_divisor == 0)
                else self.false_target
            )
            yield Throw(target, item)


def parse_starting_items(line: str) -> deque[Item]:
    "Parse line 'Starting items: {comma-separated list}'"
    return deque(Item(int(s.rstrip(","))) for s in line.strip().split()[2:])


def parse_operation(line: str) -> Operation:
    "Parse line 'Operation: new = old {operator} {operand}'"
    tokens = line.strip().split()

    match tokens[4]:
        case "+":
            op = operator.add
        case "*":
            op = operator.mul
        case _:
            raise ValueError

    if tokens[5] == "old":
        return lambda old: op(old, old)
    else:
        return lambda old: op(old, int(tokens[5]))


def parse_test_divisor(line: str) -> int:
    "Parse line 'Test: divisible by {divisor}'"
    return int(line.strip().split()[3])


def parse_target(line: str) -> int:
    "Parse line 'If (true|false): throw to monkey {num}"
    return int(line.strip().split()[5])


def gen_monkeys(inp: TextIO) -> Generator[Monkey, None, None]:
    while inp.readline():
        items = parse_starting_items(inp.readline())
        operation = parse_operation(inp.readline())
        test_divisor = parse_test_divisor(inp.readline())
        true_target = parse_target(inp.readline())
        false_target = parse_target(inp.readline())
        inp.readline()

        yield Monkey(items, operation, test_divisor, true_target, false_target)


def get_monkey_business(inp: TextIO, decrease_worry: bool, rounds: int) -> int:
    monkeys = list(gen_monkeys(inp))
    lcm = math.lcm(*(monkey.test_divisor for monkey in monkeys))

    for _ in range(rounds):
        for monkey in monkeys:
            for throw in monkey.inspect_all(decrease_worry, lcm):
                monkeys[throw.target].items.append(throw.item)

    a, b = heapq.nlargest(2, (monkey.inspect_count for monkey in monkeys))
    return a * b


def part1(inp: TextIO) -> int:
    return get_monkey_business(inp, True, 20)


def part2(inp: TextIO) -> int:
    return get_monkey_business(inp, False, 10000)
