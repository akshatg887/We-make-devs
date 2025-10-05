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
from datetime import datetime


import uuid
from memory_manager import MemoryManager

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, "../memory_storage/")  # project-local memory folder

os.makedirs(MEMORY_DIR, exist_ok=True) 
memory_mgr = MemoryManager(storage_path=MEMORY_DIR)
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
    """
    Compact summary for prompting the model.

    Returns a JSON-friendly dictionary with:
      - n_rows
      - columns (dtype names)
      - numeric_stats (count, mean, median, std, min, max, sum)
      - categorical_top_values (top 5 values as {str(value): int(count)})
      - date_columns (detected among non-numeric columns)
      - samples (list of up to max_sample_rows dicts)
    """
    summary: Dict[str, Any] = {}

    # defensive: if df is None or empty
    if df is None or len(df) == 0:
        summary["n_rows"] = 0
        summary["columns"] = {}
        summary["samples"] = []
        return summary

    summary["n_rows"] = int(len(df))
    # use dtype.name to get a stable string
    summary["columns"] = {col: df[col].dtype.name for col in df.columns}

    # numeric stats
    numeric = df.select_dtypes(include=[np.number])
    num_stats: Dict[str, Any] = {}
    for c in numeric.columns:
        s = numeric[c].dropna()
        if len(s) == 0:
            continue
        # convert to python native types for JSON safety
        count = int(s.count())
        mean = float(s.mean()) if not pd.isna(s.mean()) else None
        median = float(s.median()) if not pd.isna(s.median()) else None
        std = float(s.std()) if len(s) > 1 and not pd.isna(s.std()) else 0.0
        mn = float(s.min()) if not pd.isna(s.min()) else None
        mx = float(s.max()) if not pd.isna(s.max()) else None
        summ = float(s.sum()) if not pd.isna(s.sum()) else None

        num_stats[c] = {
            "count": count,
            "mean": mean,
            "median": median,
            "std": std,
            "min": mn,
            "max": mx,
            "sum": summ
        }
    if num_stats:
        summary["numeric_stats"] = num_stats

    # categorical top values (make keys strings and counts plain ints)
    cat_stats: Dict[str, Any] = {}
    non_num = df.select_dtypes(exclude=[np.number])
    for c in non_num.columns:
        try:
            vc = df[c].value_counts(dropna=True).head(5)
            top: Dict[str, int] = {}
            for k, v in vc.items():
                # convert key to string (JSON-friendly) and count to int
                top[str(k)] = int(v)
            cat_stats[c] = top
        except Exception:
            # if something odd happens, skip gracefully
            cat_stats[c] = {}

    if cat_stats:
        summary["categorical_top_values"] = cat_stats

    # detect date-like among non-numeric only
    date_cols: List[str] = []
    for c in non_num.columns:
        try:
            parsed = pd.to_datetime(df[c], errors="coerce")
            # require at least 50% of rows parse to dates (same heuristic you used)
            if parsed.notna().sum() >= max(1, 0.5 * len(df)):
                date_cols.append(c)
        except Exception:
            # ignore parse errors
            pass
    if date_cols:
        summary["date_columns"] = date_cols

    # sample rows as plain python types (to_dict already usually does this)
    samples = df.head(max_sample_rows).to_dict(orient="records")
    # ensure nested numpy types are converted (json.dumps will otherwise complain)
    def _coerce_obj(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.ndarray,)):
            return o.tolist()
        return o

    coerced_samples = []
    for row in samples:
        coerced = {k: _coerce_obj(v) for k, v in row.items()}
        coerced_samples.append(coerced)

    summary["samples"] = coerced_samples
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
    """
    Upload CSV -> create a session_id, persist CSV + initial memory JSON,
    call the LLM once for initial analysis (optional), and save that assistant reply
    into conversation_history. IMPORTANT: do not store system prompts in conversation history.
    """
    # read upload bytes and parse CSV
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

    # 1) session id
    session_id = str(uuid.uuid4())

    # 2) save CSV to disk under memory dir (session-scoped filename)
    tmp_csv = tempfile.NamedTemporaryFile(mode="wb", delete=False,
                                          suffix=f"_{session_id}.csv",
                                          dir=memory_mgr.storage_path)
    try:
        tmp_csv.write(contents)
        tmp_csv.flush()
    finally:
        tmp_csv.close()

    # 3) initialize minimal session memory and persist (user_id = session_id)
    initial_memory = {
        "user_id": session_id,
        "conversation_history": [],     # will hold dicts with user_message + assistant_response
        "research_data": {},
        "scraped_data": {},
        "city_opportunities": {},
        "csv_path": tmp_csv.name,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    memory_mgr.save_user_memory(session_id, initial_memory)
    # debug: confirm file was created
    mem_path = memory_mgr.get_user_memory_file(session_id)
    print(f"[upload_csv] saved memory to: {mem_path}, exists: {os.path.exists(mem_path)}")

    # 4) keep dataframe in in-memory cache for immediate work (optional)
    SESSIONS[session_id] = {"df": df}  # chat will load from disk if needed

    # 5) prepare summary and call LLM (this is the 'initial analysis' step you already had)
    summary = compact_summary(df)
    summary_lines = [f"Rows: {summary.get('n_rows', 0)}"]
    summary_lines.append("Columns:")

    columns = summary.get("columns", {})
    if isinstance(columns, dict):
        for c, t in columns.items():
            summary_lines.append(f"- {c}: {t}")
    summary_text = "\n".join(summary_lines)

    mem = memory_mgr.load_user_memory(session_id)

    # dataset key: use the filename without extension
    dataset_key = file.filename.rsplit(".", 1)[0]

    mem["research_data"][dataset_key] = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "csv_path": tmp_csv.name
    }

    memory_mgr.save_user_memory(session_id, mem)

    numeric_stats = summary.get("numeric_stats", {})
    if isinstance(numeric_stats, dict):
        for c, s in numeric_stats.items():
            summary_lines.append(f"- {c}: mean={s.get('mean', 0):.2f}, sum={s.get('sum', 0):.2f}")

    summary_lines.append("Sample rows:")
    for r in summary.get("samples", []):
        if isinstance(r, dict):
            summary_lines.append(json.dumps(r, ensure_ascii=False))

    summary_text = "\n".join(summary_lines)

    # system + user prompts for the upload-time analysis (KEPT local to this call only)
    upload_system = SYSTEM_PROMPT
    upload_user = USER_PROMPT_TEMPLATE.format(summary_text=summary_text)

    messages = [{"role": "system", "content": upload_system},
                {"role": "user", "content": upload_user}]

    try:
        resp = client.chat.completions.create(
            messages=messages,
            model=os.getenv("CEREBRAS_MODEL", CEREBRAS_MODEL),
            stream=False,
            max_completion_tokens=4000,
            temperature=0.0,
            top_p=0.9
        )
        assistant_text = resp.choices[0].message.content
    except Exception as e:
        # we still return session_id even if LLM fails; include error in response
        traceback.print_exc()
        memory_mgr.add_conversation(session_id, user_message="__upload__", assistant_response=f"(LLM failed: {e})")
        return JSONResponse(status_code=502, content={"user_id": session_id, "error": str(e)})

    # 6) save the upload conversation as a single entry in conversation_history
    # note: we use a special user_message token "__upload__" — it's stored but our chat flow will
    # exclude it when building messages for follow-up chats (this prevents "upload prompts" from restricting chat)
    memory_mgr.add_conversation(session_id, user_message="__upload__", assistant_response=assistant_text)

    # 7) return session_id and initial parsed model output (if parseable)
    parsed = extract_json_from_text(assistant_text)
    return JSONResponse(content={"user_id": session_id, "parsed": parsed or {}, "raw": assistant_text})


# ---------------- Chat endpoint ----------------
@app.post("/chat")
async def chat(session_id: str = Form(...), user_message: str = Form(...)):
    """
    Continue a chat on an existing session.
    - Saves the user message to persistent memory as a (pending) assistant response.
    - Builds a free-flowing message payload: system prompt + dataset summary + recent convo (skip __upload__).
    - Calls the LLM, replaces the pending entry with the actual assistant response, saves memory.
    - Returns assistant text and any parsed JSON.
    """

    # 1) session validity
    # Try to lazily load the session if it's missing
   # Try to lazily load the session if it's missing
    if session_id not in SESSIONS:
        memory_path = memory_mgr.get_user_memory_file(session_id)  # authoritative path

        if os.path.exists(memory_path):
            # load the memory and reconstruct minimal SESSIONS entry
            mem = memory_mgr.load_user_memory(session_id)
            # if a csv_path exists, try to load df into memory (non-blocking)
            df = None
            csv_path = mem.get("csv_path")
            try:
                if csv_path and os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
            except Exception:
                df = None
            SESSIONS[session_id] = {"df": df}
        else:
            raise HTTPException(status_code=404, detail="Invalid session_id")

    # 2) load dataset and memory
    df = SESSIONS[session_id]["df"]
    mem = memory_mgr.load_user_memory(session_id)

    # 3) persist the incoming user_message immediately as a conversation turn with a pending assistant response
    #    so we always have a durable trace (helps with crashes / retries)
    memory_mgr.add_conversation(session_id, user_message=user_message, assistant_response="(pending)")

    # reload mem (to include the pending entry)
    mem = memory_mgr.load_user_memory(session_id)

    # 4) free-flowing chat system prompt (no rigid JSON-only enforcement)
    chat_system = (
        "You are a knowledgeable data analyst. "
        "You are a strict, factual data analyst. "
        "Return ONLY a JSON object with keys: "
        "\"answer\" (Complete descriptive and detailed explanation, unless prompted otherwise by the user.), "
        "\"followUp\" (followup questions that user could be interested in next.), "
        "The user may ask questions about the dataset, insights, anomalies, charts, or recommendations. "
        "You can provide explanations, context, or clarifications. "
        "Use previous conversation and dataset summary stored in context. "
        "Output can be in text, JSON, or a mix depending on what the user asks."
    )

    # 5) dataset summary from persistent memory (do not include upload-time system prompts)
    #    memory_mgr.get_context_summary should return a short textual dataset summary & relevant recent points
    dataset_summary = memory_mgr.get_context_summary(session_id)
    messages = [
        {"role": "system", "content": chat_system},
        {"role": "system", "content": f"Dataset summary:\n{dataset_summary}"}
    ]

    # 6) append recent conversation turns from memory, skipping the special "__upload__" user token
    #    include assistant responses (except pending) and user messages
    #    keep a sliding window to avoid sending too much context
    recent = mem.get("conversation_history", [])[-30:]  # tune window size if needed
    for conv in recent:
        if not isinstance(conv, dict):
            conv = {
            "user_message": str(conv),
            "assistant_response": "",
            "timestamp": ""
            }

        u_msg = str(conv.get("user_message", "")).strip()
        a_msg = str(conv.get("assistant_response", "")).strip()

    # now you can safely use u_msg and a_msg
        if u_msg == "__upload__":
            if a_msg and a_msg != "(pending)":
                messages.append({"role": "assistant", "content": a_msg})
            continue

        if u_msg:
            messages.append({"role": "user", "content": u_msg})
        if a_msg and a_msg != "(pending)":
            messages.append({"role": "assistant", "content": a_msg})

    # 7) the latest user message is already recorded in memory as pending; still include it for prompt completeness
    messages.append({"role": "user", "content": user_message})

    # 8) call the LLM (non-streaming for simplicity). Adjust tokens/temperature/top_p to taste.
    try:
        resp = client.chat.completions.create(
            messages=messages,
            model=os.getenv("CEREBRAS_MODEL", CEREBRAS_MODEL),
            stream=False,
            max_completion_tokens=2000,
            temperature=0.0,
            top_p=0.9
        )
        # adapt to SDK response shape you have; this accesses the assistant content
        assistant_text = resp.choices[0].message.content
    except Exception as e:
        # update the pending entry to reflect failure
        mem = memory_mgr.load_user_memory(session_id)
        for i in range(len(mem["conversation_history"]) - 1, -1, -1):
            if mem["conversation_history"][i].get("assistant_response") == "(pending)":
                mem["conversation_history"][i]["assistant_response"] = f"(LLM call failed: {e})"
                mem["conversation_history"][i]["timestamp"] = datetime.now().isoformat()
                break
        memory_mgr.save_user_memory(session_id, mem)
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    # 9) replace the pending assistant response with the real assistant_text and persist
    mem = memory_mgr.load_user_memory(session_id)
    for i in range(len(mem["conversation_history"]) - 1, -1, -1):
        if mem["conversation_history"][i].get("assistant_response") == "(pending)":
            mem["conversation_history"][i]["assistant_response"] = assistant_text
            mem["conversation_history"][i]["timestamp"] = datetime.now().isoformat()
            break
    memory_mgr.save_user_memory(session_id, mem)

    # 10) try to extract JSON from the assistant (if the assistant returned structured JSON)
    parsed = extract_json_from_text(assistant_text)

    # 11) return full response to frontend (raw text + parsed if any)
    return JSONResponse({
        "user_id": session_id,
        "response": assistant_text,
        "parsed": parsed,
        "raw": assistant_text
    })



# ---------------- Health check ----------------
@app.get("/health")
async def health():
    return {"status":"ok"}

