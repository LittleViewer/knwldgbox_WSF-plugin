
import feedparser
import email.utils
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta

router = APIRouter()

# Simple in-memory cache to avoid spamming the site
CACHE_TTL = timedelta(minutes=15)
cache = {
    "timestamp": None,
    "data": []
}

FEEDS = [
    "https://frenchbreaches.com/feed.xml",
    "https://frenchbreaches.com/blog/feed.xml"
]

@router.get("/api/dataleaks/frenchbreaches")
async def get_french_breaches():
    now = datetime.now()
    if cache["timestamp"] and cache["data"] and now - cache["timestamp"] < CACHE_TTL:
        return {"status": "success", "cached": True, "data": cache["data"]}
    
    try:
        leaks = []
        for url in FEEDS:
            feed = feedparser.parse(url)
            if getattr(feed, "bozo", 0) == 1 and not feed.entries:
                continue
                
            for entry in feed.entries:
                # Format Date
                date_str = entry.get('published', '')
                dt_obj = None
                try:
                    if date_str:
                        dt_obj = email.utils.parsedate_to_datetime(date_str)
                        date_str = dt_obj.strftime("%d %b %Y - %H:%M")
                except Exception:
                    pass
                
                # Tags processing
                tags = []
                if 'tags' in entry:
                    for t in entry.tags:
                        term = t.term
                        tags.extend([x.strip() for x in term.split(",") if x.strip()])
                
                # Description
                desc = entry.get('summary', '')
                if desc.startswith('# '):
                    desc = desc[2:]
                
                if len(desc) > 300:
                    desc = desc[:297] + '...'
                
                leaks.append({
                    "id": entry.get('link', entry.get('title')),
                    "title": entry.get('title', 'Unknown'),
                    "url": entry.get('link', ''),
                    "date": date_str,
                    "description": desc,
                    "impact": "",
                    "tags": tags,
                    "timestamp": dt_obj.timestamp() if dt_obj else 0
                })
        
        # Sort by newest first
        leaks.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        for leak in leaks:
            leak.pop('timestamp', None)
            
        leaks = leaks[:30]
        
        cache["timestamp"] = now
        cache["data"] = leaks
        
        return {"status": "success", "cached": False, "data": leaks}
            
    except Exception as e:
        if cache["data"]:
            return {"status": "success", "cached": True, "error": str(e), "data": cache["data"]}
        raise HTTPException(status_code=500, detail=str(e))

