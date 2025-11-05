# 🆓 FREE Access to DuPage County Foreclosure Data

## ✅ BEST METHOD: FOIA Request (FREE & LEGAL)

**Submit FOIA request to DuPage County Sheriff's Office**

📞 **Contact**: (630) 407-2000  
📍 **Address**: 501 N. County Farm Road, Wheaton, IL 60187  
📄 **Request**: Foreclosure sale listings in CSV/Excel format  
💰 **Cost**: FREE  

**Why FOIA is Best:**
- Completely legal and free
- Can request machine-readable format (CSV, Excel, JSON)
- Can request regular updates
- Official data source

**Template**: See `foia_request_template.txt`

---

## 🔧 FREE PROGRAMMATIC SOURCES

### 1. DuPage County GIS ArcGIS REST API ⭐ **FREE API**

**URL**: `https://gis.dupageco.org/arcgis/rest/services`

**Endpoints:**
- Parcel Search: `https://gis.dupageco.org/arcgis/rest/services/ParcelSearch/DuPageAssessmentParcelSearch/MapServer/3/query`
- Parcels with Real Estate: `https://gis.dupageco.org/arcgis/rest/services/DuPage_County_IL/ParcelsWithRealEstateCC/FeatureServer/0`

**Python Example:**
```python
import requests

url = "https://gis.dupageco.org/arcgis/rest/services/ParcelSearch/DuPageAssessmentParcelSearch/MapServer/3/query"
params = {
    "where": "1=1",
    "outFields": "*",
    "f": "json"
}
response = requests.get(url, params=params)
data = response.json()
```

**Note**: Gives parcel data - need to cross-reference with foreclosure records

---

### 2. DuPage County Recorder's Office

**URL**: `https://www.dupagecounty.gov/elected_officials/recorder/search_records_online.php`

**Search for**: Document type "Foreclosure" or "Notice of Sale"

**Method**: Web scraping (check terms of service first)

---

### 3. DuPage County Circuit Clerk

**URL**: `https://www.dupagecounty.gov/elected_officials/circuit_clerk/`

**Ask**: API access or bulk data download for foreclosure cases  
**Phone**: (630) 407-8700

---

### 4. Property Records Search

**URL**: `https://propertylookup.dupagecounty.gov`

**Use**: Individual property lookups (not bulk foreclosure listings)

---

## 📋 RECOMMENDED ACTION PLAN

### Step 1: FOIA Request (Do This First!)
1. Call (630) 407-2000
2. Ask for FOIA procedures
3. Submit request for foreclosure sale listings
4. Request CSV/Excel format
5. Ask about regular updates

### Step 2: Use GIS API
1. Query parcel data
2. Cross-reference with foreclosure records
3. Build data extraction script

### Step 3: Search Recorder's Office
1. Search for foreclosure documents
2. Extract property info
3. Combine with other sources

---

## 🚫 WHAT NOT TO USE

❌ **ILFLS.com** - Charges $39/month  
❌ **Intercounty Judicial Sales** - For Cook County, not DuPage  
❌ **Paid services** - You don't need them!

---

## 📚 DOCUMENTATION

- **Full Guide**: `dupage_foreclosure_free_access_guide.md`
- **FOIA Template**: `foia_request_template.txt`
- **Python Script**: `dupage_foreclosure_free_access.py`

---

**Goal**: Access foreclosure data FREE without paying $39/month to ILFLS ✅

