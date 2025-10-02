from apify_client import ApifyClient
import csv
import json
from typing import List, Dict, Any
import os
from datetime import datetime
import random
from config.settings import settings
import requests

class ApifyDataCollector:
    def __init__(self):
        try:
            self.client = ApifyClient(settings.APIFY_API_KEY)
            self.api_available = True
            print("✅ Apify client initialized")
        except Exception as e:
            print(f"❌ Apify client failed: {e}")
            self.client = None
            self.api_available = False
    
    def scrape_places_data(self, search_queries: List[str], location: str = "") -> List[Dict[str, Any]]:
        """Scrape Google Places data using compass/crawler-google-places with fallback to mock data"""
        if not self.api_available:
            print("🔄 Using mock places data (API unavailable)")
            return self._generate_mock_places_data(search_queries, location)
        
        try:
            print(f"📍 Starting Google Places scrape for: {search_queries} in {location}")
            
            # Use compass/crawler-google-places as requested
            input_data = {
                "searchStringsArray": search_queries,
                "maxCrawledPlacesPerSearch": 25,
                "language": "en",
                "maxImages": 0,
                "includeReviews": True,
                "includeWebResults": False
            }
            
            # Run the actor
            run = self.client.actor("compass/crawler-google-places").call(run_input=input_data)
            
            # Get results
            dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            # Process and enrich the data with dynamic coordinates
            processed_items = self._process_places_data(dataset_items, location)
            
            print(f"✅ Successfully scraped {len(processed_items)} places from Google")
            
            return processed_items
            
        except Exception as e:
            print(f"❌ Google Places scraping failed: {e}")
            print("🔄 Falling back to mock data...")
            return self._generate_mock_places_data(search_queries, location)
    
    def scrape_trends_data(self, keywords: List[str], location: str) -> List[Dict[str, Any]]:
        """Scrape Google Trends data with improved fallback"""
        if not self.api_available:
            print("🔄 Using mock trends data (API unavailable)")
            return self._generate_mock_trends_data(keywords, location)
        
        try:
            print(f"📈 Starting Google Trends scrape for: {keywords} in {location}")
            
            # Try the most reliable trends actor
            try:
                input_data = {
                    "searchTerms": keywords,
                    "country": self._get_country_code(location),
                    "timeRange": "today 3-m"
                }
                
                run = self.client.actor("apify/google-trends-scraper").call(run_input=input_data)
                dataset_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
                
                if dataset_items:
                    print(f"✅ Successfully scraped {len(dataset_items)} trends data points")
                    return dataset_items
            except Exception as e:
                print(f"❌ Google Trends scraper failed: {e}")
            
            # If main actor fails, use mock data
            raise Exception("Trends scraping not available")
            
        except Exception as e:
            print(f"❌ Google Trends scraping failed: {e}")
            print("🔄 Falling back to mock data...")
            return self._generate_mock_trends_data(keywords, location)
    
    def _get_location_coordinates(self, location: str) -> Dict[str, float]:
        """Dynamically get coordinates for any Indian city/village using Nominatim"""
        try:
            print(f"🗺️ Fetching coordinates for: {location}")
            
            # Use Nominatim OpenStreetMap API for dynamic coordinates
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{location}, India",
                'format': 'json',
                'limit': 1
            }
            
            headers = {
                'User-Agent': 'MarketIntelligenceApp/1.0 (niraj@example.com)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    
                    print(f"✅ Found coordinates for {location}: {lat}, {lon}")
                    
                    # Return a bounding box around the location
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "bounds": {
                            "west": lon - 0.1,
                            "east": lon + 0.1,
                            "north": lat + 0.1,
                            "south": lat - 0.1
                        }
                    }
            
            # Fallback coordinates for major Indian cities
            fallback_coords = {
                "nashik": {"latitude": 20.0, "longitude": 73.78},
                "pune": {"latitude": 18.5204, "longitude": 73.8567},
                "mumbai": {"latitude": 19.0760, "longitude": 72.8777},
                "delhi": {"latitude": 28.6139, "longitude": 77.2090},
                "bangalore": {"latitude": 12.9716, "longitude": 77.5946},
                "hyderabad": {"latitude": 17.3850, "longitude": 78.4867},
                "chennai": {"latitude": 13.0827, "longitude": 80.2707},
                "kolkata": {"latitude": 22.5726, "longitude": 88.3639}
            }
            
            location_lower = location.lower()
            for city, coords in fallback_coords.items():
                if city in location_lower:
                    print(f"📍 Using fallback coordinates for {location}: {coords}")
                    return coords
            
            # Default to Nashik if location not found
            default_coords = {"latitude": 20.0, "longitude": 73.78}
            print(f"📍 Using default coordinates for {location}: {default_coords}")
            return default_coords
            
        except Exception as e:
            print(f"❌ Coordinate fetch failed for {location}: {e}")
            # Return Nashik as default
            return {"latitude": 20.0, "longitude": 73.78}
    
    def _get_country_code(self, location: str) -> str:
        """Get country code for trends API"""
        # For Indian locations, use "IN"
        india_keywords = ["india", "indian", "pune", "mumbai", "delhi", "bangalore", 
                         "chennai", "kolkata", "hyderabad", "nashik", "ahmedabad"]
        
        location_lower = location.lower()
        if any(keyword in location_lower for keyword in india_keywords):
            return "IN"
        
        return "US"  # Default to US
    
    def _process_places_data(self, raw_data: List[Dict], location: str) -> List[Dict[str, Any]]:
        """Process and enrich raw places data with dynamic coordinates"""
        processed_data = []
        
        # Get dynamic coordinates for the location
        location_coords = self._get_location_coordinates(location)
        
        for place in raw_data:
            # Extract relevant fields and ensure data consistency
            processed_place = {
                "name": place.get("title", place.get("name", "")),
                "address": place.get("address", f"Unknown location in {location}"),
                "rating": place.get("rating", 0),
                "user_ratings_total": place.get("reviewsCount", place.get("user_ratings_total", 0)),
                "price_level": self._parse_price_level(place.get("price", "")),
                "types": place.get("category", []),
                "latitude": place.get("location", {}).get("lat", 0),
                "longitude": place.get("location", {}).get("lng", 0),
                "open_now": place.get("isOpen", False),
                "phone_number": place.get("phone", ""),
                "website": place.get("website", ""),
                "description": place.get("description", ""),
                "hours": place.get("hours", "")
            }
            
            # If no coordinates in scraped data, use location coordinates with slight variation
            if not processed_place["latitude"] or not processed_place["longitude"]:
                processed_place["latitude"] = location_coords["latitude"] + random.uniform(-0.05, 0.05)
                processed_place["longitude"] = location_coords["longitude"] + random.uniform(-0.05, 0.05)
            
            # Only include places with valid names
            if processed_place["name"]:
                processed_data.append(processed_place)
        
        return processed_data
    
    def _parse_price_level(self, price_str: str) -> int:
        """Parse price level from string to integer"""
        if not price_str:
            return 0
        
        price_mapping = {
            "€": 1, "€€": 2, "€€€": 3, "€€€€": 4,
            "$": 1, "$$": 2, "$$$": 3, "$$$$": 4,
            "₹": 1, "₹₹": 2, "₹₹₹": 3, "₹₹₹₹": 4
        }
        
        return price_mapping.get(price_str.strip(), 0)
    
    def _generate_mock_places_data(self, search_queries: List[str], location: str = "") -> List[Dict[str, Any]]:
        """Generate realistic mock places data with dynamic coordinates"""
        print(f"🎭 Generating realistic mock places data for {location}...")
        
        # Extract business type from search queries
        business_type = self._extract_business_type(search_queries)
        
        # Get dynamic coordinates for the location
        location_coords = self._get_location_coordinates(location)
        base_lat = location_coords["latitude"]
        base_lon = location_coords["longitude"]
        
        # Dynamic business names based on business type
        business_names = self._get_business_names(business_type)
        addresses = self._get_sample_addresses(location)
        
        mock_data = []
        num_businesses = random.randint(18, 25)
        
        for i in range(num_businesses):
            rating = random.normalvariate(4.2, 0.3)
            rating = max(3.0, min(5.0, round(rating, 1)))
            
            place = {
                "name": f"{random.choice(business_names)} {i+1}",
                "address": random.choice(addresses),
                "rating": rating,
                "user_ratings_total": int(random.normalvariate(150, 80)),
                "price_level": random.randint(1, 4),
                "types": [business_type.replace(' ', '_'), "local_business"],
                "latitude": base_lat + random.uniform(-0.08, 0.08),  # Spread around location
                "longitude": base_lon + random.uniform(-0.08, 0.08),
                "open_now": random.choice([True, False]),
                "phone_number": f"+91 {random.randint(90000, 99999)}{random.randint(10000, 99999)}",
                "website": f"https://www.{business_type.replace(' ', '').lower()}{i+1}.com",
                "description": f"Professional {business_type} services in {location}",
                "hours": "9:00 AM - 6:00 PM"
            }
            
            # Adjust based on rating and business type
            if rating > 4.5:
                place["user_ratings_total"] = int(random.normalvariate(400, 150))
                place["price_level"] = random.choice([3, 4])
            elif rating < 3.5:
                place["user_ratings_total"] = int(random.normalvariate(80, 40))
                place["price_level"] = random.choice([1, 2])
            
            # Special adjustments for different business types
            if "tax" in business_type.lower() or "consultant" in business_type.lower():
                place["rating"] = random.normalvariate(4.4, 0.2)
                place["user_ratings_total"] = int(random.normalvariate(200, 100))
                place["price_level"] = random.choice([2, 3, 4])
            elif "hotel" in business_type.lower() or "luxury" in business_type.lower():
                place["rating"] = random.normalvariate(4.1, 0.4)
                place["user_ratings_total"] = int(random.normalvariate(300, 200))
                place["price_level"] = random.choice([3, 4])
            
            mock_data.append(place)
        
        print(f"📍 Generated {len(mock_data)} realistic mock places for {business_type} in {location}")
        return mock_data
    
    def _extract_business_type(self, search_queries: List[str]) -> str:
        """Extract business type from search queries"""
        if not search_queries:
            return "business"
        
        # Get the first query and extract business type
        first_query = search_queries[0].lower()
        
        # Enhanced business type mappings
        business_types = {
            'tax': 'tax consultant',
            'consultant': 'tax consultant',
            'accountant': 'tax consultant',
            'hotel': 'hotel',
            'luxury': 'luxury hotel',
            'resort': 'hotel',
            'bakery': 'bakery',
            'coffee': 'coffee shop',
            'cafe': 'coffee shop', 
            'restaurant': 'restaurant',
            'salon': 'salon',
            'beauty': 'beauty salon',
            'tech': 'tech startup',
            'startup': 'tech startup',
            'gym': 'gym',
            'fitness': 'gym',
            'doctor': 'medical clinic',
            'clinic': 'medical clinic',
            'lawyer': 'legal services',
            'legal': 'legal services'
        }
        
        for key, business_type in business_types.items():
            if key in first_query:
                return business_type
        
        # Extract from query words
        words = first_query.split()
        if len(words) > 1:
            return ' '.join(words[:2])
        return words[0] if words else "business"
    
    def _get_business_names(self, business_type: str) -> List[str]:
        """Get appropriate business names based on business type"""
        name_templates = {
            'tax consultant': [
                "Tax Solutions", "Financial Advisors", "Tax Experts", "Account Masters",
                "Tax Professionals", "Finance Hub", "Tax Advisory", "Financial Partners"
            ],
            'luxury hotel': [
                "Grand Palace", "Royal Stay", "Luxury Suites", "Premium Residency",
                "Elite Hotels", "Comfort Inn", "Heritage Stay", "Executive Suites"
            ],
            'hotel': [
                "Comfort Stay", "City Inn", "Travel Lodge", "Urban Hotel",
                "Metro Suites", "Gateway Hotel", "Plaza Inn", "City Center Hotel"
            ],
            'bakery': [
                "Fresh Bread", "Sweet Delights", "Artisan Bakes", "Golden Crust",
                "Morning Fresh", "Crust & Crumb", "Oven Fresh", "Daily Bread"
            ],
            'coffee shop': [
                "Brew Haven", "Coffee Corner", "Bean There", "Daily Grind",
                "Cafe Aroma", "Steamy Cups", "Java Junction", "Roast Masters"
            ]
        }
        
        return name_templates.get(business_type, [
            "Elite Services", "Professional Solutions", "Quality Care", "Expert Hub",
            "Premium Services", "Trusted Professionals", "Reliable Services"
        ])
    
    def _get_sample_addresses(self, location: str) -> List[str]:
        """Get sample addresses for specific location"""
        # Generic addresses that work for any Indian city
        return [
            f"123 Main Road, {location}",
            f"456 Central Avenue, {location}", 
            f"789 Market Street, {location}",
            f"321 Downtown Area, {location}",
            f"654 Commercial Complex, {location}",
            f"987 Business District, {location}",
            f"159 City Center, {location}",
            f"753 Shopping Area, {location}"
        ]
    
    def _generate_mock_trends_data(self, keywords: List[str], location: str) -> List[Dict[str, Any]]:
        """Generate realistic mock trends data"""
        print("🎭 Generating realistic mock trends data...")
        
        from datetime import datetime, timedelta
        
        mock_data = []
        base_date = datetime.now() - timedelta(days=90)
        
        # Extract business type from keywords
        business_type = self._extract_business_type(keywords)
        
        # Simulate realistic trend patterns based on business type
        if "tax" in business_type.lower():
            base_interest = random.randint(60, 85)
            trend_direction = "seasonal"
        elif "hotel" in business_type.lower():
            base_interest = random.randint(50, 80)
            trend_direction = "seasonal"
        else:
            base_interest = random.randint(40, 70)
            trend_direction = random.choice(["growing", "stable", "seasonal"])
        
        for week in range(12):
            date = base_date + timedelta(days=week * 7)
            
            if trend_direction == "growing":
                interest = base_interest + (week * 2) + random.randint(-3, 3)
            elif trend_direction == "seasonal":
                seasonal_factor = 10 * abs((week % 6) - 3)
                interest = base_interest + seasonal_factor + random.randint(-4, 4)
            else:
                interest = base_interest + random.randint(-8, 8)
            
            interest = max(15, min(95, interest))
            
            trend_point = {
                "date": date.strftime("%Y-%m-%d"),
                "value": interest,
                "query": business_type,
                "geo": location,
                "isPartial": False,
                "formattedValue": f"{interest}",
                "hasData": True,
                "relatedQueries": [
                    f"{business_type} near me",
                    f"best {business_type} in {location}",
                    f"{business_type} services",
                    f"affordable {business_type}",
                    f"professional {business_type}"
                ]
            }
            
            mock_data.append(trend_point)
        
        print(f"📈 Generated {len(mock_data)} realistic mock trends for {business_type} in {location}")
        return mock_data
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """Save data to CSV"""
        if not data:
            return
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=list(all_keys), extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data)
        
        print(f"💾 Data saved to {filename}")