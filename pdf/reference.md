# PDF Processing Reference

Advanced features, additional libraries, and troubleshooting for PDF processing.

## Advanced pypdf Features

### Compress PDF
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("large.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.compress_content_streams()
    writer.add_page(page)

with open("compressed.pdf", "wb") as output:
    writer.write(output)
```

### Add Bookmarks
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add bookmarks (outline)
writer.add_outline_item("Chapter 1", 0)  # Page index 0
writer.add_outline_item("Chapter 2", 5)  # Page index 5
child = writer.add_outline_item("Section 2.1", 6, parent=writer.outline[-1])

with open("with_bookmarks.pdf", "wb") as output:
    writer.write(output)
```

### Add Annotations
```python
from pypdf import PdfReader, PdfWriter
from pypdf.generic import AnnotationBuilder

reader = PdfReader("document.pdf")
writer = PdfWriter()
writer.append(reader)

# Add text annotation
annotation = AnnotationBuilder.text(
    text="This is a comment",
    rect=(100, 700, 150, 750),
)
writer.add_annotation(page_number=0, annotation=annotation)

# Add link annotation
link = AnnotationBuilder.link(
    rect=(100, 600, 200, 620),
    url="https://example.com"
)
writer.add_annotation(page_number=0, annotation=link)

with open("annotated.pdf", "wb") as output:
    writer.write(output)
```

### Crop Pages
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    # Get current page dimensions
    box = page.mediabox

    # Set crop box (left, bottom, right, top)
    page.cropbox.lower_left = (50, 50)
    page.cropbox.upper_right = (box.width - 50, box.height - 50)

    writer.add_page(page)

with open("cropped.pdf", "wb") as output:
    writer.write(output)
```

## pypdfium2 - High-Performance PDF Rendering

### Installation
```bash
pip install pypdfium2
```

### Render PDF to Image
```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")

# Render first page at 300 DPI
page = pdf[0]
image = page.render(scale=300/72).to_pil()
image.save("page_1.png")

# Render all pages
for i, page in enumerate(pdf):
    image = page.render(scale=300/72).to_pil()
    image.save(f"page_{i+1}.png")
```

### Get Page Dimensions
```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
page = pdf[0]

width = page.get_width()   # Points (1/72 inch)
height = page.get_height()
print(f"Page size: {width} x {height} points")
print(f"Page size: {width/72:.2f} x {height/72:.2f} inches")
```

### Extract Text with Position
```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
page = pdf[0]
textpage = page.get_textpage()

# Get all text
text = textpage.get_text_bounded()
print(text)

# Get text in specific region (x1, y1, x2, y2)
region_text = textpage.get_text_bounded(left=100, bottom=100, right=500, top=700)
```

## JavaScript: pdf-lib Advanced

### Embed Images
```javascript
const { PDFDocument, rgb } = require('pdf-lib');
const fs = require('fs');

async function embedImage() {
    const pdfDoc = await PDFDocument.create();
    const page = pdfDoc.addPage([600, 400]);

    // Embed PNG
    const pngImage = await pdfDoc.embedPng(fs.readFileSync('image.png'));

    // Or embed JPG
    // const jpgImage = await pdfDoc.embedJpg(fs.readFileSync('image.jpg'));

    // Draw image
    page.drawImage(pngImage, {
        x: 50,
        y: 100,
        width: 200,
        height: 150,
    });

    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('with_image.pdf', pdfBytes);
}
```

### Embed Fonts
```javascript
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');
const fontkit = require('@pdf-lib/fontkit');
const fs = require('fs');

async function customFont() {
    const pdfDoc = await PDFDocument.create();
    pdfDoc.registerFontkit(fontkit);

    // Embed custom font
    const fontBytes = fs.readFileSync('CustomFont.ttf');
    const customFont = await pdfDoc.embedFont(fontBytes);

    const page = pdfDoc.addPage();
    page.drawText('Custom Font Text', {
        x: 50,
        y: 500,
        font: customFont,
        size: 24,
        color: rgb(0, 0, 0),
    });

    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('custom_font.pdf', pdfBytes);
}
```

### Modify Existing PDF
```javascript
const { PDFDocument, rgb, degrees } = require('pdf-lib');
const fs = require('fs');

async function modifyPdf() {
    const existingPdfBytes = fs.readFileSync('existing.pdf');
    const pdfDoc = await PDFDocument.load(existingPdfBytes);

    const pages = pdfDoc.getPages();
    const firstPage = pages[0];

    // Add text
    firstPage.drawText('APPROVED', {
        x: 50,
        y: 50,
        size: 30,
        color: rgb(0, 0.5, 0),
        rotate: degrees(45),
    });

    // Add rectangle
    firstPage.drawRectangle({
        x: 40,
        y: 40,
        width: 150,
        height: 50,
        borderColor: rgb(0, 0.5, 0),
        borderWidth: 2,
    });

    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('modified.pdf', pdfBytes);
}
```

### Copy Pages Between PDFs
```javascript
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

async function copyPages() {
    const pdf1Bytes = fs.readFileSync('doc1.pdf');
    const pdf2Bytes = fs.readFileSync('doc2.pdf');

    const pdf1 = await PDFDocument.load(pdf1Bytes);
    const pdf2 = await PDFDocument.load(pdf2Bytes);

    // Create new document
    const mergedPdf = await PDFDocument.create();

    // Copy pages from first PDF
    const copiedPages1 = await mergedPdf.copyPages(pdf1, pdf1.getPageIndices());
    copiedPages1.forEach((page) => mergedPdf.addPage(page));

    // Copy specific pages from second PDF (pages 0 and 2)
    const copiedPages2 = await mergedPdf.copyPages(pdf2, [0, 2]);
    copiedPages2.forEach((page) => mergedPdf.addPage(page));

    const pdfBytes = await mergedPdf.save();
    fs.writeFileSync('merged.pdf', pdfBytes);
}
```

## Command-Line Tools Reference

### Ghostscript
```bash
# Convert PDF to images
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r300 -sOutputFile=page_%03d.png input.pdf

# Compress PDF
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dBATCH -sOutputFile=compressed.pdf input.pdf

# PDF settings:
# /screen   - lowest quality, smallest size
# /ebook    - medium quality
# /printer  - high quality
# /prepress - highest quality, largest size

# Convert to grayscale
gs -sDEVICE=pdfwrite -dProcessColorModel=/DeviceGray \
   -dColorConversionStrategy=/Gray -dNOPAUSE -dBATCH \
   -sOutputFile=grayscale.pdf input.pdf
```

### ImageMagick
```bash
# Convert PDF to images
convert -density 300 input.pdf output_%03d.png

# Convert images to PDF
convert image1.png image2.png image3.png output.pdf

# Resize PDF pages
convert -density 300 input.pdf -resize 50% output.pdf
```

### cpdf (Coherent PDF)
```bash
# Merge
cpdf -merge doc1.pdf doc2.pdf -o merged.pdf

# Split every page
cpdf -split input.pdf -o page%%%.pdf

# Add page numbers
cpdf -add-text "Page %Page of %EndPage" -font "Helvetica" \
     -font-size 10 -bottomright 50 input.pdf -o numbered.pdf

# Scale pages
cpdf -scale-page "0.5 0.5" input.pdf -o scaled.pdf

# Two-up printing
cpdf -twoup input.pdf -o twopage.pdf
```

## Performance Optimization

### Processing Large PDFs
```python
# Use streaming for large files
from pypdf import PdfReader, PdfWriter

# Process page by page
reader = PdfReader("large.pdf")
for i, page in enumerate(reader.pages):
    # Process each page
    text = page.extract_text()

    # Clear memory if needed
    if i % 100 == 0:
        import gc
        gc.collect()
```

### Parallel Processing
```python
from concurrent.futures import ProcessPoolExecutor
import os

def process_pdf(pdf_path):
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    return len(reader.pages), pdf_path

pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_pdf, pdf_files))

for pages, path in results:
    print(f"{path}: {pages} pages")
```

## Troubleshooting

### Corrupted PDF
```bash
# Repair with qpdf
qpdf --linearize input.pdf repaired.pdf

# Or with Ghostscript
gs -o repaired.pdf -sDEVICE=pdfwrite input.pdf
```

### Cannot Extract Text
1. **Scanned PDF** - Use OCR (pytesseract + pdf2image)
2. **Protected PDF** - Decrypt first if you have permission
3. **Font issues** - Try pdfplumber which handles encoding better

### Memory Issues
```python
# Use incremental reading
from pypdf import PdfReader

reader = PdfReader("large.pdf")
# Process pages one at a time
for page in reader.pages:
    text = page.extract_text()
    # Process text immediately, don't store
    del text
```

### Encoding Issues
```python
# pdfplumber handles encoding better
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            # Handle encoding
            text = text.encode('utf-8', errors='replace').decode('utf-8')
```

## Installation Summary

### Python
```bash
pip install pypdf        # Basic operations
pip install pdfplumber   # Text/table extraction
pip install reportlab    # PDF creation
pip install pypdfium2    # High-performance rendering
pip install pytesseract  # OCR (requires tesseract installed)
pip install pdf2image    # PDF to image conversion
pip install pandas       # For table processing
pip install openpyxl     # For Excel export
```

### Node.js
```bash
npm install pdf-lib      # PDF manipulation
npm install @pdf-lib/fontkit  # Custom fonts
```

### System Tools (macOS)
```bash
brew install poppler     # pdftotext, pdfimages
brew install qpdf        # PDF manipulation
brew install ghostscript # PDF conversion
brew install tesseract   # OCR engine
```

### System Tools (Ubuntu/Debian)
```bash
sudo apt-get install poppler-utils
sudo apt-get install qpdf
sudo apt-get install ghostscript
sudo apt-get install tesseract-ocr
```
