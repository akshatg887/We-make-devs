# app_analyze.py
import os
import io
import json
import base64
import uuid
import traceback
from typing import Dict, Any, Optional, List
from fastapi.responses import FileResponse
import tempfile
import subprocess
import shutil
from pathlib import Path


from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cerebras SDK
from cerebras.cloud.sdk import Cerebras

from cerebras_csv_insights import summary_to_text

# Load .env
load_dotenv()
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "qwen-3-235b-a22b-instruct-2507")
if not CEREBRAS_API_KEY:
    raise RuntimeError("CEREBRAS_API_KEY not set in environment or .env")

client = Cerebras(api_key=CEREBRAS_API_KEY)

app = FastAPI(title="CSV Chat & Insights (Cerebras)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# In-memory session store: session_id -> {"df": DataFrame, "chat_history": [messages]}
SESSIONS: Dict[str, Dict[str, Any]] = {}

# ---------------- Utilities ----------------

def load_csv_strict(file_bytes: bytes) -> pd.DataFrame:
    """Parse CSV bytes robustly."""
    try:
        return pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        try:
            return pd.read_csv(io.StringIO(file_bytes.decode("utf-8", errors="replace")))
        except Exception as e2:
            raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}; fallback error: {e2}")

def compact_summary(df: pd.DataFrame, max_sample_rows: int = 5) -> Dict[str, Any]:
    """Compact summary for prompting the model."""
    summary: Dict[str, Any] = {}
    summary["n_rows"] = int(len(df))
    summary["columns"] = {col: str(dtype) for col, dtype in df.dtypes.items()}

    numeric = df.select_dtypes(include=[np.number])
    num_stats: Dict[str, Any] = {}
    for c in numeric.columns:
        s = numeric[c].dropna()
        if len(s) == 0:
            continue
        num_stats[c] = {
            "count": int(s.count()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std": float(s.std()) if len(s) > 1 else 0.0,
            "min": float(s.min()),
            "max": float(s.max()),
            "sum": float(s.sum())
        }
    if num_stats:
        summary["numeric_stats"] = num_stats

    cat_stats: Dict[str, Any] = {}
    non_num = df.select_dtypes(exclude=[np.number])
    for c in non_num.columns:
        top = df[c].value_counts(dropna=True).head(5).to_dict()
        cat_stats[c] = top
    if cat_stats:
        summary["categorical_top_values"] = cat_stats

    # detect date-like among non-numeric only
    date_cols: List[str] = []
    for c in non_num.columns:
        try:
            parsed = pd.to_datetime(df[c], errors="coerce", format='mixed')
            if parsed.notna().sum() >= max(1, 0.5 * len(df)):
                date_cols.append(c)
        except Exception:
            pass
    if date_cols:
        summary["date_columns"] = date_cols

    summary["samples"] = df.head(max_sample_rows).to_dict(orient="records")
    return summary

# Balanced-brace JSON extraction to avoid partial arrays/false matches
def find_json_block(text: str) -> Optional[str]:
    text = text.strip()
    n = len(text)
    starts = [i for i, ch in enumerate(text) if ch in "{["]
    for s in starts:
        stack = []
        for i in range(s, n):
            ch = text[i]
            if ch in "{[":
                stack.append(ch)
            elif ch in "}]":
                if not stack:
                    break
                open_ch = stack.pop()
                if (open_ch == "{" and ch != "}") or (open_ch == "[" and ch != "]"):
                    break
                if not stack:
                    candidate = text[s:i+1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except Exception:
                        break
    return None

def extract_json_from_text(text: str) -> Optional[Any]:
    if not text:
        return None
    # try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass
    # balanced-brace search
    block = find_json_block(text)
    if block:
        try:
            return json.loads(block)
        except Exception:
            pass
    # code fence search
    import re
    m = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return None

# ---------------- Prompts ----------------
SYSTEM_PROMPT = (
    "You are a strict, factual data analyst. "
    "Given a CSV dataset summary, return ONLY a JSON object with keys: "
    "\"insights\" (list of short strings), "
    "\"anomalies\" (list of descriptions), "
    "\"charts\" (list of chart specs), "
    "\"recommendations\" (list of short tactical recommendations). "
    "Do NOT include any code, explanations, or commentary outside the JSON."
)


USER_PROMPT_TEMPLATE = (
    "Dataset summary:\n{summary_text}\n\nTask:\n"
    "1) Provide top 3 insights referencing exact column names.\n"
    "2) List anomalies.\n"
    "3) Propose up to 3 charts with exact existing column names (x and y) in JSON 'charts'.\n"
    "4) Give 3 actionable recommendations.\n"

)

# ---------------- Endpoints ----------------

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV, create session, run initial analysis, write and run LLM code as a temp script,
       gather generated chart files, and return chart URLs."""
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        df = load_csv_strict(contents)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

    # create session and store df
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"df": df, "chat_history": []}

    # save uploaded CSV to a temp file (so the temp script can read it)
    tmp_csv = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".csv")
    try:
        tmp_csv.write(contents)
        tmp_csv.flush()
    finally:
        tmp_csv.close()
    SESSIONS[session_id]["csv_path"] = tmp_csv.name

    # prepare summary text for model
    summary = compact_summary(df)
    summary_lines = [f"Rows: {summary['n_rows']}"]
    summary_lines.append("Columns:")
    for c, t in summary["columns"].items():
        summary_lines.append(f"- {c}: {t}")
    if "numeric_stats" in summary:
        for c, s in summary["numeric_stats"].items():
            summary_lines.append(f"- {c}: mean={s['mean']:.2f}, sum={s['sum']:.2f}")
    summary_lines.append("Sample rows:")
    for r in summary["samples"]:
        summary_lines.append(json.dumps(r, ensure_ascii=False))
    summary_text = "\n".join(summary_lines)

    # messages = system + user summary
    messages = [{"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":USER_PROMPT_TEMPLATE.format(summary_text=summary_text)}]

    # store messages in history for session context
    SESSIONS[session_id]["chat_history"].extend(messages)

    # call model (non-streaming)
    try:
        resp = client.chat.completions.create(
            messages=messages,
            model=CEREBRAS_MODEL,
            stream=False,
            max_completion_tokens=4000,
            temperature=0.0,
            top_p=0.9
        )
        assistant_text = resp.choices[0].message.content
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    # try parse JSON
    parsed = extract_json_from_text(assistant_text)
    if parsed is None:
        # try reformatter
        try:
            followup = [{"role":"system","content":"You are a JSON reformatter. Extract the JSON object from the previous assistant reply and return only that JSON."},
                        {"role":"user","content": assistant_text}]
            resp2 = client.chat.completions.create(messages=followup, model=CEREBRAS_MODEL, stream=False, max_completion_tokens=1200, temperature=0.0)
            assistant_text2 = resp2.choices[0].message.content
            parsed = extract_json_from_text(assistant_text2)
            if parsed is not None:
                assistant_text = assistant_text2
        except Exception:
            pass

    if parsed is None:
        return JSONResponse(status_code=500, content={"error":"Could not parse JSON from LLM", "raw_output": assistant_text[:5000]})

    # Prepare chart data for frontend rendering
    chart_data = []
    for chart_spec in parsed.get("charts", []):
        try:
            chart_type = chart_spec.get("type", "bar")
            x_col = chart_spec.get("x")
            y_col = chart_spec.get("y")
            
            if x_col and y_col and x_col in df.columns and y_col in df.columns:
                # Prepare data based on chart type
                if chart_type in ["bar", "line"]:
                    # Aggregate data by x column
                    if df[x_col].dtype in ['object', 'string']:
                        # Categorical x-axis
                        grouped = df.groupby(x_col)[y_col].sum().reset_index()
                        data = grouped.to_dict('records')
                    else:
                        # Numeric x-axis - take all points
                        data = df[[x_col, y_col]].dropna().to_dict('records')
                    
                    chart_data.append({
                        **chart_spec,
                        "data": data[:50]  # Limit to 50 points for performance
                    })
                elif chart_type == "pie":
                    # Pie chart - aggregate by x column
                    grouped = df.groupby(x_col)[y_col].sum().reset_index()
                    grouped.columns = ['name', 'value']
                    chart_data.append({
                        **chart_spec,
                        "data": grouped.to_dict('records')[:10]  # Limit to 10 slices
                    })
                elif chart_type == "hist":
                    # Histogram - just send the y values
                    values = df[y_col].dropna().tolist()[:500]  # Limit data points
                    chart_data.append({
                        **chart_spec,
                        "data": [{"value": v} for v in values]
                    })
        except Exception as e:
            print(f"Error preparing chart data: {e}")
            continue

    out = {
        "session_id": session_id,
        "insights": parsed.get("insights", []),
        "anomalies": parsed.get("anomalies", []),
        "charts": parsed.get("charts", []),
        "chart_data": chart_data,  # New field with actual data
        "recommendations": parsed.get("recommendations", []),
        "raw_model_output": assistant_text
    }

    return JSONResponse(content=out)

@app.post("/chat")
async def chat(session_id: str = Form(...), user_message: str = Form(...)):
    """Continue a chat on an existing session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Invalid session_id")

    df = SESSIONS[session_id]["df"]
    print(df)
    print("-------------------------------------------------------")
    history = []
    # Add dataset summary as a system message (context for LLM)
    if not any(msg.get("content","").startswith("Dataset summary") for msg in history if msg["role"]=="system"):
        df_summary_text = summary_to_text(compact_summary(df))
        history.append({"role": "system", "content": f"Dataset summary:\n{df_summary_text}"})

    # Append the user's message
    history.append({"role": "user", "content": user_message})

    # Optional guidance to the LLM
    system_prompt = (
        "You are a professional data analyst providing insights to business users. "
        "Return ONLY a valid JSON object with these keys:\n"
        "- \"answer\": A clear, professional response formatted with:\n"
        "  * Use bullet points (start with '-' or '•') for lists\n"
        "  * Use numbered lists (1., 2., 3.) for sequential steps\n"
        "  * Use short, clear sentences\n"
        "  * Break information into digestible chunks\n"
        "  * Avoid long paragraphs - max 2-3 sentences per paragraph\n"
        "  * Use section headers followed by ':' when appropriate\n"
        "  * DO NOT use markdown formatting (no **, `, or code blocks)\n"
        "  * DO NOT wrap response in quotes\n"
        "  * Make it conversational and easy to read\n"
        "- \"followUp\": Array of 2-3 relevant follow-up questions\n\n"
        "Format example for answer:\n"
        "Key Findings:\n"
        "- First important insight\n"
        "- Second important insight\n"
        "- Third important insight\n\n"
        "Recommendations:\n"
        "1. First recommendation with brief explanation\n"
        "2. Second recommendation with brief explanation\n\n"
        "If the question is unrelated to the dataset, politely redirect to dataset-related queries."
    )


    full_messages = [{"role": "system", "content": system_prompt}] + history

    # Send to model
    try:
        resp = client.chat.completions.create(
            messages=full_messages,
            model=CEREBRAS_MODEL,
            stream=False,
            max_completion_tokens=2000,
            temperature=0.0,
            top_p=0.9
        )
        assistant_text = resp.choices[0].message.content
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    # append assistant reply to session history
    history.append({"role": "assistant", "content": assistant_text})

    # Parse JSON output
    parsed = extract_json_from_text(assistant_text)
    if parsed is None:
        raise HTTPException(status_code=500, detail=f"Could not parse JSON from model output. Raw output:\n{assistant_text[:2000]}")

    return JSONResponse(content={
        "response": assistant_text,
        "parsed": parsed
    })

# ---------------- Health check ----------------
@app.get("/health")
async def health():
    return {"status":"ok"}

