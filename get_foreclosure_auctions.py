"""
Get Foreclosure Auctions - Main Script
Fetches real foreclosure auction listings from free public sources.
Shows properties sorted by lowest prices.
"""

import sys
import json
from datetime import datetime

# Check for required modules
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("="*80)
    print("MISSING DEPENDENCIES")
    print("="*80)
    print("\nPlease install required packages:")
    print("  pip install requests beautifulsoup4 lxml")
    print("\nOr run:")
    print("  pip install -r requirements.txt")
    print("="*80)
    sys.exit(1)

import re
import time
from typing import Dict, List, Optional


class ForeclosureAuctionGetter:
    """Gets foreclosure auctions from free public sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        self.properties = []
    
    def get_ilfls_listings(self, county: str) -> List[Dict]:
        """Get ILFLS free daily auction listings for a county."""
        county_lower = county.lower().replace(' ', '-')
        url = f"https://ilfls.com/free-daily-auction-lists/{county_lower}"
        
        print(f"\n[SEARCHING] Fetching ILFLS listings for {county} County...")
        print(f"   URL: {url}")
        
        properties = []
        
        try:
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                page_text = soup.get_text()
                
                # Extract properties using multiple methods
                # Method 1: Table parsing
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:
                        headers = [cell.get_text(strip=True).lower() for cell in rows[0].find_all(['th', 'td'])]
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 2:
                                prop = self._parse_row(cells, headers, county, url)
                                if prop and prop not in properties:
                                    properties.append(prop)
                
                # Method 2: Text extraction
                # Find addresses
                address_patterns = [
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*[A-Z]{2}\s+\d{5})',
                    r'(\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Blvd|Ln|Ct|Way|Pkwy|Pl|Cir)[\s\w,]+)'
                ]
                
                addresses = []
                for pattern in address_patterns:
                    matches = re.findall(pattern, page_text)
                    addresses.extend(matches)
                
                # Find case numbers
                case_numbers = re.findall(r'(\d{2}[A-Z]{2}\d+)', page_text)
                
                # Find prices
                prices = re.findall(r'\$([\d,]+(?:\.\d{2})?)', page_text)
                
                # Find dates
                dates = re.findall(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', page_text)
                
                # Create property entries
                for i, addr in enumerate(addresses[:50]):  # Limit to prevent too many
                    addr_clean = addr.strip()
                    if addr_clean and not any(p.get('address') == addr_clean for p in properties):
                        prop = {
                            'source': 'ILFLS',
                            'county': county,
                            'address': addr_clean,
                            'case_number': case_numbers[i] if i < len(case_numbers) else None,
                            'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                            'estimated_value': self._parse_price(prices[i]) if i < len(prices) else None,
                            'auction_date': dates[i] if i < len(dates) else None,
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
    
    def _parse_row(self, cells, headers: List[str], county: str, url: str) -> Optional[Dict]:
        """Parse a table row."""
        try:
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            full_text = ' '.join(cell_texts)
            
            # Find address
            address_match = re.search(
                r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]+)',
                full_text
            )
            
            if not address_match:
                address_match = re.search(r'(\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Blvd|Ln|Ct|Way|Pkwy|Pl|Cir)[\s\w,]+)', full_text)
            
            if not address_match:
                return None
            
            address = address_match.group(1).strip()
            
            # Extract other info
            case_match = re.search(r'(\d{2}[A-Z]{2}\d+)', full_text)
            price_match = re.search(r'\$([\d,]+(?:\.\d{2})?)', full_text)
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
            
            return {
                'source': 'ILFLS',
                'county': county,
                'address': address,
                'case_number': case_match.group(1) if case_match else None,
                'opening_bid': self._parse_price(price_match.group(1)) if price_match else None,
                'estimated_value': self._parse_price(price_match.group(1)) if price_match else None,
                'auction_date': date_match.group(1) if date_match else None,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
        except:
            return None
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price to float."""
        try:
            cleaned = re.sub(r'[^\d.]', '', str(price_str))
            return float(cleaned) if cleaned else None
        except:
            return None
    
    def get_all_foreclosures(self, counties: List[str] = None) -> List[Dict]:
        """Get all foreclosure listings."""
        if counties is None:
            counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
        
        print("="*80)
        print("FORECLOSURE AUCTION FINDER - FREE PUBLIC DATA")
        print("="*80)
        print(f"Searching counties: {', '.join(counties)}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        all_properties = []
        
        # Get ILFLS listings for each county
        for county in counties:
            props = self.get_ilfls_listings(county)
            all_properties.extend(props)
            time.sleep(2)  # Rate limiting
        
        # Remove duplicates
        seen = set()
        unique = []
        for prop in all_properties:
            addr_key = prop.get('address', '').lower().strip()
            if addr_key and addr_key not in seen:
                seen.add(addr_key)
                unique.append(prop)
        
        # Sort by price (lowest first)
        unique.sort(key=lambda x: x.get('opening_bid') or x.get('estimated_value') or float('inf'))
        
        self.properties = unique
        return unique
    
    def display_results(self, limit: int = 100):
        """Display results."""
        if not self.properties:
            print("\n" + "="*80)
            print("[WARNING] NO PROPERTIES FOUND IN SCRAPED DATA")
            print("="*80)
            print("\nDIRECT ACCESS TO FREE SOURCES:")
            print("\n1. ILFLS (Illinois Foreclosure Listing Service):")
            print("   • DuPage: https://ilfls.com/free-daily-auction-lists/dupage")
            print("   • Cook:   https://ilfls.com/free-daily-auction-lists/cook")
            print("   • Lake:   https://ilfls.com/free-daily-auction-lists/lake")
            print("   • Will:   https://ilfls.com/free-daily-auction-lists/will")
            print("   • Kane:   https://ilfls.com/free-daily-auction-lists/kane")
            print("\n2. HUD Home Store (Federal foreclosures):")
            print("   • https://www.hudhomestore.com")
            print("\n3. County Sheriff Offices:")
            print("   • DuPage: (630) 682-7256")
            print("   • Cook:   (312) 603-5113")
            print("\n4. Other Free Sources:")
            print("   • https://www.foreclosurelistingsusa.com")
            print("   • https://housingauctions.net")
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
            print(f"County:       {prop.get('county', 'N/A')}")
            
            if prop.get('case_number'):
                print(f"Case Number:  {prop.get('case_number')}")
            
            price = prop.get('opening_bid') or prop.get('estimated_value')
            if price:
                if isinstance(price, (int, float)):
                    print(f"Price:        ${price:,.2f}")
                else:
                    print(f"Price:        {price}")
            else:
                print(f"Price:        See source for pricing")
            
            if prop.get('auction_date'):
                print(f"Auction Date: {prop.get('auction_date')}")
            
            print(f"Source:       {prop.get('source', 'N/A')}")
            if prop.get('url'):
                print(f"Link:         {prop.get('url')}")
    
    def save_results(self, filename: str = "foreclosure_auctions.json"):
        """Save to JSON."""
        output = {
            'search_date': datetime.now().isoformat(),
            'total_properties': len(self.properties),
            'properties': self.properties,
            'notes': [
                'Data from free public sources',
                'Verify all information with official sources',
                'Prices are opening bids or estimates',
                'Always research properties before bidding'
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVED] Results saved to: {filename}")


def main():
    """Main function."""
    getter = ForeclosureAuctionGetter()
    
    # Search Illinois counties
    counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
    properties = getter.get_all_foreclosures(counties)
    
    # Display
    getter.display_results(limit=100)
    
    # Save
    getter.save_results()
    
    print("\n" + "="*80)
    print("[COMPLETE]")
    print("="*80)
    print("\nNext Steps:")
    print("1. Review properties above")
    print("2. Visit source URLs for complete details")
    print("3. Contact county offices to verify")
    print("4. Research properties thoroughly")
    print("5. Check auction requirements before bidding")
    print("="*80)


if __name__ == "__main__":
    main()

