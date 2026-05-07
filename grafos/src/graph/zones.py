from typing import Dict, List

from ..models.node import NodeType
from ..models.warehouse import Warehouse


class ZoneDivider:
    @staticmethod
    def divide_by_rows(warehouse: Warehouse, num_zones: int) -> Dict[str, List[str]]:
        zones = {}
        nodes = [n for n in warehouse.nodes.values() if n.type == NodeType.SHELF]

        if not nodes:
            return zones

        min_y = min(n.y for n in nodes)
        max_y = max(n.y for n in nodes)
        zone_height = (max_y - min_y) / num_zones

        for i in range(num_zones):
            zone_name = f"Zone_{i + 1}"
            zone_nodes = []

            for node in nodes:
                lower = min_y + i * zone_height
                upper = min_y + (i + 1) * zone_height
                if i == num_zones - 1:
                    if lower <= node.y <= upper:
                        zone_nodes.append(node.id)
                else:
                    if lower <= node.y < upper:
                        zone_nodes.append(node.id)

            zones[zone_name] = zone_nodes

        return zones

    @staticmethod
    def divide_by_cols(warehouse: Warehouse, num_zones: int) -> Dict[str, List[str]]:
        zones = {}
        nodes = [n for n in warehouse.nodes.values() if n.type == NodeType.SHELF]

        if not nodes:
            return zones

        min_x = min(n.x for n in nodes)
        max_x = max(n.x for n in nodes)
        zone_width = (max_x - min_x) / num_zones

        for i in range(num_zones):
            zone_name = f"Zone_{i + 1}"
            zone_nodes = []

            for node in nodes:
                lower = min_x + i * zone_width
                upper = min_x + (i + 1) * zone_width
                if i == num_zones - 1:
                    if lower <= node.x <= upper:
                        zone_nodes.append(node.id)
                else:
                    if lower <= node.x < upper:
                        zone_nodes.append(node.id)

            zones[zone_name] = zone_nodes

        return zones

    @staticmethod
    def divide_by_grid(
        warehouse: Warehouse, rows: int, cols: int
    ) -> Dict[str, List[str]]:
        zones = {}
        nodes = [n for n in warehouse.nodes.values() if n.type == NodeType.SHELF]

        if not nodes:
            return zones

        min_x = min(n.x for n in nodes)
        max_x = max(n.x for n in nodes)
        min_y = min(n.y for n in nodes)
        max_y = max(n.y for n in nodes)

        zone_width = (max_x - min_x) / cols
        zone_height = (max_y - min_y) / rows

        for r in range(rows):
            for c in range(cols):
                zone_name = f"Zone_R{r + 1}C{c + 1}"
                zone_nodes = []

                for node in nodes:
                    x_lower = min_x + c * zone_width
                    x_upper = min_x + (c + 1) * zone_width
                    y_lower = min_y + r * zone_height
                    y_upper = min_y + (r + 1) * zone_height

                    if (
                        x_lower <= node.x < x_upper
                        or (c == cols - 1 and node.x <= x_upper)
                    ) and (
                        y_lower <= node.y < y_upper
                        or (r == rows - 1 and node.y <= y_upper)
                    ):
                        zone_nodes.append(node.id)

                zones[zone_name] = zone_nodes

        return zones
