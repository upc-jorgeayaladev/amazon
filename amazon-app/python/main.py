import json
import asyncio
import base64
import io

from pyscript import window

from python.warehouse import Warehouse
from python.router import optimize_route, simulate_random_order


warehouse = None
selected_shelf_ids = set()


def init_app(shelfs_json, zones_json, categories_json, products_json):
    global warehouse
    warehouse = Warehouse()
    warehouse.load_data(shelfs_json, zones_json, categories_json, products_json)
    warehouse.add_dock_pick()
    return json.dumps({"status": "ok", "shelfs": len(warehouse.shelfs), "zones": len(warehouse.zones)})


def get_warehouse_data():
    if not warehouse:
        return json.dumps({"error": "not initialized"})
    data = {
        "shelfs": list(warehouse.shelfs.values()),
        "zones": list(warehouse.zones.values()),
        "categories": list(warehouse.categories.keys()),
    }
    return json.dumps(data)


def search_products(query):
    if not warehouse:
        return json.dumps([])
    q = query.lower().strip()
    results = []
    for pid, prod in warehouse.products.items():
        title = prod.get("title", "").lower()
        cat = prod.get("category", "").lower()
        if q in title or q in cat:
            shelf_id = warehouse.get_shelf_for_product(pid)
            results.append({
                "id": pid,
                "title": prod.get("title", "")[:80],
                "price": prod.get("price"),
                "rating": prod.get("rating"),
                "category": prod.get("category", ""),
                "image_url": prod.get("image_url", ""),
                "shelf": shelf_id,
            })
            if len(results) >= 50:
                break
    return json.dumps(results)


def get_products_for_shelf(shelf_id):
    if not warehouse:
        return json.dumps([])
    shelf = warehouse.shelfs.get(shelf_id)
    if not shelf:
        return json.dumps([])
    results = []
    for pid in shelf.get("products", []):
        prod = warehouse.products.get(pid)
        if prod:
            results.append({
                "id": pid,
                "title": prod.get("title", "")[:60],
                "price": prod.get("price"),
                "category": prod.get("category", ""),
            })
    return json.dumps(results)


def calculate_route(shelf_ids_json):
    if not warehouse:
        return json.dumps({"error": "not initialized"})
    shelf_ids = json.loads(shelf_ids_json)
    if not shelf_ids:
        return json.dumps({"error": "no shelves selected"})
    route = optimize_route(warehouse, shelf_ids)
    return json.dumps(route)


def simulate_order(num_products=5):
    if not warehouse:
        return json.dumps({"error": "not initialized"})
    result = simulate_random_order(warehouse, num_products)
    return json.dumps(result)


def render_matplotlib(route_json):
    if not warehouse:
        return ""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        return json.dumps({"error": "matplotlib not available"})

    route_data = json.loads(route_json) if isinstance(route_json, str) else route_json
    path = route_data.get("path", [])

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect("equal")
    ax.set_title("Smart Warehouse - Ruta Óptima (A*)", fontsize=16, fontweight="bold")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    zone_colors = {}
    for z in warehouse.zones.values():
        zone_colors[z["id"]] = z.get("color", "#cccccc")

    for shelf_id, shelf in warehouse.shelfs.items():
        zid = shelf.get("zone", "")
        color = zone_colors.get(zid, "#cccccc")
        x, y = shelf["x"], shelf["y"]
        rect = plt.Rectangle(
            (x - 4, y - 4), 8, 8,
            facecolor=color, edgecolor="#333", linewidth=0.5, alpha=0.8
        )
        ax.add_patch(rect)
        if shelf_id in selected_shelf_ids or shelf_id in path:
            rect.set_edgecolor("#FFD700")
            rect.set_linewidth(2.5)

    for z in warehouse.zones.values():
        zone_shelfs = [warehouse.shelfs[s] for s in z["shelfs"] if s in warehouse.shelfs]
        if zone_shelfs:
            xs = [s["x"] for s in zone_shelfs]
            ys = [s["y"] for s in zone_shelfs]
            cx = (min(xs) + max(xs)) / 2
            cy = (max(ys) + min(ys)) / 2
            label = z.get("label", "")
            if label != "AISLE":
                ax.text(cx, cy + 8, label, ha="center", va="bottom",
                        fontsize=8, fontweight="bold", color="#333",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

    dock = warehouse.graph.nodes.get(warehouse.dock_id, {})
    pick = warehouse.graph.nodes.get(warehouse.pick_id, {})
    ax.plot(dock.get("x", 0), dock.get("y", 55), "o", color="red",
            markersize=15, markeredgecolor="darkred", markeredgewidth=2, zorder=5)
    ax.text(dock.get("x", 0) - 2, dock.get("y", 55) + 6, "DOCK",
            ha="center", fontsize=10, fontweight="bold", color="darkred")
    ax.plot(pick.get("x", 100), pick.get("y", 55), "o", color="green",
            markersize=15, markeredgecolor="darkgreen", markeredgewidth=2, zorder=5)
    ax.text(pick.get("x", 100) + 2, pick.get("y", 55) + 6, "PICK",
            ha="center", fontsize=10, fontweight="bold", color="darkgreen")

    if len(path) > 1:
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            na = warehouse.graph.nodes.get(a, {})
            nb = warehouse.graph.nodes.get(b, {})
            if "x" in na and "x" in nb:
                ax.plot([na["x"], nb["x"]], [na["y"], nb["y"]],
                        "-", color="#FF4444", linewidth=3, alpha=0.8, zorder=4)
                if i < len(path) - 2:
                    mid_x = (na["x"] + nb["x"]) / 2
                    mid_y = (na["y"] + nb["y"]) / 2
                    ax.plot(mid_x, mid_y, "o", color="#FFD700",
                            markersize=4, zorder=5)

    ax.plot([], [], "-", color="#FF4444", linewidth=3, alpha=0.8, label="Ruta A*")
    ax.plot([], [], "o", color="#FFD700", markersize=4, label="Nodos visitados")
    legend1 = plt.Legend(ax, handles=[
        mpatches.Patch(color="#FF6B6B", label="Zona producto"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="red",
                   markersize=10, label="DOCK"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="green",
                   markersize=10, label="PICK"),
        plt.Line2D([0], [0], color="#FF4444", linewidth=3, label="Ruta A*"),
    ], loc="upper right", fontsize=9)
    ax.add_artist(legend1)

    ax.grid(True, alpha=0.3)
    ax.set_facecolor("#f8f9fa")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"


def toggle_shelf(shelf_id):
    if shelf_id in selected_shelf_ids:
        selected_shelf_ids.remove(shelf_id)
    else:
        selected_shelf_ids.add(shelf_id)
    return json.dumps(list(selected_shelf_ids))


def clear_selection():
    selected_shelf_ids.clear()
    return "ok"


window.initApp = init_app
window.getWarehouseData = get_warehouse_data
window.searchProducts = search_products
window.getProductsForShelf = get_products_for_shelf
window.calculateRoute = calculate_route
window.simulateOrder = simulate_order
window.renderMatplotlib = render_matplotlib
window.toggleShelf = toggle_shelf
window.clearSelection = clear_selection
