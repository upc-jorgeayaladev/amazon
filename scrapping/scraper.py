import asyncio
import json
import random
import re
from datetime import datetime

from playwright.async_api import async_playwright

CATEGORIES = [
    "laptops",
    "smartphones",
    "headphones",
    "books",
    "kitchen appliances",
    "smart watches",
    "gaming mice",
    "keyboards",
    "monitors",
    "tablets",
]

PRODUCTS_PER_CATEGORY = 150
TOTAL_PRODUCTS = 1500


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


async def scrape_product_details(page, product_url, product_id):
    try:
        print("    Loading product page...")
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

        print(
            f"    ✓ Scraped: {details['title'][:50] if details['title'] else 'No title'}"
        )
        return details
    except Exception as e:
        print(f"    ✗ Error scraping product: {e}")
        return {
            "id": product_id,
            "product_url": product_url,
            "error": str(e),
            "scraped_at": datetime.now().isoformat(),
        }


async def scrape_category(page, category, target_count, start_id):
    products = []
    page_num = 1
    product_id = start_id

    while len(products) < target_count:
        search_url = (
            f"https://www.amazon.com/s?k={category.replace(' ', '+')}&page={page_num}"
        )
        try:
            print(f"  Loading search page {page_num}...")
            await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(3, 5))

            await page.wait_for_selector(
                "a[href*='/dp/'], a[href*='/gp/product/']", timeout=15000
            )

            all_links = await page.locator(
                "a[href*='/dp/'], a[href*='/gp/product/']"
            ).all()
            if not all_links:
                print(f"  No products found on page {page_num}")
                break

            print(f"  Found {len(all_links)} product links on page {page_num}")

            product_urls = []
            for link in all_links:
                try:
                    href = await link.get_attribute("href")
                    if href and ("/dp/" in href or "/gp/product/" in href):
                        full_url = f"https://www.amazon.com{href.split('?')[0]}"
                        if full_url not in product_urls:
                            product_urls.append(full_url)
                except:
                    continue

            for url in product_urls:
                if len(products) >= target_count:
                    break
                print(
                    f"  Scraping product {len(products) + 1}/{target_count} in category '{category}' (ID: {product_id})"
                )
                details = await scrape_product_details(page, url, product_id)
                details["category"] = category
                products.append(details)
                product_id += 1
                await asyncio.sleep(random.uniform(2, 4))

            page_num += 1
            if page_num > 10:
                break
        except Exception as e:
            print(f"  Error in category {category} page {page_num}: {e}")
            break

    return products, product_id


async def main():
    all_products = []
    scraped_urls = set()
    product_id = 1

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

        for category in CATEGORIES:
            remaining = TOTAL_PRODUCTS - len(all_products)
            if remaining <= 0:
                break

            per_cat = min(
                PRODUCTS_PER_CATEGORY,
                remaining // (len(CATEGORIES) - CATEGORIES.index(category) + 1) + 10,
            )
            print(f"\nScraping category: {category} (target: {per_cat})")

            products, product_id = await scrape_category(
                page, category, per_cat, product_id
            )
            for p in products:
                url = p.get("product_url")
                if url and url not in scraped_urls:
                    scraped_urls.add(url)
                    all_products.append(p)

            print(f"  Total products so far: {len(all_products)}")

        await browser.close()

    with open("amazon_products.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\nScraping complete. Total products: {len(all_products)}")
    print("Saved to amazon_products.json")


if __name__ == "__main__":
    asyncio.run(main())
