"""
Comprehensive Foreclosure Scraper - ALL FREE DATA SOURCES
Includes every possible free source, prioritizing government/official sources
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
from typing import Dict, List, Optional

class ComprehensiveForeclosureScraper:
    """Comprehensive scraper using ALL free data sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.properties = []
        self.sources_tried = []
    
    # ==================== GOVERNMENT SOURCES (HIGHEST PRIORITY) ====================
    
    def get_fannie_mae_homepath(self, state="IL") -> List[Dict]:
        """Fannie Mae HomePath - Government Sponsored Enterprise."""
        print(f"\n[GOVERNMENT] Fannie Mae HomePath ({state})...")
        self.sources_tried.append('Fannie Mae HomePath')
        
        properties = []
        try:
            url = "https://www.homenext.com/PropertySearch"
            response = self.session.get(url, params={'state': state}, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:50]):
                    prop = {
                        'source': 'Fannie Mae HomePath',
                        'source_type': 'government_sponsored_enterprise',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': 'https://www.homenext.com',
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'official_government'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] Visit https://www.homenext.com and search for {state}")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_freddie_mac_homesteps(self, state="IL") -> List[Dict]:
        """Freddie Mac HomeSteps - Government Sponsored Enterprise."""
        print(f"\n[GOVERNMENT] Freddie Mac HomeSteps ({state})...")
        self.sources_tried.append('Freddie Mac HomeSteps')
        
        properties = []
        try:
            url = "https://www.homesteps.com"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                if 'illinois' in text.lower() or 'il' in text.lower():
                    addresses = re.findall(
                        r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                        text
                    )
                    
                    prices = re.findall(r'\$([\d,]+)', text)
                    
                    for i, addr in enumerate(addresses[:50]):
                        prop = {
                            'source': 'Freddie Mac HomeSteps',
                            'source_type': 'government_sponsored_enterprise',
                            'county': 'Illinois',
                            'address': addr.strip(),
                            'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                            'url': 'https://www.homesteps.com',
                            'scraped_at': datetime.now().isoformat(),
                            'quality': 'official_government'
                        }
                        properties.append(prop)
                    
                    print(f"   [SUCCESS] Found {len(properties)} properties")
                else:
                    print(f"   [INFO] Visit https://www.homesteps.com and search for {state}")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_hud_homestore(self, state="IL") -> List[Dict]:
        """HUD Home Store - U.S. Department of Housing."""
        print(f"\n[GOVERNMENT] HUD Home Store ({state})...")
        self.sources_tried.append('HUD Home Store')
        
        properties = []
        try:
            url = "https://www.hudhomestore.com"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:50]):
                    prop = {
                        'source': 'HUD Home Store',
                        'source_type': 'federal_government',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': 'https://www.hudhomestore.com',
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'official_federal'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] Visit https://www.hudhomestore.com and search for {state}")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_va_homes(self, state="IL") -> List[Dict]:
        """VA (Veterans Affairs) Foreclosed Properties."""
        print(f"\n[GOVERNMENT] VA Foreclosed Properties ({state})...")
        self.sources_tried.append('VA Foreclosed Properties')
        
        properties = []
        try:
            url = "https://www.benefits.va.gov/homeloans/purchaseco_foreclosed.asp"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # VA properties may be listed differently
                if 'illinois' in text.lower() or 'il' in text.lower():
                    addresses = re.findall(
                        r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                        text
                    )
                    
                    for addr in addresses[:30]:
                        prop = {
                            'source': 'VA Foreclosed Properties',
                            'source_type': 'federal_government',
                            'county': 'Illinois',
                            'address': addr.strip(),
                            'url': url,
                            'scraped_at': datetime.now().isoformat(),
                            'quality': 'official_federal'
                        }
                        properties.append(prop)
                    
                    print(f"   [SUCCESS] Found {len(properties)} properties")
                else:
                    print(f"   [INFO] Visit https://www.benefits.va.gov/homeloans/purchaseco_foreclosed.asp")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_usda_properties(self, state="IL") -> List[Dict]:
        """USDA Foreclosed Properties."""
        print(f"\n[GOVERNMENT] USDA Foreclosed Properties ({state})...")
        self.sources_tried.append('USDA Foreclosed Properties')
        
        properties = []
        try:
            url = "https://www.resales.usda.gov"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:30]):
                    prop = {
                        'source': 'USDA Foreclosed Properties',
                        'source_type': 'federal_government',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': 'https://www.resales.usda.gov',
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'official_federal'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] Visit https://www.resales.usda.gov")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    # ==================== COUNTY OFFICIAL SOURCES ====================
    
    def get_county_sheriff_sales(self, county: str) -> List[Dict]:
        """Get county sheriff foreclosure sales."""
        print(f"\n[OFFICIAL] {county} County Sheriff Sales...")
        self.sources_tried.append(f'{county} County Sheriff')
        
        properties = []
        
        sheriff_sources = {
            'DuPage': {
                'url': 'https://www.dupagecounty.gov/sheriff/',
                'phone': '(630) 682-7256',
                'address': '501 N. County Farm Road, Wheaton, IL 60187'
            },
            'Cook': {
                'url': 'https://www.cookcountysheriff.org/foreclosure-sales/',
                'phone': '(312) 603-5113'
            },
            'Lake': {
                'url': 'https://www.lakecountyil.gov/departments/sheriff',
                'phone': '(847) 377-4000'
            },
            'Will': {
                'url': 'https://www.willcosheriff.org/',
                'phone': '(815) 727-8575'
            },
            'Kane': {
                'url': 'https://www.kanecountyil.gov/sheriff',
                'phone': '(630) 208-2000'
            }
        }
        
        if county in sheriff_sources:
            try:
                source = sheriff_sources[county]
                response = self.session.get(source['url'], timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    
                    if 'foreclosure' in text.lower() or 'sale' in text.lower():
                        addresses = re.findall(
                            r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                            text
                        )
                        
                        case_numbers = re.findall(r'(\d{2}[A-Z]{2}\d+)', text)
                        prices = re.findall(r'\$([\d,]+)', text)
                        
                        for i, addr in enumerate(addresses[:30]):
                            prop = {
                                'source': f'{county} County Sheriff',
                                'source_type': 'county_official',
                                'county': county,
                                'address': addr.strip(),
                                'case_number': case_numbers[i] if i < len(case_numbers) else None,
                                'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                                'url': source['url'],
                                'phone': source.get('phone'),
                                'scraped_at': datetime.now().isoformat(),
                                'quality': 'official_county'
                            }
                            properties.append(prop)
                        
                        print(f"   [SUCCESS] Found {len(properties)} properties")
                    else:
                        print(f"   [INFO] Call {source.get('phone', 'county office')} for current listings")
            except Exception as e:
                print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_county_circuit_clerk(self, county: str) -> List[Dict]:
        """Get county Circuit Clerk foreclosure records."""
        print(f"\n[OFFICIAL] {county} County Circuit Clerk...")
        self.sources_tried.append(f'{county} County Circuit Clerk')
        
        properties = []
        
        clerk_sources = {
            'DuPage': 'https://www.dupagecounty.gov/elected_officials/circuit_clerk/',
            'Cook': 'https://www.cookcountyclerkofcourt.org/',
            'Lake': 'https://www.lakecountyil.gov/departments/circuit_clerk',
            'Will': 'https://www.willcountycircuitclerk.org/',
            'Kane': 'https://www.kanecountyclerk.org/'
        }
        
        if county in clerk_sources:
            try:
                url = clerk_sources[county]
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    
                    if 'foreclosure' in text.lower():
                        case_numbers = re.findall(r'(\d{2}[A-Z]{2}\d+)', text)
                        addresses = re.findall(
                            r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                            text
                        )
                        
                        for i, addr in enumerate(addresses[:20]):
                            prop = {
                                'source': f'{county} County Circuit Clerk',
                                'source_type': 'county_official_court',
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
                        print(f"   [INFO] Visit {url} and search foreclosure cases")
            except Exception as e:
                print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    # ==================== COMPREHENSIVE PLATFORMS ====================
    
    def get_auction_com(self, location="Illinois") -> List[Dict]:
        """Auction.com - Comprehensive auction platform."""
        print(f"\n[PLATFORM] Auction.com ({location})...")
        self.sources_tried.append('Auction.com')
        
        properties = []
        try:
            url = f"https://www.auction.com/search?q={location}"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:50]):
                    prop = {
                        'source': 'Auction.com',
                        'source_type': 'comprehensive_platform',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'structured_platform'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] Visit https://www.auction.com and search for {location}")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_foreclosure_listings_usa(self) -> List[Dict]:
        """ForeclosureListingsUSA - Free nationwide listings."""
        print(f"\n[PLATFORM] ForeclosureListingsUSA...")
        self.sources_tried.append('ForeclosureListingsUSA')
        
        properties = []
        try:
            url = "https://www.foreclosurelistingsusa.com/illinois-foreclosures"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:50]):
                    prop = {
                        'source': 'ForeclosureListingsUSA',
                        'source_type': 'comprehensive_platform',
                        'county': 'Illinois',
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'aggregated_listings'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
            else:
                print(f"   [INFO] Visit https://www.foreclosurelistingsusa.com")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_housing_auctions_net(self) -> List[Dict]:
        """HousingAuctions.net - Free public auction directory."""
        print(f"\n[PLATFORM] HousingAuctions.net...")
        self.sources_tried.append('HousingAuctions.net')
        
        properties = []
        try:
            url = "https://housingauctions.net/listings/"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                if 'illinois' in text.lower() or 'il' in text.lower():
                    addresses = re.findall(
                        r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                        text
                    )
                    
                    prices = re.findall(r'\$([\d,]+)', text)
                    
                    for i, addr in enumerate(addresses[:30]):
                        prop = {
                            'source': 'HousingAuctions.net',
                            'source_type': 'comprehensive_platform',
                            'county': 'Illinois',
                            'address': addr.strip(),
                            'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                            'url': url,
                            'scraped_at': datetime.now().isoformat(),
                            'quality': 'aggregated_listings'
                        }
                        properties.append(prop)
                    
                    print(f"   [SUCCESS] Found {len(properties)} properties")
                else:
                    print(f"   [INFO] Visit https://housingauctions.net")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_ilfls_free_lists(self, county: str) -> List[Dict]:
        """ILFLS Free Daily Lists - Illinois specific."""
        print(f"\n[PLATFORM] ILFLS Free Lists ({county})...")
        self.sources_tried.append(f'ILFLS {county}')
        
        properties = []
        try:
            county_lower = county.lower()
            url = f"https://ilfls.com/free-daily-auction-lists/{county_lower}"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]+)',
                    text
                )
                
                case_numbers = re.findall(r'(\d{2}[A-Z]{2}\d+)', text)
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:30]):
                    prop = {
                        'source': f'ILFLS {county}',
                        'source_type': 'state_specific',
                        'county': county,
                        'address': addr.strip(),
                        'case_number': case_numbers[i] if i < len(case_numbers) else None,
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'state_specific'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    # ==================== GENERAL PLATFORMS (FALLBACK) ====================
    
    def get_zillow_foreclosures(self, location="DuPage County IL") -> List[Dict]:
        """Zillow foreclosures."""
        print(f"\n[GENERAL] Zillow ({location})...")
        self.sources_tried.append(f'Zillow {location}')
        
        properties = []
        try:
            search_term = location.replace(" ", "-").lower()
            url = f"https://www.zillow.com/{search_term}/foreclosures/"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:30]):
                    prop = {
                        'source': f'Zillow {location}',
                        'source_type': 'general_platform',
                        'county': location,
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'general_listing'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
        except Exception as e:
            print(f"   [ERROR] {str(e)[:100]}")
        
        return properties
    
    def get_redfin_foreclosures(self, location="DuPage County") -> List[Dict]:
        """Redfin foreclosures."""
        print(f"\n[GENERAL] Redfin ({location})...")
        self.sources_tried.append(f'Redfin {location}')
        
        properties = []
        try:
            url = f"https://www.redfin.com/county/733/IL/DuPage-County/foreclosures"
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                addresses = re.findall(
                    r'(\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Court|Ct|Way|Parkway|Pkwy|Place|Pl|Circle|Cir)[\s\w,]*IL\s+\d{5})',
                    text
                )
                
                prices = re.findall(r'\$([\d,]+)', text)
                
                for i, addr in enumerate(addresses[:50]):
                    prop = {
                        'source': f'Redfin {location}',
                        'source_type': 'general_platform',
                        'county': location,
                        'address': addr.strip(),
                        'opening_bid': self._parse_price(prices[i]) if i < len(prices) else None,
                        'url': url,
                        'scraped_at': datetime.now().isoformat(),
                        'quality': 'general_listing'
                    }
                    properties.append(prop)
                
                print(f"   [SUCCESS] Found {len(properties)} properties")
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
    
    def get_all_comprehensive_sources(self, counties: List[str] = None) -> List[Dict]:
        """Get data from ALL comprehensive sources."""
        if counties is None:
            counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
        
        print("="*80)
        print("COMPREHENSIVE FORECLOSURE SCRAPER - ALL FREE SOURCES")
        print("="*80)
        print("SOURCE PRIORITY:")
        print("  1. Government Sources (Fannie Mae, Freddie Mac, HUD, VA, USDA)")
        print("  2. Official County Sources (Sheriff, Circuit Clerk)")
        print("  3. Comprehensive Platforms (Auction.com, ForeclosureListingsUSA)")
        print("  4. State-Specific (ILFLS)")
        print("  5. General Platforms (Zillow, Redfin)")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        all_properties = []
        
        # ========== GOVERNMENT SOURCES (HIGHEST PRIORITY) ==========
        print("\n" + "="*80)
        print("GOVERNMENT SOURCES (HIGHEST PRIORITY)")
        print("="*80)
        
        all_properties.extend(self.get_fannie_mae_homepath("IL"))
        time.sleep(1)
        all_properties.extend(self.get_freddie_mac_homesteps("IL"))
        time.sleep(1)
        all_properties.extend(self.get_hud_homestore("IL"))
        time.sleep(1)
        all_properties.extend(self.get_va_homes("IL"))
        time.sleep(1)
        all_properties.extend(self.get_usda_properties("IL"))
        time.sleep(1)
        
        # ========== OFFICIAL COUNTY SOURCES ==========
        print("\n" + "="*80)
        print("OFFICIAL COUNTY SOURCES")
        print("="*80)
        
        for county in counties:
            all_properties.extend(self.get_county_sheriff_sales(county))
            time.sleep(1)
            all_properties.extend(self.get_county_circuit_clerk(county))
            time.sleep(1)
        
        # ========== COMPREHENSIVE PLATFORMS ==========
        print("\n" + "="*80)
        print("COMPREHENSIVE PLATFORMS")
        print("="*80)
        
        all_properties.extend(self.get_auction_com("Illinois"))
        time.sleep(1)
        all_properties.extend(self.get_foreclosure_listings_usa())
        time.sleep(1)
        all_properties.extend(self.get_housing_auctions_net())
        time.sleep(1)
        
        # ILFLS for each county
        for county in counties:
            all_properties.extend(self.get_ilfls_free_lists(county))
            time.sleep(1)
        
        # ========== GENERAL PLATFORMS (FALLBACK) ==========
        print("\n" + "="*80)
        print("GENERAL PLATFORMS (FALLBACK)")
        print("="*80)
        
        for county in counties:
            all_properties.extend(self.get_zillow_foreclosures(f"{county} County IL"))
            time.sleep(1)
            all_properties.extend(self.get_redfin_foreclosures(f"{county} County"))
            time.sleep(1)
        
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
            'official_government': 3,
            'official_county': 4,
            'structured_platform': 5,
            'state_specific': 6,
            'aggregated_listings': 7,
            'general_listing': 8
        }
        
        unique.sort(key=lambda x: (
            quality_order.get(x.get('quality', ''), 99),
            x.get('opening_bid') or float('inf')
        ))
        
        self.properties = unique
        return unique
    
    def display_results(self, limit: int = 100):
        """Display results with source quality indicators."""
        if not self.properties:
            print("\n[WARNING] No properties found from automated scraping")
            print("\n[RECOMMENDATION] Visit these sources directly:")
            print("\nGOVERNMENT SOURCES:")
            print("  • Fannie Mae: https://www.homenext.com")
            print("  • Freddie Mac: https://www.homesteps.com")
            print("  • HUD: https://www.hudhomestore.com")
            print("  • VA: https://www.benefits.va.gov/homeloans/purchaseco_foreclosed.asp")
            print("  • USDA: https://www.resales.usda.gov")
            print("\nOFFICIAL COUNTY SOURCES:")
            print("  • DuPage Sheriff: (630) 682-7256")
            print("  • Cook Sheriff: (312) 603-5113")
            print("  • County Circuit Clerks (official court records)")
            print("\nCOMPREHENSIVE PLATFORMS:")
            print("  • Auction.com: https://www.auction.com")
            print("  • ForeclosureListingsUSA: https://www.foreclosurelistingsusa.com")
            print("  • HousingAuctions.net: https://housingauctions.net")
            print("  • ILFLS: https://ilfls.com/free-daily-auction-lists/")
            return
        
        print("\n" + "="*80)
        print("FORECLOSURE AUCTIONS - ALL SOURCES COMBINED")
        print("="*80)
        print(f"Total Found: {len(self.properties)}")
        print(f"Sources Tried: {len(self.sources_tried)}")
        print(f"Showing: {min(limit, len(self.properties))}")
        print("="*80)
        
        # Group by source type
        by_source_type = {}
        for prop in self.properties[:limit]:
            source_type = prop.get('source_type', 'unknown')
            if source_type not in by_source_type:
                by_source_type[source_type] = []
            by_source_type[source_type].append(prop)
        
        print(f"\nProperties by Source Type:")
        for source_type, props in by_source_type.items():
            print(f"  {source_type}: {len(props)}")
        
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
            print(f"Type:        {prop.get('source_type', 'N/A')}")
            print(f"Quality:     {prop.get('quality', 'N/A')}")
            
            if prop.get('url'):
                print(f"Link:        {prop.get('url')}")
    
    def save_results(self, filename: str = "comprehensive_foreclosure_data.json"):
        """Save to JSON."""
        output = {
            'search_date': datetime.now().isoformat(),
            'total_properties': len(self.properties),
            'sources_tried': self.sources_tried,
            'total_sources': len(self.sources_tried),
            'properties': self.properties,
            'data_sources': 'ALL FREE SOURCES: Government + Official + Comprehensive + General',
            'verification_note': 'Data from multiple free sources - verify with official sources before bidding'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SAVED] Results saved to: {filename}")
        print(f"[INFO] Tried {len(self.sources_tried)} different sources")


def main():
    """Main function."""
    scraper = ComprehensiveForeclosureScraper()
    counties = ['DuPage', 'Cook', 'Lake', 'Will', 'Kane']
    properties = scraper.get_all_comprehensive_sources(counties)
    scraper.display_results(limit=100)
    scraper.save_results()
    
    print("\n" + "="*80)
    print("[COMPLETE]")
    print("="*80)
    print(f"\nTried {len(scraper.sources_tried)} different free sources")
    print("\nFor BEST results, visit government sources directly:")
    print("  • Fannie Mae: https://www.homenext.com")
    print("  • Freddie Mac: https://www.homesteps.com")
    print("  • HUD: https://www.hudhomestore.com")
    print("  • VA: https://www.benefits.va.gov/homeloans/purchaseco_foreclosed.asp")
    print("  • USDA: https://www.resales.usda.gov")
    print("="*80)


if __name__ == "__main__":
    main()

