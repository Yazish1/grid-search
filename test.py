import random
from algorithms import scatter_weights, dijkstra, bfs, path_cost, build_path
rng = random.Random(1)
for _ in range(200):
    g = [[1] * 10 for _ in range(10)]
    scatter_weights(g, (0, 0), (9, 9), 0.3, 9, rng)
    d = dijkstra(g, (0, 0), (9, 9))
    b = bfs(g, (0, 0), (9, 9))
    assert path_cost(g, build_path(d["parent_of"], (9, 9))) <= path_cost(g, build_path(b["parent_of"], (9, 9)))