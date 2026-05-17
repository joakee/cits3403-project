import os
import urllib.request
import urllib.parse
import re
from app import create_app, db
from app.models import Listing

app = create_app()

def seed_images():
    with app.app_context():
        listings = Listing.query.all()
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        print(f"Generating images for {len(listings)} listings...")
        
        for listing in listings:
            safe_title = re.sub(r'[^a-z0-9]', '_', listing.title.lower().strip('_'))
            filename = f"{safe_title}_{listing.id}_v3.jpg"
            filepath = os.path.join(upload_folder, filename)
            
            if not os.path.exists(filepath):
                print(f"Downloading image for: {listing.title}...")
                prompt = urllib.parse.quote(f"A clear product photo of {listing.title}, {listing.category}")
                url = f"https://image.pollinations.ai/prompt/{prompt}?width=600&height=400&nologo=true"
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                    with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    print(f"Failed to download image for {listing.title}: {e}")
                    continue
                    
            listing.image_url = f"/static/uploads/{filename}"
            db.session.commit()
            
        print("Done generating images!")

if __name__ == '__main__':
    seed_images()
