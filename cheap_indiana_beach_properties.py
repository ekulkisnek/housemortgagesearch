"""
Cheapest Indiana Lake Michigan Properties Finder
Finds REAL properties in Indiana less than 1 mile from Lake Michigan beach
between Illinois and Michigan border, sorted by price per acre.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
import time
import math


class CheapIndianaBeachProperties:
    """Find cheapest REAL properties near Lake Michigan beaches in Indiana."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Key Lake Michigan beach locations in northern Indiana (coordinates)
        self.beach_locations = {
            'Michigan City': {'lat': 41.7075, 'lon': -86.8950},
            'Portage': {'lat': 41.5759, 'lon': -87.1762},
            'Ogden Dunes': {'lat': 41.6214, 'lon': -87.1967},
            'Burns Harbor': {'lat': 41.6281, 'lon': -87.1389},
            'Dune Acres': {'lat': 41.6489, 'lon': -87.0853},
            'Miller Beach': {'lat': 41.6300, 'lon': -87.2600},
            'West Beach': {'lat': 41.6167, 'lon': -87.1833},
            'Indiana Dunes': {'lat': 41.6500, 'lon': -87.1000},
            'Mount Baldy': {'lat': 41.6333, 'lon': -87.0667},
            'Washington Park': {'lat': 41.7075, 'lon': -86.8950}
        }
        
        # Search areas (cities/towns near beaches)
        self.search_areas = [
            'Michigan City, IN',
            'Portage, IN',
            'Ogden Dunes, IN',
            'Burns Harbor, IN',
            'Gary, IN',
            'Chesterton, IN',
            'Porter, IN',
            'Valparaiso, IN',
            'Dune Acres, IN',
            'New Buffalo, IN'
        ]
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in miles using Haversine formula."""
        R = 3959.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def find_nearest_beach_distance(self, lat: float, lon: float) -> tuple:
        """Find the nearest beach location and return distance."""
        min_distance = float('inf')
        nearest_beach = None
        for beach_name, coords in self.beach_locations.items():
            distance = self.calculate_distance(lat, lon, coords['lat'], coords['lon'])
            if distance < min_distance:
                min_distance = distance
                nearest_beach = beach_name
        return (min_distance, nearest_beach)
    
    def get_property_coordinates(self, address: str, city: str, state: str = 'IN') -> Optional[tuple]:
        """Get coordinates for a property address using geocoding."""
        try:
            geocode_url = "https://nominatim.openstreetmap.org/search"
            query = f"{address}, {city}, {state}"
            params = {'q': query, 'format': 'json', 'limit': 1, 'addressdetails': 1}
            headers = {'User-Agent': 'PropertySearchBot/1.0'}
            response = self.session.get(geocode_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return (float(data[0]['lat']), float(data[0]['lon']))
        except Exception:
            pass
        return None
    
    def format_price(self, price_str: str) -> Optional[float]:
        """Extract numeric price from price string."""
        if not price_str:
            return None
        price_str = str(price_str).replace('$', '').replace(',', '').strip()
        if 'M' in price_str.upper():
            price_str = price_str.upper().replace('M', '').strip()
            try:
                return float(price_str) * 1000000
            except:
                return None
        if 'K' in price_str.upper():
            price_str = price_str.upper().replace('K', '').strip()
            try:
                return float(price_str) * 1000
            except:
                return None
        try:
            return float(price_str)
        except:
            return None
    
    def search_zillow_real(self, city: str, state: str = 'IN', max_price: Optional[int] = None) -> List[Dict]:
        """Search Zillow for REAL properties using text extraction."""
        properties = []
        try:
            city_slug = city.lower().replace(' ', '-')
            search_url = f"https://www.zillow.com/homes/{city_slug}-{state.lower()}_rb/"
            
            if max_price:
                search_url += f"?price={0}-{max_price}"
            
            print(f"  [SEARCH] Searching Zillow: {city}, {state}")
            
            response = self.session.get(search_url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Extract addresses from text - Indiana addresses
                address_pattern = r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IN\s+\d{5})'
                addresses = re.findall(address_pattern, text)
                
                # Extract prices
                prices = re.findall(r'\$([\d,]+(?:\.\d{2})?[KMB]?)', text)
                
                # Extract lot sizes
                lot_sizes = re.findall(r'([\d.]+)\s*(?:acre|ac|acres|sq\s*ft|sqft)', text, re.I)
                
                # Find property links
                links = soup.find_all('a', href=re.compile(r'/homedetails/'))
                
                # Create property objects
                for i, addr in enumerate(addresses[:50]):
                    if ', IN' in addr:
                        price = self.format_price(prices[i]) if i < len(prices) else None
                        
                        # Extract lot size
                        lot_size_acres = None
                        if i < len(lot_sizes):
                            lot_val = float(lot_sizes[i])
                            if 'sq' in text.lower() or 'sqft' in text.lower():
                                lot_size_acres = lot_val / 43560
                            else:
                                lot_size_acres = lot_val
                        
                        # Get property link
                        prop_url = None
                        if links:
                            link_idx = min(i, len(links) - 1)
                            href = links[link_idx].get('href', '')
                            if href:
                                prop_url = href if href.startswith('http') else f"https://www.zillow.com{href}"
                        
                        # Parse address
                        parts = addr.split(',')
                        street = parts[0].strip()
                        city_name = parts[1].strip() if len(parts) > 1 else city
                        
                        prop = {
                            'address': street,
                            'city': city_name,
                            'state': 'IN',
                            'price': price,
                            'price_str': f"${price:,.0f}" if price else None,
                            'lot_size_acres': lot_size_acres,
                            'url': prop_url or search_url,
                            'source': 'Zillow',
                            'search_url': search_url
                        }
                        
                        if price:  # Only add if we have a price
                            properties.append(prop)
                
                print(f"    [FOUND] Found {len(properties)} properties from Zillow")
            else:
                print(f"    [INFO] Zillow returned status {response.status_code}")
                
        except Exception as e:
            print(f"    [ERROR] Zillow search error: {str(e)[:50]}")
        
        return properties
    
    def search_redfin_real(self, city: str, state: str = 'IN', max_price: Optional[int] = None) -> List[Dict]:
        """Search Redfin for REAL properties using text extraction."""
        properties = []
        try:
            city_slug = city.lower().replace(' ', '-')
            search_url = f"https://www.redfin.com/city/{city_slug}-{state.upper()}"
            
            if max_price:
                search_url += f"?max-price={max_price}"
            
            print(f"  [SEARCH] Searching Redfin: {city}, {state}")
            
            response = self.session.get(search_url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Extract addresses - Indiana addresses
                address_pattern = r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IN\s+\d{5})'
                addresses = re.findall(address_pattern, text)
                
                # Extract prices
                prices = re.findall(r'\$([\d,]+(?:\.\d{2})?[KMB]?)', text)
                
                # Extract lot sizes
                lot_sizes = re.findall(r'([\d.]+)\s*(?:acre|ac|acres|sq\s*ft|sqft)', text, re.I)
                
                # Find property links
                links = soup.find_all('a', href=re.compile(r'/home/'))
                
                # Create property objects
                for i, addr in enumerate(addresses[:50]):
                    if ', IN' in addr:
                        price = self.format_price(prices[i]) if i < len(prices) else None
                        
                        # Extract lot size
                        lot_size_acres = None
                        if i < len(lot_sizes):
                            lot_val = float(lot_sizes[i])
                            if 'sq' in text.lower() or 'sqft' in text.lower():
                                lot_size_acres = lot_val / 43560
                            else:
                                lot_size_acres = lot_val
                        
                        # Get property link
                        prop_url = None
                        if links:
                            link_idx = min(i, len(links) - 1)
                            href = links[link_idx].get('href', '')
                            if href:
                                prop_url = href if href.startswith('http') else f"https://www.redfin.com{href}"
                        
                        # Parse address
                        parts = addr.split(',')
                        street = parts[0].strip()
                        city_name = parts[1].strip() if len(parts) > 1 else city
                        
                        prop = {
                            'address': street,
                            'city': city_name,
                            'state': 'IN',
                            'price': price,
                            'price_str': f"${price:,.0f}" if price else None,
                            'lot_size_acres': lot_size_acres,
                            'url': prop_url or search_url,
                            'source': 'Redfin',
                            'search_url': search_url
                        }
                        
                        if price:  # Only add if we have a price
                            properties.append(prop)
                
                print(f"    [FOUND] Found {len(properties)} properties from Redfin")
            else:
                print(f"    [INFO] Redfin returned status {response.status_code}")
                
        except Exception as e:
            print(f"    [ERROR] Redfin search error: {str(e)[:50]}")
        
        return properties
    
    def search_homes_com(self, city: str, state: str = 'IN', max_price: Optional[int] = None) -> List[Dict]:
        """Search Homes.com for REAL properties."""
        properties = []
        try:
            city_slug = city.lower().replace(' ', '-')
            search_url = f"https://www.homes.com/{city_slug}-{state.lower()}/homes-for-sale/"
            
            if max_price:
                search_url += f"?priceMax={max_price}"
            
            print(f"  [SEARCH] Searching Homes.com: {city}, {state}")
            
            response = self.session.get(search_url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Extract addresses - Indiana addresses
                address_pattern = r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IN\s+\d{5})'
                addresses = re.findall(address_pattern, text)
                
                # Extract prices
                prices = re.findall(r'\$([\d,]+(?:\.\d{2})?[KMB]?)', text)
                
                # Extract lot sizes
                lot_sizes = re.findall(r'([\d.]+)\s*(?:acre|ac|acres|sq\s*ft|sqft)', text, re.I)
                
                # Find property links
                links = soup.find_all('a', href=re.compile(r'/property/'))
                
                # Create property objects
                for i, addr in enumerate(addresses[:50]):
                    if ', IN' in addr:
                        price = self.format_price(prices[i]) if i < len(prices) else None
                        
                        # Extract lot size
                        lot_size_acres = None
                        if i < len(lot_sizes):
                            lot_val = float(lot_sizes[i])
                            if 'sq' in text.lower() or 'sqft' in text.lower():
                                lot_size_acres = lot_val / 43560
                            else:
                                lot_size_acres = lot_val
                        
                        # Get property link
                        prop_url = None
                        if links:
                            link_idx = min(i, len(links) - 1)
                            href = links[link_idx].get('href', '')
                            if href:
                                prop_url = href if href.startswith('http') else f"https://www.homes.com{href}"
                        
                        # Parse address
                        parts = addr.split(',')
                        street = parts[0].strip()
                        city_name = parts[1].strip() if len(parts) > 1 else city
                        
                        prop = {
                            'address': street,
                            'city': city_name,
                            'state': 'IN',
                            'price': price,
                            'price_str': f"${price:,.0f}" if price else None,
                            'lot_size_acres': lot_size_acres,
                            'url': prop_url or search_url,
                            'source': 'Homes.com',
                            'search_url': search_url
                        }
                        
                        if price:  # Only add if we have a price
                            properties.append(prop)
                
                print(f"    [FOUND] Found {len(properties)} properties from Homes.com")
            else:
                print(f"    [INFO] Homes.com returned status {response.status_code}")
                
        except Exception as e:
            print(f"    [ERROR] Homes.com search error: {str(e)[:50]}")
        
        return properties
    
    def generate_search_urls(self, city: str, state: str = 'IN', max_price: Optional[int] = None) -> List[Dict]:
        """Generate direct search URLs for manual browsing."""
        urls = []
        
        city_slug = city.lower().replace(' ', '-')
        
        # Zillow
        zillow_url = f"https://www.zillow.com/homes/{city_slug}-{state.lower()}_rb/"
        if max_price:
            zillow_url += f"?price={0}-{max_price}"
        urls.append({'source': 'Zillow', 'url': zillow_url, 'city': city})
        
        # Redfin
        redfin_url = f"https://www.redfin.com/city/{city_slug}-{state.upper()}"
        if max_price:
            redfin_url += f"?max-price={max_price}"
        urls.append({'source': 'Redfin', 'url': redfin_url, 'city': city})
        
        # Realtor.com
        realtor_url = f"https://www.realtor.com/realestateandhomes-search/{city_slug}_{state.lower()}"
        if max_price:
            realtor_url += f"?maxPrice={max_price}"
        urls.append({'source': 'Realtor.com', 'url': realtor_url, 'city': city})
        
        # Homes.com
        homes_url = f"https://www.homes.com/{city_slug}-{state.lower()}/homes-for-sale/"
        if max_price:
            homes_url += f"?priceMax={max_price}"
        urls.append({'source': 'Homes.com', 'url': homes_url, 'city': city})
        
        return urls
    
    def search_realtor_com_real(self, city: str, state: str = 'IN', max_price: Optional[int] = None) -> List[Dict]:
        """Search Realtor.com for REAL properties using text extraction."""
        properties = []
        try:
            city_slug = city.replace(' ', '-').lower()
            search_url = f"https://www.realtor.com/realestateandhomes-search/{city_slug}_{state.lower()}"
            
            if max_price:
                search_url += f"?maxPrice={max_price}"
            
            print(f"  [SEARCH] Searching Realtor.com: {city}, {state}")
            
            response = self.session.get(search_url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Extract addresses - Indiana addresses
                address_pattern = r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IN\s+\d{5})'
                addresses = re.findall(address_pattern, text)
                
                # Extract prices
                prices = re.findall(r'\$([\d,]+(?:\.\d{2})?[KMB]?)', text)
                
                # Extract lot sizes
                lot_sizes = re.findall(r'([\d.]+)\s*(?:acre|ac|acres|sq\s*ft|sqft)', text, re.I)
                
                # Find property links
                links = soup.find_all('a', href=re.compile(r'/realestateandhomes/'))
                
                # Create property objects
                for i, addr in enumerate(addresses[:50]):
                    if ', IN' in addr:
                        price = self.format_price(prices[i]) if i < len(prices) else None
                        
                        # Extract lot size
                        lot_size_acres = None
                        if i < len(lot_sizes):
                            lot_val = float(lot_sizes[i])
                            if 'sq' in text.lower() or 'sqft' in text.lower():
                                lot_size_acres = lot_val / 43560
                            else:
                                lot_size_acres = lot_val
                        
                        # Get property link
                        prop_url = None
                        if links:
                            link_idx = min(i, len(links) - 1)
                            href = links[link_idx].get('href', '')
                            if href:
                                prop_url = href if href.startswith('http') else f"https://www.realtor.com{href}"
                        
                        # Parse address
                        parts = addr.split(',')
                        street = parts[0].strip()
                        city_name = parts[1].strip() if len(parts) > 1 else city
                        
                        prop = {
                            'address': street,
                            'city': city_name,
                            'state': 'IN',
                            'price': price,
                            'price_str': f"${price:,.0f}" if price else None,
                            'lot_size_acres': lot_size_acres,
                            'url': prop_url or search_url,
                            'source': 'Realtor.com',
                            'search_url': search_url
                        }
                        
                        if price:  # Only add if we have a price
                            properties.append(prop)
                
                print(f"    [FOUND] Found {len(properties)} properties from Realtor.com")
            else:
                print(f"    [INFO] Realtor.com returned status {response.status_code}")
                
        except Exception as e:
            print(f"    [ERROR] Realtor.com search error: {str(e)[:50]}")
        
        return properties
    
    def enrich_property_with_coordinates(self, prop: Dict) -> Dict:
        """Add coordinates to a property by geocoding its address."""
        if 'lat' in prop and 'lon' in prop:
            return prop
        
        address = prop.get('address', '')
        city = prop.get('city', '')
        state = prop.get('state', 'IN')
        
        if address:
            coords = self.get_property_coordinates(address, city, state)
            if coords:
                prop['lat'] = coords[0]
                prop['lon'] = coords[1]
                time.sleep(1)  # Be respectful to geocoding API
        
        return prop
    
    def sort_by_price_per_acre(self, properties: List[Dict]) -> List[Dict]:
        """Sort properties by price per acre (cheapest first)."""
        def get_price_per_acre(prop):
            if 'price_per_acre' in prop and prop['price_per_acre']:
                return prop['price_per_acre']
            if 'price' in prop and 'lot_size_acres' in prop:
                price = prop['price'] if isinstance(prop['price'], (int, float)) else None
                acres = prop['lot_size_acres'] if isinstance(prop['lot_size_acres'], (int, float)) else None
                if price and acres and acres > 0:
                    return price / acres
            return float('inf')
        
        return sorted(properties, key=get_price_per_acre)


def main():
    """Main function to search for cheap REAL properties near Lake Michigan."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Find cheapest REAL properties near Lake Michigan in Indiana')
    parser.add_argument('--max-price', type=int, help='Maximum price filter (e.g., 200000 for $200K)')
    parser.add_argument('--min-price', type=int, help='Minimum price filter')
    parser.add_argument('--max-distance', type=float, default=1.0, help='Maximum distance from beach in miles (default: 1.0)')
    args = parser.parse_args()
    
    searcher = CheapIndianaBeachProperties()
    
    print("="*80)
    print("CHEAPEST INDIANA LAKE MICHIGAN PROPERTIES - REAL DATA ONLY")
    print("Finding REAL properties < 1 mile from beach, sorted by price per acre")
    print("="*80)
    print(f"\n[TARGET] Target Area: Northern Indiana (between IL and MI border)")
    print(f"[BEACH] Beach Distance: < {args.max_distance} mile(s)")
    print(f"[SORT] Sorting: Cheapest per acre")
    
    if args.max_price:
        print(f"\n[PRICE] Price Filter: Up to ${args.max_price:,}")
    
    print("\n" + "="*80)
    print("SEARCHING FOR REAL PROPERTIES...")
    print("="*80)
    
    all_properties = []
    
    # Search all areas
    for area in searcher.search_areas:
        city = area.split(',')[0].strip()
        print(f"\n[SEARCH] Searching {area}...")
        
        # Search Zillow
        zillow_props = searcher.search_zillow_real(city, 'IN', args.max_price)
        all_properties.extend(zillow_props)
        
        # Search Redfin
        redfin_props = searcher.search_redfin_real(city, 'IN', args.max_price)
        all_properties.extend(redfin_props)
        
        # Search Realtor.com
        realtor_props = searcher.search_realtor_com_real(city, 'IN', args.max_price)
        all_properties.extend(realtor_props)
        
        # Search Homes.com
        homes_props = searcher.search_homes_com(city, 'IN', args.max_price)
        all_properties.extend(homes_props)
        
        time.sleep(2)  # Rate limiting
    
    # Remove duplicates
    seen = set()
    unique_properties = []
    for prop in all_properties:
        addr_key = f"{prop.get('address', '')}{prop.get('city', '')}".lower().strip()
        if addr_key and addr_key not in seen:
            seen.add(addr_key)
            unique_properties.append(prop)
    
    print(f"\n[DATA] Total unique properties found: {len(unique_properties)}")
    
    # Enrich properties with coordinates and distance
    print("\n[GEOCODE] Geocoding properties and calculating distances to beaches...")
    enriched_properties = []
    geocoded_count = 0
    
    for prop in unique_properties:
        prop = searcher.enrich_property_with_coordinates(prop)
        
        if 'lat' in prop and 'lon' in prop:
            geocoded_count += 1
            distance, beach = searcher.find_nearest_beach_distance(prop['lat'], prop['lon'])
            prop['distance_to_beach_miles'] = distance
            prop['nearest_beach'] = beach
        else:
            prop['distance_to_beach_miles'] = None
            prop['nearest_beach'] = None
        
        enriched_properties.append(prop)
    
    print(f"    [OK] Geocoded {geocoded_count} of {len(unique_properties)} properties")
    
    # Filter by distance
    properties_within_distance = [
        p for p in enriched_properties 
        if p.get('distance_to_beach_miles') is not None 
        and p.get('distance_to_beach_miles', 999) <= args.max_distance
    ]
    
    print(f"    [OK] Properties within {args.max_distance} mile(s) of beach: {len(properties_within_distance)}")
    
    # Calculate price per acre for all properties
    for prop in enriched_properties:
        if 'price' in prop and 'lot_size_acres' in prop:
            price = prop['price']
            acres = prop['lot_size_acres']
            if price and acres and acres > 0:
                if 'price_per_acre' not in prop:
                    prop['price_per_acre'] = price / acres
                    prop['price_per_acre_str'] = f"${prop['price_per_acre']:,.0f}/acre"
    
    # Sort by price per acre
    properties_with_acre_price = [p for p in properties_within_distance if 'price_per_acre' in p and p['price_per_acre']]
    properties_without_acre_price = [p for p in properties_within_distance if 'price_per_acre' not in p or not p.get('price_per_acre')]
    
    sorted_by_per_acre = searcher.sort_by_price_per_acre(properties_with_acre_price)
    sorted_by_price = sorted(properties_without_acre_price, key=lambda x: x.get('price', float('inf')))
    
    final_properties = sorted_by_per_acre + sorted_by_price
    
    # Display results
    print("\n" + "="*80)
    print(f"CHEAPEST REAL PROPERTIES PER ACRE (< {args.max_distance} MILE FROM BEACH)")
    print("="*80)
    
    if final_properties:
        print(f"\n[TOP] Top {len(final_properties)} REAL Properties (sorted by price per acre):\n")
        
        for i, prop in enumerate(final_properties[:100], 1):  # Show top 100
            print(f"{'='*80}")
            print(f"PROPERTY #{i}")
            print(f"{'='*80}")
            
            address = prop.get('address', 'N/A')
            city = prop.get('city', '')
            state = prop.get('state', 'IN')
            full_address = f"{address}, {city}, {state}" if city else address
            
            print(f"[ADDR] Address:     {full_address}")
            price_str = prop.get('price_str') or f"${prop.get('price', 0):,.0f}"
            print(f"[PRICE] Price:        {price_str}")
            
            if 'lot_size_acres' in prop and prop['lot_size_acres']:
                print(f"[LOT] Lot Size:     {prop['lot_size_acres']:.3f} acres")
            
            if 'price_per_acre' in prop and prop['price_per_acre']:
                price_per_acre_str = prop.get('price_per_acre_str') or f"${prop['price_per_acre']:,.0f}/acre"
                print(f"[ACRE] Price/Acre:   {price_per_acre_str}")
            
            if 'distance_to_beach_miles' in prop and prop['distance_to_beach_miles'] is not None:
                print(f"[BEACH] Distance:     {prop['distance_to_beach_miles']:.2f} miles to {prop.get('nearest_beach', 'beach')}")
            
            if 'url' in prop and prop['url']:
                print(f"[LINK] Direct Link:  {prop['url']}")
            
            print(f"[SOURCE] Source:       {prop.get('source', 'Unknown')}")
            print()
    else:
        print("\n[WARNING] No properties found within specified criteria.")
        print("   Try:")
        print("   - Increasing max-distance (e.g., --max-distance 2.0)")
        print("   - Removing price filters")
        print("   - Checking search URLs manually\n")
    
    # Save results to JSON
    output_file = "cheap_indiana_beach_properties.json"
    results = {
        'search_date': datetime.now().isoformat(),
        'target_area': 'Northern Indiana Lake Michigan Coast',
        'max_distance_from_beach_miles': args.max_distance,
        'max_price': args.max_price,
        'min_price': args.min_price,
        'total_properties_found': len(unique_properties),
        'properties_geocoded': geocoded_count,
        'properties_within_distance': len(properties_within_distance),
        'properties': [
            {
                'address': p.get('address', ''),
                'city': p.get('city', ''),
                'state': p.get('state', ''),
                'price': p.get('price'),
                'price_str': p.get('price_str', ''),
                'lot_size_acres': p.get('lot_size_acres'),
                'price_per_acre': p.get('price_per_acre'),
                'price_per_acre_str': p.get('price_per_acre_str', ''),
                'distance_to_beach_miles': p.get('distance_to_beach_miles'),
                'nearest_beach': p.get('nearest_beach'),
                'url': p.get('url', ''),
                'source': p.get('source', ''),
                'lat': p.get('lat'),
                'lon': p.get('lon')
            }
            for p in final_properties
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[SAVE] Results saved to: {output_file}")
    print(f"   - Found {results['total_properties_found']} total REAL properties")
    print(f"   - {results['properties_geocoded']} properties geocoded")
    print(f"   - {results['properties_within_distance']} properties within {args.max_distance} mile(s) of beach")
    print(f"   - Saved {len(results['properties'])} properties to JSON with direct links")
    
    # Generate and display search URLs
    print("\n" + "="*80)
    print("DIRECT SEARCH URLS - Click to browse properties manually:")
    print("="*80)
    all_search_urls = []
    for area in searcher.search_areas:
        city = area.split(',')[0].strip()
        urls = searcher.generate_search_urls(city, 'IN', args.max_price)
        all_search_urls.extend(urls)
    
    # Group by source
    sources = {}
    for item in all_search_urls:
        source = item['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(item)
    
    for source, items in sources.items():
        print(f"\n[{source}]")
        for item in items[:5]:  # Show first 5 cities per source
            print(f"  {item['city']}: {item['url']}")
    
    print("\n" + "="*80)
    print("[TIPS] TIPS:")
    print("="*80)
    print("• Use --max-price to filter by price: python cheap_indiana_beach_properties.py --max-price 150000")
    print("• Use --max-distance to adjust distance: python cheap_indiana_beach_properties.py --max-distance 2.0")
    print("• All properties have direct links - click to view full details")
    print("• Click the URLs above to browse properties manually if scraping doesn't work")
    print("• Verify distances manually using Google Maps for important properties")
    print("="*80)


if __name__ == "__main__":
    main()
