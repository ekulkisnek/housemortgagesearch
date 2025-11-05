# Cheapest Indiana Lake Michigan Properties Finder

## Overview

This script searches for the cheapest properties in Indiana that are less than 1 mile from Lake Michigan beaches (between Illinois and Michigan border), sorted by price per acre.

## Features

✅ Searches multiple areas in northern Indiana near Lake Michigan  
✅ Calculates distance to nearest beach using coordinates  
✅ Filters properties within specified distance (default: 1 mile)  
✅ Calculates and sorts by price per acre  
✅ Geocodes property addresses  
✅ Saves results to JSON file  

## Usage

### Basic Usage

```bash
python cheap_indiana_beach_properties.py
```

### With Price Filter

```bash
python cheap_indiana_beach_properties.py --max-price 300000
```

### With Custom Distance

```bash
python cheap_indiana_beach_properties.py --max-distance 2.0
```

### Combined Options

```bash
python cheap_indiana_beach_properties.py --max-price 200000 --max-distance 1.5
```

## Target Areas

The script searches these areas in northern Indiana:

- Michigan City, IN
- Portage, IN
- Ogden Dunes, IN
- Burns Harbor, IN
- Gary, IN (includes Miller Beach area)
- Chesterton, IN
- Porter, IN
- Valparaiso, IN
- Dune Acres, IN
- New Buffalo, IN

## Beach Locations Tracked

The script calculates distances to these Lake Michigan beach locations:

- Michigan City
- Portage
- Ogden Dunes
- Burns Harbor
- Dune Acres
- Miller Beach
- West Beach
- Indiana Dunes
- Mount Baldy
- Washington Park

## Output

The script:

1. **Displays results** in the console with:
   - Property address
   - Price
   - Lot size (acres and square feet)
   - Price per acre
   - Distance to nearest beach
   - Property URL
   - Data source

2. **Saves to JSON** file: `cheap_indiana_beach_properties.json` with:
   - All property data
   - Coordinates (latitude/longitude)
   - Distance calculations
   - Search metadata

## Limitations & Notes

⚠️ **Modern real estate websites have strong anti-scraping protection**, so automated scraping may not always work. The script attempts to extract data but may return 0 results.

### Alternative Approaches:

1. **Manual Search URLs**: The script searches these areas, but you can also manually visit:
   - Redfin: https://www.redfin.com/city/...-IN
   - Realtor.com: https://www.realtor.com/realestateandhomes-search/..._in

2. **Use the JSON output**: If you have property data from other sources, you can manually add it to the JSON file and re-run the distance filtering.

3. **County Assessor Websites**: Check these for property listings:
   - Porter County: https://www.portercountyassessor.com/
   - LaPorte County: https://www.laportecounty.org/assessor
   - Lake County: https://www.lakecountyin.org/departments/assessor

## Example Output Format

```
================================================================================
PROPERTY #1
================================================================================
[ADDR] Address:     123 Main St, Michigan City, IN
[PRICE] Price:        $150,000
[LOT] Lot Size:     0.250 acres (10,890 sqft)
[ACRE] Price/Acre:   $600,000/acre
[BEACH] Distance:     0.45 miles to Michigan City
[LINK] Link:         https://www.redfin.com/...
[SOURCE] Source:       Redfin
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

Install with:
```bash
pip install requests beautifulsoup4 lxml
```

## Distance Calculation

The script uses the Haversine formula to calculate great-circle distances between property coordinates and beach locations. This provides accurate distance measurements in miles.

## Data Sources

- Redfin (https://www.redfin.com)
- Realtor.com (https://www.realtor.com)
- Nominatim/OpenStreetMap (for geocoding)

## Tips for Finding Cheap Beach Properties

1. **Expand search area**: Use `--max-distance 2.0` to find properties within 2 miles
2. **Lower price filter**: Try `--max-price 150000` or lower
3. **Check foreclosure listings**: Look for foreclosure auctions in these counties
4. **Mobile homes**: Often cheaper options near beaches
5. **Vacant land**: May be cheapest but requires building
6. **Fixer-uppers**: Properties needing renovation often have lower prices

## Troubleshooting

If no properties are found:

1. Check your internet connection
2. Try removing price filters: `python cheap_indiana_beach_properties.py`
3. Increase distance: `python cheap_indiana_beach_properties.py --max-distance 2.0`
4. Verify the websites are accessible in your browser
5. Check the JSON output file for any partial data

