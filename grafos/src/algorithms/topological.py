from typing import Dict, List

import networkx as nx

from ..models.product import Product


class TopologicalSorting:
    @staticmethod
    def picking_order(picking_dependencies: Dict[str, List[str]]) -> List[str]:
        G = nx.DiGraph()

        for product, deps in picking_dependencies.items():
            G.add_node(product)
            for dep in deps:
                G.add_edge(dep, product)

        try:
            return list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            return []

    @staticmethod
    def create_picking_dag(
        products: List[Product], warehouse_graph: nx.Graph
    ) -> nx.DiGraph:
        dag = nx.DiGraph()

        for product in products:
            if product.location_id:
                dag.add_node(product.id, location=product.location_id)

        locations = {p.location_id for p in products if p.location_id}

        for loc1 in locations:
            for loc2 in locations:
                if loc1 != loc2:
                    try:
                        path = nx.shortest_path(warehouse_graph, loc1, loc2)
                        if len(path) > 1:
                            dag.add_edge(loc1, loc2, distance=len(path) - 1)
                    except (nx.NetworkXNoPath, nx.NodeNotFound):
                        continue

        return dag

    @staticmethod
    def get_picking_priority_order(dag: nx.DiGraph) -> List[str]:
        try:
            return list(nx.topological_sort(dag))
        except nx.NetworkXUnfeasible:
            return []
