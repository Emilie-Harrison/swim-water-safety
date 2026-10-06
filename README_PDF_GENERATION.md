# PDF Generation — Setup & Instructions

This guide explains how to regenerate all PDFs from the updated HTML files on your own computer, with the lighter blue covers.

---

## What you need

- Your computer (Windows, Mac, or Linux)
- **Google Chrome** (you almost certainly already have it)
- **Python 3.8 or later** (free download if not already installed)
- The updated HTML files from `swim-water-safety-COMPLETE.zip`

---

## Step 1 — Check Python is installed

Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows).

Type this and press Enter:

```
python3 --version
```

You should see something like `Python 3.11.2`. If you get an error, download Python from [python.org/downloads](https://www.python.org/downloads/) and install it. Accept all defaults during installation.

> **Windows users:** during installation, tick the box that says **"Add Python to PATH"**.

---

## Step 2 — Unzip the repository

Unzip `swim-water-safety-COMPLETE.zip` to a folder on your computer.

For example: `Documents/swim-water-safety/`

Place both files — `generate_pdfs.py` and `README_PDF_GENERATION.md` — **inside that same folder**, alongside all the `.html` files.

Your folder should look like:

```
swim-water-safety/
├── generate_pdfs.py           ← the script
├── README_PDF_GENERATION.md   ← this file
├── swim_safety_teacher_workbook.html
├── swim_safety_student_workbook.html
├── advanced_water_safety_year910_workbook.html
├── ... (all other .html files)
└── pdf_output/                ← will be created automatically
```

---

## Step 3 — Run the script

Open Terminal (Mac/Linux) or Command Prompt (Windows).

Navigate to your folder. For example:

**Mac/Linux:**
```bash
cd ~/Documents/swim-water-safety
```

**Windows:**
```
cd C:\Users\YourName\Documents\swim-water-safety
```

Then run:

```
python3 generate_pdfs.py
```

> **Windows users:** if `python3` doesn't work, try `python generate_pdfs.py` instead.

---

## What happens next

The script will:

1. Auto-detect Google Chrome on your computer
2. Work through each HTML file one by one
3. Apply the lighter blue cover colours
4. Save each PDF into a new `pdf_output/` folder

You'll see progress as it runs:

```
============================================================
  Swim & Water Safety — PDF Generator
============================================================

✓  Chrome found: /Applications/Google Chrome.app/...
✓  Output folder: /Users/harry/Documents/swim-water-safety/pdf_output

Generating 40 PDFs...

  [ 1/40] swim_safety_teacher_workbook.html ... ✓  793 KB
  [ 2/40] swim_safety_student_workbook.html ... ✓  6,245 KB
  [ 3/40] swim_safety_lesson_outline_year7.html ... ✓  4,863 KB
  ...

============================================================
  Done: 40 succeeded, 0 failed
  PDFs saved to: /Users/harry/Documents/swim-water-safety/pdf_output
============================================================
```

The whole run takes roughly **3–8 minutes** depending on your computer.

---

## Uploading back to GitHub

Once the PDFs are generated:

1. Copy all `.pdf` files from `pdf_output/` into the main `swim-water-safety/` folder (replacing the old ones)
2. Go to your GitHub repository at `github.com/iainharry/swim-water-safety`
3. Drag and drop the PDF files onto the repository page, or use GitHub Desktop to commit and push

---

## Troubleshooting

### "Chrome not found"

The script couldn't find Chrome automatically. Open `generate_pdfs.py` in a text editor, find this line near the top:

```python
CHROME_PATH = None
```

Change it to the full path to your Chrome installation. For example:

**Mac:**
```python
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

**Windows:**
```python
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

Save the file and run the script again.

---

### "python3: command not found" (Windows)

Try `python` instead of `python3`:

```
python generate_pdfs.py
```

If that also fails, Python isn't installed — download it from [python.org/downloads](https://www.python.org/downloads/).

---

### A few PDFs show as FAILED

Run the script again — Chrome occasionally times out on large files on the first attempt. If a file keeps failing, open it in Chrome and use **File → Print → Save as PDF** manually as a fallback.

---

### PDFs look correct but fonts seem different

This is normal if Chrome renders slightly differently to the original. The fonts (Poppins, DM Sans, DM Mono) are loaded from Google Fonts, so your computer needs internet access while generating. If working offline, the PDFs will fall back to system fonts but all content will still be correct.

---

## Changing the cover colour

If you want to adjust the blue shade further, open `generate_pdfs.py` in a text editor and find the `COLOUR_MAP` section near the top. The values are standard CSS hex colour codes — you can change the "new" values (right side) to any colour you prefer.

For reference, the current lighter blue palette uses:
- `#1565C0` — medium blue (cover start)
- `#2196F3` — standard blue (cover mid)
- `#42A5F5` / `#64B5F6` / `#90CAF9` — light blues (cover end)

A useful tool for picking colours: [coolors.co](https://coolors.co)

---

## Re-running after future HTML edits

Any time you update the HTML files (e.g. after further curriculum updates), simply run the script again. It will overwrite the existing PDFs in `pdf_output/` with fresh versions.

---

*Script prepared May 2026. Compatible with Chrome 112+ and Python 3.8+.*
