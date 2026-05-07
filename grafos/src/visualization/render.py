from typing import Dict, List, Optional

import networkx as nx

from ..models.warehouse import Warehouse


class GraphRenderer:
    @staticmethod
    def generate_dot_source(
        graph: nx.Graph,
        title: str = "Warehouse Layout",
        highlight_nodes: List[str] = None,
        highlight_path: List[str] = None,
    ) -> str:
        lines = [
            "graph Warehouse {",
            "  // " + title,
            "  splines=true;",
            "  overlap=false;",
            '  node [shape=circle, style=filled, fontname="Arial", fontsize=10];',
            '  edge [fontname="Arial", fontsize=8];',
            "",
        ]

        highlight_set = set(highlight_nodes) if highlight_nodes else set()
        path_edges = set()
        if highlight_path and len(highlight_path) > 1:
            path_edges = {
                (highlight_path[i], highlight_path[i + 1])
                for i in range(len(highlight_path) - 1)
            }

        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_type = node_data.get("type", "shelf")
            pos = node_data.get("pos", (0, 0))
            pos_str = f"{pos[0]},{pos[1]}!"

            if node_type == "dock":
                color = "red"
                fillcolor = "lightcoral"
                shape = "doublecircle"
                label = '"Dock"'
            elif node_type == "picking_station":
                color = "green"
                fillcolor = "lightgreen"
                shape = "doublecircle"
                label = '"Picking"'
            else:
                metadata = node_data.get("metadata", {})
                row = metadata.get("row", "")
                col = metadata.get("col", "")
                label = f'"{row},{col}"'
                if node in highlight_set:
                    color = "yellow"
                    fillcolor = "yellow"
                else:
                    color = "lightblue"
                    fillcolor = "lightblue"
                shape = "circle"

            lines.append(
                f'  "{node}" [label={label}, pos={pos_str}, '
                f"color={color}, fillcolor={fillcolor}, shape={shape}];"
            )

        lines.append("")

        for u, v, data in graph.edges(data=True):
            weight = data.get("weight", 1)
            edge_color = (
                "red" if (u, v) in path_edges or (v, u) in path_edges else "gray"
            )
            penwidth = min(5.0, max(0.5, weight / 2))

            lines.append(
                f'  "{u}" -- "{v}" [weight={weight}, penwidth={penwidth}, '
                f'color={edge_color}, label="{weight}"];'
            )

        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def render_warehouse_graphviz(
        graph: nx.Graph,
        title: str = "Warehouse Layout",
        save_path: Optional[str] = None,
        highlight_nodes: List[str] = None,
        highlight_path: List[str] = None,
    ) -> str:
        dot_source = GraphRenderer.generate_dot_source(
            graph, title, highlight_nodes, highlight_path
        )

        if save_path:
            dot_path = save_path.replace(".png", ".dot")
            with open(dot_path, "w") as f:
                f.write(dot_source)

            try:
                import graphviz

                dot = graphviz.Source(dot_source)
                png_path = dot.render(dot_path, format="png", cleanup=True)
                return png_path
            except Exception as e:
                print(f"Graphviz rendering failed: {e}")
                print(f"DOT file saved to: {dot_path}")
                print("Install Graphviz system tools to generate PNG automatically.")
                return dot_path

        return dot_source

    @staticmethod
    def render_warehouse(
        graph: nx.Graph,
        title: str = "Warehouse Layout",
        highlight_nodes: List[str] = None,
        highlight_path: List[str] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (20, 20),
    ):
        try:
            result = GraphRenderer.render_warehouse_graphviz(
                graph, title, save_path, highlight_nodes, highlight_path
            )
            return result
        except Exception as e:
            print(f"Graphviz failed: {e}")
            return GraphRenderer._render_with_matplotlib(
                graph, title, save_path, highlight_nodes, highlight_path, figsize
            )

    @staticmethod
    def _render_with_matplotlib(
        graph: nx.Graph,
        title: str = "Warehouse Layout",
        save_path: Optional[str] = None,
        highlight_nodes: List[str] = None,
        highlight_path: List[str] = None,
        figsize: tuple = (20, 20),
    ) -> str:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=figsize)

        pos = nx.get_node_attributes(graph, "pos")
        if not pos:
            pos = nx.spring_layout(graph, weight="weight", k=2, iterations=100)

        node_colors = []
        node_sizes = []
        for node in graph.nodes():
            node_type = graph.nodes[node].get("type", "shelf")
            if node_type == "dock":
                node_colors.append("red")
                node_sizes.append(500)
            elif node_type == "picking_station":
                node_colors.append("green")
                node_sizes.append(400)
            else:
                node_colors.append("lightblue")
                node_sizes.append(150)

        if highlight_nodes:
            for i, node in enumerate(graph.nodes()):
                if node in highlight_nodes:
                    node_colors[i] = "yellow"

        nx.draw_networkx_nodes(
            graph, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8
        )

        edges = list(graph.edges())
        weights = [graph[u][v].get("weight", 1) for u, v in edges]
        min_weight = min(weights) if weights else 1
        max_weight = max(weights) if weights else 1

        normalized_weights = []
        for w in weights:
            if max_weight > min_weight:
                normalized_weights.append(
                    0.5 + 4.5 * (w - min_weight) / (max_weight - min_weight)
                )
            else:
                normalized_weights.append(2.0)

        nx.draw_networkx_edges(
            graph, pos, edge_color="gray", alpha=0.6, width=normalized_weights
        )

        labels = {
            n: n.split("_")[1] + "," + n.split("_")[2] if "Shelf" in n else n
            for n in graph.nodes()
        }
        nx.draw_networkx_labels(graph, pos, labels=labels, font_size=6)

        if highlight_path and len(highlight_path) > 1:
            path_edges = [
                (highlight_path[i], highlight_path[i + 1])
                for i in range(len(highlight_path) - 1)
            ]
            nx.draw_networkx_edges(
                graph, pos, edgelist=path_edges, edge_color="red", width=4, alpha=0.8
            )

        plt.title(title)
        plt.axis("off")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            plt.close()
            return save_path

        return ""

    @staticmethod
    def render_zones(
        warehouse: Warehouse,
        zones: Dict[str, List[str]],
        save_path: Optional[str] = None,
    ):
        graph = warehouse.graph
        try:
            import graphviz

            dot = graphviz.Graph(comment="Warehouse Zones")
            dot.attr(splines="true", overlap="false")
            dot.attr("node", style="filled", fontname="Arial", fontsize="10")

            colors = [
                "lightblue",
                "lightgreen",
                "lightyellow",
                "lightcoral",
                "lightpink",
                "lightgray",
                "lightcyan",
                "lavender",
                "honeydew",
                "beige",
            ]

            color_map = {
                zone: colors[i % len(colors)] for i, zone in enumerate(zones.keys())
            }

            for zone_name, zone_nodes in zones.items():
                zone_color = color_map[zone_name]
                for node in zone_nodes:
                    node_data = graph.nodes[node]
                    pos = node_data.get("pos", (0, 0))
                    metadata = node_data.get("metadata", {})
                    row = metadata.get("row", "")
                    col = metadata.get("col", "")
                    label = f'"{row},{col}"'
                    dot.node(
                        node,
                        label=label,
                        pos=f"{pos[0]},{pos[1]}!",
                        fillcolor=zone_color,
                    )

            for u, v, data in graph.edges(data=True):
                weight = data.get("weight", 1)
                dot.edge(u, v, weight=str(weight), penwidth=str(min(3.0, weight / 3)))

            if save_path:
                if save_path.endswith(".png"):
                    save_path = save_path[:-4]
                dot.render(save_path, format="png", cleanup=True)

        except Exception as e:
            print(f"Graphviz failed for zones: {e}")
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            plt.figure(figsize=(12, 8))
            pos = nx.get_node_attributes(graph, "pos")
            if not pos:
                pos = nx.spring_layout(graph)

            for zone_name, zone_nodes in zones.items():
                zone_color = color_map[zone_name]
                nx.draw_networkx_nodes(
                    graph,
                    pos,
                    nodelist=zone_nodes,
                    node_color=zone_color,
                    node_size=200,
                    alpha=0.6,
                    label=zone_name,
                )

            nx.draw_networkx_edges(graph, pos, edge_color="gray", alpha=0.3)
            nx.draw_networkx_labels(graph, pos, font_size=7)
            plt.title("Warehouse Zones")
            plt.legend()
            plt.axis("off")

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches="tight")
                plt.close()

    @staticmethod
    def render_mst(
        original: nx.Graph,
        mst: nx.Graph,
        title: str = "Minimum Spanning Tree",
        save_path: Optional[str] = None,
    ):
        try:
            import graphviz

            dot = graphviz.Graph(comment=title)
            dot.attr(splines="true", overlap="false")
            dot.attr(
                "node",
                shape="circle",
                style="filled",
                fillcolor="lightblue",
                fontsize="10",
            )

            pos = nx.get_node_attributes(original, "pos")

            for node in original.nodes():
                node_data = original.nodes[node]
                p = pos.get(node, (0, 0))
                dot.node(node, pos=f"{p[0]},{p[1]}!")

            for u, v, data in original.edges(data=True):
                weight = data.get("weight", 1)
                if mst.has_edge(u, v) or mst.has_edge(v, u):
                    dot.edge(u, v, color="red", penwidth="2.0", weight=str(weight))
                else:
                    dot.edge(u, v, color="lightgray", penwidth="0.5", style="dashed")

            if save_path:
                if save_path.endswith(".png"):
                    save_path = save_path[:-4]
                dot.render(save_path, format="png", cleanup=True)

        except Exception as e:
            print(f"Graphviz failed for MST: {e}")
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            plt.figure(figsize=(12, 8))
            pos = nx.get_node_attributes(original, "pos")
            if not pos:
                pos = nx.spring_layout(original)

            nx.draw_networkx_nodes(
                original, pos, node_color="lightblue", node_size=150, alpha=0.8
            )
            nx.draw_networkx_edges(
                original, pos, edge_color="lightgray", alpha=0.3, width=1
            )
            nx.draw_networkx_edges(mst, pos, edge_color="red", width=2, alpha=0.8)
            nx.draw_networkx_labels(original, pos, font_size=8)
            plt.title(title)
            plt.axis("off")

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches="tight")
                plt.close()
