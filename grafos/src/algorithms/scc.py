from typing import Dict, List

import networkx as nx

from ..models.warehouse import Warehouse


class StronglyConnectedComponents:
    @staticmethod
    def find_interdependent_zones(warehouse: Warehouse) -> List[List[str]]:
        directed_graph = nx.DiGraph()
        directed_graph.add_nodes_from(warehouse.graph.nodes())

        for u, v, data in warehouse.graph.edges(data=True):
            weight = data.get("weight", 1)
            directed_graph.add_edge(u, v, weight=weight)
            directed_graph.add_edge(v, u, weight=weight)

        return [list(scc) for scc in nx.strongly_connected_components(directed_graph)]

    @staticmethod
    def analyze_zone_connections(
        warehouse: Warehouse, zones: Dict[str, List[str]]
    ) -> Dict:
        analysis = {}

        for zone_name, zone_nodes in zones.items():
            zone_subgraph = warehouse.graph.subgraph(zone_nodes)
            try:
                sccs = list(
                    nx.strongly_connected_components(
                        nx.DiGraph(zone_subgraph.to_directed())
                    )
                )
                analysis[zone_name] = {
                    "num_nodes": len(zone_nodes),
                    "num_sccs": len(sccs),
                    "sccs": [list(scc) for scc in sccs],
                }
            except:
                analysis[zone_name] = {
                    "num_nodes": len(zone_nodes),
                    "num_sccs": 0,
                    "sccs": [],
                }

        return analysis
