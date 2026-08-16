import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_DIR = BASE_DIR / "data" / "chunks"
OUTPUT_DIR = BASE_DIR / "data" / "benchmark"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = OUTPUT_DIR / "benchmark_chunks.json"

TARGET_SIZE = 1200


def load_chunks():

    chunks = []

    for file in sorted(SOURCE_DIR.glob("*.json")):

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(data, list):
            chunks.extend(data)

        elif isinstance(data, dict):

            if "chunks" in data:
                chunks.extend(data["chunks"])

            else:
                chunks.append(data)

    return chunks


def main():

    chunks = load_chunks()

    print(f"Original chunks: {len(chunks)}")

    benchmark_chunks = []

    copy_number = 0

    while len(benchmark_chunks) < TARGET_SIZE:

        copy_number += 1

        for chunk in chunks:

            if len(benchmark_chunks) >= TARGET_SIZE:
                break

            new_chunk = {
                "text": chunk.get("text", ""),
                "metadata": dict(
                    chunk.get("metadata", {})
                )
            }

            new_chunk["metadata"]["benchmark_copy"] = copy_number

            new_chunk["metadata"]["benchmark_index"] = (
                len(benchmark_chunks)
            )

            benchmark_chunks.append(
                new_chunk
            )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            benchmark_chunks,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Benchmark chunks created: "
        f"{len(benchmark_chunks)}"
    )

    print(
        f"Saved to:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()