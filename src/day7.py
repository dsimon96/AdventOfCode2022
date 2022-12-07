from itertools import chain
from typing import Generator, Optional, TextIO


class File:
    name: str
    size: int

    def __init__(self, name: str, size: int) -> None:
        self.name = name
        self.size = size


class Directory(File):
    parent: Optional["Directory"]
    _contents_idx: dict[str, File]  # indexed by name

    def __init__(self, name: str, parent: Optional["Directory"]) -> None:
        super().__init__(name, 0)
        self.parent = parent
        self._contents_idx = {}

    def __getitem__(self, s: str) -> File:
        return self._contents_idx[s]

    def incr_size(self, delta: int):
        self.size += delta
        if self.parent is not None:
            self.parent.incr_size(delta)

    def insert(self, f: File) -> None:
        self._contents_idx[f.name] = f
        self.incr_size(f.size)

    def walk_dirs(self) -> Generator["Directory", None, None]:
        yield self
        for d in chain.from_iterable(
            f.walk_dirs()
            for f in self._contents_idx.values()
            if isinstance(f, Directory)
        ):
            yield d


PROMPT = "$"
CD = "cd"
LS = "ls"
DIR = "dir"


def do_cd(root: Directory, cur: Directory, arg: str) -> Directory:
    if arg == "/":
        return root
    elif arg == "..":
        parent = cur.parent
        assert parent is not None
        return parent
    else:
        file = cur[arg]
        assert isinstance(file, Directory), "cding to parent of root is undefined"
        return file


def discover_filesystem(inp: TextIO) -> Directory:
    root = Directory("/", None)
    cur = root

    for line in inp:
        tokens = line.rstrip().split()

        if tokens[0] == PROMPT:
            cmd = tokens[1]
            if cmd == LS:
                pass
            elif cmd == CD:
                cur = do_cd(root, cur, tokens[2])
            else:
                raise ValueError(f"Unrecognized cmd {cmd}")
        else:
            # assume this line is the output of a prior 'ls'
            if tokens[0] == DIR:
                file = Directory(tokens[1], cur)
            else:
                file = File(tokens[1], int(tokens[0]))

            cur.insert(file)

    return root


def part1(inp: TextIO) -> int:
    fs = discover_filesystem(inp)

    return sum(d.size for d in fs.walk_dirs() if d.size <= 100000)


TOTAL_DISK_SIZE = 70000000
MIN_UNUSED = 30000000


def part2(inp: TextIO) -> int:
    fs = discover_filesystem(inp)
    total_used = fs.size
    max_used = TOTAL_DISK_SIZE - MIN_UNUSED
    min_to_free = total_used - max_used
    # could do this more efficiently - if a directory is not large enough that deleting
    # it would free up enough space, then we don't need to consider any of its
    # subdirectories
    return min(d.size for d in fs.walk_dirs() if d.size >= min_to_free)
