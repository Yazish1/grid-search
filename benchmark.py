from algorithms import bfs, dfs, dijkstra, start_search, path_cost, make_grid, random_grid, WALL
import random
import csv
def summarise(grid, result, time_ms, path):
    return {"expanded": result["nodes_popped"], "max_frontier": result["max_frontier_size"],"time_ms": time_ms, "path_cost": path_cost(grid, path)}
def run_one_grid(grid, start, goal):
    result, time_ms, path = start_search(bfs, grid, start, goal)
    if not result["found"]:
        return None
    results = {"BFS": summarise(grid, result, time_ms, path)}

    result, time_ms, path = start_search(dfs, grid, start, goal)
    results["DFS"] = summarise(grid, result, time_ms, path)

    result, time_ms, path = start_search(dijkstra, grid, start, goal)
    results["Dijkstra"] = summarise(grid, result, time_ms, path)

    assert results["Dijkstra"]["path_cost"] <= results["BFS"]["path_cost"]
    assert results["Dijkstra"]["path_cost"] <= results["DFS"]["path_cost"]
    return results


def average(kept, name, stat):
    total = 0
    for result in kept:
        total += result[name][stat] 
    return total / len(kept)
def run_benchmark(sizes, trials_per_size, wall_density, weight_density, seed):
    complete_results = []
    rng = random.Random(seed)
    for size in sizes:
        start = (0,0)
        goal = (size-1,size-1)
        kept = []
        for i in range(trials_per_size):
            grid = random_grid(size, size, wall_density, weight_density, rng)
            results = run_one_grid(grid, start, goal)
            if not results:
                continue
            kept.append(results)
        
        if not kept:
            print(f"warning: no solvable grids at size {size}")
            continue
        
        for name in ["BFS", "DFS", "Dijkstra"]:
            complete_results.append({
                "size": size,
                "algorithm": name,
                "grids_used": len(kept),
                "avg_expanded": average(kept, name, "expanded"),
                "avg_max_frontier": average(kept, name, "max_frontier"),
                "avg_time_ms": average(kept, name, "time_ms"),
                "avg_path_cost": average(kept, name, "path_cost")
            })
    return complete_results
            

def save_results(results, filename):
    if not results:
        print("No data saved")
        return False    
    try:
        with open(filename, "w", newline="") as file:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)        
            writer.writeheader()
            writer.writerows(results)
    except FileNotFoundError:
        print("File not found")
        return False
    return True
    

def print_table(rows):
    print(f"{'size':>5} {'algorithm':<10} {'grids':>6} {'expanded':>10} {'frontier':>10} {'time_ms':>9} {'cost':>8}")
    for r in rows:
        print(f"{r['size']:>5} {r['algorithm']:<10} {r['grids_used']:>6} "
              f"{r['avg_expanded']:>10.1f} {r['avg_max_frontier']:>10.1f} "
              f"{r['avg_time_ms']:>9.3f} {r['avg_path_cost']:>8.1f}")

g = make_grid(5, 5)
out = run_one_grid(g, (0, 0), (4, 4))
assert set(out) == {"BFS", "DFS", "Dijkstra"}
assert out["Dijkstra"]["path_cost"] <= out["BFS"]["path_cost"]

walled = make_grid(5, 5)
for c in range(5):
    walled[2][c] = WALL
assert run_one_grid(walled, (0, 0), (4, 4)) is None

rows = run_benchmark([10, 20], 50, 0.2, 0.2, 42)
assert len(rows) == 6
assert all(r["grids_used"] > 0 for r in rows)

def without_time(rows):
    return [{k: v for k, v in r.items() if k != "avg_time_ms"} for r in rows]

assert without_time(rows) == without_time(run_benchmark([10, 20], 50, 0.2, 0.2, 42))


if __name__ == "__main__":
    rows = run_benchmark(sizes=[25, 50, 100], trials_per_size=200,
                         wall_density=0.25, weight_density=0.2, seed=42)
    print_table(rows)
    save_results(rows, "results.csv")