# PDF Forms Guide

This guide covers filling out PDF forms programmatically using Python and JavaScript libraries.

## Python: pypdf (AcroForms)

### List Form Fields
```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_fields()

for field_name, field_data in fields.items():
    print(f"Field: {field_name}")
    print(f"  Type: {field_data.get('/FT', 'Unknown')}")
    print(f"  Value: {field_data.get('/V', 'Empty')}")
```

### Fill Form Fields
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

# Clone pages from reader
writer.append(reader)

# Fill fields
writer.update_page_form_field_values(
    writer.pages[0],
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "555-1234",
    }
)

with open("filled_form.pdf", "wb") as output:
    writer.write(output)
```

### Fill Checkboxes and Radio Buttons
```python
# For checkboxes, use the export value (often "/Yes" or "/1")
writer.update_page_form_field_values(
    writer.pages[0],
    {
        "agree_terms": "/Yes",  # Check the box
        "newsletter": "/Off",   # Uncheck
        "gender": "/Male",      # Radio button value
    }
)
```

### Fill Dropdown/Combo Boxes
```python
# Use the exact option value from the PDF
writer.update_page_form_field_values(
    writer.pages[0],
    {
        "country": "United States",
        "state": "California",
    }
)
```

## JavaScript: pdf-lib (Node.js)

### Install
```bash
npm install pdf-lib
```

### List Form Fields
```javascript
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

async function listFields(pdfPath) {
    const pdfBytes = fs.readFileSync(pdfPath);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const form = pdfDoc.getForm();

    const fields = form.getFields();
    fields.forEach(field => {
        const name = field.getName();
        const type = field.constructor.name;
        console.log(`${name} (${type})`);
    });
}

listFields('form.pdf');
```

### Fill Text Fields
```javascript
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

async function fillForm(inputPath, outputPath) {
    const pdfBytes = fs.readFileSync(inputPath);
    const pdfDoc = await PDFDocument.load(pdfBytes);
    const form = pdfDoc.getForm();

    // Fill text fields
    form.getTextField('first_name').setText('John');
    form.getTextField('last_name').setText('Doe');
    form.getTextField('email').setText('john@example.com');

    // Fill checkbox
    form.getCheckBox('agree_terms').check();

    // Fill dropdown
    form.getDropdown('country').select('United States');

    // Fill radio group
    form.getRadioGroup('gender').select('Male');

    // Flatten form (make fields non-editable)
    form.flatten();

    const filledPdfBytes = await pdfDoc.save();
    fs.writeFileSync(outputPath, filledPdfBytes);
}

fillForm('form.pdf', 'filled_form.pdf');
```

### Create New Form Fields
```javascript
const { PDFDocument, rgb } = require('pdf-lib');

async function createForm() {
    const pdfDoc = await PDFDocument.create();
    const page = pdfDoc.addPage([550, 750]);
    const form = pdfDoc.getForm();

    // Add text field
    const nameField = form.createTextField('name');
    nameField.setText('');
    nameField.addToPage(page, {
        x: 50,
        y: 700,
        width: 200,
        height: 20,
    });

    // Add checkbox
    const checkbox = form.createCheckBox('agree');
    checkbox.addToPage(page, {
        x: 50,
        y: 650,
        width: 15,
        height: 15,
    });

    // Add dropdown
    const dropdown = form.createDropdown('country');
    dropdown.addOptions(['USA', 'Canada', 'UK', 'Other']);
    dropdown.select('USA');
    dropdown.addToPage(page, {
        x: 50,
        y: 600,
        width: 150,
        height: 20,
    });

    const pdfBytes = await pdfDoc.save();
    require('fs').writeFileSync('new_form.pdf', pdfBytes);
}

createForm();
```

## Common Field Types

| Type | pypdf Code | pdf-lib Method |
|------|------------|----------------|
| Text | `/Tx` | `getTextField()` |
| Checkbox | `/Btn` (with `/AS`) | `getCheckBox()` |
| Radio | `/Btn` (with `/Kids`) | `getRadioGroup()` |
| Dropdown | `/Ch` | `getDropdown()` |
| List | `/Ch` | `getOptionList()` |
| Signature | `/Sig` | `getSignature()` |

## Troubleshooting

### Field Not Found
```python
# Get exact field names
reader = PdfReader("form.pdf")
print(list(reader.get_fields().keys()))
```

### Field Value Not Appearing
Some PDFs require "flattening" to make values visible:
```python
# pypdf - set need_appearances
writer = PdfWriter()
writer.append(reader)
writer.update_page_form_field_values(...)

# Force appearance generation
if "/AcroForm" in writer._root_object:
    writer._root_object["/AcroForm"].update({
        NameObject("/NeedAppearances"): BooleanObject(True)
    })
```

```javascript
// pdf-lib - flatten form
form.flatten();
```

### XFA Forms (Complex Forms)
XFA forms (XML-based) are not supported by most libraries. Options:
1. Use Adobe Acrobat to convert to AcroForm
2. Use pdftk to fill: `pdftk form.pdf fill_form data.fdf output filled.pdf`
3. Use a commercial solution like Adobe PDF Services API

### Locked/Encrypted Forms
```python
# Check if PDF is encrypted
reader = PdfReader("form.pdf")
if reader.is_encrypted:
    reader.decrypt("password")  # If you know the password
```

## Best Practices

1. **Always inspect fields first** - List all field names and types before filling
2. **Match exact values** - Use the exact export values for checkboxes/radios
3. **Test with a viewer** - Some viewers render forms differently
4. **Flatten when sharing** - Flatten forms to prevent editing
5. **Preserve original** - Always save to a new file, don't overwrite the template
