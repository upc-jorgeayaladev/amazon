from typing import Dict, List, Optional

import networkx as nx

from .node import Node
from .product import Product


class Warehouse:
    def __init__(self, name: str, width: float, height: float):
        self.name = name
        self.width = width
        self.height = height
        self.nodes: Dict[str, Node] = {}
        self.products: Dict[str, Product] = {}
        self.graph = nx.Graph()

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            type=node.type.value,
            pos=(node.x, node.y),
            capacity=node.capacity,
            current_load=node.current_load,
            metadata=node.metadata,
        )

    def add_edge(
        self,
        node1_id: str,
        node2_id: str,
        weight: float = 1.0,
        capacity: float = float("inf"),
    ):
        if node1_id in self.nodes and node2_id in self.nodes:
            self.graph.add_edge(node1_id, node2_id, weight=weight, capacity=capacity)

    def add_product(self, product: Product):
        self.products[product.id] = product

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    def get_products_at_location(self, node_id: str) -> List[Product]:
        return [p for p in self.products.values() if p.location_id == node_id]

    def get_graph(self) -> nx.Graph:
        return self.graph

    def __repr__(self):
        return f"Warehouse({self.name}, nodes={len(self.nodes)}, products={len(self.products)})"
