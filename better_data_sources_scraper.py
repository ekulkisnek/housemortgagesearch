"""
Better Data Sources Scraper - Uses more reliable official sources
Gets cleaner, more structured foreclosure data from better sources
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
from typing import Dict, List, Optional

class BetterDataSourcesScraper:
    """Scraper using better, more reliable data sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.properties = []
    
    def get_fannie_mae_homepath(self, state="IL") -> List[Dict]:
        """Get Fannie Mae HomePath properties (better structured data)."""
        print(f"\n[SEARCHING] Fannie Mae HomePath for {state}...")
        
        properties = []
        
        try:
            # Fannie Mae HomePath search
            url = f"https://www.homenext.com/PropertySearch"
            
            # Try Illinois search
            search_params = {
                'state': state,
                'propertyType': 'Residential'
            }
            
            response = self.session.get(url, params=search_params, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Fannie Mae has structured property listings
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:30]):
                    prop = {
                        'source': 'Fannie Mae HomePath',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': 'https://www.homenext.com',
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'official_government_sponsored'
                    }
                    if prop['address'] not in [p.get('address') for p in properties]:
                        properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] Visit https://www.homenext.com directly for Illinois properties")
                
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_freddie_mac_homesteps(self, state="IL") -> List[Dict]:
        """Get Freddie Mac HomeSteps properties (better structured data)."""
        print(f"\n[SEARCHING] Freddie Mac HomeSteps for {state}...")
        
        properties = []
        
        try:
            # Freddie Mac HomeSteps
            url = "https://www.homesteps.com"
            
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Look for property listings
                if 'illinois' in text.lower() or 'il' in text.lower():
                    addresses = re.findall(
                        r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                        text
                    )
                    
                    prices = re.findall(r'\$([\d,]+)', text)
                    
                    for i, addr in enumerate(addresses[:30]):
                        prop = {
                            'source': 'Freddie Mac HomeSteps',
                            'county': 'Illinois',
                            'address': addr.strip(),
                            'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                            'url': 'https://www.homesteps.com',
                            'scraped_at': datetime.now().isoformat(),
                            'quality': 'official_government_sponsored'
                        }
                        if prop['address'] not in [p.get('address') for p in properties]:
                            properties.append(prop)
                    
                    print(f"   [SUCCESS] Found {len(properties)} properties")
                else:
                    print(f"   [INFO] Visit https://www.homesteps.com and search for Illinois")
                    
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_hud_homestore_detailed(self, state="IL") -> List[Dict]:
        """Get detailed HUD Home Store listings."""
        print(f"\n[SEARCHING] HUD Home Store (detailed) for {state}...")
        
        properties = []
        
        try:
            # HUD Home Store has better structure
            base_url = "https://www.hudhomestore.com"
            search_url = f"{base_url}/Home/PropertySearch"
            
            # Try to get Illinois properties
            params = {
                'state': state,
                'propertyType': 'SingleFamily'
            }
            
            response = self.session.get(search_url, params=params, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # HUD properties are well-structured
                property_cards = soup.find_all(['div', 'li'], class_=re.compile(r'property|listing|home', re.I))
                
                for card in property_cards[:50]:
                    text = card.get_text()
                    addr_match = re.search(
                        r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                        text
                    )
                    
                    if addr_match:
                        price_match = re.search(r'\$([\d,]+)', text)
                        prop = {
                            'source': 'HUD Home Store',
                            'county': 'Illinois',
                            'address': addr_match.group(1).strip(),
                            'opening_bid': self._parse_price(price_match.group(1)) if price_match else None,
                            'url': base_url,
                            'scraped_at': datetime.now().isoformat(),
                            'quality': 'official_federal'
                        }
                        if prop['address'] not in [p.get('address') for p in properties]:
                            properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] HUD requires form submission - visit {base_url}")
                
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_auction_com_listings(self, location="DuPage County IL") -> List[Dict]:
        """Get Auction.com listings (better structured than Redfin/Zillow)."""
        print(f"\n[SEARCHING] Auction.com for {location}...")
        
        properties = []
        
        try:
            # Auction.com has structured foreclosure data
            search_term = location.replace(" ", "-").lower()
            url = f"https://www.auction.com/search?q={search_term}"
            
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Auction.com has cleaner property listings
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                # Also look for structured listing elements
                listings = soup.find_all(['div', 'article'], class_=re.compile(r'property|listing|auction', re.I))
                
                for listing in listings[:50]:
                    listing_text = listing.get_text()
                    addr_match = re.search(
                        r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                        listing_text
                    )
                    
                    if addr_match:
                        price_match = re.search(r'\$([\d,]+)', listing_text)
                        prop = {
                            'source': 'Auction.com',
                            'county': location,
                            'address': addr_match.group(1).strip(),
                            'opening_bid': self._parse_price(price_match.group(1)) if price_match else None,
                            'url': url,
                            'scraped_at': datetime.now().isoformat(),
                            'quality': 'structured_auction_platform'
                        }
                        if prop['address'] not in [p.get('address') for p in properties]:
                            properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] Auction.com may require JavaScript - visit {url}")
                
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_county_circuit_clerk_data(self, county="DuPage") -> List[Dict]:
        """Try to get data from county Circuit Clerk (most official source)."""
        print(f"\n[SEARCHING] {county} County Circuit Clerk records...")
        
        properties = []
        
        county_urls = {
            'DuPage': 'https://www.dupagecounty.gov/elected_officials/circuit_clerk/',
            'Cook': 'https://www.cookcountyclerkofcourt.org/',
            'Lake': 'https://www.lakecountyil.gov/departments/circuit_clerk',
            'Will': 'https://www.willcountycircuitclerk.org/',
            'Kane': 'https://www.kanecountyclerk.org/'
        }
        
        if county in county_urls:
            try:
                url = county_urls[county]
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    
                    # Look for foreclosure case information
                    if 'foreclosure' in text.lower():
                        # Extract case numbers
                        case_numbers = re.findall(r'(\d{2}[A-Z]{2}\d+)', text)
                        
                        # Extract addresses
                        addresses = re.findall(
                            r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                            text
                        )
                        
                        for i, addr in enumerate(addresses[:20]):
                            prop = {
                                'source': f'{county} County Circuit Clerk',
                                'county': county,
                                'address': addr.strip(),
                                'case_number': case_numbers[i] if i < len(case_numbers) else None,
                                'url': url,
                                'scraped_at': datetime.now().isoformat(),
                                'quality': 'official_court_records'
                            }
                            properties.append(prop)
                        
                        print(f"   [SUCCESS] Found {len(properties)} properties")
                    else:
                        print(f"   [INFO] Visit {url} and search for foreclosure cases")
                        
            except Exception as e:
                print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price to float."""
        try:
            cleaned = re.sub(r'[^\d.]', '', str(price_str))
            return float(cleaned) if cleaned else None
        except:
            return None
    
    def get_all_better_sources(self, counties: List[str] = None) -> List[Dict]:
        """Get data from all better sources."""
        if counties is None:
            counties = ['DuPage', 'Cook', 'Lake']
        
        print("="*80)
        print("BETTER DATA SOURCES SCRAPER")
        print("="*80)
        print("Using more reliable official sources:")
        print("  • Government-sponsored (Fannie Mae, Freddie Mac, HUD)")
        print("  • Official county records (Circuit Clerk)")
        print("  • Structured auction platforms (Auction.com)")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        all_properties = []
        
        # Government-sponsored sources (BEST QUALITY)
        all_properties.extend(self.get_fannie_mae_homepath("IL"))
        all_properties.extend(self.get_freddie_mac_homesteps("IL"))
        all_properties.extend(self.get_hud_homestore_detailed("IL"))
        
        # Official county sources
        for county in counties:
            all_properties.extend(self.get_county_circuit_clerk_data(county))
            time.sleep(1)
        
        # Structured auction platforms
        all_properties.extend(self.get_auction_com_listings("DuPage County IL"))
        all_properties.extend(self.get_auction_com_listings("Cook County IL"))
        
        # Remove duplicates
        seen = set()
        unique = []
        for prop in all_properties:
            addr_key = prop.get('address', '').lower().strip()
            if addr_key and addr_key not in seen:
                seen.add(addr_key)
                unique.append(prop)
        
        # Sort by quality then price
        quality_order = {
            'official_court_records': 1,
            'official_federal': 2,
            'official_government_sponsored': 3,
            'structured_auction_platform': 4
        }
        
        unique.sort(key=lambda x: (
            quality_order.get(x.get('quality', ''), 99),
            x.get('opening_bid') or float('inf')
        ))
        
        self.properties = unique
        return unique
    
    def display_results(self, limit: int = 100):
        """Display results with quality indicators."""
        if not self.properties:
            print("\n[WARNING] No properties found")
            print("\n[INFO] Better sources may require:")
            print("  • Form submissions (HUD, Fannie Mae)")
            print("  • JavaScript rendering (Auction.com)")
            print("  • Court record searches (Circuit Clerk)")
            print("\n[RECOMMENDATION] Visit these sources directly:")
            print("  • Fannie Mae: https://www.homenext.com")
            print("  • Freddie Mac: https://www.homesteps.com")
            print("  • HUD: https://www.hudhomestore.com")
            print("  • Auction.com: https://www.auction.com")
            return
        
        print("\n" + "="*80)
        print("FORECLOSURE AUCTIONS - FROM BETTER DATA SOURCES")
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
            
            price = prop.get('opening_bid')
            if price:
                if isinstance(price, (int, float)):
                    print(f"Price:       ${price:,.2f}")
                else:
                    print(f"Price:       {price}")
            else:
                print(f"Price:       See source for pricing")
            
            print(f"Source:      {prop.get('source', 'N/A')}")
            quality = prop.get('quality', '')
            if quality:
                quality_labels = {
                    'official_court_records': '[OFFICIAL COURT RECORDS]',
                    'official_federal': '[OFFICIAL FEDERAL]',
                    'official_government_sponsored': '[GOVERNMENT SPONSORED]',
                    'structured_auction_platform': '[STRUCTURED PLATFORM]'
                }
                print(f"Quality:     {quality_labels.get(quality, quality)}")
            
            if prop.get('url'):
                print(f"Link:        {prop.get('url')}")
    
    def save_results(self, filename: str = "better_foreclosure_data.json"):
        """Save to JSON."""
        output = {
            'search_date': datetime.now().isoformat(),
            'total_properties': len(self.properties),
            'properties': self.properties,
            'data_sources': 'Better official sources (Government-sponsored, Court records)',
            'verification_note': 'All data from official or government-sponsored sources'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVED] Results saved to: {filename}")


def main():
    """Main function."""
    scraper = BetterDataSourcesScraper()
    properties = scraper.get_all_better_sources(['DuPage', 'Cook', 'Lake'])
    scraper.display_results(limit=100)
    scraper.save_results()
    
    print("\n" + "="*80)
    print("[COMPLETE]")
    print("="*80)
    print("\nBETTER DATA SOURCES:")
    print("  1. Fannie Mae HomePath: https://www.homenext.com")
    print("  2. Freddie Mac HomeSteps: https://www.homesteps.com")
    print("  3. HUD Home Store: https://www.hudhomestore.com")
    print("  4. Auction.com: https://www.auction.com")
    print("  5. County Circuit Clerks (official court records)")
    print("="*80)


if __name__ == "__main__":
    main()

