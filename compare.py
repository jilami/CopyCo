import html
from pathlib import Path
import json

# Sample config
config = {
    "delimiter": ",",  # Set to None for fixed-length
    "field_names": ["ID", "Name", "Age", "City"],
    "exclude_fields": ["Age"],
    "field_lengths": [5, 10, 3, 10],  # Used if delimiter is None
    "key_fields": ["ID"]  # Optional, can be empty
}

# Example input lines (you can read from files instead)
file1_lines = [
    "00123,John Doe ,25,New York",
    "00124,Jane Doe ,30,Chicago",
    "00125,Jim Beam ,28,Boston"
]

file2_lines = [
    "00123,John Doe ,26,New York",
    "00124,Jane Doe ,30,Houston",
    "00126,Jim Beam ,28,Boston"
]

def parse_line(line, config):
    if config["delimiter"] is not None:
        parts = [p.strip() for p in line.split(config["delimiter"])]
    else:
        parts = []
        idx = 0
        for length in config["field_lengths"]:
            parts.append(line[idx:idx+length].strip())
            idx += length
    return dict(zip(config["field_names"], parts))

def build_key(row, keys):
    return tuple(row.get(k, "") for k in keys)

# Parse both files
parsed1 = [parse_line(line, config) for line in file1_lines]
parsed2 = [parse_line(line, config) for line in file2_lines]

# Build comparison index
if config["key_fields"]:
    dict1 = {build_key(r, config["key_fields"]): r for r in parsed1}
    dict2 = {build_key(r, config["key_fields"]): r for r in parsed2}
    all_keys = sorted(set(dict1.keys()) | set(dict2.keys()))
else:
    dict1 = dict(enumerate(parsed1))
    dict2 = dict(enumerate(parsed2))
    all_keys = sorted(set(dict1.keys()) | set(dict2.keys()))

# Create rows with onclick and mismatches
html_rows = []
for key in all_keys:
    r1 = dict1.get(key, {})
    r2 = dict2.get(key, {})
    row1_cells = []
    row2_cells = []

    for field in config["field_names"]:
        if field in config["exclude_fields"]:
            continue
        val1 = html.escape(r1.get(field, ""))
        val2 = html.escape(r2.get(field, ""))
        if val1 != val2:
            row1_cells.append(f"<td data-mismatch='true'>{val1}</td>")
            row2_cells.append(f"<td data-mismatch='true'>{val2}</td>")
        else:
            row1_cells.append(f"<td>{val1}</td>")
            row2_cells.append(f"<td>{val2}</td>")

    html_rows.append(f"<tr class='file1' onclick='highlightRow(this)'>{''.join(row1_cells)}</tr>")
    html_rows.append(f"<tr class='file2' onclick='highlightRow(this)'>{''.join(row2_cells)}</tr>")

# Assemble HTML output
html_template = f"""
<html>
<head>
<style>
.scrollable-table {{
  overflow-x: auto;
  overflow-y: auto;
  height: 500px;
  border: 1px solid #ccc;
}}
table {{
  border-collapse: collapse;
  width: max-content;
  min-width: 100%;
  table-layout: fixed;
}}
th, td {{
  border: 1px solid #999;
  padding: 6px;
  white-space: nowrap;
  font-size: 13px;
  background-color: white;
}}
thead th {{
  position: sticky;
  top: 0;
  background: #f1f1f1;
  z-index: 4;
}}
td[data-mismatch='true'] {{
  background-color: #fdd;
}}
tr.file2 td[data-mismatch='true'] {{
  background-color: #fbb;
}}
tr.selected-row td {{
  background-color: #ffffcc !important;
}}
</style>
<script>
function highlightRow(row) {{
  document.querySelectorAll("tr").forEach(r => {{
    r.classList.remove("selected-row");
  }});
  row.classList.add("selected-row");
}}
</script>
</head>
<body>
<div class="scrollable-table">
  <table>
    <thead>
      <tr>{"".join(f"<th>{html.escape(f)}</th>" for f in config["field_names"] if f not in config["exclude_fields"])}</tr>
    </thead>
    <tbody>
      {''.join(html_rows)}
    </tbody>
  </table>
</div>
</body>
</html>
"""

# Save to file
output_path = "file_comparison_clickable_highlight.html"
Path(output_path).write_text(html_template)
print(f"✅ HTML file created: {output_path}")
