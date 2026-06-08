import math


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.heuristics = {}

    def add_node(self, node_id, x=0, y=0, **attrs):
        self.nodes[node_id] = {"x": x, "y": y, **attrs}
        if node_id not in self.edges:
            self.edges[node_id] = {}

    def add_edge(self, from_node, to_node, weight=1.0, bidirectional=True):
        self.edges[from_node][to_node] = weight
        if bidirectional:
            if to_node not in self.edges:
                self.edges[to_node] = {}
            self.edges[to_node][from_node] = weight

    def get_neighbors(self, node_id):
        return list(self.edges.get(node_id, {}).items())

    def get_weight(self, from_node, to_node):
        return self.edges.get(from_node, {}).get(to_node, float("inf"))

    def distance(self, a, b):
        na = self.nodes.get(a)
        nb = self.nodes.get(b)
        if not na or not nb:
            return 0
        return math.sqrt((na["x"] - nb["x"]) ** 2 + (na["y"] - nb["y"]) ** 2)

    def set_heuristic(self, node_id, goal_id):
        self.heuristics[node_id] = self.distance(node_id, goal_id)

    def get_heuristic(self, node_id):
        return self.heuristics.get(node_id, 0)

    def node_count(self):
        return len(self.nodes)

    def edge_count(self):
        return sum(len(adj) for adj in self.edges.values()) // 2
