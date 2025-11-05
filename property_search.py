"""
Property Mortgage and Lien Search Tool
Searches for mortgage and lien information on a property address.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import json


class PropertySearch:
    """Search for mortgage and lien information on properties."""
    
    def __init__(self):
        self.cook_county_recorder_url = "https://cookrecorder.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_property(self, address: str) -> Dict:
        """
        Search for mortgage and lien information on a property.
        
        Args:
            address: Property address (e.g., "3557 N Marshfield Ave")
            
        Returns:
            Dictionary containing property information, mortgages, and liens
        """
        print(f"Searching for property: {address}")
        
        # Normalize address
        normalized_address = self._normalize_address(address)
        
        result = {
            'address': normalized_address,
            'mortgages': [],
            'liens': [],
            'property_info': {},
            'source': 'Cook County Recorder of Deeds'
        }
        
        # Try to search Cook County records
        try:
            cook_county_data = self._search_cook_county(normalized_address)
            if cook_county_data:
                result.update(cook_county_data)
        except Exception as e:
            print(f"Error searching Cook County records: {e}")
        
        return result
    
    def _normalize_address(self, address: str) -> str:
        """Normalize address format."""
        # Remove extra spaces and capitalize
        address = ' '.join(address.split())
        # Ensure "N", "S", "E", "W" are capitalized
        address = re.sub(r'\b([nsew])\b', lambda m: m.group(1).upper(), address, flags=re.IGNORECASE)
        return address
    
    def _search_cook_county(self, address: str) -> Optional[Dict]:
        """
        Search Cook County Recorder of Deeds records.
        Note: This is a placeholder - actual implementation would require
        accessing their database or API.
        """
        print(f"\nAttempting to access Cook County Recorder of Deeds records...")
        print(f"Property address: {address}")
        
        # Cook County Recorder of Deeds search
        # Their public search is typically at: https://cookrecorder.com/search
        # This would require form submission and parsing results
        
        # For now, return instructions
        return {
            'instructions': [
                "1. Visit Cook County Recorder of Deeds: https://cookrecorder.com/search",
                f"2. Search for property address: {address}",
                "3. Look for documents labeled as 'Mortgage' or 'Deed of Trust'",
                "4. Look for documents labeled as 'Lien', 'Mechanic's Lien', 'Tax Lien', etc.",
                "5. Check the 'Assessor' section for property details"
            ],
            'direct_search_url': f"https://cookrecorder.com/search?q={address.replace(' ', '+')}"
        }
    
    def search_alternative_sources(self, address: str) -> Dict:
        """
        Search alternative sources for property information.
        """
        print(f"\nSearching alternative sources for: {address}")
        
        results = {
            'zillow': None,
            'redfin': None,
            'assessor': None
        }
        
        # Zillow search
        try:
            zillow_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}_rb/"
            results['zillow'] = {
                'url': zillow_url,
                'note': 'Zillow may show property history but not detailed lien information'
            }
        except Exception as e:
            print(f"Error with Zillow search: {e}")
        
        # Cook County Assessor
        try:
            assessor_url = "https://www.cookcountyassessor.com/"
            results['assessor'] = {
                'url': assessor_url,
                'note': 'Cook County Assessor provides property assessment information'
            }
        except Exception as e:
            print(f"Error with Assessor search: {e}")
        
        return results


def main():
    """Main function to search for property information."""
    searcher = PropertySearch()
    
    # Search for the specific property
    address = "3557 N Marshfield Ave"
    results = searcher.search_property(address)
    
    print("\n" + "="*60)
    print("PROPERTY SEARCH RESULTS")
    print("="*60)
    print(f"\nAddress: {results['address']}")
    
    if 'instructions' in results:
        print("\n📋 Search Instructions:")
        for instruction in results['instructions']:
            print(f"   {instruction}")
        
        if 'direct_search_url' in results:
            print(f"\n🔗 Direct Search URL: {results['direct_search_url']}")
    
    # Alternative sources
    alt_results = searcher.search_alternative_sources(address)
    print("\n📚 Alternative Sources:")
    for source, data in alt_results.items():
        if data:
            print(f"   {source.capitalize()}: {data.get('url', 'N/A')}")
            if 'note' in data:
                print(f"      Note: {data['note']}")
    
    # Save results to JSON
    output_file = "property_search_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'property': results,
            'alternative_sources': alt_results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "="*60)
    print("\n⚠️  IMPORTANT: For official mortgage and lien records,")
    print("   you must access Cook County Recorder of Deeds directly:")
    print("   https://cookrecorder.com/search")
    print("="*60)


if __name__ == "__main__":
    main()

