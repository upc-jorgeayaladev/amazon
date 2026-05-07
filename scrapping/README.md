# Amazon Product Scraper

Script de web scraping para extraer información de productos de Amazon usando Playwright.

## Descripción

Este proyecto realiza scraping a Amazon.com y extrae un total de **1500+ productos** distribuidos en **12 categorías** diferentes. Por cada producto se obtienen todas sus características disponibles y se almacenan en un archivo JSON.

### Scripts incluidos

| Script | Función |
|--------|---------|
| `scraper.py` | Scraping principal: recorre categorías y extrae productos |
| `add.py` | Agrega más productos al JSON existente (nuevas categorías) |
| `correct.py` | Corrige errores en el JSON (URLs malformadas, reintentos) |

## Características extraídas

Por cada producto se extrae:
- ID único (autoincremental)
- Título
- Precio
- Rating (calificación decimal del 0 al 5)
- Número de reseñas
- Descripción del producto
- Características principales (feature bullets)
- Especificaciones técnicas
- URL de la imagen principal del producto
- Hasta 4 URLs de imágenes adicionales
- URL del producto
- Categoría
- Fecha y hora del scraping

## Categorías

Los productos se distribuyen en las siguientes categorías:
1. Laptops
2. Smartphones
3. Headphones
4. Books
5. Kitchen appliances
6. Smart watches
7. Gaming mice
8. Keyboards
9. Monitors
10. Tablets
11. Wireless earbuds (`add.py`)
12. Coffee machines (`add.py`)

## Requisitos

- Python 3.8+
- Playwright
- Entorno virtual (incluido)

## Instalación y uso

### 1. Activar el entorno virtual

```powershell
cd scrapping
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias (solo primera vez)

```powershell
pip install playwright
playwright install chromium
```

### 3. Ejecutar el scraping principal

```powershell
python scraper.py
```

### 4. Corregir errores del JSON

Si hay productos con errores (URLs malformadas, fallos de scraping), ejecuta:

```powershell
python correct.py
```

### 5. Agregar más productos

Para añadir productos adicionales hasta alcanzar 1600 (usa categorías extra):

```powershell
python add.py
```

### 6. Ver resultados

Al finalizar, se generará el archivo `amazon_products.json` con todos los productos extraídos.

## Estructura del JSON de salida

```json
[
  {
    "id": 1,
    "title": "Nombre del producto",
    "price": 299.99,
    "rating": 4.5,
    "review_count": "1,234 ratings",
    "description": "Descripción del producto",
    "features": ["Feature 1", "Feature 2"],
    "specifications": {
      "Brand": "Samsung",
      "Model": "XYZ"
    },
    "image_url": "https://...",
    "images_url": ["https://...", "https://...", "https://...", "https://..."],
    "product_url": "https://www.amazon.com/...",
    "category": "smartphones",
    "scraped_at": "2026-05-06T21:50:00"
  }
]
```

## Notas importantes

- Los scripts incluyen delays aleatorios entre peticiones para evitar bloqueos
- Se ejecutan en modo visible (`headless=False`) para depuración y evitar detección como bot
- Amazon puede tener medidas anti-scraping; si el script se detiene, intenta ejecutarlo nuevamente
- El tiempo estimado de ejecución es de 30-60 minutos debido a las 1500 peticiones
- Asegúrate de tener una conexión a internet estable
- El uso de este script debe cumplir con los Términos de Servicio de Amazon y el robots.txt

## Solución de problemas

Si el script falla por bloqueos de Amazon:
- Espera unos minutos y ejecuta `python correct.py` para re-intentar los fallos
- Luego ejecuta `python add.py` para completar los productos faltantes
- Si los bloqueos persisten, cambia el user-agent en el código
- Aumenta los tiempos de espera (sleep) entre peticiones si es necesario
