"""
Foreclosure Auction Finder - Free Public Data Sources
Fetches real foreclosure auction listings from multiple free public sources.
Shows properties sorted by lowest prices.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re
from datetime import datetime, timedelta
import time
from urllib.parse import urljoin, quote


class ForeclosureAuctionFinder:
    """Finds foreclosure auctions from free public sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.properties = []
        
    def find_all_foreclosures(self, counties: List[str] = None) -> List[Dict]:
        """
        Find all foreclosure auctions from free public sources.
        
        Args:
            counties: List of counties to search (e.g., ['DuPage', 'Cook', 'Lake'])
            
        Returns:
            List of foreclosure properties with prices
        """
        if counties is None:
            counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
        
        print("="*80)
        print("FORECLOSURE AUCTION FINDER - FREE PUBLIC DATA SOURCES")
        print("="*80)
        print(f"\nSearching for foreclosure auctions in: {', '.join(counties)}")
        print(f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Search all free sources
        print("🔍 Searching ILFLS (Illinois Foreclosure Listing Service)...")
        self._search_ilfls(counties)
        
        print("\n🔍 Searching HUD.gov foreclosure listings...")
        self._search_hud_foreclosures()
        
        print("\n🔍 Searching County Sheriff websites...")
        self._search_county_sheriff_sites(counties)
        
        print("\n🔍 Searching public auction platforms...")
        self._search_public_auction_sites()
        
        # Sort by price (lowest first)
        self.properties.sort(key=lambda x: self._extract_price(x.get('opening_bid', 0) or x.get('estimated_value', 0) or float('inf')))
        
        print(f"\n✅ Found {len(self.properties)} foreclosure auction properties")
        
        return self.properties
    
    def _search_ilfls(self, counties: List[str]):
        """Search ILFLS.com free daily auction lists."""
        try:
            for county in counties:
                county_lower = county.lower()
                url = f"https://ilfls.com/free-daily-auction-lists/{county_lower}"
                
                print(f"  Checking ILFLS for {county} County...")
                
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try to find property listings in the page
                        # ILFLS typically shows properties in tables or divs
                        tables = soup.find_all('table')
                        property_divs = soup.find_all(['div', 'tr'], class_=re.compile(r'property|listing|foreclosure|auction', re.I))
                        
                        # Look for common patterns
                        text_content = soup.get_text()
                        
                        # Extract addresses and case numbers
                        addresses = re.findall(r'\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Blvd|Ln|Ct|Way|Pkwy|Pl|Cir)[\s\w,]*', text_content)
                        case_numbers = re.findall(r'Case\s+[Nn]o[.:]?\s*(\d{2}[A-Z]{2}\d+)', text_content)
                        
                        # If we find structured data, parse it
                        if tables:
                            for table in tables:
                                rows = table.find_all('tr')
                                for row in rows[1:]:  # Skip header
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 3:
                                        prop = self._parse_ilfls_row(cells, county)
                                        if prop:
                                            self.properties.append(prop)
                        
                        # If we can't parse structured data, at least note that data exists
                        if addresses or case_numbers:
                            print(f"    Found {len(addresses)} addresses, {len(case_numbers)} case numbers")
                            # Create entries from addresses found
                            for i, addr in enumerate(addresses[:20]):  # Limit to first 20
                                prop = {
                                    'source': 'ILFLS',
                                    'county': county,
                                    'address': addr.strip(),
                                    'url': url,
                                    'case_number': case_numbers[i] if i < len(case_numbers) else None,
                                    'auction_date': None,
                                    'opening_bid': None,
                                    'estimated_value': None,
                                    'scraped_at': datetime.now().isoformat()
                                }
                                self.properties.append(prop)
                        
                except requests.exceptions.RequestException as e:
                    print(f"    Error accessing {url}: {e}")
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"  Error searching ILFLS: {e}")
    
    def _parse_ilfls_row(self, cells, county: str) -> Optional[Dict]:
        """Parse a table row from ILFLS."""
        try:
            text = ' '.join([cell.get_text(strip=True) for cell in cells])
            
            # Extract address
            address_match = re.search(r'(\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Blvd|Ln|Ct|Way|Pkwy|Pl|Cir)[\s\w,]+)', text)
            address = address_match.group(1) if address_match else None
            
            # Extract case number
            case_match = re.search(r'(\d{2}[A-Z]{2}\d+)', text)
            case_number = case_match.group(1) if case_match else None
            
            # Extract prices
            price_match = re.search(r'\$([\d,]+)', text)
            price = self._parse_price(price_match.group(1)) if price_match else None
            
            # Extract date
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
            auction_date = date_match.group(1) if date_match else None
            
            if address:
                return {
                    'source': 'ILFLS',
                    'county': county,
                    'address': address,
                    'case_number': case_number,
                    'auction_date': auction_date,
                    'opening_bid': price,
                    'estimated_value': price,
                    'scraped_at': datetime.now().isoformat()
                }
        except Exception as e:
            pass
        return None
    
    def _search_hud_foreclosures(self):
        """Search HUD.gov foreclosure listings."""
        try:
            # HUD Home Store - free foreclosure listings
            hud_urls = [
                "https://www.hudhomestore.com/Home/Index.aspx",
                "https://www.hudhomestore.com/Listing/PropertySearchResult.aspx"
            ]
            
            # Try to get HUD listings
            # Note: HUD website may require form submission
            search_url = "https://www.hudhomestore.com/Home/PropertySearch"
            
            print("  Checking HUD Home Store...")
            
            # Get the search page first
            try:
                response = self.session.get("https://www.hudhomestore.com", timeout=15)
                if response.status_code == 200:
                    # HUD listings typically require state/county selection
                    # For Illinois properties
                    print("    HUD Home Store accessible - properties may require state/county selection")
                    print("    Visit: https://www.hudhomestore.com to search for Illinois properties")
            except Exception as e:
                print(f"    Error accessing HUD: {e}")
                
        except Exception as e:
            print(f"  Error searching HUD: {e}")
    
    def _search_county_sheriff_sites(self, counties: List[str]):
        """Search county sheriff websites for foreclosure sales."""
        county_urls = {
            'Cook': 'https://www.cookcountysheriff.org/foreclosure-sales/',
            'DuPage': 'https://www.dupagecounty.gov/sheriff/',
            'Lake': 'https://www.lakecountyil.gov/departments/sheriff',
            'Will': 'https://www.willcosheriff.org/',
            'Kane': 'https://www.kanecountyil.gov/sheriff'
        }
        
        for county in counties:
            if county in county_urls:
                print(f"  Checking {county} County Sheriff website...")
                try:
                    url = county_urls[county]
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text()
                        
                        # Look for foreclosure sale information
                        if any(keyword in text.lower() for keyword in ['foreclosure', 'sale', 'auction']):
                            # Extract addresses and dates
                            addresses = re.findall(r'\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Blvd|Ln|Ct|Way|Pkwy|Pl|Cir)[\s\w,]*', text)
                            
                            if addresses:
                                print(f"    Found {len(addresses)} potential properties")
                                
                except Exception as e:
                    print(f"    Error accessing {county} Sheriff site: {e}")
                
                time.sleep(1)
    
    def _search_public_auction_sites(self):
        """Search other free public auction sites."""
        sites = [
            {
                'name': 'ForeclosureListingsUSA',
                'url': 'https://www.foreclosurelistingsusa.com',
                'note': 'Free nationwide listings'
            },
            {
                'name': 'HousingAuctions.net',
                'url': 'https://housingauctions.net',
                'note': 'Free public auction links'
            }
        ]
        
        for site in sites:
            print(f"  Checking {site['name']}...")
            try:
                response = self.session.get(site['url'], timeout=15)
                if response.status_code == 200:
                    print(f"    {site['name']} accessible - {site['note']}")
                    print(f"    Visit: {site['url']} for listings")
            except Exception as e:
                print(f"    Error accessing {site['name']}: {e}")
    
    def _extract_price(self, price) -> float:
        """Extract numeric price value."""
        if price is None:
            return float('inf')
        if isinstance(price, (int, float)):
            return float(price)
        if isinstance(price, str):
            # Remove $ and commas
            cleaned = re.sub(r'[^\d.]', '', str(price))
            try:
                return float(cleaned)
            except:
                return float('inf')
        return float('inf')
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float."""
        try:
            cleaned = re.sub(r'[^\d.]', '', str(price_str))
            return float(cleaned)
        except:
            return None
    
    def display_results(self, limit: int = 50):
        """Display results sorted by price."""
        print("\n" + "="*80)
        print("FORECLOSURE AUCTION RESULTS - SORTED BY LOWEST PRICE")
        print("="*80)
        
        if not self.properties:
            print("\n⚠️  No properties found in free public sources.")
            print("\n💡 Try these direct sources:")
            print("   1. ILFLS: https://ilfls.com/free-daily-auction-lists/dupage")
            print("   2. HUD Home Store: https://www.hudhomestore.com")
            print("   3. County Sheriff Offices (contact directly)")
            return
        
        displayed = 0
        for i, prop in enumerate(self.properties[:limit], 1):
            if displayed >= limit:
                break
            
            print(f"\n{'='*80}")
            print(f"PROPERTY #{i}")
            print(f"{'='*80}")
            print(f"📍 Address: {prop.get('address', 'N/A')}")
            print(f"🏛️  County: {prop.get('county', 'N/A')}")
            print(f"📋 Case Number: {prop.get('case_number', 'N/A')}")
            
            price = prop.get('opening_bid') or prop.get('estimated_value')
            if price:
                print(f"💰 Opening Bid/Est. Value: ${price:,.2f}" if isinstance(price, (int, float)) else f"💰 Opening Bid/Est. Value: {price}")
            else:
                print(f"💰 Opening Bid/Est. Value: Contact source for pricing")
            
            if prop.get('auction_date'):
                print(f"📅 Auction Date: {prop.get('auction_date')}")
            
            print(f"🔗 Source: {prop.get('source', 'N/A')}")
            if prop.get('url'):
                print(f"🌐 URL: {prop.get('url')}")
            
            displayed += 1
        
        print(f"\n{'='*80}")
        print(f"Showing {displayed} of {len(self.properties)} properties")
        print(f"{'='*80}")
    
    def save_results(self, filename: str = "foreclosure_auctions.json"):
        """Save results to JSON file."""
        output = {
            'search_date': datetime.now().isoformat(),
            'total_properties': len(self.properties),
            'properties': self.properties
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")


def main():
    """Main function."""
    finder = ForeclosureAuctionFinder()
    
    # Search for foreclosures in Illinois counties
    counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
    properties = finder.find_all_foreclosures(counties)
    
    # Display results
    finder.display_results(limit=50)
    
    # Save to file
    finder.save_results()
    
    print("\n" + "="*80)
    print("📝 IMPORTANT NOTES:")
    print("="*80)
    print("• All data is from FREE public sources")
    print("• Prices shown are opening bids or estimated values")
    print("• Always verify information with official sources before bidding")
    print("• Contact county sheriff offices for most current listings")
    print("• ILFLS: https://ilfls.com/free-daily-auction-lists/")
    print("="*80)


if __name__ == "__main__":
    main()

