import matplotlib.pyplot as plt

# Data
labels = ["Before", "Now"]
time_in_seconds = [15 * 60, 5]  

# Bar chart
plt.figure(figsize=(6, 5))
bars = plt.bar(labels, time_in_seconds, color=["steelblue", "orange"])

# Labels
plt.ylabel("Time (seconds)")
plt.title("Time to deploy and run a code change in Databricks")

# Add value labels on top of bars
for bar, value in zip(bars, time_in_seconds):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        value + 10,
        value,
        ha='center',
        va='bottom',
        fontsize=10,
    )

# Open chart in window
plt.show()
