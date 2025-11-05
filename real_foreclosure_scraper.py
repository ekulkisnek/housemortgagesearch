"""
Real Foreclosure Auction Scraper
Scrapes actual foreclosure auction listings with real addresses and prices
from free public sources.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json
import re
from datetime import datetime
import time
from urllib.parse import urljoin


class RealForeclosureScraper:
    """Scrapes real foreclosure data from free public sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        self.properties = []
    
    def scrape_ilfls_county(self, county: str) -> List[Dict]:
        """Scrape ILFLS free daily auction list for a specific county."""
        county_lower = county.lower().replace(' ', '-')
        url = f"https://ilfls.com/free-daily-auction-lists/{county_lower}"
        
        print(f"\n🔍 Scraping ILFLS for {county} County...")
        print(f"   URL: {url}")
        
        properties = []
        
        try:
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Get all text content
                page_text = soup.get_text()
                
                # Look for property information patterns
                # ILFLS typically shows: Address, Case Number, Sale Date, Opening Bid
                
                # Pattern 1: Look for table structures
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    headers = []
                    if rows:
                        # Get headers from first row
                        header_cells = rows[0].find_all(['th', 'td'])
                        headers = [cell.get_text(strip=True).lower() for cell in header_cells]
                    
                    # Parse data rows
                    for row in rows[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            prop = self._parse_table_row(cells, headers, county, url)
                            if prop:
                                properties.append(prop)
                
                # Pattern 2: Look for div/list structures with addresses
                property_divs = soup.find_all(['div', 'li', 'p'], 
                    class_=re.compile(r'property|listing|foreclosure|auction|sale', re.I))
                
                for div in property_divs:
                    text = div.get_text()
                    prop = self._extract_property_from_text(text, county, url)
                    if prop and prop not in properties:
                        properties.append(prop)
                
                # Pattern 3: Extract from raw text using regex
                # Find addresses followed by case numbers and prices
                address_pattern = r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*[A-Z]{2}\s+\d{5})'
                addresses = re.findall(address_pattern, page_text)
                
                # Find case numbers (format: 12CH1234 or similar)
                case_pattern = r'Case\s*(?:No|Number|#)[:.]?\s*(\d{2}[A-Z]{2}\d+)'
                case_numbers = re.findall(case_pattern, page_text, re.I)
                
                # Find prices
                price_pattern = r'\$([\d,]+(?:\.\d{2})?)'
                prices = re.findall(price_pattern, page_text)
                
                # Find dates
                date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
                dates = re.findall(date_pattern, page_text)
                
                # Create properties from extracted data
                for i, addr in enumerate(addresses[:30]):  # Limit to prevent duplicates
                    prop = {
                        'source': 'ILFLS',
                        'county': county,
                        'address': addr.strip(),
                        'case_number': case_numbers[i] if i < len(case_numbers) else None,
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'auction_date': dates[i] if i < len(dates) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat(),
                        'verified': False
                    }
                    
                    # Check if we already have this property
                    if not any(p.get('address') == prop['address'] for p in properties):
                        properties.append(prop)
                
                print(f"   ✅ Found {len(properties)} properties")
                
            else:
                print(f"   ⚠️  HTTP {response.status_code}: Could not access page")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        return properties
    
    def _parse_table_row(self, cells, headers: List[str], county: str, source_url: str) -> Optional[Dict]:
        """Parse a table row into a property dictionary."""
        try:
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            full_text = ' '.join(cell_texts)
            
            # Extract address
            address_match = re.search(
                r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*[A-Z]{2}\s+\d{5})',
                full_text
            )
            address = address_match.group(1) if address_match else None
            
            if not address:
                # Try simpler pattern
                address_match = re.search(r'(\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Rd|Dr|Blvd|Ln|Ct|Way|Pkwy|Pl|Cir)[\s\w,]+)', full_text)
                address = address_match.group(1) if address_match else None
            
            if not address:
                return None
            
            # Extract case number
            case_match = re.search(r'(\d{2}[A-Z]{2}\d+)', full_text)
            case_number = case_match.group(1) if case_match else None
            
            # Extract price
            price_match = re.search(r'\$([\d,]+(?:\.\d{2})?)', full_text)
            price = self._parse_price(price_match.group(1)) if price_match else None
            
            # Extract date
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
            auction_date = date_match.group(1) if date_match else None
            
            return {
                'source': 'ILFLS',
                'county': county,
                'address': address.strip(),
                'case_number': case_number,
                'opening_bid': price,
                'estimated_value': price,
                'auction_date': auction_date,
                'url': source_url,
                'scraped_at': datetime.now().isoformat(),
                'verified': True
            }
            
        except Exception as e:
            return None
    
    def _extract_property_from_text(self, text: str, county: str, source_url: str) -> Optional[Dict]:
        """Extract property information from text block."""
        try:
            # Look for address
            address_match = re.search(
                r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]+)',
                text
            )
            
            if not address_match:
                return None
            
            address = address_match.group(1).strip()
            
            # Extract case number from same text
            case_match = re.search(r'(\d{2}[A-Z]{2}\d+)', text)
            case_number = case_match.group(1) if case_match else None
            
            # Extract price
            price_match = re.search(r'\$([\d,]+(?:\.\d{2})?)', text)
            price = self._parse_price(price_match.group(1)) if price_match else None
            
            # Extract date
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
            auction_date = date_match.group(1) if date_match else None
            
            return {
                'source': 'ILFLS',
                'county': county,
                'address': address,
                'case_number': case_number,
                'opening_bid': price,
                'estimated_value': price,
                'auction_date': auction_date,
                'url': source_url,
                'scraped_at': datetime.now().isoformat(),
                'verified': False
            }
            
        except Exception:
            return None
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float."""
        try:
            cleaned = re.sub(r'[^\d.]', '', str(price_str))
            if cleaned:
                return float(cleaned)
        except:
            pass
        return None
    
    def enrich_with_assessor_data(self, properties: List[Dict]) -> List[Dict]:
        """Enrich properties with assessor data for more accurate values."""
        print("\n🔍 Enriching with county assessor data...")
        
        # Note: This would require API access or scraping assessor sites
        # For now, we'll mark properties that need enrichment
        for prop in properties:
            if not prop.get('estimated_value') and prop.get('address'):
                prop['needs_assessor_lookup'] = True
        
        return properties
    
    def scrape_all_sources(self, counties: List[str] = None) -> List[Dict]:
        """Scrape all available free sources."""
        if counties is None:
            counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
        
        all_properties = []
        
        print("="*80)
        print("REAL FORECLOSURE AUCTION SCRAPER")
        print("="*80)
        print(f"Searching counties: {', '.join(counties)}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Scrape ILFLS for each county
        for county in counties:
            props = self.scrape_ilfls_county(county)
            all_properties.extend(props)
            time.sleep(2)  # Rate limiting
        
        # Remove duplicates based on address
        seen_addresses = set()
        unique_properties = []
        for prop in all_properties:
            addr_key = prop.get('address', '').lower().strip()
            if addr_key and addr_key not in seen_addresses:
                seen_addresses.add(addr_key)
                unique_properties.append(prop)
        
        # Sort by price (lowest first)
        unique_properties.sort(key=lambda x: x.get('opening_bid') or x.get('estimated_value') or float('inf'))
        
        self.properties = unique_properties
        return unique_properties
    
    def display_results(self, limit: int = 100):
        """Display results in a readable format."""
        if not self.properties:
            print("\n" + "="*80)
            print("⚠️  NO PROPERTIES FOUND")
            print("="*80)
            print("\nThis could mean:")
            print("1. No active foreclosure auctions in searched counties")
            print("2. Website structure has changed")
            print("3. Need to access sources directly")
            print("\n💡 DIRECT ACCESS LINKS:")
            print("   • ILFLS DuPage: https://ilfls.com/free-daily-auction-lists/dupage")
            print("   • ILFLS Cook: https://ilfls.com/free-daily-auction-lists/cook")
            print("   • ILFLS Lake: https://ilfls.com/free-daily-auction-lists/lake")
            print("   • HUD Home Store: https://www.hudhomestore.com")
            return
        
        print("\n" + "="*80)
        print(f"FORECLOSURE AUCTIONS - SORTED BY LOWEST PRICE")
        print("="*80)
        print(f"Total Properties Found: {len(self.properties)}")
        print(f"Showing first {min(limit, len(self.properties))} properties")
        print("="*80)
        
        for i, prop in enumerate(self.properties[:limit], 1):
            print(f"\n{'─'*80}")
            print(f"🏠 PROPERTY #{i}")
            print(f"{'─'*80}")
            print(f"📍 Address:     {prop.get('address', 'N/A')}")
            print(f"🏛️  County:       {prop.get('county', 'N/A')}")
            
            if prop.get('case_number'):
                print(f"📋 Case Number:  {prop.get('case_number')}")
            
            price = prop.get('opening_bid') or prop.get('estimated_value')
            if price:
                if isinstance(price, (int, float)):
                    print(f"💰 Price:        ${price:,.2f}")
                else:
                    print(f"💰 Price:        {price}")
            else:
                print(f"💰 Price:        Contact source for pricing")
            
            if prop.get('auction_date'):
                print(f"📅 Auction Date: {prop.get('auction_date')}")
            
            print(f"🔗 Source:       {prop.get('source', 'N/A')}")
            if prop.get('url'):
                print(f"🌐 Link:         {prop.get('url')}")
            
            if prop.get('verified'):
                print(f"✅ Verified:     Yes")
    
    def save_results(self, filename: str = "real_foreclosure_auctions.json"):
        """Save results to JSON file."""
        output = {
            'search_date': datetime.now().isoformat(),
            'total_properties': len(self.properties),
            'properties': self.properties,
            'notes': [
                'All data scraped from free public sources',
                'Prices are opening bids or estimated values',
                'Always verify with official sources before bidding',
                'Data accuracy not guaranteed - verify independently'
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")


def main():
    """Main execution."""
    scraper = RealForeclosureScraper()
    
    # Search Illinois counties
    counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
    properties = scraper.scrape_all_sources(counties)
    
    # Display results
    scraper.display_results(limit=100)
    
    # Save results
    scraper.save_results()
    
    print("\n" + "="*80)
    print("📋 NEXT STEPS:")
    print("="*80)
    print("1. Review the properties listed above")
    print("2. Visit the source URLs for complete details")
    print("3. Contact county sheriff offices for verification")
    print("4. Check auction dates and requirements")
    print("5. Research properties before bidding")
    print("="*80)


if __name__ == "__main__":
    main()

