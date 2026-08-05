import os
import subprocess
import markdown

md_path = "/Users/yusuf/Documents/Project/Persekutuan-Kewer-Mahasiswa/USER_GUIDE_AND_INSTALLATION.md"
html_path = "/Users/yusuf/Documents/Project/Persekutuan-Kewer-Mahasiswa/USER_GUIDE_AND_INSTALLATION.html"
pdf_path = "/Users/yusuf/Documents/Project/Persekutuan-Kewer-Mahasiswa/USER_GUIDE_AND_INSTALLATION.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Convert markdown to html with extra extensions (tables, fenced code, toc, nl2br)
html_body = markdown.markdown(
    md_content,
    extensions=['extra', 'tables', 'fenced_code', 'codehilite', 'nl2br', 'sane_lists']
)

# Custom enterprise PDF styling
html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>KIDECO Fuel Ratio AI - Installation & User Guide</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

@page {{
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {{
        content: counter(page);
    }}
}}

* {{
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.6;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
}}

h1, h2, h3, h4, h5, h6 {{
    color: #0f172a;
    font-weight: 700;
    line-height: 1.25;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}}

h1 {{
    font-size: 20pt;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 8px;
    margin-top: 0;
    color: #0369a1;
}}

h2 {{
    font-size: 14.5pt;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 1.8em;
    color: #0f172a;
}}

h3 {{
    font-size: 12pt;
    color: #334155;
}}

p {{
    margin-top: 0;
    margin-bottom: 0.8em;
}}

a {{
    color: #0284c7;
    text-decoration: none;
}}

ul, ol {{
    margin-top: 0;
    margin-bottom: 0.8em;
    padding-left: 1.5em;
}}

li {{
    margin-bottom: 0.3em;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 9pt;
    page-break-inside: avoid;
}}

th, td {{
    border: 1px solid #cbd5e1;
    padding: 7px 10px;
    text-align: left;
}}

th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
}}

tr:nth-child(even) {{
    background-color: #f8fafc;
}}

code {{
    font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
    font-size: 8.5pt;
    background-color: #f1f5f9;
    color: #0f766e;
    padding: 2px 5px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
}}

pre {{
    background-color: #0f172a;
    color: #f8fafc;
    padding: 12px 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 8.5pt;
    line-height: 1.45;
    margin: 0.8em 0;
    page-break-inside: avoid;
}}

pre code {{
    background-color: transparent;
    color: inherit;
    padding: 0;
    border: none;
    font-size: 8.5pt;
}}

blockquote {{
    border-left: 4px solid #0284c7;
    background-color: #f0f9ff;
    padding: 10px 14px;
    margin: 1em 0;
    border-radius: 0 6px 6px 0;
    color: #0369a1;
    font-size: 9.5pt;
}}

hr {{
    border: 0;
    height: 1px;
    background: #e2e8f0;
    margin: 1.5em 0;
}}

.header-badge {{
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 8pt;
    margin-bottom: 12px;
}}
</style>
</head>
<body>
<div class="header-badge">PT KIDECO JAYA AGUNG • AI FUEL RATIO SYSTEM</div>
{html_body}
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("HTML generated successfully at:", html_path)

# Execute headless Chrome to generate PDF
chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print("PDF generated successfully at:", pdf_path)
    file_size = os.path.getsize(pdf_path)
    print(f"PDF File Size: {file_size:,} bytes")
else:
    print("Chrome Error:", res.stderr)
