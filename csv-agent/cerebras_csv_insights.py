# cerebras_csv_insights.py
import os
import json
import math
import tempfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cerebras.cloud.sdk import Cerebras
from typing import Dict, Any, List
import re
from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()

# initialize client
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

# ---------- Utilities ----------

def load_csv(path: str, max_rows: int = 20000) -> pd.DataFrame:
    """
    Load CSV robustly. If file is very large, read first N rows and sample rest.
    """
    total = 0
    try:
        # quick attempt to infer number of rows (not exact for all files)
        for i, _ in enumerate(open(path, "rb")):
            total += 1
            if total > max_rows + 10:
                break
    except Exception:
        total = None

    if total is None or total <= max_rows:
        df = pd.read_csv(path)
    else:
        # read in chunks and sample
        reader = pd.read_csv(path, chunksize=50000)
        parts = []
        n = 0
        for chunk in reader:
            parts.append(chunk.sample(min(len(chunk), 5000)))
            n += len(chunk)
            if n > max_rows * 5:
                break
        df = pd.concat(parts, ignore_index=True)
    return df

def compact_summary(df: pd.DataFrame, max_sample_rows: int = 5) -> Dict[str,Any]:
    """Return compact numeric + categorical stats + sample rows for prompt."""
    summary = {}
    summary['n_rows'] = int(len(df))
    summary['columns'] = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # numeric stats
    numeric = df.select_dtypes(include=[np.number])
    num_stats = {}
    for c in numeric.columns:
        s = numeric[c].dropna()
        if len(s) == 0:
            continue
        num_stats[c] = {
            "count": int(s.count()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std": float(s.std()),
            "min": float(s.min()),
            "max": float(s.max()),
            "sum": float(s.sum())
        }
    if num_stats:
        summary['numeric_stats'] = num_stats

    # categorical top values
    cat_stats = {}
    non_num = df.select_dtypes(exclude=[np.number])
    for c in non_num.columns:
        top = df[c].value_counts(dropna=True).head(5).to_dict()
        cat_stats[c] = top
    if cat_stats:
        summary['categorical_top_values'] = cat_stats

    # detect date-like columns
    date_cols = []
    for c in df.columns:
        try:
            parsed = pd.to_datetime(df[c], errors='coerce')
            if parsed.notna().sum() > 0.5 * len(df):
                date_cols.append(c)
        except Exception:
            pass
    if date_cols:
        summary['date_columns'] = date_cols

    # sample rows (small)
    summary['samples'] = df.head(max_sample_rows).to_dict(orient='records')
    return summary

def summary_to_text(summary: Dict[str,Any], max_lines: int = 2000) -> str:
    """Turn summary dict to compact text for prompting."""
    lines = []
    lines.append(f"Rows: {summary.get('n_rows')}")
    lines.append("Columns and dtypes:")
    for c, t in summary['columns'].items():
        lines.append(f"- {c}: {t}")
    if 'numeric_stats' in summary:
        lines.append("Numeric column stats (count, mean, median, std, min, max, sum):")
        for c, s in summary['numeric_stats'].items():
            lines.append(f"- {c}: {s['count']}, {s['mean']:.2f}, {s['median']:.2f}, {s['std']:.2f}, {s['min']:.2f}, {s['max']:.2f}, {s['sum']:.2f}")
    if 'categorical_top_values' in summary:
        lines.append("Top categorical values (top 5):")
        for c, tv in summary['categorical_top_values'].items():
            lines.append(f"- {c}: {tv}")
    if 'date_columns' in summary:
        lines.append("Detected date columns: " + ", ".join(summary['date_columns']))
    lines.append("Sample rows:")
    for r in summary['samples']:
        lines.append("  " + json.dumps(r, ensure_ascii=False))
    text = "\n".join(lines)
    if len(text) > max_lines:
        return text[:max_lines]
    return text

# robust JSON extractor: some LLMs append commentary - we try to find last JSON block
def extract_json_from_text(s: str) -> Any:
    # find last { ... } or [ ... ] in text
    s = s.strip()
    # search for first { that leads to valid json
    matches = list(re.finditer(r"(\{|\[)", s))
    for m in reversed(matches):
        start = m.start()
        candidate = s[start:]
        try:
            return json.loads(candidate)
        except Exception:
            # try to balance braces progressively
            for end in range(len(candidate), 0, -1):
                try:
                    return json.loads(candidate[:end])
                except Exception:
                    continue
    # fallback: None
    return None

# ---------- Prompt templates ----------
SYSTEM_PROMPT = (
    "You are a strict, factual data analyst. "
    "Given a compact summary of a CSV dataset, return a JSON object ONLY with keys: "
    "\"insights\" (list of short strings), "
    "\"anomalies\" (list of descriptions), "
    "\"charts\" (list of chart specs), "
    "\"recommendations\" (list of short tactical recommendations). "
    "Each chart spec should be an object {\"type\":\"line|bar|hist|pie\",\"x\":\"col\",\"y\":\"col\",\"title\":\"...\"}.\n"
    "Do NOT include any extraneous commentary outside the JSON.\n"
)

USER_PROMPT_TEMPLATE = (
    "Dataset summary:\n{summary_text}\n\n"
    "Task:\n"
    "1) Provide top 3 insights (1-2 short sentences each) referencing columns from dataset.\n"
    "2) List any anomalies or suspicious rows/columns.\n"
    "3) Propose 1-3 charts with exact x and y column names in the JSON 'charts' list.\n"
    "4) Give 3 actionable recommendations.\n\n"
    "Return a single valid JSON object as described. If you cannot produce a field, return empty list for it."
)

# ---------- Main function to analyze CSV ----------

def analyze_csv_via_cerebras(csv_path: str, model_name: str = "qwen-3-235b-a22b-instruct-2507", stream: bool = True) -> Dict[str,Any]:
    df = load_csv(csv_path)
    summary = compact_summary(df)
    summary_text = summary_to_text(summary)

    messages = [
        {"role":"system", "content": SYSTEM_PROMPT},
        {"role":"user", "content": USER_PROMPT_TEMPLATE.format(summary_text=summary_text)}
    ]

    # streaming or non-streaming
    if stream:
        # accumulate the streamed text
        accum = ""
        stream_iter = client.chat.completions.create(
            messages=messages,
            model=model_name,
            stream=True,
            max_completion_tokens=4000,
            temperature=0.0,
            top_p=0.9
        )
        print("Streaming response...\n")
        for chunk in stream_iter:
            # some SDKs yield chunk.choices[0].delta.content
            try:
                delta = chunk.choices[0].delta.get("content") or chunk.choices[0].delta.get("message", {}).get("content")
            except Exception:
                # fallback
                try:
                    delta = chunk.choices[0].delta.content
                except Exception:
                    delta = None
            if delta:
                print(delta, end="", flush=True)
                accum += delta
        print("\n\n--- End stream ---\n")
        assistant_text = accum
    else:
        resp = client.chat.completions.create(
            messages=messages,
            model=model_name,
            stream=False,
            max_completion_tokens=4000,
            temperature=0.0,
            top_p=0.9
        )
        assistant_text = resp.choices[0].message["content"]

    # Try to extract JSON
    parsed = extract_json_from_text(assistant_text)
    if parsed is None:
        # fallback: ask model to reformat by posting again (non-stream) asking to only reply with JSON
        followup_msgs = [
            {"role":"system","content":"You are a JSON formatter. Extract the JSON object from the previous assistant reply and return only that JSON."},
            {"role":"user","content": assistant_text}
        ]
        resp2 = client.chat.completions.create(messages=followup_msgs, model=model_name, stream=False, max_completion_tokens=1200)
        text2 = resp2.choices[0].message["content"]
        parsed = extract_json_from_text(text2)
    if parsed is None:
        raise RuntimeError("Could not parse JSON from model output. Raw output:\n" + assistant_text[:2000])

    # Render charts if any
    chart_files = []
    charts = parsed.get("charts", []) if isinstance(parsed, dict) else []
    for i, cs in enumerate(charts):
        try:
            fname = render_chart_spec(cs, df, index=i)
            chart_files.append(fname)
        except Exception as e:
            print("Chart render failed:", e)

    # compile final result
    result = {
        "summary": summary,
        "raw_model_output": assistant_text,
        "parsed": parsed,
        "chart_files": chart_files
    }
    return result

# ---------- Chart renderer ----------
def render_chart_spec(spec: Dict[str,Any], df: pd.DataFrame, index: int = 0) -> str:
    ctype = spec.get("type")
    x = spec.get("x")
    y = spec.get("y")
    title = spec.get("title", f"chart_{index}")

    # safe checks
    if x not in df.columns and y not in df.columns:
        raise ValueError(f"Chart columns not found: {x},{y}")

    tmp = tempfile.gettempdir()
    outpath = os.path.join(tmp, f"chart_{index}.png")

    plt.figure(figsize=(6,4))
    if ctype == "line":
        df2 = df.copy()
        df2[x] = pd.to_datetime(df2[x], errors='coerce') if not np.issubdtype(df2[x].dtype, np.number) else df2[x]
        df2 = df2.sort_values(x)
        plt.plot(df2[x], df2[y], marker="o")
        plt.xlabel(x); plt.ylabel(y); plt.title(title)
    elif ctype == "bar":
        agg = df.groupby(x)[y].sum().reset_index().sort_values(y, ascending=False)
        plt.bar(agg[x].astype(str), agg[y])
        plt.xlabel(x); plt.ylabel(y); plt.title(title); plt.xticks(rotation=45)
    elif ctype == "hist":
        plt.hist(df[y].dropna(), bins=30)
        plt.xlabel(y); plt.title(title)
    elif ctype == "pie":
        agg = df.groupby(x)[y].sum()
        agg.plot.pie(y=y, autopct="%1.1f%%")
    else:
        # fallback: try line by default
        df2 = df.copy()
        df2[x] = pd.to_datetime(df2[x], errors='coerce') if not np.issubdtype(df2[x].dtype, np.number) else df2[x]
        df2 = df2.sort_values(x)
        plt.plot(df2[x], df2[y], marker='o')
        plt.xlabel(x); plt.ylabel(y); plt.title(title)

    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
    print("Saved chart to", outpath)
    return outpath

# ---------- Example run ----------
if __name__ == "__main__":
    # replace with real file path
    csv_path = "sample_sales.csv"
    if not os.path.exists(csv_path):
        # create a tiny sample for demo
        pd.DataFrame({
            "date":["2025-09-01","2025-09-02","2025-09-03","2025-09-04","2025-09-05"],
            "product":["A","A","B","A","B"],
            "amount":[200,250,180,300,220],
            "orders":[10,12,8,15,11]
        }).to_csv(csv_path, index=False)

    result = analyze_csv_via_cerebras(csv_path, model_name="qwen-3-235b-a22b-instruct-2507", stream=True)
    print("\nParsed JSON:\n", json.dumps(result["parsed"], indent=2, ensure_ascii=False))
    print("Charts:", result["chart_files"])
