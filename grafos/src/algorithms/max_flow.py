from typing import Dict, List, Tuple

import networkx as nx


class MaxFlowAlgorithm:
    @staticmethod
    def ford_fulkerson(
        graph: nx.DiGraph, source: str, sink: str
    ) -> Tuple[float, nx.DiGraph]:
        flow_value, flow_dict = nx.maximum_flow(
            graph, source, sink, capacity="capacity"
        )

        flow_graph = nx.DiGraph()
        flow_graph.add_nodes_from(graph.nodes(data=True))

        for u in flow_dict:
            for v in flow_dict[u]:
                if flow_dict[u][v] > 0:
                    capacity = graph[u][v].get("capacity", float("inf"))
                    flow_graph.add_edge(u, v, flow=flow_dict[u][v], capacity=capacity)

        return flow_value, flow_graph

    @staticmethod
    def create_order_flow_graph(
        warehouse_graph: nx.Graph, orders: List[Dict]
    ) -> nx.DiGraph:
        flow_graph = nx.DiGraph()

        flow_graph.add_node("SOURCE")
        flow_graph.add_node("SINK")

        shelf_nodes = [
            n for n, d in warehouse_graph.nodes(data=True) if d.get("type") == "shelf"
        ]

        for shelf in shelf_nodes:
            flow_graph.add_edge(
                "SOURCE",
                shelf,
                capacity=warehouse_graph.nodes[shelf].get("capacity", 100),
            )

        for i, order in enumerate(orders):
            order_node = f"ORDER_{i}"
            flow_graph.add_node(order_node)

            for shelf in shelf_nodes:
                flow_graph.add_edge(shelf, order_node, capacity=order.get("demand", 10))

            flow_graph.add_edge(order_node, "SINK", capacity=order.get("demand", 10))

        return flow_graph

    @staticmethod
    def calculate_order_throughput(flow_value: float, total_orders: int) -> float:
        return flow_value / total_orders if total_orders > 0 else 0
