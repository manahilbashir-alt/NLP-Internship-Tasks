"""
================================================================================
 DAY 17 - STAGE 1: PDF -> STRUCTURED MARKDOWN (Docling-based)
================================================================================
"""

import time
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import (
    TextItem,
    SectionHeaderItem,
    TableItem,
    PictureItem,
    DocItemLabel,
)


# ------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = PROJECT_ROOT / "data" / "MACHINE LEARNING.pdf"

OUTPUT_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = OUTPUT_DIR / "images"
MARKDOWN_PATH = OUTPUT_DIR / "structured.md"


def setup_output_dirs():
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)

    print(f"[setup] Output folder ready at: {OUTPUT_DIR}")


def convert_pdf(pdf_path: Path):
    """
    Converts a PDF using Docling.

    The heavy TableFormer model is disabled to reduce RAM/pagefile usage.
    This is especially important on Windows systems with limited memory.
    """

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found at {pdf_path}. "
            f"Check the exact filename in data/."
        )

    print(
        f"[convert] Reading PDF: {pdf_path.name} "
        f"(first run can take a while)..."
    )

    start = time.time()

    # ------------------------------------------------------------
    # Docling PDF pipeline
    # ------------------------------------------------------------

    pipeline_options = PdfPipelineOptions()

    # IMPORTANT:
    # Disable the heavy TableFormer model.
    # This prevents the Windows paging-file error (1455).
    pipeline_options.do_table_structure = False

    # Keep picture extraction enabled.
    pipeline_options.generate_picture_images = True

    # Image quality.
    pipeline_options.images_scale = 2.0

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )

    result = converter.convert(str(pdf_path))

    doc = result.document

    elapsed = time.time() - start

    print(
        f"[convert] Done in {elapsed:.1f}s. "
        f"Pages: {len(doc.pages)} | "
        f"Texts: {len(doc.texts)} | "
        f"Tables: {len(doc.tables)} | "
        f"Pictures: {len(doc.pictures)}"
    )

    return doc


def table_to_markdown(table_item: TableItem, doc) -> str:
    """
    Turns a Docling table into a Markdown table string.
    """

    try:
        df = table_item.export_to_dataframe(doc)

    except Exception as e:
        return f"*[Table could not be parsed: {e}]*"

    if df.empty:
        return "*[Empty table]*"

    headers = list(df.columns.astype(str))

    header_row = "| " + " | ".join(headers) + " |"

    separator_row = (
        "| " + " | ".join(["---"] * len(headers)) + " |"
    )

    body_rows = [
        "| " + " | ".join(str(v) for v in row.tolist()) + " |"
        for _, row in df.iterrows()
    ]

    return "\n".join(
        [header_row, separator_row] + body_rows
    )


def save_picture(
    picture_item: PictureItem,
    doc,
    image_index: int
) -> str:
    """
    Saves a Docling picture as PNG.
    """

    image_filename = f"figure_{image_index:03d}.png"

    image_path = IMAGES_DIR / image_filename

    try:
        pil_image = picture_item.get_image(doc)

        if pil_image is not None:
            pil_image.save(image_path)

            return f"images/{image_filename}"

        else:
            print(
                f"[warn] Picture {image_index} had no image data."
            )

    except Exception as e:
        print(
            f"[warn] Could not save image "
            f"{image_index}: {e}"
        )

    return ""


def is_formula(text_item: TextItem) -> bool:
    """
    Checks whether a text item is a formula.
    """

    return getattr(
        text_item,
        "label",
        None
    ) == DocItemLabel.FORMULA


def build_markdown(doc) -> str:
    """
    Walk through the document in reading order and create Markdown.

    Page markers are inserted as:
        <!-- page:N -->

    These markers allow the chunking stage to preserve page numbers.
    """

    parts = []

    last_page = None

    image_index = 0

    for item, _level in doc.iterate_items():

        page_no = (
            item.prov[0].page_no
            if item.prov
            else last_page
        )

        # --------------------------------------------------------
        # Page marker
        # --------------------------------------------------------

        if (
            page_no is not None
            and page_no != last_page
        ):

            parts.append(
                f"\n<!-- page:{page_no} -->\n"
            )

            last_page = page_no

        # --------------------------------------------------------
        # Section heading
        # --------------------------------------------------------

        if isinstance(
            item,
            SectionHeaderItem
        ):

            parts.append(
                f"\n## {item.text.strip()}\n"
            )

        # --------------------------------------------------------
        # Formula
        # --------------------------------------------------------

        elif (
            isinstance(item, TextItem)
            and is_formula(item)
        ):

            parts.append(
                f"\n$$\n"
                f"{item.text.strip()}\n"
                f"$$\n"
            )

        # --------------------------------------------------------
        # Normal text
        # --------------------------------------------------------

        elif isinstance(item, TextItem):

            text = item.text.strip()

            if text:
                parts.append(text)

        # --------------------------------------------------------
        # Table
        # --------------------------------------------------------

        elif isinstance(item, TableItem):

            parts.append(
                f"\n{table_to_markdown(item, doc)}\n"
            )

        # --------------------------------------------------------
        # Picture
        # --------------------------------------------------------

        elif isinstance(item, PictureItem):

            image_index += 1

            rel_path = save_picture(
                item,
                doc,
                image_index
            )

            caption = ""

            try:
                caption = (
                    item.caption_text(doc)
                    or ""
                )

            except Exception:
                pass

            if rel_path:

                parts.append(
                    f"\n![{caption or 'figure'}]"
                    f"({rel_path})\n"
                )

                if caption:

                    parts.append(
                        f"*Figure: {caption}*\n"
                    )

    return "\n".join(parts)


def save_markdown(
    markdown_body: str,
    title="Machine Learning - Lecture Notes"
):
    """
    Saves structured Markdown to data/structured.md.
    """

    full_markdown = (
        f"# {title}\n\n"
        + markdown_body
    )

    MARKDOWN_PATH.write_text(
        full_markdown,
        encoding="utf-8"
    )

    print(
        f"[save] Structured markdown written to: "
        f"{MARKDOWN_PATH}"
    )


def main():

    setup_output_dirs()

    doc = convert_pdf(PDF_PATH)

    markdown_body = build_markdown(doc)

    save_markdown(markdown_body)

    print(
        "\n[done] Stage 1 complete. "
        "Next: run chunking/recursive_chunker.py"
    )


if __name__ == "__main__":
    main()


def ingest_pdf_to_markdown(
    pdf_path: Path
) -> str:
    """
    Runs the same Stage 1 pipeline for an uploaded PDF.

    Used by:
        POST /api/rag/ingest

    Returns Markdown directly instead of overwriting
    data/structured.md.
    """

    doc = convert_pdf(pdf_path)

    markdown_body = build_markdown(doc)

    title = pdf_path.stem

    return (
        f"# {title}\n\n"
        + markdown_body
    )