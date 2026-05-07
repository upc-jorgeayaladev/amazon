import networkx as nx


class MinimumSpanningTree:
    @staticmethod
    def kruskal_mst(graph: nx.Graph) -> nx.Graph:
        mst = nx.Graph()
        mst.add_nodes_from(graph.nodes(data=True))

        edges = [(u, v, data.get("weight", 1)) for u, v, data in graph.edges(data=True)]
        edges.sort(key=lambda x: x[2])

        uf = {}

        def find(x):
            if x not in uf:
                uf[x] = x
            if uf[x] != x:
                uf[x] = find(uf[x])
            return uf[x]

        def union(x, y):
            root_x = find(x)
            root_y = find(y)
            if root_x != root_y:
                uf[root_x] = root_y

        for u, v, weight in edges:
            if find(u) != find(v):
                mst.add_edge(u, v, weight=weight)
                union(u, v)

        return mst

    @staticmethod
    def prim_mst(graph: nx.Graph, start_node: str = None) -> nx.Graph:
        if start_node is None:
            start_node = list(graph.nodes())[0]

        mst = nx.Graph()
        mst.add_nodes_from(graph.nodes(data=True))

        visited = {start_node}
        edges = []

        for v, data in graph[start_node].items():
            edges.append((data.get("weight", 1), start_node, v))

        while edges and len(visited) < len(graph.nodes()):
            edges.sort()
            weight, u, v = edges.pop(0)

            if v in visited:
                continue

            mst.add_edge(u, v, weight=weight)
            visited.add(v)

            for w, data in graph[v].items():
                if w not in visited:
                    edges.append((data.get("weight", 1), v, w))

        return mst

    @staticmethod
    def get_mst_cost(mst: nx.Graph) -> float:
        return sum(data.get("weight", 1) for _, _, data in mst.edges(data=True))
