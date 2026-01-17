#TODO: compile all code into a nice module
import json
import math
import os
from pathlib import Path
from typing import Tuple, Generator

import numpy as np
import pandas as pd


# process each line of 'data' from the file,
@DeprecationWarning
def process_data(x: str) -> list[float , str, ...]:
    split = x.strip().split(",")
    return [float(split[0]), *split[1:]] # force first value to a float (the time) for later use

def getFiles(dir:str, filetype:str = ".csv") -> list[Path]:
    if not Path(dir).exists() and Path(dir).is_dir():
        os.mkdir(dir)
    return [Path(dir) / file for file in os.listdir(dir) if Path(file).suffix == filetype]
# read data from file & calculate time differences
def read(path: str | Path) -> Tuple[list[float],list[str]]:
    df = pd.read_csv(path)
    times = df['timestamp']
    timediffs = [0] + [*np.diff(np.array(times))] # [0] + [float(times[a] - times[a-1]) for a in range(1,len(times))]
    if 'attack' in df:
        attack = list(df['attack'])
    else:
        attack = None
    return timediffs, attack, times

# useful function I wrote, like 'range', but returns windows, aka [(0,2),(2,4),(4,6)] for indexing
def window(*args: int | float, include_extra: bool = True) -> Generator[tuple[int | float, int | float], None, None]:
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

#TODO generalize cache wrapper to use for any function
#TODO FIX CACHE for simple vs not outputs
def calc_cache(func):
    def wrapper(file, *args, cache = True, **kwargs):
        if not isinstance(file, Path):
            file = Path(file)

        cached_dir = Path("./cache")
        if cache and not cached_dir.exists():
            os.mkdir(cached_dir)
        cached_file_path = cached_dir / (file.stem + ".json")
        if cached_file_path.exists() and cache:
            print(f"Retrieved data for {file.name}")
            with open(cached_file_path) as f:
                return json.load(f)
        else:
            print(f"Calculating data for {file.name}")
            data = func(file, *args, **kwargs)
            if cache:
                with open(cached_file_path, "w") as fout:
                    json.dump(data, fout)
            return data
    return wrapper
