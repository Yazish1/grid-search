import csv
import matplotlib.pyplot as plt

STYLES = {
    "BFS": {"linewidth": 6, "alpha": 0.5, "zorder": 1},
    "DFS": {"linewidth": 2, "zorder": 2},
    "Dijkstra": {"linewidth": 2, "linestyle": "--", "markersize": 4, "zorder": 3},
}


def load_rows(filename):
    rows = []
    with open(filename, newline="") as f:
        for row in csv.DictReader(f):
            row["size"] = int(row["size"])
            row["grids_used"] = int(row["grids_used"])
            for key in ("avg_expanded", "avg_max_frontier", "avg_time_ms", "avg_path_cost"):
                row[key] = float(row[key])
            rows.append(row)
    return rows


def plot_stat(rows, column, ylabel, filename):
    by_algorithm = {}
    for row in rows:
        by_algorithm.setdefault(row["algorithm"], []).append((row["size"], row[column]))

    for name, points in by_algorithm.items():
        points.sort()
        sizes = [size for size, _ in points]
        values = [value for _, value in points]
        style = STYLES.get(name, {})
        plt.plot(sizes, values, marker="o", label=name, **style)

    plt.xlabel("Grid size (N x N)")
    plt.ylabel(ylabel)
    plt.title(ylabel + " by grid size")
    plt.xticks(sorted({row["size"] for row in rows}))
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.clf()


if __name__ == "__main__":
    rows = load_rows("results.csv")
    plot_stat(rows, "avg_expanded", "Average nodes expanded", "expanded.png")
    plot_stat(rows, "avg_path_cost", "Average path cost", "cost.png")
    plot_stat(rows, "avg_max_frontier", "Average peak frontier size", "frontier.png")
    print("Saved expanded.png, cost.png and frontier.png")