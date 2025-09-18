import matplotlib.pyplot as plt

# Colors
white = "#FFFFFF"
black = "#020202"
sandstone = "#ECEAE4"
teal = "#14E7E8"
violet = "#7C8CEF"

# Scheme
light_mode = False
primary_color = white if light_mode else black
text_color = black if light_mode else white
grid_color = sandstone if light_mode else "#333333"

# Data
labels = ["Before", "Now"]
time_in_seconds = [15 * 60, 5]

# Bar chart
fig, ax = plt.subplots(figsize=(6, 5), facecolor=primary_color)
bars = ax.bar(labels, time_in_seconds, color=[teal, violet])

# Axis background
ax.set_facecolor(primary_color)

# Labels & title
ax.set_ylabel("Time (seconds)", color=text_color)
ax.set_title("Deploy and run a local code change in Databricks", color=text_color)

# Ticks
ax.tick_params(colors=text_color)

# Spines
for spine in ax.spines.values():
    spine.set_color(text_color)

# Grid (optional, subtle)
ax.yaxis.grid(True, linestyle="--", color=grid_color, alpha=0.5)

# Add value labels on top of bars
for bar, value in zip(bars, time_in_seconds):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 10,
        value,
        ha="center",
        va="bottom",
        fontsize=10,
        color=text_color,
    )

# Open chart in window
plt.show()
