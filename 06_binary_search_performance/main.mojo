import benchmark
from benchmark import Unit
from collections import List


alias SIZE = 1_000_000
alias MAX_ITERS = 100
alias NUM_WARMUP = 0


fn binary_search(element: Int, array: List[Int]) -> Int:
    var start = 0
    var stop = len(array) - 1
    while start <= stop:
        var index = (start + stop) // 2
        var pivot = array[index]
        if pivot == element:
            return index
        elif pivot > element:
            stop = index - 1
        elif pivot < element:
            start = index + 1
    return -1


# create at compile-time, so not optimised away by compiler
@parameter
fn get_collection() -> List[Int]:
    var list = List[Int](SIZE)
    for i in range(SIZE):
        list.append(i)
    return list


fn main() raises:
    fn measure():
        _ = binary_search(SIZE - 1, get_collection())

    var report = benchmark.run[measure](NUM_WARMUP, MAX_ITERS)
    var time_s = report.mean()
    var time_ms = time_s * 1_000
    print("{} ms - {} items - binary search - Mojo".format(time_ms, SIZE))
