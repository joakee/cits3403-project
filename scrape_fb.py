import asyncio
import os
import re
import random
import urllib.parse
import urllib.request
from playwright.async_api import async_playwright

from app import create_app, db
from app.models import Listing

app = create_app()

async def scrape_all_listings():
    with app.app_context():
        listings = Listing.query.all()
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        print(f"Starting Facebook Marketplace scraper for {len(listings)} listings...")
        
        async with async_playwright() as p:
            # Headful mode is required for Facebook
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()
            
            for index, listing in enumerate(listings):
                safe_title = re.sub(r'[^a-z0-9]', '_', listing.title.lower().strip('_'))
                filename = f"{safe_title}_{listing.id}_fb.jpg"
                filepath = os.path.join(upload_folder, filename)
                
                print(f"[{index+1}/{len(listings)}] Searching FB Marketplace for: '{listing.title}'...")
                
                encoded_query = urllib.parse.quote(listing.title)
                search_url = f"https://www.facebook.com/marketplace/search/?query={encoded_query}"
                
                try:
                    # Navigate and wait for some basic loading
                    await page.goto(search_url, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3000)
                    
                    image_src = None
                    images = await page.locator("img").all()
                    
                    for img in images:
                        src = await img.get_attribute("src")
                        if not src:
                            continue
                        if "scontent" in src and "fbcdn.net" in src:
                            image_src = src
                            break
                            
                    if image_src:
                        req = urllib.request.Request(image_src, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                        })
                        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                            out_file.write(response.read())
                        
                        listing.image_url = f"/static/uploads/{filename}"
                        db.session.commit()
                        print(f"  -> Successfully saved to {filename} and updated DB.")
                    else:
                        print(f"  -> Could not find a suitable image for '{listing.title}'.")
                        
                except Exception as e:
                    print(f"  -> Error while scraping '{listing.title}': {e}")
                
                # Random delay between 2-5 seconds to avoid being quickly blocked by Facebook's anti-bot systems
                delay = random.uniform(2.0, 5.0)
                await page.wait_for_timeout(delay * 1000)
                
            await browser.close()
        print("Scraping completed!")

if __name__ == "__main__":
    asyncio.run(scrape_all_listings())
