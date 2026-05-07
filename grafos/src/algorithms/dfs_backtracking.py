from typing import List, Tuple

from ..models.node import Node


class BacktrackingAlgorithm:
    @staticmethod
    def find_optimal_location_combinations(
        nodes: List[Node], products_needed: int, start_combination: List[str] = None
    ) -> List[List[str]]:
        if start_combination is None:
            start_combination = []

        all_combinations = []

        def backtrack(current: List[str], remaining: int, start_idx: int):
            if remaining == 0:
                all_combinations.append(current[:])
                return

            for i in range(start_idx, len(nodes)):
                node = nodes[i]
                if node.can_store(products_needed):
                    current.append(node.id)
                    backtrack(current, remaining - 1, i + 1)
                    current.pop()

        backtrack(start_combination, products_needed, 0)
        return all_combinations

    @staticmethod
    def brute_force_assignment(
        products: list, locations: List[Node]
    ) -> List[Tuple[str, str]]:
        assignments = []

        def backtrack(
            prod_idx: int, used_locations: set, current: List[Tuple[str, str]]
        ):
            if prod_idx == len(products):
                assignments.append(current[:])
                return

            product = products[prod_idx]
            for loc in locations:
                if loc.id not in used_locations and loc.can_store(product.weight):
                    used_locations.add(loc.id)
                    current.append((product.id, loc.id))
                    backtrack(prod_idx + 1, used_locations, current)
                    current.pop()
                    used_locations.remove(loc.id)

        backtrack(0, set(), [])
        return assignments
