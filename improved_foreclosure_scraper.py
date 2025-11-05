"""
Improved Foreclosure Scraper - Combines all sources for best results
Uses better sources when available, falls back to others
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
from typing import Dict, List, Optional

class ImprovedForeclosureScraper:
    """Improved scraper combining all available sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.properties = []
    
    def get_all_sources_combined(self, counties: List[str] = None) -> List[Dict]:
        """Get data from all sources, prioritizing better ones."""
        if counties is None:
            counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
        
        print("="*80)
        print("IMPROVED FORECLOSURE SCRAPER - ALL SOURCES")
        print("="*80)
        print("Priority Order:")
        print("  1. Government sources (Fannie Mae, Freddie Mac, HUD)")
        print("  2. Official court records (Circuit Clerk)")
        print("  3. Sheriff offices")
        print("  4. Structured platforms (Auction.com)")
        print("  5. General platforms (Redfin, Zillow)")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        all_properties = []
        
        # Try better sources first
        print("\n[PRIORITY 1] Government-Sponsored Sources...")
        try:
            from better_data_sources_scraper import BetterDataSourcesScraper
            better_scraper = BetterDataSourcesScraper()
            gov_props = better_scraper.get_all_better_sources(counties)
            all_properties.extend(gov_props)
            print(f"  Found {len(gov_props)} from government sources")
        except:
            print("  [SKIP] Better sources scraper not available")
        
        # Try current sources as fallback
        print("\n[PRIORITY 2] General Platforms (Fallback)...")
        try:
            from real_data_scraper import RealDataScraper
            fallback_scraper = RealDataScraper()
            fallback_props = fallback_scraper.get_all_real_data()
            all_properties.extend(fallback_props)
            print(f"  Found {len(fallback_props)} from general platforms")
        except:
            print("  [SKIP] Fallback scraper not available")
        
        # Remove duplicates
        seen = set()
        unique = []
        for prop in all_properties:
            addr_key = prop.get('address', '').lower().strip()
            if addr_key and addr_key not in seen:
                seen.add(addr_key)
                unique.append(prop)
        
        # Sort by source quality then price
        quality_order = {
            'official_court_records': 1,
            'official_federal': 2,
            'official_government_sponsored': 3,
            'structured_auction_platform': 4,
            'structured_platform': 5
        }
        
        unique.sort(key=lambda x: (
            quality_order.get(x.get('quality', ''), 99),
            x.get('opening_bid') or float('inf')
        ))
        
        self.properties = unique
        return unique
    
    def display_results(self, limit: int = 100):
        """Display results."""
        if not self.properties:
            print("\n[WARNING] No properties found")
            print("\n[RECOMMENDATION] Visit these sources directly:")
            print("  Better Sources:")
            print("    • Fannie Mae: https://www.homenext.com")
            print("    • Freddie Mac: https://www.homesteps.com")
            print("    • HUD: https://www.hudhomestore.com")
            print("    • Auction.com: https://www.auction.com")
            print("  Current Sources:")
            print("    • Redfin: https://www.redfin.com/county/733/IL/DuPage-County/foreclosures")
            print("    • Zillow: https://www.zillow.com/dupage-county-il/foreclosures/")
            return
        
        print("\n" + "="*80)
        print("FORECLOSURE AUCTIONS - ALL SOURCES COMBINED")
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
            
            print(f"Source:      {prop.get('source', 'N/A')}")
            if prop.get('quality'):
                print(f"Quality:     {prop.get('quality')}")
            
            if prop.get('url'):
                print(f"Link:        {prop.get('url')}")
    
    def save_results(self, filename: str = "improved_foreclosure_data.json"):
        """Save to JSON."""
        output = {
            'search_date': datetime.now().isoformat(),
            'total_properties': len(self.properties),
            'properties': self.properties,
            'data_sources': 'Combined: Government sources + General platforms',
            'recommendation': 'Visit better sources directly for most reliable data'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVED] Results saved to: {filename}")


def main():
    """Main function."""
    scraper = ImprovedForeclosureScraper()
    properties = scraper.get_all_sources_combined(['DuPage', 'Cook', 'Lake'])
    scraper.display_results(limit=100)
    scraper.save_results()
    
    print("\n" + "="*80)
    print("[COMPLETE]")
    print("="*80)
    print("\nFor BEST quality data, visit:")
    print("  • Fannie Mae: https://www.homenext.com")
    print("  • Freddie Mac: https://www.homesteps.com")
    print("  • HUD: https://www.hudhomestore.com")
    print("  • County Circuit Clerks (official court records)")
    print("="*80)


if __name__ == "__main__":
    main()

