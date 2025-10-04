# CSV Agent Integration Guide

## Overview

The CSV Agent has been successfully integrated with the BizGenie AI application. Users can now upload CSV files and receive AI-powered insights, anomaly detection, chart recommendations, and actionable recommendations.

## Architecture

### Backend (csv-agent/)

- **Port**: 8001 (configurable via NEXT_PUBLIC_CSV_API_URL)
- **Framework**: FastAPI
- **AI Model**: Cerebras Qwen-3-235b
- **Files**:
  - `app_analyze.py` - Main FastAPI server
  - `cerebras_csv_insights.py` - CSV analysis logic
  - `requirements.txt` - Python dependencies

### Frontend (src/app/root/page.jsx)

- **Features**:
  - File upload button with CSV validation
  - Attached file preview with remove option
  - Session-based follow-up questions
  - Beautiful UI for displaying insights, anomalies, charts, and recommendations

### API Layer (src/services/api.js)

- **Functions**:
  - `uploadCSV(file)` - Upload CSV and get analysis
  - `chatWithCSV(sessionId, userMessage)` - Ask follow-up questions

## Setup Instructions

### 1. Install CSV Agent Dependencies

```bash
cd csv-agent
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `csv-agent/` directory:

```env
CEREBRAS_API_KEY=your_cerebras_api_key_here
CEREBRAS_MODEL=qwen-3-235b-a22b-instruct-2507
```

### 3. Start the CSV Agent Backend

```bash
cd csv-agent
uvicorn app_analyze:app --reload --port 8001
```

The CSV agent will be available at `http://localhost:8001`

### 4. Start the Main Backend

```bash
cd "Research Agent Backend"
# Activate your environment and run
uvicorn app:app --reload --port 8000
```

### 5. Start the Frontend

```bash
# In the root directory
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### Upload and Analyze CSV

1. Click the paperclip icon (📎) in the input area or the "Upload CSV for Analysis" button on the welcome screen
2. Select a CSV file from your computer
3. Optionally add a message or question
4. Click "Send" to upload and analyze

### Features Provided

**Initial Analysis Returns:**

- **Insights**: Top 3-5 key findings from the data
- **Anomalies**: Detected data quality issues or outliers
- **Chart Recommendations**: Suggested visualizations with column mappings
- **Recommendations**: Actionable suggestions based on the data

**Follow-up Questions:**

- After uploading a CSV, you can ask follow-up questions
- The session is maintained using a session_id
- Ask questions like:
  - "What are the top 5 products by revenue?"
  - "Show me trends over time"
  - "Are there any correlations in this data?"
  - "Give me more recommendations"

### Example Workflow

```
User: [Uploads sample_sales.csv] "Analyze this sales data"
AI: [Returns insights, anomalies, charts, recommendations]

User: "What products are performing best?"
AI: [Analyzes the CSV session and provides detailed answer]

User: "Give me more insights about seasonal trends"
AI: [Provides follow-up analysis]
```

## API Endpoints

### CSV Agent (Port 8001)

#### POST /upload_csv

Upload a CSV file and receive initial analysis.

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body: `file` (CSV file)

**Response:**

```json
{
  "session_id": "uuid-here",
  "insights": ["insight 1", "insight 2", ...],
  "anomalies": ["anomaly 1", "anomaly 2", ...],
  "charts": [
    {
      "type": "line",
      "x": "date",
      "y": "sales",
      "title": "Sales Over Time"
    }
  ],
  "recommendations": ["recommendation 1", ...],
  "raw_model_output": "..."
}
```

#### POST /chat

Ask follow-up questions about an uploaded CSV.

**Request:**

- Method: POST
- Content-Type: application/x-www-form-urlencoded
- Body:
  - `session_id`: Session ID from upload
  - `user_message`: Your question

**Response:**

```json
{
  "response": "Full text response",
  "parsed": {
    "answer": "Detailed explanation",
    "followUp": ["question 1", "question 2", ...]
  }
}
```

#### GET /health

Health check endpoint.

## UI Components

### File Upload Area

- Paperclip icon button for attaching CSV files
- Only accepts `.csv` files
- Shows file preview with name and size
- Remove button to clear attachment

### Message Display

**User Messages:**

- Shows attached file indicator when CSV is uploaded

**CSV Analysis Response:**

- **Insights Section**: Blue card with bullet points
- **Anomalies Section**: Orange warning card
- **Chart Recommendations**: Grid of chart specs with type/axes info
- **Recommendations**: Green card with actionable items

**Follow-up Responses:**

- Text-based answer
- Follow-up question suggestions as clickable pills

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CSV_API_URL=http://localhost:8001
```

### CSV Agent (.env)

```env
CEREBRAS_API_KEY=your_api_key
CEREBRAS_MODEL=qwen-3-235b-a22b-instruct-2507
```

## Error Handling

- **Invalid file type**: Shows error message "Please select a CSV file"
- **Backend unavailable**: Shows connection error with clear message
- **Parse errors**: Backend returns detailed error messages
- **Session not found**: Returns 404 with "Invalid session_id"

## Customization

### Change CSV API Port

Update in `src/services/api.js`:

```javascript
const CSV_API_BASE_URL =
  process.env.NEXT_PUBLIC_CSV_API_URL || "http://localhost:8001";
```

### Modify Analysis Prompt

Edit prompts in `csv-agent/app_analyze.py`:

- `SYSTEM_PROMPT`: System instructions
- `USER_PROMPT_TEMPLATE`: User query template

### Adjust UI Styling

All CSV-related UI is in `src/app/root/page.jsx`:

- Search for `csvData` to find display components
- Modify Tailwind classes for styling

## Troubleshooting

### CSV Agent Not Responding

1. Check if the server is running: `http://localhost:8001/health`
2. Verify CEREBRAS_API_KEY is set in .env
3. Check console for CORS errors

### File Upload Fails

1. Ensure file is valid CSV format
2. Check file size (default limit: 20000 rows)
3. Verify Content-Type is multipart/form-data

### Session Lost

- Sessions are stored in-memory
- Restarting the CSV agent clears all sessions
- For persistence, implement Redis/DB storage

## Future Enhancements

1. **Chart Rendering**: Display actual charts instead of specs
2. **Data Preview**: Show first few rows of uploaded CSV
3. **Export Results**: Download insights as PDF/JSON
4. **Multiple Files**: Support comparing multiple CSV files
5. **Session Persistence**: Store sessions in database
6. **Advanced Visualizations**: Interactive charts with Plotly/D3.js
7. **Data Transformation**: Allow data cleaning and preprocessing

## Testing

### Manual Testing

1. Use `csv-agent/sample_sales.csv` for testing
2. Upload and verify all sections display correctly
3. Test follow-up questions
4. Verify session persistence across questions

### API Testing (using curl)

```bash
# Upload CSV
curl -X POST "http://localhost:8001/upload_csv" \
  -F "file=@sample_sales.csv"

# Chat
curl -X POST "http://localhost:8001/chat" \
  -d "session_id=your-session-id&user_message=What are the top products?"

# Health check
curl http://localhost:8001/health
```

## Support

For issues or questions:

1. Check logs in FastAPI terminal
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Check browser console for frontend errors

---

**Integration Complete! 🎉**

The CSV agent is now fully integrated with BizGenie AI. Users can seamlessly switch between business research queries and CSV data analysis within the same interface.
