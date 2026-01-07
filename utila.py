import json
from typing import Tuple, Generator, Any, overload
import math
from pathlib import Path
import os


# process each line of 'data' from the file
def process_data(x: str) -> list[float , str, ...]:
    split = x.strip().split(",")
    return [float(split[0]), *split[1:]] # force first value to a float (the time) for later use


# read data from file & calculate time differences
def read(path: str | Path) -> Tuple[list[float],list[str]]:
    timediffs = []
    with open(path, "r") as fin:
        timestamp, arbitration_id, data_field = fin.readline().split(",") # ignore headers
        data = list(map(process_data, fin.read().strip().split("\n"))) # use process_data function for each line, to extract values


        # calculate time differences
        lasttime=data[0][0]
        for line in data:
            timestamp, arbitration_id, data_field = line
            timediffs.append(timestamp-lasttime)
            lasttime = timestamp
    return timediffs, data


# useful function I wrote, like 'range', but returns windows, aka [(0,2),(2,4),(4,6)] for indexing
# technically works with floats, but cant use float index
def window(*args: list[int | float], include_extra: bool = True) -> Generator[tuple[int | float, int | float], None, None]:
    boundCalc = math.ceil if include_extra else math.floor

    def _window(start: int | float, end: int | float, size: int | float, include_extra: bool) -> Generator[tuple[int | float, int | float], None, None]:
        if size <= 0: raise ValueError("size parameter must be greater than zero")
        for i in range(boundCalc((end - start) / size)):
            yield [start + i * size, start + min((end - start), (i + 1) * size)]

    if len(args) == 3:
        return _window(*args, include_extra=include_extra)
    elif len(args) == 2:
        return _window(0, *args, include_extra=include_extra)
    raise NotImplementedError("Use implemented parameters: (start, end, size) OR (end, size)")


def calc_cache(func):
    def wrapper(file, *args, **kwargs):
        cached_dir = Path("./cache") / (file.stem + ".json")
        if cached_dir.exists():
            print(f"Retrieved data for {file.name}")
            with open(cached_dir) as f:
                return json.load(f)
        else:
            print(f"Calculating data for {file.name}")
            data = func(file, *args, **kwargs)
            with open(cached_dir, "w") as fout:
                json.dump(data, fout)
            return data
    return wrapper
