import json
import os
from typing import List, Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path) as f:
        return json.load(f)

def parse_fixed_line(line: str, widths: List[int]) -> List[str]:
    pos = 0
    return [line[pos + sum(widths[:i]):pos + sum(widths[:i+1])].strip() for i in range(len(widths))]

def parse_delimited_line(line: str, delimiter: str) -> List[str]:
    return line.strip().split(delimiter)

def load_file(filepath: str, config: Dict[str, Any]) -> Dict[Any, Dict[str, str]]:
    data = {}
    with open(filepath) as f:
        for line in f:
            if config["file_type"] == "fixed":
                fields = parse_fixed_line(line, config["field_widths"])
            else:
                fields = parse_delimited_line(line, config["delimiter"])
            record = dict(zip(config["field_names"], fields))
            key = tuple(record[k] for k in config["key_fields"]) if config.get("key_fields") else line
            data[key] = record
    return data

def compare_files(data1: Dict, data2: Dict, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    field_names = [f for f in config["field_names"] if f not in config["ignore_fields"]]
    all_keys = set(data1.keys()).union(set(data2.keys()))
    differences = []

    for key in all_keys:
        row1 = data1.get(key)
        row2 = data2.get(key)
        if row1 != row2:
            row_diff = {"key": key, "differences": {}}
            for field in field_names:
                val1 = row1.get(field) if row1 else "<MISSING>"
                val2 = row2.get(field) if row2 else "<MISSING>"
                if val1 != val2:
                    row_diff["differences"][field] = {"file1": val1, "file2": val2}
            if row_diff["differences"]:
                differences.append(row_diff)
    return differences

def save_diff_to_html(diff_result: List[Dict[str, Any]], output_file="comparison_report.html"):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Comparison Report</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f2f2f2; }
            tr:hover { background-color: #f5f5f5; }
            .highlight { background-color: #fff3cd; }
        </style>
    </head>
    <body>
        <h2>File Comparison Report</h2>
        <table>
            <tr>
                <th>Key</th>
                <th>Field</th>
                <th>File1 Value</th>
                <th>File2 Value</th>
            </tr>
    """

    for item in diff_result:
        key_str = ", ".join(item['key']) if isinstance(item['key'], tuple) else str(item['key'])
        for field, vals in item["differences"].items():
            html += f"""
                <tr class="highlight">
                    <td>{key_str}</td>
                    <td>{field}</td>
                    <td>{vals['file1']}</td>
                    <td>{vals['file2']}</td>
                </tr>
            """

    html += """
        </table>
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML report saved at: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    config = load_config("config.json")
    file1_data = load_file("file1.txt", config)
    file2_data = load_file("file2.txt", config)
    differences = compare_files(file1_data, file2_data, config)
    save_diff_to_html(differences, output_file="diff_report.html")
