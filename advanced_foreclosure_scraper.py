"""
Advanced Foreclosure Scraper - Gets Real Data from Multiple Free Sources
Uses Selenium for JavaScript-rendered pages and multiple free sources
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
from typing import Dict, List, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[INFO] Selenium not available - will use requests only")


class AdvancedForeclosureScraper:
    """Advanced scraper that gets real foreclosure data."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.properties = []
        self.driver = None
        
    def get_ilfls_with_selenium(self, county: str) -> List[Dict]:
        """Get ILFLS data using Selenium to execute JavaScript."""
        if not SELENIUM_AVAILABLE:
            print(f"[SKIP] Selenium not available for {county}")
            return []
        
        print(f"\n[SEARCHING] Using Selenium for {county} County ILFLS...")
        
        try:
            if not self.driver:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                self.driver = webdriver.Chrome(options=chrome_options)
            
            url = f"https://ilfls.com/free-daily-auction-lists/{county.lower()}"
            self.driver.get(url)
            
            # Wait for Angular to load data
            time.sleep(5)
            
            # Get page source after JavaScript execution
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for property listings
            properties = self._extract_properties_from_html(soup, county, url)
            
            return properties
            
        except Exception as e:
            print(f"   [ERROR] Selenium error: {str(e)[:100]}")
            return []
    
    def get_foreclosure_listings_usa(self) -> List[Dict]:
        """Scrape ForeclosureListingsUSA.com."""
        print("\n[SEARCHING] ForeclosureListingsUSA.com...")
        
        properties = []
        
        try:
            # Try Illinois listings
            url = "https://www.foreclosurelistingsusa.com/illinois-foreclosures"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Extract addresses
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                # Extract prices
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:50]):
                    prop = {
                        'source': 'ForeclosureListingsUSA',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [WARNING] HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_hud_foreclosures(self) -> List[Dict]:
        """Get HUD foreclosure listings."""
        print("\n[SEARCHING] HUD Home Store...")
        
        properties = []
        
        try:
            # HUD Home Store - Illinois search
            url = "https://www.hudhomestore.com/Home/PropertySearch"
            
            # Try to get search results
            search_params = {
                'state': 'IL',
                'propertyType': '1'  # Single Family
            }
            
            response = self.session.get(url, params=search_params, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # HUD properties typically have addresses and prices
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:30]):
                    prop = {
                        'source': 'HUD Home Store',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] HUD requires form submission - visit https://www.hudhomestore.com")
                
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_cook_county_sheriff(self) -> List[Dict]:
        """Get Cook County Sheriff foreclosure sales."""
        print("\n[SEARCHING] Cook County Sheriff...")
        
        properties = []
        
        try:
            url = "https://www.cookcountysheriff.org/foreclosure-sales/"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Extract addresses
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                case_numbers = re.findall(r'Case\s+[Nn]o[.:]?\s*(\d{2}[A-Z]{2}\d+)', text)
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:30]):
                    prop = {
                        'source': 'Cook County Sheriff',
                        'county': 'Cook',
                        'address': addr.strip(),
                        'case_number': case_numbers[i] if i < len(case_numbers) else None,
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [WARNING] HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def _extract_properties_from_html(self, soup: BeautifulSoup, county: str, url: str) -> List[Dict]:
        """Extract properties from HTML."""
        properties = []
        text = soup.get_text()
        
        # Look for property listings
        # Try to find addresses in various formats
        address_patterns = [
            r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
            r'(\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Blvd|Ln|Ct|Way|Pkwy|Pl|Cir)[\s\w,]+IL)'
        ]
        
        addresses = []
        for pattern in address_patterns:
            matches = re.findall(pattern, text)
            addresses.extend(matches)
        
        # Remove duplicates
        addresses = list(dict.fromkeys(addresses))
        
        # Find case numbers
        case_numbers = re.findall(r'(\d{2}[A-Z]{2}\d+)', text)
        
        # Find prices
        prices = re.findall(r'\$([\d,]+(?:\.\d{2})?)', text)
        
        # Find dates
        dates = re.findall(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        
        for i, addr in enumerate(addresses[:50]):
            prop = {
                'source': 'ILFLS',
                'county': county,
                'address': addr.strip(),
                'case_number': case_numbers[i] if i < len(case_numbers) else None,
                'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                'estimated_value': self._parse_price(prices[i]) if i < len(prices) else None,
                'auction_date': dates[i] if i < len(dates) else None,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            properties.append(prop)
        
        return properties
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price to float."""
        try:
            cleaned = re.sub(r'[^\d.]', '', str(price_str))
            return float(cleaned) if cleaned else None
        except:
            return None
    
    def get_all_foreclosures(self, counties: List[str] = None) -> List[Dict]:
        """Get all foreclosure listings from all sources."""
        if counties is None:
            counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
        
        print("="*80)
        print("ADVANCED FORECLOSURE AUCTION SCRAPER")
        print("="*80)
        print(f"Searching counties: {', '.join(counties)}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        all_properties = []
        
        # Try ILFLS with Selenium if available
        if SELENIUM_AVAILABLE:
            for county in counties:
                props = self.get_ilfls_with_selenium(county)
                all_properties.extend(props)
                time.sleep(2)
        else:
            print("\n[INFO] Install selenium for JavaScript-rendered pages:")
            print("  pip install selenium")
            print("  Also need ChromeDriver: https://chromedriver.chromium.org/")
        
        # Get from other free sources
        all_properties.extend(self.get_foreclosure_listings_usa())
        all_properties.extend(self.get_hud_foreclosures())
        all_properties.extend(self.get_cook_county_sheriff())
        
        # Remove duplicates
        seen = set()
        unique = []
        for prop in all_properties:
            addr_key = prop.get('address', '').lower().strip()
            if addr_key and addr_key not in seen:
                seen.add(addr_key)
                unique.append(prop)
        
        # Sort by price
        unique.sort(key=lambda x: x.get('opening_bid') or x.get('estimated_value') or float('inf'))
        
        self.properties = unique
        return unique
    
    def display_results(self, limit: int = 100):
        """Display results."""
        if not self.properties:
            print("\n" + "="*80)
            print("[WARNING] NO PROPERTIES FOUND")
            print("="*80)
            print("\nThe websites may use JavaScript rendering.")
            print("Try installing Selenium: pip install selenium")
            print("\nOr visit these sources directly:")
            print("  • ILFLS: https://ilfls.com/free-daily-auction-lists/")
            print("  • HUD: https://www.hudhomestore.com")
            print("  • ForeclosureListingsUSA: https://www.foreclosurelistingsusa.com")
            return
        
        print("\n" + "="*80)
        print(f"FORECLOSURE AUCTIONS - SORTED BY LOWEST PRICE")
        print("="*80)
        print(f"Total Found: {len(self.properties)}")
        print(f"Showing: {min(limit, len(self.properties))}")
        print("="*80)
        
        for i, prop in enumerate(self.properties[:limit], 1):
            print(f"\n{'-'*80}")
            print(f"PROPERTY #{i}")
            print(f"{'-'*80}")
            print(f"Address:     {prop.get('address', 'N/A')}")
            print(f"County:      {prop.get('county', 'N/A')}")
            
            if prop.get('case_number'):
                print(f"Case Number: {prop.get('case_number')}")
            
            price = prop.get('opening_bid') or prop.get('estimated_value')
            if price:
                if isinstance(price, (int, float)):
                    print(f"Price:       ${price:,.2f}")
                else:
                    print(f"Price:       {price}")
            else:
                print(f"Price:       See source for pricing")
            
            if prop.get('auction_date'):
                print(f"Auction Date: {prop.get('auction_date')}")
            
            print(f"Source:      {prop.get('source', 'N/A')}")
            if prop.get('url'):
                print(f"Link:        {prop.get('url')}")
    
    def save_results(self, filename: str = "foreclosure_auctions.json"):
        """Save to JSON."""
        output = {
            'search_date': datetime.now().isoformat(),
            'total_properties': len(self.properties),
            'properties': self.properties
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVED] Results saved to: {filename}")
    
    def __del__(self):
        """Cleanup."""
        if self.driver:
            self.driver.quit()


def main():
    """Main function."""
    scraper = AdvancedForeclosureScraper()
    
    counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
    properties = scraper.get_all_foreclosures(counties)
    
    scraper.display_results(limit=100)
    scraper.save_results()
    
    print("\n" + "="*80)
    print("[COMPLETE]")
    print("="*80)


if __name__ == "__main__":
    main()

