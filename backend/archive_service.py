import nodriver as uc
import asyncio
import base64
from fastapi import APIRouter
from pydantic import BaseModel
import os
import uuid
from urllib.parse import urlparse
import time

router = APIRouter()

class ArchiveRequest(BaseModel):
    url: str

from config import ARCHIVES_DIR

@router.post("/api/archive")
async def archive_url_endpoint(req: ArchiveRequest):
    url = req.url
    # Format a safe filename based on the domain
    parsed = urlparse(url)
    domain = parsed.netloc if parsed.netloc else parsed.path.replace('/', '_')
    domain = domain.replace(":", "_")
    timestamp = int(time.time())
    archive_id = f"{domain}_{timestamp}_{uuid.uuid4().hex[:6]}"
    
    archive_path_base = os.path.join(ARCHIVES_DIR, archive_id)
    pdf_path = f"{archive_path_base}.pdf"
    png_path = f"{archive_path_base}.png"

    try:
        # Launch chromium
        browser = await uc.start(headless=True)
        
        try:
            # Go to URL
            page = await browser.get(url)
            
            # Wait an extra 3 seconds for dynamic JS elements (like images or tweets) to render fully
            await asyncio.sleep(3)
            
            # Save PDF (print_background ensures CSS colors/images are rendered)
            result = await page.send(uc.cdp.page.print_to_pdf(print_background=True))
            pdf_data = base64.b64decode(result[0])
            with open(pdf_path, 'wb') as f:
                f.write(pdf_data)
            
            # Save Full Page Screenshot
            await page.save_screenshot(png_path, full_page=True)
        finally:
            browser.stop()
            
        return {
            "status": "success",
            "archive_id": archive_id,
            "url": url,
            "pdf_file": f"{archive_id}.pdf",
            "png_file": f"{archive_id}.png",
            "timestamp": timestamp
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }

@router.get("/api/archives")
def get_archives():
    if not os.path.exists(ARCHIVES_DIR):
        return []
    
    files = os.listdir(ARCHIVES_DIR)
    archives = {}
    
    for f in files:
        if f.endswith('.pdf') or f.endswith('.png'):
            archive_id = f.rsplit('.', 1)[0]
            if archive_id not in archives:
                archives[archive_id] = {
                    "archive_id": archive_id,
                    "pdf_file": None,
                    "png_file": None
                }
            if f.endswith('.pdf'):
                archives[archive_id]["pdf_file"] = f
            elif f.endswith('.png'):
                archives[archive_id]["png_file"] = f
                
    return list(archives.values())

@router.delete("/api/archives/{archive_id}")
def delete_archive_endpoint(archive_id: str):
    pdf_path = os.path.join(ARCHIVES_DIR, f"{archive_id}.pdf")
    png_path = os.path.join(ARCHIVES_DIR, f"{archive_id}.png")
    
    deleted = False
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        deleted = True
    if os.path.exists(png_path):
        os.remove(png_path)
        deleted = True
        
    return {"success": deleted}

