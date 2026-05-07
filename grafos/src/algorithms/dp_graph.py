from typing import Dict, List

import networkx as nx


class DPOnGraphs:
    @staticmethod
    def multiple_orders_shortest_paths(
        graph: nx.Graph, orders: List[List[str]], start: str
    ) -> Dict:
        dp = {start: 0}
        parent = {start: None}

        all_nodes = set()
        for order in orders:
            all_nodes.update(order)

        for node in graph.nodes():
            if node != start:
                dp[node] = float("inf")

        for order in orders:
            new_dp = dp.copy()
            for node in order:
                for prev_node in dp:
                    if dp[prev_node] < float("inf"):
                        try:
                            dist = nx.shortest_path_length(
                                graph, prev_node, node, weight="weight"
                            )
                            if dp[prev_node] + dist < new_dp[node]:
                                new_dp[node] = dp[prev_node] + dist
                                parent[node] = prev_node
                        except:
                            continue
            dp = new_dp

        return {"distances": dp, "parents": parent}

    @staticmethod
    def knapsack_route_optimization(
        graph: nx.Graph, items: List[Dict], capacity: int, start: str
    ) -> Dict:
        n = len(items)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        selected = [[False] * (capacity + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(capacity + 1):
                item_weight = items[i - 1]["weight"]
                item_value = items[i - 1].get("priority", 1)

                if item_weight <= w:
                    if dp[i - 1][w] < dp[i - 1][w - item_weight] + item_value:
                        dp[i][w] = dp[i - 1][w - item_weight] + item_value
                        selected[i][w] = True
                    else:
                        dp[i][w] = dp[i - 1][w]
                else:
                    dp[i][w] = dp[i - 1][w]

        w = capacity
        chosen_items = []
        for i in range(n, 0, -1):
            if selected[i][w]:
                chosen_items.append(items[i - 1])
                w -= items[i - 1]["weight"]

        return {
            "max_value": dp[n][capacity],
            "selected_items": chosen_items,
            "total_weight": sum(item["weight"] for item in chosen_items),
        }

    @staticmethod
    def floyd_warshall_all_pairs(graph: nx.Graph) -> Dict:
        return dict(nx.floyd_warshall(graph, weight="weight"))
