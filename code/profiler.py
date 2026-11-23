import time
import math
from statistics import mean


timings = {}


def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter_ns() - start
        if func.__qualname__ not in timings:
            timings[func.__qualname__] = []
        timings[func.__qualname__].append(elapsed)
        return result

    return wrapper


def percentile(samples, p):
    samples.sort()
    idx = math.ceil(p * len(samples)) - 1
    return samples[idx]


def print_timings():
    for name, samples in timings.items():
        calls = len(samples)
        average = mean(samples)
        maximum = max(samples)
        ninetieth_percentile = percentile(samples, .90)
        ninety_fifth_percentile = percentile(samples, .95)
        ninety_ninth_percentile = percentile(samples, .99)
        ninety_nine_point_ninth_percentile = percentile(samples, .999)
        print(
            f"{name}:",
            f"calls={calls}",
            f"avg={average / 1_000_000:.3f} ms",
            f"max={maximum / 1_000_000:.3f} ms",
            f"90p={ninetieth_percentile / 1_000_000:.3f} ms",
            f"95p={ninety_fifth_percentile / 1_000_000:.3f} ms",
            f"99p={ninety_ninth_percentile / 1_000_000:.3f} ms",
            f"99.9p={ninety_nine_point_ninth_percentile / 1_000_000:.3f} ms",
        )


def clear_timings():
    timings.clear()