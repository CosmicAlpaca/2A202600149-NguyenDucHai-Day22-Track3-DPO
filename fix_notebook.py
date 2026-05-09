import json

def fix_notebook(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = cell.get("source", [])
            # Convert list of strings to string
            source_str = "".join(source)
            if "def format_alpaca_to_chat(row):" in source_str:
                print(f"Found format_alpaca_to_chat in {file_path}")
                # Replace the old function implementation
                # The old implementation is roughly:
                new_source_str = source_str.replace(
                    "    if row.get(\"instruction\"):\n        prompt = row[\"instruction\"]\n        if row.get(\"input\"):\n            prompt += \"\\n\\n\" + row[\"input\"]\n        messages.append({\"role\": \"user\", \"content\": prompt})\n\n    if row.get(\"output\"):\n        messages.append({\"role\": \"assistant\", \"content\": row[\"output\"]})",
                    "    instruction = row.get(\"instruction_vi\") or row.get(\"instruction\")\n    input_text = row.get(\"input_vi\") or row.get(\"input\")\n    output = row.get(\"output_vi\") or row.get(\"output\")\n\n    if instruction:\n        prompt = instruction\n        if input_text:\n            prompt += \"\\n\\n\" + input_text\n        messages.append({\"role\": \"user\", \"content\": prompt})\n\n    if output:\n        messages.append({\"role\": \"assistant\", \"content\": output})"
                )
                
                if "ds_formatted = ds_formatted.filter(lambda x: x[\"text\"] != \"\")" not in new_source_str:
                     new_source_str = new_source_str.replace(
                         "ds_formatted = ds.map(format_alpaca_to_chat, remove_columns=ds.column_names)",
                         "ds_formatted = ds.map(format_alpaca_to_chat, remove_columns=ds.column_names)\nds_formatted = ds_formatted.filter(lambda x: x[\"text\"] != \"\")"
                     )

                # Convert string back to list of strings
                # splitlines(True) keeps the \n character
                cell["source"] = [s + "\n" for s in new_source_str.split("\n")]
                # remove the last \n if it wasn't there
                if not new_source_str.endswith("\n") and len(cell["source"]) > 0:
                     cell["source"][-1] = cell["source"][-1][:-1]

    with open(file_path, "w", encoding="utf-8") as f:
        # colab json is typically unformatted (minified)
        json.dump(nb, f, ensure_ascii=False, separators=(',', ':'))

fix_notebook("colab/Lab22_DPO_T4.ipynb")
fix_notebook("colab/Lab22_DPO_BigGPU.ipynb")
