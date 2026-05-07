from typing import Dict, List, Tuple

import networkx as nx


class DynamicProgramming:
    @staticmethod
    def tsp_dp(
        graph: nx.Graph, start: str, nodes_to_visit: List[str]
    ) -> Tuple[List[str], float]:
        if not nodes_to_visit:
            return [start], 0.0

        all_nodes = [start] + nodes_to_visit
        n = len(all_nodes)
        node_to_idx = {node: i for i, node in enumerate(all_nodes)}

        dist = [[float("inf")] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    dist[i][j] = 0
                else:
                    try:
                        d = nx.shortest_path_length(
                            graph, all_nodes[i], all_nodes[j], weight="weight"
                        )
                        dist[i][j] = d
                    except:
                        dist[i][j] = float("inf")

        memo = {}

        def dp(mask: int, pos: int) -> float:
            if mask == (1 << n) - 1:
                return dist[pos][0] if dist[pos][0] < float("inf") else float("inf")

            if (mask, pos) in memo:
                return memo[(mask, pos)]

            ans = float("inf")
            for next_pos in range(n):
                if mask & (1 << next_pos) == 0:
                    if dist[pos][next_pos] < float("inf"):
                        new_cost = dist[pos][next_pos] + dp(
                            mask | (1 << next_pos), next_pos
                        )
                        ans = min(ans, new_cost)

            memo[(mask, pos)] = ans
            return ans

        def get_path(mask: int, pos: int) -> List[str]:
            if mask == (1 << n) - 1:
                return [all_nodes[0]] if dist[pos][0] < float("inf") else []

            best_next = None
            best_cost = float("inf")

            for next_pos in range(n):
                if mask & (1 << next_pos) == 0:
                    if dist[pos][next_pos] < float("inf"):
                        new_cost = dist[pos][next_pos] + dp(
                            mask | (1 << next_pos), next_pos
                        )
                        if new_cost < best_cost:
                            best_cost = new_cost
                            best_next = next_pos

            if best_next is None:
                return []

            return [all_nodes[best_next]] + get_path(mask | (1 << best_next), best_next)

        min_cost = dp(1, 0)

        if min_cost < float("inf"):
            path = [all_nodes[0]] + get_path(1, 0)
            return path, min_cost

        return [], float("inf")

    @staticmethod
    def optimize_repeated_routes(graph: nx.Graph, routes: List[List[str]]) -> Dict:
        memo = {}

        def route_cost(route: List[str]) -> float:
            total = 0
            for i in range(len(route) - 1):
                key = (route[i], route[i + 1])
                if key not in memo:
                    try:
                        memo[key] = nx.shortest_path_length(
                            graph, route[i], route[i + 1], weight="weight"
                        )
                    except:
                        memo[key] = float("inf")
                total += memo[key]
            return total

        optimizations = []
        for route in routes:
            cost = route_cost(route)
            optimizations.append({"route": route, "cost": cost, "length": len(route)})

        optimizations.sort(key=lambda x: x["cost"])
        return {
            "routes": optimizations,
            "total_cost": sum(r["cost"] for r in optimizations),
            "best_route": optimizations[0]["route"] if optimizations else [],
        }
