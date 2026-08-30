from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException

from ingestion import extract_text, chunk_text
from rag import add_documents, get_sources


app = FastAPI(
    title="Day 21 RAG API",
    description="FastAPI backend for the RAG application",
    version="1.0.0"
)


UPLOAD_DIR = (
    Path(__file__).parent.parent / "data" / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@app.get("/")
def root():
    return {
        "message": "Day 21 RAG API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/rag/ingest")
async def ingest_document(
    file: UploadFile = File(...)
):

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF, DOCX, and TXT "
                "files are supported."
            )
        )

    file_path = UPLOAD_DIR / file.filename

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        text = extract_text(
            str(file_path)
        )

        if not text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "No text could be extracted "
                    "from the document."
                )
            )

        chunks = chunk_text(text)

        chunk_count = add_documents(
            chunks,
            file.filename
        )

        return {
            "message": (
                "Document ingested successfully"
            ),
            "filename": file.filename,
            "characters": len(text),
            "chunks": chunk_count
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/api/rag/sources")
def sources():

    return {
        "sources": get_sources()
    }