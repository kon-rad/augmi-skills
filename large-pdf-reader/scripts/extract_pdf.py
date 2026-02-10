#!/usr/bin/env python3
"""
Large PDF Reader - Extract text from large PDF books

Processes PDFs page-by-page to avoid memory issues and saves
extracted text to organized markdown files.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

def extract_with_pypdf(pdf_path: str, start_page: int = 1, end_page: int = None):
    """Extract text using pypdf (fast, good for most PDFs)."""
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    if end_page is None:
        end_page = total_pages

    # Get metadata
    metadata = {
        'title': reader.metadata.title if reader.metadata else None,
        'author': reader.metadata.author if reader.metadata else None,
        'total_pages': total_pages,
        'extracted_pages': f"{start_page}-{end_page}"
    }

    pages = []
    for i in range(start_page - 1, min(end_page, total_pages)):
        try:
            text = reader.pages[i].extract_text()
            pages.append({
                'page_num': i + 1,
                'text': text or ''
            })
        except Exception as e:
            pages.append({
                'page_num': i + 1,
                'text': f'[Error extracting page: {e}]'
            })

        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Processed page {i + 1}/{end_page}...")

    return metadata, pages


def extract_with_pdfplumber(pdf_path: str, start_page: int = 1, end_page: int = None):
    """Extract text using pdfplumber (better for complex layouts)."""
    import pdfplumber

    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)

        if end_page is None:
            end_page = total_pages

        metadata = {
            'title': pdf.metadata.get('Title') if pdf.metadata else None,
            'author': pdf.metadata.get('Author') if pdf.metadata else None,
            'total_pages': total_pages,
            'extracted_pages': f"{start_page}-{end_page}"
        }

        for i in range(start_page - 1, min(end_page, total_pages)):
            try:
                text = pdf.pages[i].extract_text()
                pages.append({
                    'page_num': i + 1,
                    'text': text or ''
                })
            except Exception as e:
                pages.append({
                    'page_num': i + 1,
                    'text': f'[Error extracting page: {e}]'
                })

            if (i + 1) % 10 == 0:
                print(f"  Processed page {i + 1}/{end_page}...")

    return metadata, pages


def save_extracted_text(metadata: dict, pages: list, output_dir: str, chunk_size: int = 50, single_file: bool = False):
    """Save extracted text to organized markdown files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save metadata
    metadata_content = f"""# {metadata.get('title') or 'Extracted PDF'}

**Author:** {metadata.get('author') or 'Unknown'}
**Total Pages:** {metadata.get('total_pages')}
**Extracted Pages:** {metadata.get('extracted_pages')}
**Extracted On:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
"""

    with open(output_path / 'metadata.md', 'w', encoding='utf-8') as f:
        f.write(metadata_content)

    if single_file:
        # Write all to one file
        with open(output_path / 'full-text.md', 'w', encoding='utf-8') as f:
            f.write(metadata_content)
            f.write("\n# Full Text\n\n")
            for page in pages:
                f.write(f"\n---\n## Page {page['page_num']}\n\n")
                f.write(page['text'])
                f.write("\n")
        print(f"  Saved: {output_path / 'full-text.md'}")
    else:
        # Write in chunks
        chunks_dir = output_path / 'chunks'
        chunks_dir.mkdir(exist_ok=True)

        chunk_files = []
        for i in range(0, len(pages), chunk_size):
            chunk_pages = pages[i:i + chunk_size]
            start_num = chunk_pages[0]['page_num']
            end_num = chunk_pages[-1]['page_num']

            chunk_filename = f"pages-{start_num:03d}-{end_num:03d}.md"
            chunk_files.append(chunk_filename)

            with open(chunks_dir / chunk_filename, 'w', encoding='utf-8') as f:
                f.write(f"# Pages {start_num} - {end_num}\n\n")
                for page in chunk_pages:
                    f.write(f"\n---\n## Page {page['page_num']}\n\n")
                    f.write(page['text'])
                    f.write("\n")

            print(f"  Saved: {chunks_dir / chunk_filename}")

        # Write full text file too
        with open(output_path / 'full-text.md', 'w', encoding='utf-8') as f:
            f.write(metadata_content)
            f.write("\n# Full Text\n\n")
            for page in pages:
                f.write(f"\n---\n## Page {page['page_num']}\n\n")
                f.write(page['text'])
                f.write("\n")
        print(f"  Saved: {output_path / 'full-text.md'}")

        # Write summary/index
        with open(output_path / 'summary.md', 'w', encoding='utf-8') as f:
            f.write(metadata_content)
            f.write("\n## Chunk Files\n\n")
            for cf in chunk_files:
                f.write(f"- [chunks/{cf}](chunks/{cf})\n")
        print(f"  Saved: {output_path / 'summary.md'}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Extract text from large PDF books',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input book.pdf --output extracted/
  %(prog)s --input book.pdf --output extracted/ --start-page 1 --end-page 50
  %(prog)s --input book.pdf --output extracted/ --chunk-size 25
  %(prog)s --input book.pdf --output extracted/ --single-file
  %(prog)s --input book.pdf --output extracted/ --engine pdfplumber
        """
    )

    parser.add_argument('--input', '-i', required=True, help='Path to the PDF file')
    parser.add_argument('--output', '-o', default='./extracted/', help='Output directory')
    parser.add_argument('--start-page', type=int, default=1, help='First page to extract (1-indexed)')
    parser.add_argument('--end-page', type=int, default=None, help='Last page to extract')
    parser.add_argument('--chunk-size', type=int, default=50, help='Pages per chunk file')
    parser.add_argument('--single-file', action='store_true', help='Output all text to one file')
    parser.add_argument('--engine', choices=['pypdf', 'pdfplumber'], default='pypdf',
                       help='PDF extraction engine to use')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    print(f"Extracting: {args.input}")
    print(f"Output to: {args.output}")
    print(f"Engine: {args.engine}")
    print()

    # Extract text
    if args.engine == 'pdfplumber':
        metadata, pages = extract_with_pdfplumber(
            args.input, args.start_page, args.end_page
        )
    else:
        metadata, pages = extract_with_pypdf(
            args.input, args.start_page, args.end_page
        )

    print(f"\nExtracted {len(pages)} pages")

    # Save
    output_path = save_extracted_text(
        metadata, pages, args.output,
        chunk_size=args.chunk_size,
        single_file=args.single_file
    )

    print(f"\nDone! Output saved to: {output_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
