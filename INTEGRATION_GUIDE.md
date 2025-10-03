# 🚀 BizGenie AI - FastAPI Backend Integration Guide

## Overview

Your frontend is now fully integrated with the Research Agent FastAPI backend! Users can ask business questions and receive comprehensive AI-powered market research.

---

## 📋 Quick Start Guide

### **Step 1: Start the Backend Server**

Navigate to the Research Agent Backend folder and start the FastAPI server:

```powershell
cd "Research Agent Backend"

# Activate virtual environment (if not already activated)
.\my_env\Scripts\Activate.ps1

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

**Backend will run on:** `http://localhost:8000`

**Verify backend is running:**

- Open browser: `http://localhost:8000` (should show API welcome page)
- Health check: `http://localhost:8000/health`

---

### **Step 2: Start the Frontend**

In a **new terminal**, navigate to your project root:

```powershell
# Install dependencies (if not done)
npm install

# Start the Next.js development server
npm run dev
```

**Frontend will run on:** `http://localhost:3000`

---

### **Step 3: Test the Integration**

1. **Open your browser:** `http://localhost:3000/root`
2. **Try these example queries:**
   - "coffee shop in Mumbai"
   - "pharmacy in Pune"
   - "bakery in Delhi"
3. **Watch the magic happen!** The AI will:
   - Analyze your query
   - Fetch real-time market data from Google Maps & Trends
   - Display comprehensive research with:
     - Market overview
     - Competitor analysis
     - Key insights
     - Top competitors with ratings

---

## 📁 Files Created/Modified

### **New Files:**

1. **`src/services/api.js`** - API service layer

   - Handles all HTTP requests to FastAPI backend
   - Parses user queries intelligently
   - Error handling and retry logic

2. **`.env.local`** - Environment configuration
   - Stores backend API URL
   - Easy to update for production deployment

### **Modified Files:**

1. **`src/app/root/page.jsx`** - Main chat interface
   - Added state management for messages
   - Integrated API calls with loading states
   - Beautiful UI for displaying research data

---

## 🔧 How It Works

### **User Flow:**

```
User Input → Parse Query → FastAPI Request → AI Processing → Display Results
```

### **Technical Flow:**

1. **User types query** (e.g., "coffee shop in Mumbai")
2. **`parseUserQuery()`** extracts:
   - Business Type: "coffee shop"
   - Location: "Mumbai"
3. **`getComprehensiveResearch()`** calls FastAPI endpoint:
   ```
   GET /api/comprehensive-research?business_type=coffee%20shop&location=Mumbai
   ```
4. **Backend processes:**
   - Google Maps data scraping (SearchAPI)
   - Google Trends analysis
   - AI agents generate insights
   - Competitor analysis
5. **Frontend receives structured JSON:**
   ```json
   {
     "metadata": {...},
     "structured_analysis": {...},
     "competitor_analysis": {...},
     "comprehensive_analysis": {...}
   }
   ```
6. **UI renders beautiful cards** with:
   - Market overview
   - Competitor metrics
   - Top competitors
   - Key insights

---

## 🎨 Features Implemented

### ✅ **Smart Query Parsing**

- Automatically detects business type and location
- Supports 20+ Indian cities
- Asks for clarification if needed

### ✅ **Real-time Chat Interface**

- Message history with user/assistant distinction
- Typing indicators during processing
- Smooth auto-scrolling

### ✅ **Comprehensive Data Display**

- **Market Overview Card** - Industry insights
- **Competitor Analysis Card** - Metrics & top competitors
- **Key Insights Card** - AI-generated recommendations

### ✅ **Error Handling**

- Network error detection
- Backend connection issues
- User-friendly error messages

### ✅ **Loading States**

- Animated typing indicators
- Disabled inputs during processing
- Spinning loader on send button

### ✅ **Responsive Design**

- Mobile-friendly layout
- Clean, minimal UI with blue theme
- Smooth animations

---

## 🔌 Available API Endpoints

### **1. Comprehensive Research** (Main Endpoint)

```javascript
getComprehensiveResearch(businessType, location, options);
```

**Example:**

```javascript
const data = await getComprehensiveResearch("coffee shop", "Mumbai", {
  includeRawData: false,
  useCache: true,
});
```

### **2. City Opportunities**

```javascript
getCityOpportunities(city, options);
```

**Example:**

```javascript
const data = await getCityOpportunities("Mumbai", {
  includeAnalysis: true,
  maxOpportunities: 5,
});
```

### **3. Raw Scraped Data**

```javascript
getRawScrapedData(businessType, location);
```

**Example:**

```javascript
const data = await getRawScrapedData("pharmacy", "Pune");
```

---

## 🐛 Troubleshooting

### **Issue: "Unable to connect to the backend server"**

**Solution:**

1. Verify backend is running: `http://localhost:8000`
2. Check `.env.local` has correct URL
3. Restart both servers

### **Issue: CORS Errors**

**Solution:**

- Backend already has CORS configured in `main.py`
- Verify both servers are on same machine
- Check firewall settings

### **Issue: Slow Responses**

**Solution:**

- First request takes longer (no cache)
- Subsequent requests use cache (faster)
- Check your internet connection (API fetches real-time data)

### **Issue: Empty Results**

**Solution:**

- Try different business types/locations
- Some locations may have limited data
- Check backend logs for API rate limits

---

## 🎯 Example Queries That Work Great

✅ **Good Queries:**

- "coffee shop in Mumbai"
- "pharmacy in Pune"
- "bakery in Delhi"
- "salon in Bangalore"
- "restaurant in Chennai"

❌ **Queries That Need Improvement:**

- "coffee" (missing location)
- "Mumbai" (missing business type)
- "tell me about coffee shops" (unclear location)

**Tip:** Always include both business type AND location for best results!

---

## 🚀 Next Steps & Enhancements

### **Phase 1: Completed ✅**

- [x] API service layer
- [x] Chat interface
- [x] Data display components
- [x] Error handling
- [x] Loading states

### **Phase 2: Future Enhancements 🔜**

- [ ] Chat history persistence (save conversations)
- [ ] Export reports as PDF
- [ ] Advanced filters (price range, ratings)
- [ ] Map visualization of competitors
- [ ] Multi-language support
- [ ] Voice input integration

---

## 📚 Code Examples

### **Calling the API Directly:**

```javascript
import { getComprehensiveResearch } from "@/services/api";

async function analyzeMarket() {
  try {
    const result = await getComprehensiveResearch("coffee shop", "Mumbai", {
      useCache: true,
    });

    console.log(
      "Total Competitors:",
      result.competitor_analysis.total_competitors
    );
    console.log("Average Rating:", result.competitor_analysis.average_rating);
  } catch (error) {
    console.error("Error:", error.message);
  }
}
```

### **Parsing User Queries:**

```javascript
import { parseUserQuery } from "@/services/api";

const parsed = parseUserQuery("coffee shop in Mumbai");
// Returns: { businessType: "coffee shop", location: "Mumbai", needsClarification: false }

const parsed2 = parseUserQuery("just coffee");
// Returns: { businessType: "just coffee", location: null, needsClarification: true }
```

---

## 📞 Support & Resources

### **Backend Documentation:**

- FastAPI Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### **Frontend:**

- Next.js Docs: https://nextjs.org/docs
- React Hooks: https://react.dev/reference/react

### **Key Dependencies:**

- **Backend:** FastAPI, LangChain, SearchAPI, OpenAI
- **Frontend:** Next.js 15, React 19, TailwindCSS

---

## 🎉 Success!

Your BizGenie AI is now fully integrated and ready to provide powerful market intelligence! Try asking it about different businesses across Indian cities and watch it analyze comprehensive market data in real-time.

**Happy Building! 🚀**

---

## 📝 Quick Reference

### **Start Backend:**

```powershell
cd "Research Agent Backend"
.\my_env\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

### **Start Frontend:**

```powershell
npm run dev
```

### **Environment Variables:**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Test URL:**

```
http://localhost:3000/root
```

---

**Created with ❤️ for BizGenie AI**
