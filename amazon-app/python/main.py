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

    product_shelves = {}
    for shelf_id, shelf in warehouse.shelfs.items():
        for product_id in shelf.get("products", []):
            product_shelves[product_id] = shelf_id

    products = []
    for product_id, product in warehouse.products.items():
        products.append({
            "id": product_id,
            "title": product.get("title") or f"Producto {product_id}",
            "price": product.get("price", 0),
            "rating": product.get("rating"),
            "category": product.get("category", "other"),
            "image_url": product.get("image_url", ""),
            "stock": product.get("stock", 0),
            "shelf": product_shelves.get(product_id),
        })

    data = {
        "shelfs": list(warehouse.shelfs.values()),
        "zones": list(warehouse.zones.values()),
        "categories": list(warehouse.categories.keys()),
        "products": products,
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
        from matplotlib.lines import Line2D
    except ImportError:
        return json.dumps({"error": "matplotlib not available"})

    try:
        route_data = json.loads(route_json) if isinstance(route_json, str) else route_json
        path = route_data.get("path", [])
        path_shelves = set(path)

        fig, ax = plt.subplots(figsize=(12, 9))
        fig.patch.set_facecolor("#f4f7fa")
        ax.set_xlim(-8, 108)
        ax.set_ylim(-8, 108)
        ax.set_aspect("equal")
        ax.set_title("Nexus Warehouse - Ruta optimizada", fontsize=16, fontweight="bold")
        ax.set_xlabel("Coordenada X")
        ax.set_ylabel("Coordenada Y")

        zone_colors = {
            zone["id"]: zone.get("color", "#cccccc")
            for zone in warehouse.zones.values()
        }

        for shelf_id, shelf in warehouse.shelfs.items():
            color = zone_colors.get(shelf.get("zone", ""), "#cccccc")
            rect = mpatches.FancyBboxPatch(
                (shelf["x"] - 3.5, shelf["y"] - 3.5),
                7,
                7,
                boxstyle="round,pad=0.12,rounding_size=0.8",
                facecolor=color,
                edgecolor="#f59e0b" if shelf_id in path_shelves else "#334155",
                linewidth=2.6 if shelf_id in path_shelves else 0.6,
                alpha=0.9,
                zorder=2,
            )
            ax.add_patch(rect)
            ax.text(
                shelf["x"],
                shelf["y"],
                f'{shelf["row"]},{shelf["col"]}',
                ha="center",
                va="center",
                fontsize=5.5,
                color="#0f172a",
                zorder=3,
            )

        for zone in warehouse.zones.values():
            if zone.get("label") == "AISLE":
                continue
            zone_shelves = [
                warehouse.shelfs[shelf_id]
                for shelf_id in zone["shelfs"]
                if shelf_id in warehouse.shelfs
            ]
            if zone_shelves:
                center_x = sum(shelf["x"] for shelf in zone_shelves) / len(zone_shelves)
                top_y = min(shelf["y"] for shelf in zone_shelves) - 7
                ax.text(
                    center_x,
                    top_y,
                    zone.get("category") or zone["id"],
                    ha="center",
                    va="center",
                    fontsize=7,
                    fontweight="bold",
                    color="#172033",
                    bbox=dict(
                        boxstyle="round,pad=0.25",
                        facecolor="white",
                        edgecolor=zone.get("color", "#cccccc"),
                        alpha=0.92,
                    ),
                    zorder=6,
                )

        dock = warehouse.graph.nodes.get(warehouse.dock_id, {})
        pick = warehouse.graph.nodes.get(warehouse.pick_id, {})

        if len(path) > 1:
            for index in range(len(path) - 1):
                start = warehouse.graph.nodes.get(path[index], {})
                end = warehouse.graph.nodes.get(path[index + 1], {})
                if "x" in start and "x" in end:
                    ax.plot(
                        [start["x"], end["x"]],
                        [start["y"], end["y"]],
                        color="#ef4444",
                        linewidth=3.2,
                        alpha=0.9,
                        zorder=4,
                    )

        ax.scatter(
            [dock.get("x", 0)],
            [dock.get("y", 55)],
            s=190,
            c="#ef4444",
            edgecolors="#7f1d1d",
            linewidths=2,
            zorder=7,
        )
        ax.scatter(
            [pick.get("x", 100)],
            [pick.get("y", 55)],
            s=190,
            c="#22c55e",
            edgecolors="#14532d",
            linewidths=2,
            zorder=7,
        )
        ax.text(dock.get("x", 0), dock.get("y", 55) + 6, "DOCK",
                ha="center", fontsize=9, fontweight="bold", color="#7f1d1d")
        ax.text(pick.get("x", 100), pick.get("y", 55) + 6, "PICK",
                ha="center", fontsize=9, fontweight="bold", color="#14532d")

        ax.legend(
            handles=[
                mpatches.Patch(facecolor="#94a3b8", edgecolor="#334155", label="Estantería"),
                Line2D([0], [0], color="#ef4444", linewidth=3, label="Ruta A*"),
                Line2D([0], [0], marker="o", color="w", markerfacecolor="#ef4444",
                       markeredgecolor="#7f1d1d", markersize=9, label="DOCK"),
                Line2D([0], [0], marker="o", color="w", markerfacecolor="#22c55e",
                       markeredgecolor="#14532d", markersize=9, label="PICK"),
            ],
            loc="upper right",
            fontsize=8,
            framealpha=0.95,
        )

        ax.grid(True, color="#cbd5e1", alpha=0.45, linewidth=0.7)
        ax.set_facecolor("#eef3f7")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    except Exception as error:
        try:
            plt.close("all")
        except Exception:
            pass
        return json.dumps({"error": f"No se pudo generar el gráfico: {error}"})


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
