import asyncio
import os
import re
import random
import urllib.parse
import urllib.request

from playwright.async_api import async_playwright

from app import create_app, db
from app.models import Listing, ListingImage

app = create_app()

# Minimum dimensions (px) for an image to be considered a product photo.
# Filters out avatars, icons, and small UI images.
MIN_IMAGE_DIM = 300

# Maximum product images to save per listing.
MAX_IMAGES_PER_LISTING = 8

# Aria-labels Facebook uses for the carousel "next" button (try each in order).
CAROUSEL_NEXT_LABELS = [
    "Next photo",
    "Go to next photo",
    "Next image",
    "Next",
]


async def _collect_product_images(page):
    """Return fbcdn image URLs that are large enough to be product photos."""
    return await page.evaluate(f"""() => {{
        const imgs = Array.from(document.querySelectorAll('img'));
        const seen = new Set();
        const results = [];
        for (const img of imgs) {{
            const src = img.src || '';
            if (!src.includes('scontent') || !src.includes('fbcdn.net')) continue;
            if (seen.has(src)) continue;
            const w = img.naturalWidth || img.offsetWidth;
            const h = img.naturalHeight || img.offsetHeight;
            if (w > {MIN_IMAGE_DIM} && h > {MIN_IMAGE_DIM}) {{
                seen.add(src);
                results.push(src);
            }}
        }}
        return results;
    }}""")


async def _advance_carousel(page):
    """Try to click a carousel 'next' button. Returns True if clicked."""
    for label in CAROUSEL_NEXT_LABELS:
        btn = page.locator(f"[aria-label='{label}']").first
        try:
            if await btn.is_visible(timeout=400):
                await btn.click()
                return True
        except Exception:
            pass
    return False


async def _scrape_listing_images(page, listing):
    """
    Navigate to the FB Marketplace search, open the first result's detail page,
    cycle through the image carousel, and return a list of product image URLs.
    """
    encoded_query = urllib.parse.quote(listing.title)
    search_url = f"https://www.facebook.com/marketplace/search/?query={encoded_query}"

    await page.goto(search_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)

    # Click the first search result to open the listing detail page.
    first_result = page.locator("a[href*='/marketplace/item/']").first
    href = await first_result.get_attribute("href")
    if not href:
        return []

    detail_url = f"https://www.facebook.com{href}" if href.startswith("/") else href
    await page.goto(detail_url, wait_until="domcontentloaded")
    await page.wait_for_timeout(4000)

    # Scroll slightly to trigger lazy-loading of images.
    await page.evaluate("window.scrollTo(0, 300)")
    await page.wait_for_timeout(1000)

    # Collect the initial set of visible product images.
    product_srcs = list(await _collect_product_images(page))

    # Click through the carousel to expose any additional images.
    for _ in range(MAX_IMAGES_PER_LISTING - 1):
        clicked = await _advance_carousel(page)
        if not clicked:
            break
        await page.wait_for_timeout(800)
        new_srcs = await _collect_product_images(page)
        added = 0
        for src in new_srcs:
            if src not in product_srcs:
                product_srcs.append(src)
                added += 1
        if added == 0:
            # No new images found — we've gone full circle.
            break

    return product_srcs[:MAX_IMAGES_PER_LISTING]


def _download_image(src, filepath):
    req = urllib.request.Request(src, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    })
    with urllib.request.urlopen(req, timeout=15) as response, open(filepath, 'wb') as out:
        out.write(response.read())


async def scrape_multi_images():
    with app.app_context():
        all_listings = Listing.query.all()
        targets = random.sample(all_listings, len(all_listings) // 2)

        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        print(f"Scraping multiple FB images for {len(targets)} listings...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 720},
            )
            page = await context.new_page()

            for index, listing in enumerate(targets):
                print(f"[{index + 1}/{len(targets)}] '{listing.title}'...")

                try:
                    srcs = await _scrape_listing_images(page, listing)
                except Exception as e:
                    print(f"  -> Error navigating to listing: {e}")
                    srcs = []

                if not srcs:
                    print(f"  -> No product images found.")
                    await page.wait_for_timeout(random.uniform(2000, 4000))
                    continue

                safe_title = re.sub(r'[^a-z0-9]', '_', listing.title.lower()).strip('_')
                saved = 0

                for i, src in enumerate(srcs):
                    filename = f"{safe_title}_{listing.id}_fb_{i}.jpg"
                    filepath = os.path.join(upload_folder, filename)
                    try:
                        _download_image(src, filepath)
                        img = ListingImage()  # type: ignore[call-arg]
                        img.listing_id = listing.id
                        img.image_url = f"/static/uploads/{filename}"
                        img.order = i
                        db.session.add(img)
                        saved += 1
                    except Exception as e:
                        print(f"  -> Failed to download image {i}: {e}")

                if saved:
                    if not listing.image_url:
                        listing.image_url = f"/static/uploads/{safe_title}_{listing.id}_fb_0.jpg"
                    db.session.commit()
                print(f"  -> Saved {saved} image(s).")

                await page.wait_for_timeout(random.uniform(2000, 5000))

            await browser.close()

        print("Done!")


if __name__ == "__main__":
    asyncio.run(scrape_multi_images())
