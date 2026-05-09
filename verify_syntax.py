import json
import ast
import sys

def verify_syntax(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            # replace colab magic commands with pass
            source_lines = source.split("\n")
            cleaned_source = "\n".join([line if not line.strip().startswith("!") else "pass" for line in source_lines])
            try:
                ast.parse(cleaned_source)
            except SyntaxError as e:
                print(f"Syntax error in {file_path} cell {i}: {e}")
                print(cleaned_source)
                sys.exit(1)
    print(f"{file_path} syntax OK")

verify_syntax("colab/Lab22_DPO_T4.ipynb")
verify_syntax("colab/Lab22_DPO_BigGPU.ipynb")
