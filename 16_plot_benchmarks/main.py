import matplotlib.pyplot as plt

# Colors
white = "#FFFFFF"
black = "#020202"
sandstone = "#ECEAE4"
teal = "#14E7E8"
violet = "#7C8CEF"

# Scheme
light_mode = True
primary_color = white if light_mode else black
text_color = black if light_mode else white
grid_color = sandstone if light_mode else "#333333"

labels = ["Soundex", "Metaphone"]

python_6k = [0.0052, 0.0184]
rust_6k = [0.0020, 0.0008]

python_9m = [12.6843, 47.2550]
rust_9m = [0.4404, 0.9938]


def plot_benchmark(labels, python_times, rust_times, dataset_label, filename):
    x = range(len(labels))
    width = 0.35
    plt.rcParams["axes.facecolor"] = primary_color
    plt.figure(figsize=(6, 4), facecolor=primary_color, edgecolor=text_color)
    plt.bar(
        [i - width / 2 for i in x], python_times, width, label="Python", color=violet
    )
    plt.bar([i + width / 2 for i in x], rust_times, width, label="Rust", color=teal)
    plt.ylabel("Time (seconds)", color=text_color)
    plt.title(
        f"Phonetic Algorithms Applied to Dataset with {dataset_label}", color=text_color
    )
    plt.xticks(x, labels, color=text_color)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7, color=grid_color)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


plot_benchmark(labels, python_6k, rust_6k, "6K Names", "phonetics_6k_comparison.png")
plot_benchmark(labels, python_9m, rust_9m, "9M Names", "phonetics_9m_comparison.png")
