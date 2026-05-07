from itertools import permutations
from typing import List, Tuple

from ..models.node import Node
from ..models.product import Product


class BruteForceAlgorithm:
    @staticmethod
    def initial_assignment(
        products: List[Product], locations: List[Node]
    ) -> List[Tuple[str, str]]:
        if not products or not locations:
            return []

        best_assignment = None
        min_total_distance = float("inf")

        for perm in permutations(locations, len(products)):
            valid = True
            for i, (product, location) in enumerate(zip(products, perm)):
                if not location.can_store(product.weight):
                    valid = False
                    break

            if valid:
                total_weight = sum(p.weight for p in products)
                if total_weight < min_total_distance:
                    min_total_distance = total_weight
                    best_assignment = [(p.id, l.id) for p, l in zip(products, perm)]

        return best_assignment if best_assignment else []

    @staticmethod
    def try_all_location_combinations(
        products: List[Product], locations: List[Node]
    ) -> List[List[Tuple[str, str]]]:
        from itertools import product as cartesian_product

        all_combinations = []

        location_ids = [loc.id for loc in locations]

        for combo in cartesian_product(location_ids, repeat=len(products)):
            valid = True
            for i, (prod, loc_id) in enumerate(zip(products, combo)):
                loc = next((l for l in locations if l.id == loc_id), None)
                if not loc or not loc.can_store(prod.weight):
                    valid = False
                    break

            if valid:
                all_combinations.append(
                    [(p.id, combo[i]) for i, p in enumerate(products)]
                )

        return all_combinations
