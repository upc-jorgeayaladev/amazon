import heapq


def a_star(graph, start, goal):
    if start not in graph.nodes or goal not in graph.nodes:
        return [], float("inf")

    for node in graph.nodes:
        graph.set_heuristic(node, goal)

    open_set = [(graph.get_heuristic(start), 0, start)]
    came_from = {}
    g_score = {start: 0}
    closed = set()

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current in closed:
            continue

        if current == goal:
            path = reconstruct_path(came_from, current)
            return path, g_score[current]

        closed.add(current)

        for neighbor, weight in graph.get_neighbors(current):
            if neighbor in closed:
                continue

            tentative = g_score[current] + weight

            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f_score = tentative + graph.get_heuristic(neighbor)
                heapq.heappush(open_set, (f_score, tentative, neighbor))

    return [], float("inf")


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
