import asyncio
import socket
import ssl
import httpx
import dns.resolver
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from urllib.parse import urlparse
from datetime import datetime
from Wappalyzer import Wappalyzer, WebPage

router = APIRouter()

@router.get("/api/target/dns")
async def get_dns_records(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    records = {"A": [], "AAAA": [], "MX": [], "TXT": [], "NS": [], "CNAME": []}
    
    # We will query sequentially or concurrently. Doing it sequentially for simplicity.
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 3

    for rtype in records.keys():
        try:
            answers = resolver.resolve(domain, rtype)
            for rdata in answers:
                records[rtype].append(rdata.to_text().strip('"'))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
            pass
        except Exception:
            pass
            
    return {"status": "success", "data": records}


@router.get("/api/target/ssl")
async def get_ssl_info(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        # Parse certificate
        issuer = dict(x[0] for x in cert.get('issuer', []))
        subject = dict(x[0] for x in cert.get('subject', []))
        
        valid_from = datetime.strptime(cert['notBefore'], "%b %d %H:%M:%S %Y %Z")
        valid_to = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
        
        sans = []
        for san in cert.get('subjectAltName', []):
            if san[0] == 'DNS':
                sans.append(san[1])
                
        days_remaining = (valid_to - datetime.utcnow()).days

        return {
            "status": "success",
            "data": {
                "issuer": issuer.get('organizationName', issuer.get('commonName', 'Unknown')),
                "subject": subject.get('commonName', 'Unknown'),
                "valid_from": valid_from.isoformat(),
                "valid_to": valid_to.isoformat(),
                "days_remaining": days_remaining,
                "sans": sans[:10], # Limit to first 10
                "version": cert.get('version'),
                "serial_number": cert.get('serialNumber')
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/api/target/headers")
async def get_security_headers(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    url = f"https://{domain}"
    
    try:
        async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
            response = await client.get(url, follow_redirects=True)
            
        headers = response.headers
        
        security_headers = {
            "Strict-Transport-Security": headers.get("Strict-Transport-Security"),
            "Content-Security-Policy": headers.get("Content-Security-Policy"),
            "X-Frame-Options": headers.get("X-Frame-Options"),
            "X-Content-Type-Options": headers.get("X-Content-Type-Options"),
            "Referrer-Policy": headers.get("Referrer-Policy"),
            "Permissions-Policy": headers.get("Permissions-Policy"),
            "Server": headers.get("Server"),
            "X-Powered-By": headers.get("X-Powered-By")
        }
        
        return {"status": "success", "data": security_headers}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def check_port(host, port, timeout=2):
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return port, True
    except Exception:
        return port, False


@router.get("/api/target/ports")
async def get_open_ports(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 993, 995, 3306, 3389, 5432, 8080, 8443]
    
    tasks = [check_port(domain, port) for port in common_ports]
    results = await asyncio.gather(*tasks)
    
    open_ports = [port for port, is_open in results if is_open]
    
    return {"status": "success", "data": open_ports}


@router.get("/api/target/crawl")
async def get_crawl_data(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    base_url = f"https://{domain}"
    robots_url = f"{base_url}/robots.txt"
    
    crawl_rules = []
    internal_links = set()
    external_links = set()
    
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            # 1. Fetch robots.txt
            try:
                robots_res = await client.get(robots_url, follow_redirects=True)
                if robots_res.status_code == 200:
                    current_agent = "*"
                    for line in robots_res.text.splitlines():
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                            
                        if line.lower().startswith('user-agent:'):
                            current_agent = line.split(':', 1)[1].strip()
                        elif line.lower().startswith('allow:'):
                            crawl_rules.append({"agent": current_agent, "rule": "Allow", "path": line.split(':', 1)[1].strip()})
                        elif line.lower().startswith('disallow:'):
                            crawl_rules.append({"agent": current_agent, "rule": "Disallow", "path": line.split(':', 1)[1].strip()})
            except Exception:
                pass
                
            # Extract sitemaps from robots.txt
            sitemap_urls = [f"{base_url}/sitemap.xml"]
            if 'robots_res' in locals() and getattr(robots_res, 'status_code', 0) == 200:
                for line in robots_res.text.splitlines():
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        if sitemap_url not in sitemap_urls:
                            sitemap_urls.append(sitemap_url)
                            
            # 2. Fetch sitemaps to get more pages
            for s_url in sitemap_urls[:3]: # limit to 3 sitemaps to avoid hangs
                try:
                    s_res = await client.get(s_url, follow_redirects=True)
                    if s_res.status_code == 200:
                        soup_s = BeautifulSoup(s_res.text, 'html.parser')
                        for loc in soup_s.find_all('loc'):
                            url = loc.text.strip()
                            parsed_loc = urlparse(url)
                            if not parsed_loc.netloc or parsed_loc.netloc == domain or parsed_loc.netloc.endswith(f".{domain}"):
                                path = parsed_loc.path
                                if not path: path = "/"
                                internal_links.add(path)
                except Exception:
                    pass
                
            # 3. Fetch homepage to get links
            try:
                home_res = await client.get(base_url, follow_redirects=True)
                if home_res.status_code == 200:
                    soup = BeautifulSoup(home_res.text, 'html.parser')
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href'].strip()
                        if href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
                            continue
                            
                        parsed_href = urlparse(href)
                        if not parsed_href.netloc or parsed_href.netloc == domain or parsed_href.netloc.endswith(f".{domain}"):
                            # Internal link
                            path = parsed_href.path
                            if not path:
                                path = "/"
                            internal_links.add(path)
                        else:
                            # External link
                            external_links.add(href)
            except Exception:
                pass
                
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    return {
        "status": "success",
        "data": {
            "rules": crawl_rules[:100], 
            "internal_links": sorted(list(internal_links))[:500], 
            "external_links": sorted(list(external_links))[:500],
            "internal_count": len(internal_links),
            "external_count": len(external_links)
        }
    }

@router.get("/api/target/subdomains")
async def get_subdomains(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    subdomains = set()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Try HackerTarget first
            try:
                ht_res = await client.get(f"https://api.hackertarget.com/hostsearch/?q={domain}")
                if ht_res.status_code == 200:
                    for line in ht_res.text.splitlines():
                        if ',' in line:
                            sub = line.split(',')[0].strip().lower()
                            if sub and sub.endswith(domain):
                                subdomains.add(sub)
            except Exception:
                pass
                
            # Try crt.sh as backup if HT fails
            if not subdomains:
                try:
                    res = await client.get(f"https://crt.sh/?q=%.{domain}&output=json")
                    if res.status_code == 200:
                        data = res.json()
                        for entry in data:
                            name = entry.get('name_value', '')
                            for sub in name.split('\n'):
                                sub = sub.strip().lower()
                                if sub and sub.endswith(domain) and '*' not in sub:
                                    subdomains.add(sub)
                except Exception:
                    pass
                
            return {"status": "success", "data": sorted(list(subdomains))[:100]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/api/target/technologies")
async def get_technologies(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    try:
        wappalyzer = Wappalyzer.latest()
        webpage = WebPage.new_from_url(f"https://{domain}")
        technologies = wappalyzer.analyze_with_versions_and_categories(webpage)
        
        tech_list = []
        for tech_name, tech_info in technologies.items():
            categories = []
            for c in tech_info.get("categories", []):
                if isinstance(c, str):
                    categories.append(c)
                elif isinstance(c, dict):
                    categories.append(c.get("name", ""))
                    
            tech_list.append({
                "name": tech_name,
                "versions": tech_info.get("versions", []),
                "categories": categories
            })
            
        return {"status": "success", "data": tech_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/api/target/wayback")
async def get_wayback(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    url = f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&fl=timestamp&collapse=urlkey"
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            # Get first snapshot
            first_res = await client.get(f"{url}&limit=1")
            first_data = first_res.json() if first_res.status_code == 200 and len(first_res.content) > 10 else []
            
            # Get last snapshot
            last_res = await client.get(f"{url}&limit=1&fastLatest=true")
            last_data = last_res.json() if last_res.status_code == 200 and len(last_res.content) > 10 else []
            
            first_date = first_data[1][0] if len(first_data) > 1 else None
            last_date = last_data[1][0] if len(last_data) > 1 else None
            
            return {
                "status": "success",
                "data": {
                    "first_snapshot": first_date,
                    "last_snapshot": last_date,
                    "archive_url": f"https://web.archive.org/web/*/{domain}"
                }
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/api/target/geolocation")
async def get_geolocation(domain: str):
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    try:
        ip = socket.gethostbyname(domain)
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f"http://ip-api.com/json/{ip}")
            if res.status_code == 200:
                data = res.json()
                if data.get('status') == 'success':
                    return {
                        "status": "success", 
                        "data": {
                            "ip": ip,
                            "country": data.get("country"),
                            "city": data.get("city"),
                            "isp": data.get("isp"),
                            "org": data.get("org"),
                            "lat": data.get("lat"),
                            "lon": data.get("lon")
                        }
                    }
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    return {"status": "error", "message": "Could not resolve geolocation"}
