# Binary Search Comparison

```bash
cd 06_binary_search_performance
```

## Python

Install snakeviz:
```bash
python -m pip install snakeviz
```

Run the script with profiling:
```bash
python -m cProfile -o python.prof main.py
```

Open the analysis:
```bash
snakeviz python.prof
```
