from typing import Dict, List


class UFDSNode:
    def __init__(self, value: str):
        self.value = value
        self.parent = self
        self.rank = 0


class UnionFind:
    def __init__(self):
        self.nodes: Dict[str, UFDSNode] = {}

    def make_set(self, value: str):
        if value not in self.nodes:
            self.nodes[value] = UFDSNode(value)

    def find(self, value: str) -> str:
        node = self.nodes.get(value)
        if not node:
            return None

        if node.parent != node:
            node.parent = self.nodes[self.find(node.parent.value)]

        return node.parent.value

    def union(self, val1: str, val2: str):
        root1 = self.find(val1)
        root2 = self.find(val2)

        if root1 == root2:
            return

        node1 = self.nodes[root1]
        node2 = self.nodes[root2]

        if node1.rank < node2.rank:
            node1.parent = node2
        elif node1.rank > node2.rank:
            node2.parent = node1
        else:
            node2.parent = node1
            node1.rank += 1

    def get_clusters(self) -> List[List[str]]:
        clusters = {}
        for value in self.nodes:
            root = self.find(value)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(value)

        return list(clusters.values())


class ProductClustering:
    @staticmethod
    def cluster_by_category(products: list) -> Dict[str, List[str]]:
        uf = UnionFind()

        for product in products:
            uf.make_set(product.id)

        category_groups = {}
        for product in products:
            if product.category not in category_groups:
                category_groups[product.category] = []
            category_groups[product.category].append(product.id)

        for category, product_ids in category_groups.items():
            for i in range(1, len(product_ids)):
                uf.union(product_ids[0], product_ids[i])

        clusters = uf.get_clusters()
        result = {}
        for cluster in clusters:
            category = next(
                (p.category for p in products if p.id == cluster[0]), "Unknown"
            )
            result[category] = cluster

        return result
