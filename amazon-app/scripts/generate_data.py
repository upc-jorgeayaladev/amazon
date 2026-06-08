import json
import math
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAFOS_DIR = os.path.join(os.path.dirname(BASE_DIR), "grafos")

ZONE_ROWS = 4
ZONE_COLS = 4
CATEGORIES = [
    "laptops", "smartphones", "headphones", "books",
    "kitchen appliances", "smart watches", "gaming mice", "keyboards",
    "monitors", "tablets", "wireless earbuds", "coffee machines",
]
CATEGORY_ZONE_MAP = {}
idx = 0
for r in range(ZONE_ROWS - 1):
    for c in range(ZONE_COLS):
        zone_name = f"Zone_R{r+1}C{c+1}"
        if idx < len(CATEGORIES):
            CATEGORY_ZONE_MAP[zone_name] = CATEGORIES[idx]
            idx += 1
        else:
            CATEGORY_ZONE_MAP[zone_name] = None

for c in range(ZONE_COLS):
    zone_name = f"Zone_R{ZONE_ROWS}C{c+1}"
    CATEGORY_ZONE_MAP[zone_name] = None

ZONE_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
    "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
    "#BB8FCE", "#85C1E9", "#F0B27A", "#82E0AA",
    "#E8E8E8", "#E8E8E8", "#E8E8E8", "#E8E8E8",
]


def load_warehouse_layout():
    path = os.path.join(GRAFOS_DIR, "data", "warehouse_layout.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_products():
    path = os.path.join(BASE_DIR, "data", "products.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_zone_for_shelf(row, col):
    rows_per_zone = []
    base = 0
    for r in range(ZONE_ROWS):
        count = (10 - base) // (ZONE_ROWS - r)
        rows_per_zone.append(count)
        base += count

    cols_per_zone = []
    base = 0
    for c in range(ZONE_COLS):
        count = (10 - base) // (ZONE_COLS - c)
        cols_per_zone.append(count)
        base += count

    zone_row = 0
    acc = 0
    for r, cnt in enumerate(rows_per_zone):
        if row < acc + cnt:
            zone_row = r
            break
        acc += cnt

    zone_col = 0
    acc = 0
    for c, cnt in enumerate(cols_per_zone):
        if col < acc + cnt:
            zone_col = c
            break
        acc += cnt

    return f"Zone_R{zone_row+1}C{zone_col+1}"


def build_zones(layout, products_by_category):
    nodes = layout["nodes"]
    shelfs = [n for n in nodes if n["type"] == "shelf"]

    zone_shelfs = defaultdict(list)
    shelf_zone_map = {}

    for s in shelfs:
        row = s["metadata"]["row"]
        col = s["metadata"]["col"]
        zone_name = get_zone_for_shelf(row, col)
        shelf_zone_map[s["id"]] = zone_name
        zone_shelfs[zone_name].append(s)

    zones = []
    color_idx = 0
    for r in range(ZONE_ROWS):
        for c in range(ZONE_COLS):
            zone_name = f"Zone_R{r+1}C{c+1}"
            shelfs_in_zone = zone_shelfs.get(zone_name, [])
            category = CATEGORY_ZONE_MAP.get(zone_name)

            connections = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ZONE_ROWS and 0 <= nc < ZONE_COLS:
                    neighbor = f"Zone_R{nr+1}C{nc+1}"
                    connections.append({"to": neighbor, "weight": 10.0})

            zones.append({
                "id": zone_name,
                "category": category,
                "shelfs": [s["id"] for s in shelfs_in_zone],
                "connections": connections,
                "color": ZONE_COLORS[color_idx],
                "label": category.replace(" ", "\n") if category else "AISLE",
            })
            color_idx += 1

    return zones, shelf_zone_map


def assign_products_to_shelfs(products_by_category, shelfs_by_zone, shelf_capacity):
    assignment = {}
    zone_ids = list(shelfs_by_zone.keys())

    for zone_name, products in products_by_category.items():
        shelfs = shelfs_by_zone.get(zone_name, [])
        if not shelfs:
            continue
        per_shelf = math.ceil(len(products) / len(shelfs))
        for i, p in enumerate(products):
            shelf_idx = i // per_shelf
            if shelf_idx >= len(shelfs):
                shelf_idx = len(shelfs) - 1
            shelf_id = shelfs[shelf_idx]["id"]
            if shelf_id not in assignment:
                assignment[shelf_id] = []
            assignment[shelf_id].append(p["id"])

    return assignment


def build_shelfs(layout, shelf_zone_map, assignment, products_by_category):
    nodes = layout["nodes"]
    shelfs = [n for n in nodes if n["type"] == "shelf"]

    result = []
    for s in shelfs:
        zone_name = shelf_zone_map[s["id"]]
        cat = CATEGORY_ZONE_MAP.get(zone_name)
        shelf_id = s["id"]
        prod_ids = assignment.get(shelf_id, [])

        load = len(prod_ids)
        result.append({
            "id": shelf_id,
            "x": s["x"],
            "y": s["y"],
            "zone": zone_name,
            "category": cat,
            "capacity": max(s["capacity"], load),
            "current_load": load,
            "products": prod_ids,
            "row": s["metadata"]["row"],
            "col": s["metadata"]["col"],
        })

    return result


def build_categories(products_by_category):
    result = {}
    for cat, prods in products_by_category.items():
        result[cat] = [p["id"] for p in prods]
    return result


def get_edges_for_graph(layout):
    return layout["edges"]


def main():
    print("Loading warehouse layout...")
    layout = load_warehouse_layout()

    print("Loading products...")
    products = load_products()
    print(f"  {len(products)} products loaded")

    products_by_category = defaultdict(list)
    for p in products:
        products_by_category[p["category"]].append(p)

    print("Building zones...")
    zones, shelf_zone_map = build_zones(layout, products_by_category)
    print(f"  {len(zones)} zones created")

    shelfs_by_category = defaultdict(list)
    for s in layout["nodes"]:
        if s["type"] != "shelf":
            continue
        zone_name = shelf_zone_map[s["id"]]
        cat = CATEGORY_ZONE_MAP.get(zone_name)
        if cat:
            shelfs_by_category[cat].append(s)

    print("Assigning products to shelves...")
    assignment = assign_products_to_shelfs(
        products_by_category, shelfs_by_category, 20
    )

    print("Building shelf data...")
    shelfs = build_shelfs(layout, shelf_zone_map, assignment, products_by_category)
    print(f"  {len(shelfs)} shelves created")

    print("Building categories data...")
    categories = build_categories(products_by_category)
    print(f"  {len(categories)} categories")

    print("\nSaving files...")
    data_dir = os.path.join(BASE_DIR, "data")

    with open(os.path.join(data_dir, "zones.json"), "w", encoding="utf-8") as f:
        json.dump(zones, f, ensure_ascii=False, indent=2)
    print(f"  zones.json ({len(zones)} zones)")

    with open(os.path.join(data_dir, "shelfs.json"), "w", encoding="utf-8") as f:
        json.dump(shelfs, f, ensure_ascii=False, indent=2)
    print(f"  shelfs.json ({len(shelfs)} shelves)")

    with open(os.path.join(data_dir, "categories.json"), "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    print(f"  categories.json ({len(categories)} categories)")

    total_assigned = sum(len(s["products"]) for s in shelfs)
    print(f"\nTotal products assigned to shelves: {total_assigned}")
    print("Done!")


if __name__ == "__main__":
    main()
