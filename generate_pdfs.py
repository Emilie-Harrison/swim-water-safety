#!/usr/bin/env python3
"""
Swim & Water Safety — Local PDF Generator
==========================================
Generates PDFs from the updated HTML files using Chrome/Chromium headless.
Applies lighter blue cover colours as requested.

Requirements: Python 3.8+, Google Chrome or Chromium
See README_PDF_GENERATION.md for full setup instructions.
"""

import os
import re
import sys
import shutil
import tempfile
import subprocess
import platform
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — edit these if needed
# ─────────────────────────────────────────────────────────────────────────────

# Folder containing the HTML files (default: same folder as this script)
HTML_DIR = Path(__file__).parent

# Where to save the generated PDFs (default: pdf_output/ next to this script)
OUTPUT_DIR = HTML_DIR / "pdf_output"

# Chrome executable path — leave as None to auto-detect
CHROME_PATH = None  # e.g. r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# ─────────────────────────────────────────────────────────────────────────────
# COVER COLOUR LIGHTENING
# Old dark navy/near-black covers → lighter mid-blue palette
# ─────────────────────────────────────────────────────────────────────────────

COLOUR_MAP = [
    # Very dark navy → medium blue
    ("#020c1a", "#1565C0"),
    ("#050d1e", "#1565C0"),
    # Dark navy mid-stops → standard blue
    ("#0a1e3d", "#2196F3"),
    # Dark blue start stops → lighter
    ("#003554", "#1976D2"),
    ("#005f8c", "#2196F3"),
    ("#005F8C", "#2196F3"),
    ("#006494", "#2196F3"),
    # End blues — lightened
    ("#1565c0", "#42A5F5"),
    ("#1565C0", "#42A5F5"),
    ("#0582CA", "#64B5F6"),
    ("#00A6FB", "#90CAF9"),
    # curr-strip bar below cover
    ("#0a1e3d", "#1565C0"),
]

# ─────────────────────────────────────────────────────────────────────────────
# HTML FILES TO CONVERT
# Files excluded: index.html (website nav page), interactive tools,
# student_digital_portfolio (web-only), swim_safety_student_workbook_PRINT
# (separate print layout), water_safety_interactive_quiz (JS-only tool)
# ─────────────────────────────────────────────────────────────────────────────

PDF_TARGETS = [
    # Year 7–8 core resources
    "swim_safety_teacher_workbook.html",
    "swim_safety_student_workbook.html",
    "swim_safety_lesson_outline_year7.html",
    "swim_safety_workbook_simplified.html",
    "swim_safety_workbook_extension.html",
    "pool_practical_companion_unit.html",
    # Year 9–10 core resources
    "advanced_water_safety_year910_teacher.html",
    "advanced_water_safety_year910_workbook.html",
    "advanced_water_safety_year910_lesson_outline.html",
    "advanced_water_safety_year910_rubric.html",
    "advanced_water_safety_year910_scaffolded.html",
    "advanced_water_safety_year910_extension.html",
    "advanced_water_safety_year910_data_pack.html",
    "advanced_water_safety_year910_community_project.html",
    "advanced_water_safety_year910_parent_info.html",
    "advanced_water_safety_year910_quiz_bank.html",
    "advanced_water_safety_year910_webquest.html",
    "advanced_water_safety_year910_practical_integration.html",
    "advanced_water_safety_year910_literacy_unit.html",
    "advanced_water_safety_year910_guest_speaker.html",
    # Shared resources
    "water_safety_unit_overview.html",
    "water_safety_assessment_gradebook.html",
    "water_safety_glossary.html",
    "water_safety_quiz_question_bank.html",
    "water_safety_relief_teacher_pack.html",
    "water_safety_scenario_cards.html",
    "water_safety_debate_framework.html",
    "water_safety_diverse_learners.html",
    "water_safety_cultural_considerations.html",
    "water_safety_excursion_risk_management.html",
    "water_safety_student_self_assessment.html",
    "water_safety_teacher_professional_learning.html",
    "water_safety_resource_directory.html",
    "water_safety_feedback_form.html",
    "water_safety_parent_info_sheet.html",
    "water_safety_parent_info_multilingual.html",
    "water_safety_myths_facts_poster.html",
    "water_safety_poster_pack.html",  # via swim_safety_poster_pack
    "swim_safety_poster_pack.html",
    "swimming_carnival_student_briefing.html",
    "swimming_carnival_safety_briefing.html",
    "swim_water_safety_australian_curriculum_alignment.html",
    "Copyright_Ownership_Licensing_Summary.html",
]


# ─────────────────────────────────────────────────────────────────────────────
# CHROME DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def find_chrome():
    """Auto-detect Chrome/Chromium executable path."""
    if CHROME_PATH and Path(CHROME_PATH).exists():
        return CHROME_PATH

    system = platform.system()

    if system == "Darwin":  # macOS
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
    elif system == "Windows":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Chromium\Application\chrome.exe",
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        ]
    else:  # Linux
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]

    for path in candidates:
        if Path(path).exists():
            return path

    # Try PATH
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found

    return None


# ─────────────────────────────────────────────────────────────────────────────
# HTML PREPARATION
# ─────────────────────────────────────────────────────────────────────────────

def prepare_html(source_path: Path, tmp_dir: str) -> Path:
    """
    Create a modified copy of the HTML with lighter cover colours.
    Returns path to the temporary modified file.
    """
    content = source_path.read_text(encoding="utf-8")

    # Apply colour lightening only inside <style> blocks
    def lighten_styles(html: str) -> str:
        result = []
        i = 0
        while i < len(html):
            style_start = html.find("<style", i)
            if style_start == -1:
                result.append(html[i:])
                break
            result.append(html[i:style_start])
            style_end = html.find("</style>", style_start)
            if style_end == -1:
                result.append(html[style_start:])
                break
            block = html[style_start : style_end + 8]
            for old, new in COLOUR_MAP:
                block = block.replace(old, new)
            result.append(block)
            i = style_end + 8
        return "".join(result)

    content = lighten_styles(content)

    # Write modified HTML to temp file
    tmp_path = Path(tmp_dir) / f"_tmp_{source_path.name}"
    tmp_path.write_text(content, encoding="utf-8")
    return tmp_path


# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(chrome: str, html_path: Path, output_path: Path) -> bool:
    """Render an HTML file to PDF using Chrome headless."""
    # Convert to file:// URL (Chrome requires absolute path)
    file_url = html_path.as_uri()

    cmd = [
        chrome,
        "--headless=new",           # Modern headless mode (Chrome 112+)
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-web-security",   # Allows local file:// access to fonts/resources
        "--allow-file-access-from-files",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",  # Wait up to 5s for JS/fonts to load
        f"--print-to-pdf={output_path}",
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        file_url,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return output_path.exists() and output_path.stat().st_size > 10_000
    except subprocess.TimeoutExpired:
        print(f"    ⚠ Timeout rendering {html_path.name}")
        return False
    except Exception as e:
        print(f"    ⚠ Error: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Swim & Water Safety — PDF Generator")
    print("=" * 60)

    # Find Chrome
    chrome = find_chrome()
    if not chrome:
        print(
            "\n❌  Chrome/Chromium not found.\n"
            "    Install Google Chrome and try again, or set CHROME_PATH\n"
            "    at the top of this script.\n"
            "    Download: https://www.google.com/chrome/\n"
        )
        sys.exit(1)
    print(f"\n✓  Chrome found: {chrome}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓  Output folder: {OUTPUT_DIR}\n")

    # Filter to files that actually exist
    targets = [f for f in PDF_TARGETS if (HTML_DIR / f).exists()]
    missing_html = [f for f in PDF_TARGETS if not (HTML_DIR / f).exists()]

    if missing_html:
        print(f"⚠  Skipping {len(missing_html)} HTML files not found in {HTML_DIR}:")
        for f in missing_html:
            print(f"     - {f}")
        print()

    print(f"Generating {len(targets)} PDFs...\n")

    # Use a temp directory for modified HTML files
    with tempfile.TemporaryDirectory() as tmp_dir:
        results = {"ok": [], "failed": []}

        for i, html_name in enumerate(targets, 1):
            html_path = HTML_DIR / html_name
            pdf_name = html_path.stem + ".pdf"
            output_path = OUTPUT_DIR / pdf_name

            print(f"  [{i:2}/{len(targets)}] {html_name}", end=" ... ", flush=True)

            # Prepare modified HTML with lighter colours
            tmp_html = prepare_html(html_path, tmp_dir)

            # Generate PDF
            ok = generate_pdf(chrome, tmp_html, output_path)

            if ok:
                size_kb = output_path.stat().st_size // 1024
                print(f"✓  {size_kb:,} KB")
                results["ok"].append(pdf_name)
            else:
                print("✗  FAILED")
                results["failed"].append(pdf_name)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  Done: {len(results['ok'])} succeeded, {len(results['failed'])} failed")
    if results["failed"]:
        print("\n  Failed files:")
        for f in results["failed"]:
            print(f"    - {f}")
    print(f"\n  PDFs saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
