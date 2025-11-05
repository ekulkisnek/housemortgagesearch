"""Test script to inspect ILFLS website structure and extract real data."""
import requests
from bs4 import BeautifulSoup
import re
import json

def inspect_ilfls_page(county="dupage"):
    """Inspect the actual structure of ILFLS page."""
    url = f"https://ilfls.com/free-daily-auction-lists/{county}"
    
    print(f"Inspecting: {url}")
    print("="*80)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=20)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save HTML for inspection
            with open(f'ilfls_{county}_page.html', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            print(f"Saved HTML to: ilfls_{county}_page.html")
            
            # Look for tables
            tables = soup.find_all('table')
            print(f"\nFound {len(tables)} tables")
            
            # Look for specific patterns
            text = soup.get_text()
            
            # Find all addresses
            addresses = re.findall(r'\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*', text)
            print(f"\nFound {len(addresses)} addresses:")
            for i, addr in enumerate(addresses[:10], 1):
                print(f"  {i}. {addr}")
            
            # Find case numbers
            case_nums = re.findall(r'(\d{2}[A-Z]{2}\d+)', text)
            print(f"\nFound {len(case_nums)} case numbers:")
            for i, case_num in enumerate(case_nums[:10], 1):
                print(f"  {i}. {case_num}")
            
            # Find prices
            prices = re.findall(r'\$([\d,]+(?:\.\d{2})?)', text)
            print(f"\nFound {len(prices)} prices:")
            for i, price in enumerate(prices[:10], 1):
                print(f"  {i}. ${price}")
            
            # Check for iframe or embedded content
            iframes = soup.find_all('iframe')
            print(f"\nFound {len(iframes)} iframes")
            for iframe in iframes:
                src = iframe.get('src', '')
                print(f"  Iframe src: {src}")
            
            # Look for data attributes or scripts
            scripts = soup.find_all('script')
            print(f"\nFound {len(scripts)} script tags")
            
            # Check for JSON data in scripts
            for script in scripts:
                script_text = script.string
                if script_text and ('address' in script_text.lower() or 'property' in script_text.lower()):
                    print("  Found script with potential property data")
                    # Look for JSON
                    json_match = re.search(r'\{[^{}]*"address"[^{}]*\}', script_text)
                    if json_match:
                        print(f"    Found JSON-like data: {json_match.group()[:200]}")
            
            # Print a sample of the page text
            print("\n" + "="*80)
            print("SAMPLE PAGE TEXT (first 2000 chars):")
            print("="*80)
            print(text[:2000])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_ilfls_page("dupage")

