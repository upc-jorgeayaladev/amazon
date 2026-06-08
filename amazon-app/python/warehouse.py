import json
from python.graph import Graph


class Warehouse:
    def __init__(self):
        self.graph = Graph()
        self.shelfs = {}
        self.zones = {}
        self.categories = {}
        self.products = {}
        self.dock_id = "Dock_0"
        self.pick_id = "Picking_0"

    def load_data(self, shelfs_json, zones_json, categories_json, products_json):
        shelfs_data = json.loads(shelfs_json) if isinstance(shelfs_json, str) else shelfs_json
        zones_data = json.loads(zones_json) if isinstance(zones_json, str) else zones_json
        self.categories = json.loads(categories_json) if isinstance(categories_json, str) else categories_json
        products_data = json.loads(products_json) if isinstance(products_json, str) else products_json

        self.products = {p["id"]: p for p in products_data}
        self.zones = {z["id"]: z for z in zones_data}

        for s in shelfs_data:
            self.shelfs[s["id"]] = s
            self.graph.add_node(
                s["id"],
                x=s["x"],
                y=s["y"],
                zone=s["zone"],
                category=s["category"],
                capacity=s["capacity"],
                current_load=s["current_load"],
                type="shelf",
                row=s["row"],
                col=s["col"],
            )

        # Build edges between shelfs from positions
        shelfs_by_row_col = {}
        for s in shelfs_data:
            shelfs_by_row_col[(s["row"], s["col"])] = s["id"]

        for s in shelfs_data:
            r, c = s["row"], s["col"]
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = shelfs_by_row_col.get((r + dr, c + dc))
                if neighbor:
                    dist = self.graph.distance(s["id"], neighbor)
                    self.graph.add_edge(s["id"], neighbor, weight=dist)

    def add_dock_pick(self, dock_x=0, dock_y=55, pick_x=100, pick_y=55):
        self.graph.add_node(
            self.dock_id, x=dock_x, y=dock_y, type="dock"
        )
        self.graph.add_node(
            self.pick_id, x=pick_x, y=pick_y, type="pick"
        )

        nearest_to_dock = min(
            self.shelfs.values(),
            key=lambda s: self.graph.distance(self.dock_id, s["id"])
        )
        self.graph.add_edge(
            self.dock_id, nearest_to_dock["id"],
            weight=self.graph.distance(self.dock_id, nearest_to_dock["id"])
        )

        nearest_to_pick = min(
            self.shelfs.values(),
            key=lambda s: self.graph.distance(self.pick_id, s["id"])
        )
        self.graph.add_edge(
            self.pick_id, nearest_to_pick["id"],
            weight=self.graph.distance(self.pick_id, nearest_to_pick["id"])
        )

    def get_shelf_for_product(self, product_id):
        for shelf_id, shelf in self.shelfs.items():
            if product_id in shelf["products"]:
                return shelf_id
        return None

    def get_products_in_zone(self, zone_id):
        zone = self.zones.get(zone_id)
        if not zone:
            return []
        result = []
        for shelf_id in zone["shelfs"]:
            shelf = self.shelfs.get(shelf_id, {})
            for pid in shelf.get("products", []):
                if pid in self.products:
                    result.append(self.products[pid])
        return result

    def get_zone_color(self, zone_id):
        zone = self.zones.get(zone_id, {})
        return zone.get("color", "#cccccc")

    def get_zone_label(self, zone_id):
        zone = self.zones.get(zone_id, {})
        return zone.get("label", zone_id)
