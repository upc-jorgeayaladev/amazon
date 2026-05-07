from typing import Dict, Tuple

import networkx as nx

from ..models.warehouse import Warehouse


class WarehouseLayout:
    @staticmethod
    def get_positions(warehouse: Warehouse) -> Dict[str, Tuple[float, float]]:
        return nx.get_node_attributes(warehouse.graph, "pos")

    @staticmethod
    def calculate_zone_bounds(warehouse: Warehouse, zone_nodes: list) -> Dict:
        if not zone_nodes:
            return {}

        xs = [warehouse.nodes[n].x for n in zone_nodes if n in warehouse.nodes]
        ys = [warehouse.nodes[n].y for n in zone_nodes if n in warehouse.nodes]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
            "center_x": sum(xs) / len(xs),
            "center_y": sum(ys) / len(ys),
        }

    @staticmethod
    def assign_zones_to_nodes(warehouse: Warehouse, zones: Dict[str, list]):
        for zone_name, node_ids in zones.items():
            for node_id in node_ids:
                if node_id in warehouse.nodes:
                    warehouse.nodes[node_id].metadata["zone"] = zone_name
                    warehouse.graph.nodes[node_id]["metadata"] = warehouse.nodes[
                        node_id
                    ].metadata
