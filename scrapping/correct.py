import asyncio
import json
import random
import re
from datetime import datetime

from playwright.async_api import async_playwright


def parse_price(price_text):
    if not price_text:
        return None
    cleaned = price_text.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except:
        return None


def parse_rating(rating_text):
    if not rating_text:
        return None
    match = re.search(r"(\d+\.?\d*)", rating_text)
    if match:
        try:
            return float(match.group(1))
        except:
            pass
    return None


def fix_url(product_url):
    """Attempt to fix malformed URLs"""
    if not product_url:
        return None

    # Pattern to find Amazon product URLs
    patterns = [
        r"(https://www\.amazon\.com/dp/[A-Z0-9]{10})",
        r"(https://www\.amazon\.com/gp/product/[A-Z0-9]{10})",
        r"(https://www\.amazon\.com/[^\s]*?/dp/[A-Z0-9]{10})",
    ]

    for pattern in patterns:
        match = re.search(pattern, product_url)
        if match:
            return match.group(1)

    # If URL starts with https://www.amazon.com but has garbage after
    if "amazon.com" in product_url:
        # Try to extract just the amazon.com part with proper product path
        amazon_match = re.search(
            r"(https://www\.amazon\.com).*?(/dp/[A-Z0-9]{10})", product_url
        )
        if amazon_match:
            return amazon_match.group(1) + amazon_match.group(2)

    return None


async def scrape_product_details(page, product_url, product_id):
    try:
        print(f"    Re-scraping product ID {product_id}...")
        await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(random.uniform(2, 3))

        details = {"id": product_id}

        title = await page.locator("#productTitle").first.text_content(timeout=10000)
        details["title"] = title.strip() if title else None

        price_selectors = [
            ".a-price .a-offscreen",
            ".a-price-whole",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
        ]
        price_text = None
        for sel in price_selectors:
            try:
                price_text = await page.locator(sel).first.text_content(timeout=3000)
                if price_text:
                    break
            except:
                continue
        details["price"] = parse_price(price_text) if price_text else None

        rating_text = None
        rating_selectors = [
            "#acrPopover .a-icon-alt",
            ".a-star-medium .a-icon-alt",
            "[data-hook='rating-out-of-text']",
        ]
        for sel in rating_selectors:
            try:
                rating_text = await page.locator(sel).first.text_content(timeout=3000)
                if rating_text:
                    break
            except:
                continue
        details["rating"] = parse_rating(rating_text) if rating_text else None

        review_text = None
        try:
            review_text = await page.locator(
                "#acrCustomerReviewText"
            ).first.text_content(timeout=3000)
        except:
            pass
        details["review_count"] = review_text.strip() if review_text else None

        desc_text = None
        desc_selectors = [
            "#productDescription p",
            "#productDescription",
            "#feature-bullets .a-unordered-list",
        ]
        for sel in desc_selectors:
            try:
                desc_text = await page.locator(sel).first.text_content(timeout=3000)
                if desc_text:
                    break
            except:
                continue
        details["description"] = desc_text.strip() if desc_text else None

        features = []
        feature_bullets = page.locator(
            "#feature-bullets li:not(.aok-hidden) span.a-list-item, #feature-bullets li"
        )
        count = await feature_bullets.count()
        for i in range(min(count, 10)):
            try:
                text = await feature_bullets.nth(i).text_content(timeout=2000)
                if text and text.strip():
                    features.append(text.strip())
            except:
                continue
        details["features"] = features

        specs = {}
        spec_rows = page.locator(
            "#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr, .prodDetTable tr"
        )
        count = await spec_rows.count()
        for i in range(count):
            try:
                row = spec_rows.nth(i)
                th = await row.locator(
                    "th, .a-text-bold, td:first-child"
                ).first.text_content(timeout=2000)
                td = await row.locator("td, .a-text-normal").last.text_content(
                    timeout=2000
                )
                if th and td and th.strip() and td.strip():
                    specs[th.strip()] = td.strip()
            except:
                continue
        details["specifications"] = specs

        img = None
        img_selectors = ["#landingImage", "#imgBlkFront", "#main-image"]
        for sel in img_selectors:
            try:
                img = await page.locator(sel).get_attribute("src", timeout=3000)
                if img:
                    break
            except:
                continue
        details["image_url"] = img

        images_url = []
        try:
            alt_images = page.locator(
                "#altImages img, #imageBlock img, [data-action='main-image-click'] img"
            )
            count = await alt_images.count()
            for i in range(min(count, 4)):
                try:
                    src = await alt_images.nth(i).get_attribute("src", timeout=2000)
                    if src and src not in images_url and "sprite" not in src.lower():
                        images_url.append(src)
                except:
                    continue
        except:
            pass
        details["images_url"] = images_url

        details["product_url"] = product_url
        details["scraped_at"] = datetime.now().isoformat()
        details.pop("error", None)

        print(
            f"    ✓ Corrected: {details['title'][:50] if details['title'] else 'No title'}"
        )
        return details
    except Exception as e:
        print(f"    ✗ Still failed: {e}")
        return {
            "id": product_id,
            "product_url": product_url,
            "error": str(e),
            "scraped_at": datetime.now().isoformat(),
        }


async def main():
    # Load existing products
    try:
        with open("amazon_products.json", "r", encoding="utf-8") as f:
            products = json.load(f)
        print(f"Loaded {len(products)} products")
    except FileNotFoundError:
        print("No amazon_products.json found")
        return

    # Find products with errors
    error_products = []
    fixed_products = []

    for i, product in enumerate(products):
        if "error" in product:
            error_products.append((i, product))
        elif product.get("product_url") and "amazon.comhttps" in product.get(
            "product_url", ""
        ):
            error_products.append((i, product))

    print(f"Found {len(error_products)} products with errors")

    if not error_products:
        print("No errors to fix!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = await context.new_page()

        for idx, (original_idx, product) in enumerate(error_products):
            print(
                f"\nFixing product {idx + 1}/{len(error_products)} (ID: {product.get('id')})"
            )

            # Try to fix URL
            fixed_url = fix_url(product.get("product_url", ""))
            if not fixed_url:
                print(f"  Could not fix URL: {product.get('product_url')}")
                continue

            print(f"  Fixed URL: {fixed_url}")

            # Re-scrape the product
            corrected = await scrape_product_details(page, fixed_url, product.get("id"))
            corrected["category"] = product.get("category", "unknown")
            fixed_products.append((original_idx, corrected))
            await asyncio.sleep(random.uniform(2, 4))

        await browser.close()

    # Update the original products list
    for original_idx, corrected in fixed_products:
        products[original_idx] = corrected

    # Save the corrected JSON
    with open("amazon_products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print("\nCorrection complete!")
    print(f"Total products: {len(products)}")
    print(f"Fixed products: {len(fixed_products)}")
    print("Saved to amazon_products.json")


if __name__ == "__main__":
    asyncio.run(main())
