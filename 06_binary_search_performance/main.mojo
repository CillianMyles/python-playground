from benchmark import run, keep
from collections import List


alias SIZE = 1000000
alias NUM_WARMUP = 0
alias MAX_ITERS = 100


fn mojo_binary_search(element: Int, array: List[Int]) -> Int:
    var start = 0
    var stop = len(array) - 1
    while start <= stop:
        let index = (start + stop) // 2
        let pivot = array[index]
        if pivot == element:
            return index
        elif pivot > element:
            stop = index - 1
        elif pivot < element:
            start = index + 1
    return -1


@parameter  # statement runs at compile-time.
fn get_collection() -> List[Int]:
    var v = List[Int](SIZE)
    for i in range(SIZE):
        v.append(i)
    return v


fn test_mojo_binary_search() -> Float64:
    fn test_closure():
        _ = mojo_binary_search(SIZE - 1, get_collection())
    return Float64(run[test_closure] benchmark(NUM_WARMUP, MAX_ITERS).run[test_closure]()) / 1e9


fn main():
    print(
        "Average execution time of func in sec ",
        test_mojo_binary_search(),
    )
