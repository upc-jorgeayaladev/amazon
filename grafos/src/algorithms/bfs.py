from typing import List, Optional, Tuple

import networkx as nx


class BFSAlgorithm:
    @staticmethod
    def shortest_path(graph: nx.Graph, start: str, end: str) -> Tuple[List[str], float]:
        try:
            path = nx.shortest_path(graph, start, end, weight=None)
            distance = sum(
                graph[path[i]][path[i + 1]].get("weight", 1)
                for i in range(len(path) - 1)
            )
            return path, distance
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [], float("inf")

    @staticmethod
    def shortest_paths_from_source(graph: nx.Graph, source: str) -> dict:
        return dict(nx.single_source_shortest_path_length(graph, source))

    @staticmethod
    def find_nearest_picking_station(
        graph: nx.Graph, start: str, station_nodes: List[str]
    ) -> Tuple[Optional[str], float]:
        min_dist = float("inf")
        nearest = None

        for station in station_nodes:
            _, dist = BFSAlgorithm.shortest_path(graph, start, station)
            if dist < min_dist:
                min_dist = dist
                nearest = station

        return nearest, min_dist
