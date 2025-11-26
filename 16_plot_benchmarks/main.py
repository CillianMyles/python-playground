import matplotlib.pyplot as plt

labels_6k = ["Soundex", "Metaphone"]
python_6k = [0.0052, 0.0184]
rust_6k = [0.0020, 0.0008]

labels_9m = ["Soundex", "Metaphone"]
python_9m = [12.6843, 47.2550]
rust_9m = [0.4404, 0.9938]


def plot_benchmark(labels, python_times, rust_times, dataset_label, filename):
    x = range(len(labels))
    width = 0.35
    plt.figure(figsize=(6, 4))
    plt.bar([i - width / 2 for i in x], python_times, width, label="Python")
    plt.bar([i + width / 2 for i in x], rust_times, width, label="Rust")
    plt.ylabel("Median Time (s, lower is better)")
    plt.title(f"Phonetic Benchmark — {dataset_label}")
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


plot_benchmark(labels_6k, python_6k, rust_6k, "6K Names", "phonetics_6k_comparison.png")
plot_benchmark(labels_9m, python_9m, rust_9m, "9M Names", "phonetics_9m_comparison.png")
