import time
from statistics import mean


timings = {}


def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter_ns() - start
        if func.__name__ not in timings:
            timings[func.__name__] = []
        timings[func.__name__].append(elapsed)
        return result

    return wrapper


def print_timings():
    for name, samples in timings.items():
        calls = len(samples)
        average = mean(samples)
        maximum = max(samples)

        print(
            f"{name}:",
            f"calls={calls}",
            f"avg={average / 1_000_000:.3f} ms",
            f"max={maximum / 1_000_000:.3f} ms",
        )