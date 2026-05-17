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

async def scrape_multi_images():
    with app.app_context():
        all_listings = Listing.query.all()
        sample = random.sample(all_listings, len(all_listings) // 2)
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        print(f"Scraping multiple FB images for {len(sample)} listings...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()

            for index, listing in enumerate(sample):
                existing = ListingImage.query.filter_by(listing_id=listing.id).all()
                for old in existing:
                    old_path = os.path.join(app.root_path, old.image_url.lstrip('/').replace('/', os.sep))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                    db.session.delete(old)
                if existing:
                    db.session.commit()
                    print(f"[{index+1}/{len(sample)}] Deleted {len(existing)} old image(s) for '{listing.title}'.")

                print(f"[{index+1}/{len(sample)}] Finding FB listing for: '{listing.title}'...")

                encoded_query = urllib.parse.quote(listing.title)
                search_url = f"https://www.facebook.com/marketplace/search/?query={encoded_query}"

                try:
                    await page.goto(search_url, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                    # Click the first marketplace result to open its detail page
                    first_result = page.locator("a[href*='/marketplace/item/']").first
                    href = await first_result.get_attribute("href")
                    if not href:
                        print(f"  -> No listing found for '{listing.title}'.")
                        continue

                    detail_url = f"https://www.facebook.com{href}" if href.startswith("/") else href
                    await page.goto(detail_url, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)

                    # Collect all fbcdn images from the detail page
                    images = await page.locator("img").all()
                    srcs = []
                    for img in images:
                        src = await img.get_attribute("src")
                        if src and "scontent" in src and "fbcdn.net" in src and src not in srcs:
                            srcs.append(src)

                    if not srcs:
                        print(f"  -> No images found on detail page for '{listing.title}'.")
                        continue

                    safe_title = re.sub(r'[^a-z0-9]', '_', listing.title.lower().strip('_'))
                    saved = 0

                    for i, src in enumerate(srcs):
                        filename = f"{safe_title}_{listing.id}_fb_multi_{i}.jpg"
                        filepath = os.path.join(upload_folder, filename)

                        try:
                            req = urllib.request.Request(src, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                            })
                            with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                                out_file.write(response.read())

                            db.session.add(ListingImage(
                                listing_id=listing.id,
                                image_url=f"/static/uploads/{filename}",
                                order=i
                            ))
                            saved += 1
                        except Exception as e:
                            print(f"  -> Failed to download image {i} for '{listing.title}': {e}")

                    db.session.commit()
                    print(f"  -> Saved {saved} image(s) for '{listing.title}'.")

                except Exception as e:
                    print(f"  -> Error scraping '{listing.title}': {e}")

                delay = random.uniform(2.0, 5.0)
                await page.wait_for_timeout(delay * 1000)

            await browser.close()

        print("Done!")

if __name__ == "__main__":
    asyncio.run(scrape_multi_images())
