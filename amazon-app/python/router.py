from python.astar import a_star


def optimize_route(warehouse, target_shelves):
    if not target_shelves:
        return {"path": [], "total_distance": 0, "segments": []}

    graph = warehouse.graph
    dock = warehouse.dock_id
    pick = warehouse.pick_id

    targets = list(target_shelves)
    remaining = targets.copy()
    current = dock
    full_path = [dock]
    total_dist = 0.0
    segments = []

    while remaining:
        nearest = None
        nearest_dist = float("inf")
        nearest_path = []

        for t in remaining:
            path, dist = a_star(graph, current, t)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = t
                nearest_path = path

        if nearest is None:
            break

        if nearest_path and nearest_path[0] == current:
            nearest_path = nearest_path[1:]

        full_path.extend(nearest_path)
        total_dist += nearest_dist

        finish_path, finish_dist = a_star(graph, nearest, pick)
        segments.append({
            "from": current,
            "to": nearest,
            "path": nearest_path,
            "distance": nearest_dist,
        })

        current = nearest
        remaining.remove(nearest)

    final_path, final_dist = a_star(graph, current, pick)
    if final_path and final_path[0] == current:
        final_path = final_path[1:]

    full_path.extend(final_path)
    total_dist += final_dist

    segments.append({
        "from": current,
        "to": pick,
        "path": final_path,
        "distance": final_dist,
    })

    full_path.append(pick)

    return {
        "path": full_path,
        "total_distance": round(total_dist, 2),
        "segments": segments,
    }


def simulate_random_order(warehouse, num_products=5):
    import random

    all_product_ids = list(warehouse.categories.values())
    flat_ids = []
    for ids in all_product_ids:
        flat_ids.extend(ids)

    if not flat_ids:
        return {"products": [], "route": None}

    selected = random.sample(flat_ids, min(num_products, len(flat_ids)))
    target_shelves = set()

    products_info = []
    for pid in selected:
        shelf_id = warehouse.get_shelf_for_product(pid)
        if shelf_id:
            target_shelves.add(shelf_id)
            prod = warehouse.products.get(pid, {})
            products_info.append({
                "id": pid,
                "title": prod.get("title", f"Product {pid}")[:60],
                "shelf": shelf_id,
            })

    route = optimize_route(warehouse, list(target_shelves))

    return {
        "products": products_info,
        "shelves_visited": list(target_shelves),
        "route": route,
    }
