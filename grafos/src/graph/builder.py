from ..models.node import Node, NodeType
from ..models.warehouse import Warehouse


class WarehouseGraphBuilder:
    @staticmethod
    def create_grid_warehouse(
        name: str, rows: int, cols: int, shelf_capacity: int = 100
    ) -> Warehouse:
        warehouse = Warehouse(name, width=cols * 10, height=rows * 10)

        for i in range(rows):
            for j in range(cols):
                node_id = f"Shelf_{i}_{j}"
                node = Node(
                    id=node_id,
                    type=NodeType.SHELF,
                    x=j * 10 + 5,
                    y=i * 10 + 5,
                    capacity=shelf_capacity,
                    metadata={"row": i, "col": j},
                )
                warehouse.add_node(node)

        for i in range(rows):
            for j in range(cols):
                current = f"Shelf_{i}_{j}"
                if j < cols - 1:
                    right = f"Shelf_{i}_{j + 1}"
                    dist = 10
                    warehouse.add_edge(current, right, weight=dist)
                if i < rows - 1:
                    down = f"Shelf_{i + 1}_{j}"
                    dist = 10
                    warehouse.add_edge(current, down, weight=dist)

        return warehouse

    @staticmethod
    def add_dock(warehouse: Warehouse, x: float, y: float) -> Node:
        dock = Node(
            id="Dock_0",
            type=NodeType.DOCK,
            x=x,
            y=y,
            capacity=1000,
            metadata={"type": "loading"},
        )
        warehouse.add_node(dock)

        center_x, center_y = warehouse.width / 2, warehouse.height / 2
        min_dist = float("inf")
        nearest = None
        for node_id, node in warehouse.nodes.items():
            if node.type == NodeType.SHELF:
                dist = ((node.x - center_x) ** 2 + (node.y - center_y) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest = node_id

        if nearest:
            warehouse.add_edge("Dock_0", nearest, weight=min_dist)

        return dock

    @staticmethod
    def add_picking_station(warehouse: Warehouse, x: float, y: float) -> Node:
        station = Node(
            id="Picking_0", type=NodeType.PICKING_STATION, x=x, y=y, capacity=500
        )
        warehouse.add_node(station)
        return station

    @staticmethod
    def create_sample_warehouse() -> Warehouse:
        warehouse = WarehouseGraphBuilder.create_grid_warehouse(
            "SmartWarehouse", rows=5, cols=6, shelf_capacity=100
        )
        WarehouseGraphBuilder.add_dock(warehouse, x=0, y=25)
        WarehouseGraphBuilder.add_picking_station(warehouse, x=30, y=25)

        return warehouse
