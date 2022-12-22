from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TextIO, Type

Value = complex


class Operator(ABC):
    @staticmethod
    @abstractmethod
    def forward(lhs: Value, rhs: Value) -> Value:
        pass


class Plus(Operator):
    @staticmethod
    def forward(lhs: Value, rhs: Value) -> Value:
        return lhs + rhs


class Minus(Operator):
    @staticmethod
    def forward(lhs: Value, rhs: Value) -> Value:
        return lhs - rhs


class Mul(Operator):
    @staticmethod
    def forward(lhs: Value, rhs: Value) -> Value:
        return lhs * rhs


class Div(Operator):
    @staticmethod
    def forward(lhs: Value, rhs: Value) -> Value:
        return lhs / rhs


OPERATORS: dict[str, Type[Operator]] = {"+": Plus, "-": Minus, "*": Mul, "/": Div}


@dataclass
class OperatorExpression:
    lhs: Value | str
    rhs: Value | str
    operator: Type[Operator]


Expression = Value | OperatorExpression


@dataclass
class Monkey:
    expr: Expression


def parse_monkeys(inp: TextIO):
    res = dict[str, Monkey]()
    for line in inp:
        tokens = line.split()
        name = tokens[0][:-1]
        if len(tokens) == 2:
            monkey = Monkey(int(tokens[1]))
        else:
            lhs = tokens[1]
            rhs = tokens[3]
            if lhs.isnumeric():
                lhs = complex(int(lhs))
            if rhs.isnumeric():
                rhs = complex(int(rhs))
            monkey = Monkey(OperatorExpression(lhs, rhs, OPERATORS[tokens[2]]))
        res[name] = monkey

    return res


def resolve(monkeys: dict[str, Monkey], arg: Value | str) -> Value:
    if isinstance(arg, Value):
        return arg
    monkey = monkeys[arg]
    if isinstance(monkey.expr, OperatorExpression):
        expr = monkey.expr
        monkey.expr = expr.operator.forward(
            resolve(monkeys, expr.lhs), resolve(monkeys, expr.rhs)
        )
    return monkey.expr


def part1(inp: TextIO) -> int:
    monkeys = parse_monkeys(inp)
    res = resolve(monkeys, "root")
    return int(res.real)


def part2(inp: TextIO) -> int:
    monkeys = parse_monkeys(inp)
    root = monkeys["root"]
    human = monkeys["humn"]
    human.expr = complex(0, 1)  # Using the imaginary unit as a placeholder for 'humn'
    assert not isinstance(root.expr, Value)
    lhs = resolve(monkeys, root.expr.lhs)
    rhs = resolve(monkeys, root.expr.rhs)

    # Solve a + bx = c + dx for x
    real_part = lhs.real - rhs.real
    imag_part = rhs.imag - lhs.imag
    return int(real_part / imag_part)
