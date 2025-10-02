# tools/searchapi_client.py
import requests
import csv
import json
from typing import List, Dict, Any
import os
from datetime import datetime, timedelta
import random
from config.settings import settings
import time

class SearchAPIClient:
    def __init__(self):
        self.api_key = settings.SEARCHAPI_API_KEY
        self.base_url = "https://www.searchapi.io/api/v1/search"
        self.api_available = bool(self.api_key and self.api_key != "demo_key")
        
        if self.api_available:
            print("✅ SearchAPI client initialized")
        else:
            print("❌ SearchAPI client not available - using mock data")
    
    def search_google_maps(self, query: str, location: str = "", max_results: int = 20) -> List[Dict[str, Any]]:
        """Search Google Maps for businesses using SearchAPI"""
        if not self.api_available:
            print("🔄 Using mock Google Maps data")
            return self._generate_mock_places_data([query], location)
        
        try:
            print(f"📍 Searching Google Maps for: {query} in {location}")
            
            params = {
                "engine": "google_maps",
                "q": query,
                "api_key": self.api_key,
                "type": "search",
                "hl": "en"
            }
            
            if location:
                params["location"] = location
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            places_data = self._process_google_maps_data(data.get("local_results", []))
            
            print(f"✅ Found {len(places_data)} places from Google Maps")
            return places_data
            
        except Exception as e:
            print(f"❌ Google Maps search failed: {e}")
            print("🔄 Falling back to mock data...")
            return self._generate_mock_places_data([query], location)
    
    def search_google_trends(self, keyword: str, location: str = "IN", timeframe: str = "today 3-m") -> List[Dict[str, Any]]:
        """Get Google Trends data using SearchAPI"""
        if not self.api_available:
            print("🔄 Using mock Google Trends data")
            return self._generate_mock_trends_data([keyword], location)
        
        try:
            print(f"📈 Getting Google Trends for: {keyword} in {location}")
            
            params = {
                "engine": "google_trends",
                "q": keyword,
                "api_key": self.api_key,
                "data_type": "TIMESERIES",
                "cat": "0",
                "geo": location,
                "date": timeframe
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            trends_data = self._process_google_trends_data(data, keyword)
            
            print(f"✅ Retrieved {len(trends_data)} trends data points")
            return trends_data
            
        except Exception as e:
            print(f"❌ Google Trends search failed: {e}")
            print("🔄 Falling back to mock data...")
            return self._generate_mock_trends_data([keyword], location)
    
    def get_related_searches(self, keyword: str, location: str = "IN") -> List[Dict[str, Any]]:
        """Get related searches and rising queries"""
        if not self.api_available:
            return self._generate_related_searches(keyword)
        
        try:
            params = {
                "engine": "google_trends",
                "q": keyword,
                "api_key": self.api_key,
                "data_type": "RELATED_QUERIES",
                "geo": location
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return self._process_related_searches(data)
            
        except Exception as e:
            print(f"❌ Related searches failed: {e}")
            return self._generate_related_searches(keyword)
    
    def _process_google_maps_data(self, local_results: List[Dict]) -> List[Dict[str, Any]]:
        """Process Google Maps API response"""
        processed_data = []
        
        for place in local_results:
            processed_place = {
                "name": place.get("title", ""),
                "address": place.get("address", ""),
                "rating": place.get("rating", 0),
                "reviews": place.get("reviews", 0),
                "type": place.get("type", ""),
                "phone": place.get("phone", ""),
                "website": place.get("website", ""),
                "description": place.get("description", ""),
                "hours": place.get("hours", ""),
                "price_level": self._parse_price_level(place.get("price", "")),
                "latitude": place.get("gps_coordinates", {}).get("latitude", 0),
                "longitude": place.get("gps_coordinates", {}).get("longitude", 0),
                "position": place.get("position", 0),
                "thumbnail": place.get("thumbnail", "")
            }
            
            if processed_place["name"]:
                processed_data.append(processed_place)
        
        return processed_data
    
    # In searchapi_client.py, update the _process_google_trends_data method:

    def _process_google_trends_data(self, trends_data: Dict, keyword: str) -> List[Dict[str, Any]]:
        """Process Google Trends API response"""
        processed_data = []
        
        # Handle different response formats from SearchAPI
        timeline_data = trends_data.get("interest_over_time", {}).get("timeline_data", [])
        
        for point in timeline_data:
            # Extract value safely - handle different data types
            raw_value = point.get("values", [{}])[0].get("value", 0)
            
            # Convert to integer if it's a string
            if isinstance(raw_value, str):
                try:
                    value = int(float(raw_value))
                except (ValueError, TypeError):
                    value = 0
            else:
                value = int(raw_value) if raw_value else 0
            
            processed_point = {
                "date": point.get("date", ""),
                "value": value,  # Now guaranteed to be int
                "query": keyword,
                "formatted_value": point.get("values", [{}])[0].get("query", ""),
                "has_data": True
            }
            processed_data.append(processed_point)
        
        return processed_data

    def _process_related_searches(self, trends_data: Dict) -> List[Dict[str, Any]]:
        """Process related searches data"""
        related_queries = []
        
        rising_queries = trends_data.get("related_queries", {}).get("rising", [])
        top_queries = trends_data.get("related_queries", {}).get("top", [])
        
        for query in rising_queries[:10]:
            related_queries.append({
                "query": query.get("query", ""),
                "value": query.get("value", 0),
                "type": "rising"
            })
        
        for query in top_queries[:10]:
            related_queries.append({
                "query": query.get("query", ""),
                "value": query.get("value", 0),
                "type": "top"
            })
        
        return related_queries
    
    def _parse_price_level(self, price_str: str) -> int:
        """Parse price level from string to integer"""
        if not price_str:
            return 0
        
        price_mapping = {
            "€": 1, "€€": 2, "€€€": 3, "€€€€": 4,
            "$": 1, "$$": 2, "$$$": 3, "$$$$": 4,
            "₹": 1, "₹₹": 2, "₹₹₹": 3, "₹₹₹₹": 4,
            "💲": 1, "💲💲": 2, "💲💲💲": 3, "💲💲💲💲": 4
        }
        
        return price_mapping.get(price_str.strip(), 0)
    
    # Mock data generators (fallback when API is unavailable)
    def _generate_mock_places_data(self, search_queries: List[str], location: str = "") -> List[Dict[str, Any]]:
        """Generate realistic mock Google Maps data"""
        print(f"🎭 Generating realistic mock Google Maps data for {location}...")
        
        business_type = self._extract_business_type(search_queries)
        business_names = self._get_business_names(business_type)
        addresses = self._get_sample_addresses(location)
        
        mock_data = []
        num_businesses = random.randint(15, 25)
        
        # Get location coordinates
        location_coords = self._get_location_coordinates(location)
        base_lat = location_coords["latitude"]
        base_lon = location_coords["longitude"]
        
        for i in range(num_businesses):
            rating = random.normalvariate(4.2, 0.3)
            rating = max(3.0, min(5.0, round(rating, 1)))
            
            place = {
                "name": f"{random.choice(business_names)} {i+1}",
                "address": random.choice(addresses),
                "rating": rating,
                "reviews": int(random.normalvariate(150, 80)),
                "type": business_type,
                "phone": f"+91 {random.randint(90000, 99999)}{random.randint(10000, 99999)}",
                "website": f"https://www.{business_type.replace(' ', '').lower()}{i+1}.com",
                "description": f"Professional {business_type} services in {location}",
                "hours": "9:00 AM - 6:00 PM",
                "price_level": random.randint(1, 4),
                "latitude": base_lat + random.uniform(-0.08, 0.08),
                "longitude": base_lon + random.uniform(-0.08, 0.08),
                "position": i + 1,
                "thumbnail": f"https://example.com/thumb_{i+1}.jpg"
            }
            
            # Adjust based on business type
            if "tax" in business_type.lower() or "consultant" in business_type.lower():
                place["rating"] = random.normalvariate(4.4, 0.2)
                place["reviews"] = int(random.normalvariate(200, 100))
                place["price_level"] = random.choice([2, 3, 4])
            elif "hotel" in business_type.lower() or "luxury" in business_type.lower():
                place["rating"] = random.normalvariate(4.1, 0.4)
                place["reviews"] = int(random.normalvariate(300, 200))
                place["price_level"] = random.choice([3, 4])
            
            mock_data.append(place)
        
        print(f"📍 Generated {len(mock_data)} realistic mock places for {business_type} in {location}")
        return mock_data
    
    def _generate_mock_trends_data(self, keywords: List[str], location: str) -> List[Dict[str, Any]]:
        """Generate realistic mock Google Trends data"""
        print("🎭 Generating realistic mock Google Trends data...")
        
        from datetime import datetime, timedelta
        
        mock_data = []
        base_date = datetime.now() - timedelta(days=90)
        business_type = self._extract_business_type(keywords)
        
        # Simulate realistic trend patterns
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
                "formatted_value": f"{interest}",
                "has_data": True
            }
            
            mock_data.append(trend_point)
        
        print(f"📈 Generated {len(mock_data)} realistic mock trends for {business_type} in {location}")
        return mock_data
    
    def _generate_related_searches(self, keyword: str) -> List[Dict[str, Any]]:
        """Generate mock related searches"""
        related_queries = [
            {"query": f"{keyword} near me", "value": 95, "type": "top"},
            {"query": f"best {keyword} services", "value": 85, "type": "top"},
            {"query": f"affordable {keyword}", "value": 78, "type": "top"},
            {"query": f"{keyword} prices", "value": 72, "type": "top"},
            {"query": f"professional {keyword}", "value": 65, "type": "top"},
            {"query": f"new {keyword} trends", "value": 45, "type": "rising"},
            {"query": f"{keyword} online booking", "value": 38, "type": "rising"},
            {"query": f"premium {keyword} services", "value": 32, "type": "rising"}
        ]
        
        return related_queries
    
    def _extract_business_type(self, search_queries: List[str]) -> str:
        """Extract business type from search queries"""
        if not search_queries:
            return "business"
        
        first_query = search_queries[0].lower()
        
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
            'fitness': 'gym'
        }
        
        for key, business_type in business_types.items():
            if key in first_query:
                return business_type
        
        words = first_query.split()
        return ' '.join(words[:2]) if len(words) > 1 else words[0] if words else "business"
    
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
    
    def _get_location_coordinates(self, location: str) -> Dict[str, float]:
        """Get coordinates for location"""
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
                return coords
        
        return {"latitude": 18.5204, "longitude": 73.8567}  # Default to Pune
    
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