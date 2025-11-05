"""Find ILFLS API endpoint by inspecting network requests."""
import requests
from bs4 import BeautifulSoup
import json
import re

def find_api_endpoint():
    """Try to find the API endpoint ILFLS uses."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Try common API patterns
    base_url = "https://ilfls.com"
    
    # Check for API endpoints
    api_patterns = [
        "/api/foreclosures",
        "/api/auctions",
        "/api/listings",
        "/api/dupage",
        "/api/cook",
        "/api/foreclosure-listings",
    ]
    
    print("Trying to find API endpoint...")
    
    for pattern in api_patterns:
        url = base_url + pattern
        try:
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"\n[FOUND] API endpoint: {url}")
                    print(f"Data: {json.dumps(data, indent=2)[:500]}")
                    return url
                except:
                    pass
        except:
            pass
    
    # Try to get the main page and look for API calls in scripts
    url = "https://ilfls.com/free-daily-auction-lists/dupage"
    response = session.get(url, timeout=20)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')
        
        print("\nChecking scripts for API endpoints...")
        for script in scripts:
            if script.string:
                # Look for HTTP calls
                if 'http' in script.string.lower() or 'api' in script.string.lower():
                    # Look for URLs
                    urls = re.findall(r'https?://[^\s"\'<>]+', script.string)
                    for url_match in urls:
                        if 'api' in url_match.lower() or 'foreclosure' in url_match.lower():
                            print(f"  Found potential API: {url_match}")
        
        # Look for data attributes
        data_elements = soup.find_all(attrs={'data-api': True})
        for elem in data_elements:
            print(f"  Found data-api attribute: {elem.get('data-api')}")
    
    # Try direct data access patterns
    print("\nTrying direct data URLs...")
    data_urls = [
        "https://ilfls.com/api/foreclosures/dupage",
        "https://ilfls.com/api/auctions/dupage",
        "https://ilfls.com/data/foreclosures/dupage.json",
        "https://ilfls.com/data/dupage-foreclosures.json",
    ]
    
    for data_url in data_urls:
        try:
            response = session.get(data_url, timeout=10)
            if response.status_code == 200:
                print(f"[FOUND] Data URL: {data_url}")
                try:
                    data = response.json()
                    print(f"Data preview: {json.dumps(data, indent=2)[:500]}")
                    return data_url
                except:
                    print(f"  Response: {response.text[:200]}")
        except Exception as e:
            pass
    
    print("\n[INFO] Could not find direct API endpoint")
    print("ILFLS likely loads data via JavaScript")
    return None

if __name__ == "__main__":
    find_api_endpoint()

