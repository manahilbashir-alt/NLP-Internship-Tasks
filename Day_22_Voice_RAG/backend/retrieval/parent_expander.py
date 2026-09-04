import json
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = BACKEND_ROOT / "vectorstores" / "FAISS_db" / "metadata.json"


class ParentExpander:
    def __init__(self):
        self.chunks_by_id = {}
        self.reload()

    def reload(self):
        all_chunks = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        self.chunks_by_id = {c["chunk_id"]: c for c in all_chunks}

    def expand(self, chunk_id: str, window: int = 2) -> dict:
        chunk_ids_in_window = [chunk_id]

        current_id = chunk_id
        for _ in range(window):
            current_chunk = self.chunks_by_id.get(current_id)
            if not current_chunk or not current_chunk.get("prev_chunk_id"):
                break
            current_id = current_chunk["prev_chunk_id"]
            chunk_ids_in_window.insert(0, current_id)

        current_id = chunk_id
        for _ in range(window):
            current_chunk = self.chunks_by_id.get(current_id)
            if not current_chunk or not current_chunk.get("next_chunk_id"):
                break
            current_id = current_chunk["next_chunk_id"]
            chunk_ids_in_window.append(current_id)

        combined_text = "\n".join(
            self.chunks_by_id[cid]["content"]
            for cid in chunk_ids_in_window if cid in self.chunks_by_id
        )
        return {"chunk_ids": chunk_ids_in_window, "combined_text": combined_text}