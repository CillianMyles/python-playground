from typing import List
import timeit


SIZE = 1_000_000
MAX_ITERS = 100


def binary_search(element: int, array: List[int]) -> int:
    start = 0
    stop = len(array) - 1
    while start <= stop:
        index = (start + stop) // 2
        pivot = array[index]
        if pivot == element:
            return index
        elif pivot > element:
            stop = index - 1
        elif pivot < element:
            start = index + 1
    return -1


# generate at compile-time
def get_collection() -> List[int]:
    return [i for i in range(SIZE)]


def main():
    time_s = timeit.timeit(
        lambda: binary_search(SIZE - 1, get_collection()),
        number=MAX_ITERS,
    )
    time_ms = time_s * 1_000
    print(f"{time_ms} ms - {SIZE!r} items - binary search - Python")


if __name__ == "__main__":
    main()
