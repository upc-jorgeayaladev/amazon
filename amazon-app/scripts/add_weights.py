import json
import re
import random

random.seed(42)

WEIGHT_RANGES = {
    "laptops": (1.2, 3.5),
    "smartphones": (0.15, 0.35),
    "tablets": (0.3, 0.8),
    "headphones": (0.15, 0.4),
    "wireless earbuds": (0.03, 0.08),
    "keyboards": (0.3, 1.5),
    "gaming mice": (0.07, 0.15),
    "monitors": (3.0, 8.0),
    "smart watches": (0.03, 0.08),
    "coffee machines": (3.0, 8.0),
    "kitchen appliances": (1.0, 7.0),
    "books": (0.2, 1.5),
}

CONVERSION_TO_KG = {
    "kilograms": 1.0,
    "pounds": 0.453592,
    "ounces": 0.0283495,
    "grams": 0.001,
    "g": 0.001,
    "hundredths pounds": 0.00453592,
}


def parse_weight(weight_str):
    if not weight_str or weight_str == "N/A":
        return None
    match = re.match(r"([\d.]+)\s+(.+)", weight_str, re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).strip().lower()
    factor = CONVERSION_TO_KG.get(unit)
    if factor is None:
        return None
    return round(value * factor, 4)


def get_default_weight(category):
    low, high = WEIGHT_RANGES.get(category, (0.5, 2.0))
    return round(random.uniform(low, high), 2)


def main():
    with open("data/products.json", encoding="utf-8") as f:
        products = json.load(f)

    stats = {"parsed": 0, "default": 0, "failed": 0}

    for p in products:
        specs = p.get("specifications", {})
        raw = specs.get("Item Weight", "N/A")
        weight_kg = parse_weight(raw)

        if weight_kg is not None:
            p["weight"] = weight_kg
            stats["parsed"] += 1
        else:
            p["weight"] = get_default_weight(p.get("category", "unknown"))
            stats["default"] += 1

    with open("data/products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"Total: {len(products)}")
    print(f"  Peso parseado de specifications: {stats['parsed']}")
    print(f"  Peso asignado por categoría: {stats['default']}")

    sample = random.sample(products, 5)
    print("\nMuestra:")
    for p in sample:
        print(f"  id={p['id']} cat={p['category']} weight={p['weight']}kg")


if __name__ == "__main__":
    main()
