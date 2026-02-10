---
name: large-pdf-reader
description: >
  Extracts text from large PDF books by processing them in chunks to avoid memory issues.
  Handles books of any size by extracting text page-by-page and saving to markdown files.
  Use when the standard Read tool fails with "PDF too large" errors, or when processing
  entire books for summarization, analysis, or content creation.
---

# Large PDF Reader Skill

Read and extract text from large PDF books that exceed normal processing limits.

## Overview

This skill solves the "PDF too large" problem by:
1. Processing PDFs page-by-page to avoid memory issues
2. Saving extracted text to markdown files organized by chapter/section
3. Supporting incremental reading for very large books
4. Preserving structure with page numbers and section markers

## Usage

### Extract Full Book

```bash
python .claude/skills/large-pdf-reader/scripts/extract_pdf.py \
  --input READING/book.pdf \
  --output READING/book-extracted/
```

### Extract Specific Pages

```bash
python .claude/skills/large-pdf-reader/scripts/extract_pdf.py \
  --input READING/book.pdf \
  --output READING/book-extracted/ \
  --start-page 1 \
  --end-page 50
```

### Extract with Chunk Size

```bash
python .claude/skills/large-pdf-reader/scripts/extract_pdf.py \
  --input READING/book.pdf \
  --output READING/book-extracted/ \
  --chunk-size 50
```

## Output Structure

```
READING/book-extracted/
├── metadata.md           # Book metadata (title, author, pages)
├── full-text.md          # Complete extracted text
├── chunks/
│   ├── pages-001-050.md  # Chunked sections
│   ├── pages-051-100.md
│   └── ...
└── summary.md            # Auto-generated table of contents
```

## Script Options

| Flag | Description | Default |
|------|-------------|---------|
| `--input` | Path to the PDF file | Required |
| `--output` | Output directory | `./extracted/` |
| `--start-page` | First page to extract (1-indexed) | `1` |
| `--end-page` | Last page to extract | Last page |
| `--chunk-size` | Pages per chunk file | `50` |
| `--single-file` | Output all text to one file | `False` |

## Requirements

```bash
pip install pypdf pdfplumber
```

## Workflow for Book Summarization

1. **Extract text**: Run the extraction script
2. **Read chunks**: Process extracted markdown files
3. **Summarize**: Generate summaries for each section
4. **Synthesize**: Create overall book summary

## Example: Summarizing a Book

```bash
# Step 1: Extract the PDF
python .claude/skills/large-pdf-reader/scripts/extract_pdf.py \
  --input READING/superintelligence.pdf \
  --output READING/superintelligence-extracted/

# Step 2: The extracted text is now readable
# Claude can read the markdown files without size limits
```

## Troubleshooting

### "Cannot extract text"
The PDF may be scanned images. Use OCR:
```bash
python .claude/skills/large-pdf-reader/scripts/extract_pdf.py \
  --input book.pdf --output extracted/ --use-ocr
```

### Memory issues persist
Reduce chunk size:
```bash
--chunk-size 20
```

### Garbled text
The PDF may have unusual encoding. Try pdfplumber mode:
```bash
--engine pdfplumber
```
