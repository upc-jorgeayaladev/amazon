# Grafos - Smart Warehouse Management

Este módulo modela un almacén inteligente usando teoría de grafos para el caso de estudio de "Gestión de almacenes inteligentes".

## Algoritmos Implementados

| Algoritmo | Descripción | Archivo |
|-----------|-------------|---------|
| Fuerza Bruta | Asignación inicial de productos | `algorithms/brute_force.py` |
| Backtracking | Combinaciones de ubicaciones | `algorithms/dfs_backtracking.py` |
| Divide y Vencerás | Dividir almacén por zonas | `graph/zones.py` |
| Grafos | Layout del almacén | `graph/builder.py` |
| BFS | Rutas más cortas | `algorithms/bfs.py` |
| Topológico | Orden de picking | `algorithms/topological.py` |
| SCC | Zonas interdependientes | `algorithms/scc.py` |
| UFDS | Clusters de productos | `algorithms/ufds.py` |
| MST | Conexiones eficientes | `algorithms/mst.py` |
| Flujo Máximo | Flujo de pedidos | `algorithms/max_flow.py` |
| Voraces | Picking más cercano | `algorithms/greedy.py` |
| DP | Optimización de rutas repetidas | `algorithms/dp.py` |
| DP en Grafos | Múltiples pedidos simultáneos | `algorithms/dp_graph.py` |

## Estructura del Proyecto

```
grafos/
├── requirements.txt          # Dependencias
├── README.md               # Documentación
├── src/
│   ├── models/             # Modelos de datos
│   │   ├── node.py         # Nodos del grafo
│   │   ├── product.py      # Productos
│   │   └── warehouse.py    # Almacén como grafo
│   ├── graph/              # Construcción y manejo del grafo
│   │   ├── builder.py      # Constructor del almacén
│   │   ├── layout.py       # Layout y zonas
│   │   └── zones.py        # División en zonas
│   ├── algorithms/         # Algoritmos
│   │   ├── brute_force.py
│   │   ├── dfs_backtracking.py
│   │   ├── bfs.py
│   │   ├── topological.py
│   │   ├── scc.py
│   │   ├── ufds.py
│   │   ├── mst.py
│   │   ├── max_flow.py
│   │   ├── greedy.py
│   │   ├── dp.py
│   │   └── dp_graph.py
│   └── visualization/      # Renderizado de grafos
│       └── render.py
├── data/                   # Datos de ejemplo
│   ├── warehouse_layout.json
│   └── products.json
└── examples/               # Ejemplos de uso
    └── demo.py
```

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```python
from src.models.warehouse import Warehouse
from src.graph.builder import WarehouseGraphBuilder

# Crear almacén de ejemplo
warehouse = WarehouseGraphBuilder.create_sample_warehouse()

# Usar algoritmos
from src.algorithms.bfs import BFSAlgorithm
path, distance = BFSAlgorithm.shortest_path(warehouse.graph, "Dock_0", "Shelf_4_5")
```

## Demo

```bash
cd examples
python demo.py
```

## Dependencias

- networkx >= 3.0
- graphviz >= 0.20
- matplotlib >= 3.7
- pydot >= 1.4
