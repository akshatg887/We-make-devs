# memory_manager.py
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class MemoryManager:
    def __init__(self, storage_path: str = "../memory_storage/"):
        """Initialize manager and ensure storage directory exists"""
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def get_user_memory_file(self, user_id: str) -> str:
        """Return path like: user_memory/user_<id>_memory.json"""
        return os.path.join(self.storage_path, f"user_{user_id}_memory.json")

    def load_user_memory(self, user_id: str) -> dict:
        """Load user memory if file exists; else empty structure. Ensure conversation_history is list of dicts."""
        file_path = self.get_user_memory_file(user_id)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                mem = json.load(f)
        else:
            mem = {
                "user_id": user_id,
                "conversation_history": [],
                "research_data": {},
                "scraped_data": {},
                "city_opportunities": {},
                "csv_path": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

        # normalize conversation_history: ensure every entry is a dict
        conv_history = mem.get("conversation_history", [])
        mem["conversation_history"] = [
            c if isinstance(c, dict)
            else {"user_message": str(c), "assistant_response": "", "timestamp": datetime.now().isoformat()}
            for c in conv_history
        ]


        return mem

    def save_user_memory(self, user_id: str, memory_data: dict):
        """Write memory to disk with update timestamp (atomic write)."""
        file_path = self.get_user_memory_file(user_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        memory_data["updated_at"] = datetime.now().isoformat()
        # write to temp file then atomically replace
        tmp_path = file_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, file_path)
        except Exception as e:
            # cleanup tmp file on failure
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            raise
        # optional debug log
        print(f"[MemoryManager] Saved memory for user {user_id} -> {file_path}")

    def get_context_summary(self, user_id: str, max_chats: int = 5) -> str:
        """
        Create a compact textual summary of recent conversations for LLM context.
        Excludes upload sentinel "__upload__" user messages (but includes assistant output from them if present).
        """
        memory = self.load_user_memory(user_id)
        convs = memory.get("conversation_history", []) or []

        # Normalize and filter entries
        norm: List[Dict[str, str]] = []
        for e in convs:
            if isinstance(e, dict):
                user_msg = str(e.get("user_message", "") or "")
                assistant_msg = str(e.get("assistant_response", "") or "")
                ts = str(e.get("timestamp") or datetime.now().isoformat())
            else:
                user_msg = str(e)
                assistant_msg = ""
                ts = datetime.now().isoformat()
            norm.append({"user_message": user_msg, "assistant_response": assistant_msg, "timestamp": ts})

        # Exclude "__upload__" user messages but keep assistant responses
        filtered = []
        for item in norm:
            if item["user_message"] == "__upload__":
                if item["assistant_response"]:
                    filtered.append({
                        "user_message": "(upload assistant output)",
                        "assistant_response": item["assistant_response"],
                        "timestamp": item["timestamp"]
                    })
                continue
            filtered.append(item)

        recent = filtered[-max_chats:]

        # Build textual summary safely
        lines = []
        for r in recent:
            # Ensure r is a dict (normalize malformed entries)
            if not isinstance(r, dict):
                r = {"user_message": str(r), "assistant_response": "", "timestamp": ""}
            # Now it's safe to call .get()
            u = str(r.get("user_message", "")).strip()
            a = str(r.get("assistant_response", "")).strip()
            ts = str(r.get("timestamp", ""))
            # Truncate long entries for readability
            if len(u) > 400:
                u = u[:400] + "..."
            if len(a) > 800:
                a = a[:800] + "..."
            lines.append(f"[{ts}] User: {u}\nAssistant: {a}\n")


        if not lines:
            return "No recent conversation history available."

        return "\n".join(lines)

    def add_conversation(self, user_id: str, user_message: str, assistant_response: str = ""):
        """
        Append a conversation entry to the user's memory.
        Each entry is a dict with user_message, assistant_response, timestamp.
        Keeps last 200 entries to bound memory size.
        """
        mem = self.load_user_memory(user_id)

        entry = {
            "user_message": str(user_message) if user_message is not None else "",
            "assistant_response": str(assistant_response) if assistant_response is not None else "",
            "timestamp": datetime.now().isoformat()
        }

        if "conversation_history" not in mem or not isinstance(mem["conversation_history"], list):
            mem["conversation_history"] = []

        mem["conversation_history"].append(entry)
        mem["conversation_history"] = mem["conversation_history"][-200:]
        mem["updated_at"] = datetime.now().isoformat()

        self.save_user_memory(user_id, mem)
