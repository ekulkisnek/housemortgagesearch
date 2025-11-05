# DuPage County Foreclosure Data - FREE Programmatic Access

## 🎯 Goal: Access foreclosure sale data via code without paying $39/month to ILFLS

---

## ✅ BEST FREE METHOD: FOIA Request

### Submit FOIA Request to DuPage County Sheriff's Office

**Why FOIA is Best:**
- ✅ Completely FREE
- ✅ Legitimate and legal
- ✅ Can request data in machine-readable format (CSV, Excel, JSON)
- ✅ Can set up regular requests for ongoing data

**How to Do It:**

1. **Contact DuPage County Sheriff's Office**
   - Phone: (630) 407-2000
   - Address: 501 N. County Farm Road, Wheaton, IL 60187
   - Ask for: FOIA Officer or Public Records Request

2. **Submit FOIA Request**
   - Request: "Foreclosure sale listings" or "Schedule of foreclosure sales"
   - Format: Request data in CSV, Excel, or JSON format
   - Frequency: Ask if you can receive regular updates (weekly/monthly)
   - Cost: FREE for reasonable requests

3. **Sample FOIA Request:**
   ```
   Subject: FOIA Request - Foreclosure Sale Listings
   
   I am requesting the following public records under the Illinois Freedom of 
   Information Act:
   
   - Current schedule of foreclosure sales
   - Property addresses, case numbers, sale dates
   - Any available foreclosure sale listings in CSV or Excel format
   
   If possible, please provide this data in a machine-readable format (CSV, 
   Excel, or JSON) suitable for programmatic access.
   
   Thank you for your assistance.
   ```

4. **Automate Regular Requests**
   - Submit FOIA requests on a regular schedule (weekly/monthly)
   - Some agencies may provide automated data feeds if requested
   - Build a script to process the received data files

---

## 🔧 FREE PROGRAMMATIC ACCESS METHODS

### Method 1: DuPage County GIS ArcGIS REST API

**URL**: `https://gis.dupageco.org/arcgis/rest/services`

**Available Endpoints:**

1. **Parcel Search**
   - URL: `https://gis.dupageco.org/arcgis/rest/services/ParcelSearch/DuPageAssessmentParcelSearch/MapServer`
   - Provides: Parcel data with assessment information
   - Query endpoint: `/MapServer/3/query`

2. **Parcels with Real Estate Data**
   - URL: `https://gis.dupageco.org/arcgis/rest/services/DuPage_County_IL/ParcelsWithRealEstateCC/FeatureServer/0`
   - Provides: Comprehensive parcel and real estate data

**Python Example:**
```python
import requests

# Query all parcels (or use specific criteria)
gis_url = "https://gis.dupageco.org/arcgis/rest/services/ParcelSearch/DuPageAssessmentParcelSearch/MapServer/3/query"

params = {
    "where": "1=1",  # Get all parcels, or filter: "ASSESSED_VALUE > 100000"
    "outFields": "*",  # Get all fields
    "f": "json",
    "returnGeometry": "false"  # Don't need geometry for data analysis
}

response = requests.get(gis_url, params=params)
parcel_data = response.json()

# Process parcel data
if 'features' in parcel_data:
    for feature in parcel_data['features']:
        attributes = feature.get('attributes', {})
        print(f"Parcel: {attributes.get('PIN', 'N/A')}")
        print(f"Address: {attributes.get('ADDRESS', 'N/A')}")
```

**Note:** This gives you parcel data, but you'll need to cross-reference with foreclosure records.

---

### Method 2: DuPage County Recorder's Office Search

**URL**: `https://www.dupagecounty.gov/elected_officials/recorder/search_records_online.php`

**What to Search For:**
- Document Type: "Foreclosure" or "Notice of Sale"
- Date Range: Recent dates for current foreclosures
- Extract: Property addresses, case numbers, sale dates

**Web Scraping Approach:**
```python
import requests
from bs4 import BeautifulSoup

# Note: Check website's terms of service before scraping
# Implement rate limiting and respectful access

recorder_url = "https://www.dupagecounty.gov/elected_officials/recorder/search_records_online.php"

# You'll need to:
# 1. Navigate to search interface
# 2. Submit search form with document type "Foreclosure"
# 3. Parse results page
# 4. Extract property information

# Example structure (adjust based on actual website):
session = requests.Session()

# Get search page
search_page = session.get(recorder_url)

# Submit search form (adjust parameters based on actual form)
search_data = {
    'document_type': 'Foreclosure',
    'date_from': '2024-01-01',
    'date_to': '2025-12-31'
}

results = session.post(recorder_url, data=search_data)
# Parse results...
```

**Important:** 
- Check robots.txt and terms of service
- Implement rate limiting (don't overload their servers)
- Respectful scraping practices

---

### Method 3: DuPage County Circuit Clerk - Court Records

**URL**: `https://www.dupagecounty.gov/elected_officials/circuit_clerk/`

**What to Access:**
- Chancery Division cases (foreclosure cases are filed here)
- Case type: Foreclosure
- Extract: Case numbers, parties, sale dates

**Contact for API Access:**
- Phone: (630) 407-8700
- Ask: "Do you provide API access or bulk data downloads for foreclosure cases?"

**If API Available:**
```python
# Example if API becomes available
api_url = "https://api.dupagecounty.gov/circuit_clerk/cases"
params = {
    "division": "Chancery",
    "case_type": "Foreclosure",
    "format": "json"
}
response = requests.get(api_url, params=params)
foreclosure_cases = response.json()
```

---

### Method 4: DuPage County Property Records Search

**URL**: `https://propertylookup.dupagecounty.gov`

**Use Case:**
- Search properties by address or PIN
- Check for foreclosure-related information
- Cross-reference with other data sources

**Note:** This is more for individual property lookups rather than bulk foreclosure listings.

---

## 🔄 COMBINED APPROACH STRATEGY

### Recommended Workflow:

1. **Start with FOIA Request** (Best option)
   - Get official foreclosure sale listings
   - Request regular updates
   - Build automation around received data

2. **Use GIS API for Parcel Data**
   - Get all parcels or recent sales
   - Cross-reference with foreclosure records

3. **Search Recorder's Office**
   - Find foreclosure documents
   - Extract property addresses and case numbers
   - Match with GIS parcel data

4. **Monitor Court Records** (if accessible)
   - Track new foreclosure cases
   - Get sale dates from court orders

---

## 📋 CODE TEMPLATE: Complete Solution

```python
"""
DuPage County Foreclosure Data - Free Access
Combines multiple free sources
"""

import requests
import json
from datetime import datetime, timedelta
import time

class DuPageForeclosureFreeAccess:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_parcels_from_gis(self, limit=1000):
        """Get parcel data from GIS API."""
        url = "https://gis.dupageco.org/arcgis/rest/services/ParcelSearch/DuPageAssessmentParcelSearch/MapServer/3/query"
        
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "returnGeometry": "false",
            "resultRecordCount": limit
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting GIS data: {e}")
        
        return None
    
    def search_recorder_for_foreclosures(self, date_from, date_to):
        """Search Recorder's Office for foreclosure documents."""
        # Note: This requires understanding the actual search form structure
        # You'll need to inspect the website and adjust accordingly
        
        recorder_url = "https://www.dupagecounty.gov/elected_officials/recorder/search_records_online.php"
        
        # This is a template - adjust based on actual website structure
        # You may need to use Selenium for JavaScript-heavy sites
        pass
    
    def submit_foia_request(self):
        """Template for FOIA request submission."""
        foia_info = {
            'office': 'DuPage County Sheriff\'s Office',
            'phone': '(630) 407-2000',
            'email': 'Contact via phone for FOIA procedures',
            'request': 'Foreclosure sale listings in CSV/Excel format'
        }
        
        print("FOIA Request Template:")
        print(json.dumps(foia_info, indent=2))
        
        return foia_info
    
    def combine_data_sources(self):
        """Combine data from multiple free sources."""
        results = {
            'parcels': [],
            'foreclosures': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Get parcel data
        parcel_data = self.get_parcels_from_gis(limit=100)
        if parcel_data and 'features' in parcel_data:
            results['parcels'] = [
                feature['attributes'] 
                for feature in parcel_data['features']
            ]
        
        # Search for foreclosures (implement based on available access)
        # results['foreclosures'] = self.search_recorder_for_foreclosures(...)
        
        return results

# Usage
if __name__ == "__main__":
    access = DuPageForeclosureFreeAccess()
    
    # Get FOIA request info
    access.submit_foia_request()
    
    # Get parcel data
    data = access.combine_data_sources()
    
    # Save results
    with open('foreclosure_data.json', 'w') as f:
        json.dump(data, f, indent=2)
```

---

## ⚠️ IMPORTANT CONSIDERATIONS

### Legal and Ethical:
1. **Check Terms of Service** before scraping any website
2. **Respect Rate Limits** - don't overload servers
3. **FOIA is Legal** - use it for legitimate data requests
4. **Robots.txt** - check if scraping is allowed

### Technical:
1. **Rate Limiting** - add delays between requests
2. **Error Handling** - websites may change
3. **Data Validation** - verify data accuracy
4. **Caching** - don't re-fetch unchanged data

### Data Quality:
1. Free sources may not be as comprehensive as paid services
2. May require combining multiple sources
3. Regular updates may require ongoing maintenance
4. FOIA requests ensure official data

---

## 📞 CONTACTS FOR FREE DATA ACCESS

### DuPage County Sheriff's Office (FOIA)
- **Phone**: (630) 407-2000
- **FOIA Request**: Ask for FOIA procedures
- **Request**: Foreclosure sale listings in CSV/Excel format

### DuPage County Circuit Clerk
- **Phone**: (630) 407-8700
- **Ask**: API access or bulk data download for foreclosure cases

### DuPage County Recorder
- **Phone**: (630) 407-5400
- **Ask**: Bulk data access or automated data feeds

---

## 🎯 RECOMMENDED ACTION PLAN

1. **Immediate**: Submit FOIA request to Sheriff's Office
   - Request foreclosure sale listings
   - Request CSV/Excel format
   - Ask about regular updates

2. **Short-term**: Explore GIS API
   - Test parcel data queries
   - Understand data structure
   - Build data extraction script

3. **Medium-term**: Investigate Recorder's Office
   - Check if scraping is allowed
   - Build search automation
   - Extract foreclosure documents

4. **Long-term**: Automate data collection
   - Combine multiple sources
   - Regular FOIA requests
   - Data processing pipeline

---

**Last Updated**: January 2025  
**Goal**: Access foreclosure data without paying $39/month to ILFLS

