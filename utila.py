import atexit
import math
import os
import time
from functools import cache
from pathlib import Path
from typing import Generator, Any
import dotenv
import numpy as np
import pandas as pd
import requests

dotenv.load_dotenv()

def getFiles(dir:str, filetype:str = ".csv") -> list[Path]:
    if not Path(dir).exists() and Path(dir).is_dir():
        os.mkdir(dir)
    return [Path(dir) / file for file in os.listdir(dir) if Path(file).suffix == filetype]


# read data from file & calculate time differences
@cache # functools cache
def read(path: str | Path) -> tuple[list[int], list[Any] | None, Any]:
    if not isinstance(path, Path):
        path = Path(path)
    df = pd.read_csv(path)
    times = df['timestamp']
    timediffs = [0] + [*np.diff(np.array(times))] # [0] + [float(times[a] - times[a-1]) for a in range(1,len(times))]
    if 'attack' in df:
        attack = list(map(int, df['attack']))
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


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time()-start} seconds")
        return value
    return wrapper

def discord_log(text):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url is None:
        data = {"content": text}
        response = requests.post(webhook_url, json=data)
        return response

def log_time_setup():
    start = time.time()
    def log_time(start):
        print(f"Took {time.time() - start} seconds.")
    atexit.register(log_time, start)