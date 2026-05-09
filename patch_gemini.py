import json

def patch_gemini(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            
            # Patch Colab Secrets
            if "for key in [\"OPENAI_API_KEY\", \"ANTHROPIC_API_KEY\", \"WANDB_API_KEY\"]:" in source:
                new_source = source.replace(
                    "for key in [\"OPENAI_API_KEY\", \"ANTHROPIC_API_KEY\", \"WANDB_API_KEY\"]:",
                    "for key in [\"OPENAI_API_KEY\", \"ANTHROPIC_API_KEY\", \"GEMINI_API_KEY\", \"WANDB_API_KEY\"]:"
                )
                cell["source"] = [s + "\n" for s in new_source.split("\n")]
                if not new_source.endswith("\n") and len(cell["source"]) > 0:
                     cell["source"][-1] = cell["source"][-1][:-1]
                source = new_source

            # Patch install_packages
            if "reqs = [" in source and "\"openai\", \"anthropic\"" in source:
                new_source = source.replace(
                    "\"openai\", \"anthropic\"",
                    "\"openai\", \"anthropic\", \"google-genai\""
                )
                cell["source"] = [s + "\n" for s in new_source.split("\n")]
                if not new_source.endswith("\n") and len(cell["source"]) > 0:
                     cell["source"][-1] = cell["source"][-1][:-1]
                source = new_source

            # Patch Judge Functions
            if "def judge_with_openai(rows):" in source and "def judge_with_anthropic(rows):" in source:
                if "def judge_with_gemini(rows):" not in source:
                    gemini_func = """
def judge_with_gemini(rows):
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None
    client = genai.Client()
    results = []
    for p, sft, dpo in zip(EVAL_PROMPTS, sft_outputs, dpo_outputs):
        msg = JUDGE_PROMPT_TEMPLATE.format(
            prompt=p["prompt"], category=p["category"], sft=sft, dpo=dpo
        )
        try:
            resp = client.models.generate_content(
                model=os.environ.get("JUDGE_MODEL", "gemini-2.5-flash"),
                contents=msg,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                )
            )
            parsed = json.loads(resp.text)
        except Exception as e:
            parsed = {"winner": "tie", "justification": f"Gemini error: {e}"[:200]}
        
        parsed["id"] = p["id"]
        parsed["category"] = p["category"]
        results.append(parsed)
    return results
"""
                    new_source = source + "\n" + gemini_func
                    cell["source"] = [s + "\n" for s in new_source.split("\n")]
                    if not new_source.endswith("\n") and len(cell["source"]) > 0:
                         cell["source"][-1] = cell["source"][-1][:-1]
                    source = new_source

            # Patch Execution Logic
            if "if os.environ.get(\"OPENAI_API_KEY\"):" in source and "elif os.environ.get(\"ANTHROPIC_API_KEY\"):" in source:
                if "elif os.environ.get(\"GEMINI_API_KEY\"):" not in source:
                    new_source = source.replace(
                        "elif os.environ.get(\"ANTHROPIC_API_KEY\"):\n    print(\"Found ANTHROPIC_API_KEY — running claude-haiku judge\")\n    judge_results = judge_with_anthropic(rows)",
                        "elif os.environ.get(\"ANTHROPIC_API_KEY\"):\n    print(\"Found ANTHROPIC_API_KEY — running claude-haiku judge\")\n    judge_results = judge_with_anthropic(rows)\nelif os.environ.get(\"GEMINI_API_KEY\"):\n    print(\"Found GEMINI_API_KEY — running gemini judge\")\n    judge_results = judge_with_gemini(rows)"
                    )
                    cell["source"] = [s + "\n" for s in new_source.split("\n")]
                    if not new_source.endswith("\n") and len(cell["source"]) > 0:
                         cell["source"][-1] = cell["source"][-1][:-1]
                    source = new_source

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, separators=(',', ':'))

patch_gemini("colab/Lab22_DPO_T4.ipynb")
patch_gemini("colab/Lab22_DPO_BigGPU.ipynb")
