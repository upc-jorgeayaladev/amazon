import sys
import os
import networkx as nx
import matplotlib
import json
matplotlib.use('Agg')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.node import Node, NodeType
from src.models.product import Product
from src.models.warehouse import Warehouse
from src.graph.builder import WarehouseGraphBuilder
from src.graph.layout import WarehouseLayout
from src.graph.zones import ZoneDivider
from src.algorithms.bfs import BFSAlgorithm
from src.algorithms.dfs_backtracking import BacktrackingAlgorithm
from src.algorithms.topological import TopologicalSorting
from src.algorithms.scc import StronglyConnectedComponents
from src.algorithms.ufds import ProductClustering, UnionFind
from src.algorithms.mst import MinimumSpanningTree
from src.algorithms.max_flow import MaxFlowAlgorithm
from src.algorithms.greedy import GreedyAlgorithm
from src.algorithms.dp import DynamicProgramming
from src.algorithms.dp_graph import DPOnGraphs
from src.algorithms.brute_force import BruteForceAlgorithm
from src.visualization.render import GraphRenderer

def load_warehouse_from_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'warehouse_layout.json')
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    warehouse = Warehouse(data['name'], data['width'], data['height'])
    
    for node_data in data['nodes']:
        node = Node(
            id=node_data['id'],
            type=NodeType(node_data['type']),
            x=node_data['x'],
            y=node_data['y'],
            capacity=node_data.get('capacity', 0),
            metadata=node_data.get('metadata', {})
        )
        warehouse.add_node(node)
    
    for edge_data in data['edges']:
        warehouse.add_edge(
            edge_data['source'],
            edge_data['target'],
            weight=edge_data.get('weight', 1.0)
        )
    
    return warehouse

def load_products_from_json(warehouse):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'products.json')
    with open(data_path, 'r') as f:
        products_data = json.load(f)
    
    products = []
    for p_data in products_data:
        product = Product(
            id=p_data['id'],
            name=p_data['name'],
            sku=p_data['sku'],
            weight=p_data['weight'],
            volume=p_data['volume'],
            category=p_data['category'],
            dimensions=p_data['dimensions'],
            demand_frequency=p_data.get('demand_frequency', 0),
            location_id=p_data.get('location_id')
        )
        products.append(product)
        warehouse.add_product(product)
    
    return products

def demo_all_algorithms():
    print("=" * 60)
    print("SMART WAREHOUSE GRAPH ALGORITHMS DEMO (100 Shelves, 1500 Products)")
    print("=" * 60)
    
    warehouse = load_warehouse_from_json()
    products = load_products_from_json(warehouse)
    
    print(f"\nWarehouse loaded: {warehouse}")
    print(f"Nodes: {len(warehouse.nodes)}")
    print(f"Edges: {warehouse.graph.number_of_edges()}")
    print(f"Products: {len(products)}")
    
    print("\n" + "=" * 60)
    print("1. DIVIDE Y VENCER: Dividing warehouse into zones (4x4 grid)")
    print("=" * 60)
    zones = ZoneDivider.divide_by_grid(warehouse, rows=4, cols=4)
    for zone_name, nodes in sorted(zones.items()):
        print(f"  {zone_name}: {len(nodes)} shelves")
    WarehouseLayout.assign_zones_to_nodes(warehouse, zones)
    
    print("\n" + "=" * 60)
    print("2. BFS: Shortest path from Dock to farthest Shelf")
    print("=" * 60)
    path, distance = BFSAlgorithm.shortest_path(warehouse.graph, "Dock_0", "Shelf_9_9")
    print(f"  Path length: {len(path)} steps")
    print(f"  Distance: {distance}")
    print(f"  First 5 nodes: {' -> '.join(path[:5])}")
    
    print("\n" + "=" * 60)
    print("3. GREEDY: Nearest neighbor picking (10 random targets)")
    print("=" * 60)
    import random
    random.seed(42)
    all_shelves = [n for n in warehouse.nodes.keys() if 'Shelf' in n]
    targets = random.sample(all_shelves, 10)
    greedy_path, greedy_dist = GreedyAlgorithm.nearest_neighbor_picking(
        warehouse.graph, "Dock_0", targets
    )
    print(f"  Targets: {len(targets)} shelves")
    print(f"  Greedy path length: {len(greedy_path)} steps")
    print(f"  Total distance: {greedy_dist}")
    
    print("\n" + "=" * 60)
    print("4. MST: Minimum Spanning Tree (Kruskal)")
    print("=" * 60)
    mst = MinimumSpanningTree.kruskal_mst(warehouse.graph)
    mst_cost = MinimumSpanningTree.get_mst_cost(mst)
    print(f"  MST edges: {mst.number_of_edges()}")
    print(f"  MST total cost: {mst_cost}")
    
    print("\n" + "=" * 60)
    print("5. BACKTRACKING: Location combinations (sample with 5 shelves)")
    print("=" * 60)
    shelf_nodes = [warehouse.nodes[n] for n in all_shelves[:5]]
    combinations = BacktrackingAlgorithm.find_optimal_location_combinations(
        shelf_nodes, products_needed=3
    )
    print(f"  Found {len(combinations)} combinations for 3 products")
    if combinations:
        print(f"  First combination: {combinations[0]}")
    
    print("\n" + "=" * 60)
    print("6. TOPOLOGICAL SORT: Picking order (sample 5 products)")
    print("=" * 60)
    sample_products = products[:5]
    dependencies = {
        sample_products[0].id: [sample_products[1].id],
        sample_products[1].id: [],
        sample_products[2].id: [sample_products[0].id],
        sample_products[3].id: [sample_products[1].id],
        sample_products[4].id: [sample_products[2].id, sample_products[3].id]
    }
    order = TopologicalSorting.picking_order(dependencies)
    print(f"  Picking order: {order}")
    
    print("\n" + "=" * 60)
    print("7. SCC: Strongly Connected Components")
    print("=" * 60)
    sccs = StronglyConnectedComponents.find_interdependent_zones(warehouse)
    print(f"  Found {len(sccs)} SCCs")
    for i, scc in enumerate(sccs[:3]):
        print(f"  SCC {i+1}: {len(scc)} nodes")
    
    print("\n" + "=" * 60)
    print("8. UFDS: Product clustering by category (sample 100 products)")
    print("=" * 60)
    sample_100 = products[:100]
    clusters = ProductClustering.cluster_by_category(sample_100)
    print(f"  Categories found: {len(clusters)}")
    for category, items in list(clusters.items())[:3]:
        print(f"  {category}: {len(items)} products")
    
    print("\n" + "=" * 60)
    print("9. MAX FLOW: Order throughput (simplified)")
    print("=" * 60)
    flow_graph = nx.DiGraph()
    flow_graph.add_edge("SOURCE", "Shelf_0_0", capacity=100)
    flow_graph.add_edge("Shelf_0_0", "ORDER_1", capacity=50)
    flow_graph.add_edge("ORDER_1", "SINK", capacity=50)
    flow_value, _ = MaxFlowAlgorithm.ford_fulkerson(flow_graph, "SOURCE", "SINK")
    print(f"  Max flow value: {flow_value}")
    
    print("\n" + "=" * 60)
    print("10. DYNAMIC PROGRAMMING: TSP optimization (sample 8 nodes)")
    print("=" * 60)
    tsp_nodes = ["Dock_0"] + all_shelves[:7]
    tsp_path, tsp_cost = DynamicProgramming.tsp_dp(warehouse.graph, "Dock_0", tsp_nodes[1:])
    print(f"  Optimal TSP path length: {len(tsp_path)} steps")
    print(f"  Total cost: {tsp_cost}")
    print(f"  Path: {' -> '.join(tsp_path[:5])}...")
    
    print("\n" + "=" * 60)
    print("11. DP ON GRAPHS: Multiple orders")
    print("=" * 60)
    orders = [
        ["Shelf_0_0", "Shelf_2_2", "Shelf_4_4"],
        ["Shelf_5_5", "Shelf_7_7", "Shelf_9_9"]
    ]
    result = DPOnGraphs.multiple_orders_shortest_paths(warehouse.graph, orders, "Dock_0")
    print(f"  Computed distances for multiple orders")
    
    print("\n" + "=" * 60)
    print("12. BRUTE FORCE: Initial assignment (sample 3 products, 3 locations)")
    print("=" * 60)
    test_products = products[:3]
    test_locations = [warehouse.nodes[n] for n in all_shelves[:3]]
    assignment = BruteForceAlgorithm.initial_assignment(test_products, test_locations)
    print(f"  Brute force assignment: {assignment}")
    
    print("\n" + "=" * 60)
    print("VISUALIZATION (Full warehouse - 100 shelves)")
    print("=" * 60)
    print("  Rendering full warehouse graph with proportional distances...")
    GraphRenderer.render_warehouse(
        warehouse.graph, 
        title="Smart Warehouse - 100 Shelves with Proportional Distances",
        save_path="../warehouse_full.png",
        figsize=(20, 20)
    )
    print("  Saved to warehouse_full.png")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    demo_all_algorithms()
