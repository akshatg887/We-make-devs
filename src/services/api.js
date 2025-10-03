/**
 * API Service Layer for FastAPI Backend Communication
 * Handles all HTTP requests to the Research Agent Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail ||
          `API Error: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      throw new Error(
        "Unable to connect to the backend server. Please ensure the server is running."
      );
    }
    throw error;
  }
}

/**
 * Get comprehensive business research
 * @param {string} businessType - Type of business (e.g., "coffee shop", "pharmacy")
 * @param {string} location - City location (e.g., "Mumbai", "Pune")
 * @param {object} options - Additional options
 * @returns {Promise<object>} Comprehensive research data
 */
export async function getComprehensiveResearch(
  businessType,
  location,
  options = {}
) {
  const params = new URLSearchParams({
    business_type: businessType,
    location: location,
    include_raw_data: options.includeRawData || false,
    use_cache: options.useCache !== undefined ? options.useCache : true,
  });

  return await apiFetch(`/api/comprehensive-research?${params}`);
}

/**
 * Get city business opportunities
 * @param {string} city - City name
 * @param {object} options - Additional options
 * @returns {Promise<object>} City opportunities data
 */
export async function getCityOpportunities(city, options = {}) {
  const params = new URLSearchParams({
    city: city,
    include_analysis:
      options.includeAnalysis !== undefined ? options.includeAnalysis : true,
    max_opportunities: options.maxOpportunities || 5,
  });

  return await apiFetch(`/api/city-opportunities?${params}`);
}

/**
 * Get raw scraped data from Google Maps
 * @param {string} businessType - Type of business
 * @param {string} location - City location
 * @returns {Promise<object>} Raw scraped data
 */
export async function getRawScrapedData(businessType, location) {
  const params = new URLSearchParams({
    business_type: businessType,
    location: location,
  });

  return await apiFetch(`/api/raw-scraped-data?${params}`);
}

/**
 * Check backend health status
 * @returns {Promise<object>} Health status
 */
export async function checkHealth() {
  return await apiFetch("/health");
}

/**
 * Parse user query to extract business type and location
 * @param {string} query - User's natural language query
 * @returns {object} Parsed business type and location
 */
export function parseUserQuery(query) {
  const originalQuery = query.trim();
  const lowerQuery = query.toLowerCase().trim();

  // Common Indian cities (for better matching)
  const commonCities = [
    "mumbai",
    "delhi",
    "bangalore",
    "bengaluru",
    "hyderabad",
    "ahmedabad",
    "chennai",
    "kolkata",
    "surat",
    "pune",
    "jaipur",
    "lucknow",
    "kanpur",
    "nagpur",
    "indore",
    "thane",
    "bhopal",
    "visakhapatnam",
    "pimpri",
    "patna",
    "vadodara",
    "nashik",
    "meerut",
    "rajkot",
    "varanasi",
    "srinagar",
    "aurangabad",
    "dhanbad",
    "amritsar",
    "allahabad",
    "gwalior",
    "jabalpur",
    "coimbatore",
    "vijayawada",
    "jodhpur",
    "madurai",
    "raipur",
    "kota",
    "guwahati",
  ];

  let location = null;
  let businessType = null;

  // Pattern 1: "business type in location" (most common)
  const inPattern = /(.+)\s+(?:in|at|near)\s+(.+)/i;
  const inMatch = originalQuery.match(inPattern);

  if (inMatch) {
    businessType = inMatch[1].trim();
    location = inMatch[2].trim();
    // Capitalize first letter of location
    location = location.charAt(0).toUpperCase() + location.slice(1);
  } else {
    // Pattern 2: Try to find a known city in the query
    for (const city of commonCities) {
      if (lowerQuery.includes(city)) {
        location = city.charAt(0).toUpperCase() + city.slice(1);
        // Extract business type as everything before the city name
        const cityIndex = lowerQuery.indexOf(city);
        businessType = originalQuery.substring(0, cityIndex).trim();
        break;
      }
    }
  }

  // Clean up business type
  if (businessType) {
    businessType = businessType
      .replace(
        /^(open|start|opening|starting|find|search|looking for|look for|tell me about|show me)\s+/i,
        ""
      )
      .replace(/\s+(in|at|near)\s*$/i, "")
      .replace(/^(a|an|the)\s+/i, "")
      .trim();
  }

  // Clean up location
  if (location) {
    location = location.replace(/^(in|at|near)\s+/i, "").trim();
    // Capitalize each word in location (for multi-word cities)
    location = location
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(" ");
  }

  return {
    businessType: businessType || null,
    location: location || null,
    needsClarification: !businessType || !location,
  };
}
