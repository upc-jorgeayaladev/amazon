from typing import List, Optional, Tuple

import networkx as nx

from ..models.node import Node


class GreedyAlgorithm:
    @staticmethod
    def nearest_neighbor_picking(
        graph: nx.Graph, start: str, targets: List[str]
    ) -> Tuple[List[str], float]:
        if not targets:
            return [start], 0.0

        path = [start]
        current = start
        remaining = set(targets)
        total_distance = 0.0

        while remaining:
            nearest = None
            min_dist = float("inf")

            for target in remaining:
                try:
                    dist = nx.shortest_path_length(
                        graph, current, target, weight="weight"
                    )
                    if dist < min_dist:
                        min_dist = dist
                        nearest = target
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

            if nearest is None:
                break

            path.append(nearest)
            total_distance += min_dist
            remaining.remove(nearest)
            current = nearest

        return path, total_distance

    @staticmethod
    def nearest_shelf_for_product(
        shelves: List[Node], product_weight: float, current_pos: str, graph: nx.Graph
    ) -> Tuple[Optional[str], float]:
        nearest = None
        min_dist = float("inf")

        for shelf in shelves:
            if shelf.can_store(product_weight):
                try:
                    dist = nx.shortest_path_length(
                        graph, current_pos, shelf.id, weight="weight"
                    )
                    if dist < min_dist:
                        min_dist = dist
                        nearest = shelf.id
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

        return nearest, min_dist

    @staticmethod
    def greedy_assignment(
        products: list, shelves: List[Node], graph: nx.Graph
    ) -> List[Tuple[str, str]]:
        assignments = []
        assigned_shelves = set()

        for product in sorted(products, key=lambda p: p.demand_frequency, reverse=True):
            best_shelf = None
            best_dist = float("inf")

            for shelf in shelves:
                if shelf.id not in assigned_shelves and shelf.can_store(product.weight):
                    if shelf.metadata.get("zone") == product.category:
                        best_shelf = shelf
                        break

                    if shelf.current_load < shelf.capacity * 0.8:
                        try:
                            dist = nx.shortest_path_length(
                                graph, "Dock_0", shelf.id, weight="weight"
                            )
                            if dist < best_dist:
                                best_dist = dist
                                best_shelf = shelf
                        except:
                            continue

            if best_shelf:
                best_shelf.add_load(product.weight)
                product.assign_location(best_shelf.id)
                assignments.append((product.id, best_shelf.id))
                assigned_shelves.add(best_shelf.id)

        return assignments
