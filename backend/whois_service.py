import whois
import requests
import os
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/api/whois")
async def get_whois(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    try:
        w = whois.whois(domain)
        # whois returns a dictionary-like object. We need to convert it to a standard dict and handle datetime objects.
        result = {}
        for key, value in w.items():
            if isinstance(value, list):
                result[key] = [str(v) if hasattr(v, 'isoformat') else v for v in value]
            elif hasattr(value, 'isoformat'):
                result[key] = str(value)
            else:
                result[key] = value
                
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/api/urlscan")
async def get_urlscan(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    try:
        # Search urlscan for public results of this domain
        headers = {}
        api_key = os.getenv('URLSCAN_API_KEY')
        if api_key:
            headers['API-Key'] = api_key
            
        res = requests.get(f"https://urlscan.io/api/v1/search/?q=page.domain:{domain}", headers=headers)
        res.raise_for_status()
        data = res.json()
        
        if not data.get("results") or len(data["results"]) == 0:
            return {"status": "error", "message": "No public scan results found for this domain on urlscan.io."}
            
        latest_scan = data["results"][0]
        
        # Try to fetch detailed result if we have an API key
        detailed_data = None
        if api_key:
            try:
                res_detail = requests.get(f"https://urlscan.io/api/v1/result/{latest_scan['task']['uuid']}/", headers=headers)
                if res_detail.status_code == 200 and 'warning' not in res_detail.json():
                    detailed_data = res_detail.json()
            except Exception:
                pass
                
        latest_scan["detailed"] = detailed_data
        
        return {"status": "success", "data": latest_scan}
    except Exception as e:
        return {"status": "error", "message": str(e)}
