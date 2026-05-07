# Amazon Project

Repositorio con dos proyectos independientes de Python enfocados en análisis de datos, automatización y teoría de grafos.

---

## Estructura

```
amazon/
├── grafos/        # Gestión inteligente de almacenes con teoría de grafos
└── scrapping/     # Web scraping de productos de Amazon con Playwright
```

---

## `grafos/` — Smart Warehouse

Simulación de un almacén inteligente modelado como grafo usando **NetworkX**. Implementa **13 algoritmos clásicos** de teoría de grafos aplicados a logística.

### Tecnologías
Python, NetworkX, Graphviz, matplotlib, pydot

### Algoritmos implementados
| Algoritmo | Aplicación |
|-----------|-----------|
| Fuerza Bruta | Asignación de productos |
| Backtracking | Combinaciones óptimas |
| BFS | Rutas más cortas |
| Orden Topológico | Secuencia de picking |
| SCC (Kosaraju) | Zonas interdependientes |
| Union-Find | Clustering por categoría |
| MST (Kruskal Prim) | Conexiones eficientes |
| Flujo Máximo (Ford-Fulkerson) | Throughput de pedidos |
| Voraz (vecino más cercano) | Ruta de picking |
| DP (TSP con bitmask) | Ruta óptima de picking |
| DP en Grafos (Floyd-Warshall) | Múltiples pedidos |
| Divide y Vencerás | Zonificación del almacén |

### Uso
```powershell
cd grafos
pip install -r requirements.txt
python examples/demo.py
```

---

## `scrapping/` — Amazon Product Scraper

Web scraping de **1500+ productos** de Amazon usando **Playwright**, distribuidos en 12 categorías con todas sus características.

### Scripts
| Script | Función |
|--------|---------|
| `scraper.py` | Scraping principal |
| `correct.py` | Corrige errores del JSON |
| `add.py` | Agrega más productos |

### Características por producto
id, título, precio, rating (0-5), reseñas, descripción, features, especificaciones, imagen principal, hasta 4 imágenes adicionales, URL, categoría.

### Uso
```powershell
cd scrapping
.\venv\Scripts\Activate.ps1
python scraper.py
python correct.py
python add.py
```

---

Para más detalles de cada proyecto, consulta su respectivo `README.md`.
