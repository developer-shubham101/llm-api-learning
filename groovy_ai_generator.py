# ============================================================
# CLI VERSION (NON-STREAMLIT)
# Run:
# python groovy_ai_generator.py
# ============================================================

import requests
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from config import LLM_URL, MODEL

# ============================================================
# CONFIG
# ============================================================
OUTPUT_DIR = "generated_dataset"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# LLM CALL
# ============================================================
def ask_llm(system_prompt, user_prompt, temperature=0.7):
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "temperature": temperature,
        "max_tokens": 1200,
    }

    response = requests.post(LLM_URL, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

# ============================================================
# DOCUMENT PLANNER
# ============================================================
def plan_documents(user_prompt, num_files):
    planner_prompt = f'''
You are a dataset planning AI.

Generate a JSON array only.

User Request:
{user_prompt}

Create exactly {num_files} files.

Each item must contain:
- file_name
- document_type
- short_description
- temperature

Return valid JSON only.
'''

    raw = ask_llm(
        "You only output valid JSON.",
        planner_prompt,
        0.3,
    )

    raw = raw.replace("```json", "").replace("```", "")

    return json.loads(raw)

# ============================================================
# DOCUMENT GENERATOR
# ============================================================
def generate_document(company_name, item):
    file_name = item["file_name"]
    document_type = item["document_type"]
    short_description = item["short_description"]
    temperature = item.get("temperature", 0.7)

    content_prompt = f'''
Create realistic enterprise quality content.

Company Name:
{company_name}

Document Type:
{document_type}

Description:
{short_description}

Requirements:
- realistic
- detailed
- production style
- natural language
- no placeholders
- clean formatting
'''

    content = ask_llm(
        "You are an enterprise document generator AI.",
        content_prompt,
        temperature,
    )

    meta = {
        "file_name": file_name,
        "document_type": document_type,
        "company_name": company_name,
        "created_at": str(datetime.now()),
        "temperature": temperature,
        "source": "groovy-ai-local-llm",
        "model": MODEL,
        "tags": [document_type],
    }

    return {
        "file_name": file_name,
        "content": content,
        "meta": meta,
    }

# ============================================================
# SAVE FILES
# ============================================================
def save_document(dataset_folder, doc):
    txt_path = os.path.join(dataset_folder, f"{doc['file_name']}.txt")
    json_path = os.path.join(dataset_folder, f"{doc['file_name']}.meta.json")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(doc["content"])

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(doc["meta"], f, indent=2)

# ============================================================
# CLI INPUT
# ============================================================

def get_user_input():
    print("🚀 Groovy AI Dataset Generator")
    print("=" * 60)

    user_prompt = input(
        """
Describe what dataset you want to generate:
> """
    )

    company_name = input(
        """
Company / Dataset Name: """
    ) or "NovaByte Technologies"

    try:
        num_files = int(input(
            """
Number of Files: """
        ) or 10)
    except:
        num_files = 10

    try:
        parallel_workers = int(input(
            "Parallel Workers: "
        ) or 3)
    except:
        parallel_workers = 3

    return {
        "user_prompt": user_prompt,
        "company_name": company_name,
        "num_files": num_files,
        "parallel_workers": parallel_workers,
    }

# ============================================================
# GENERATION
# ============================================================
def main():

    config = get_user_input()

    user_prompt = config["user_prompt"]
    company_name = config["company_name"]
    num_files = config["num_files"]
    parallel_workers = config["parallel_workers"]

    print("\n🧠 Planning documents...")

    plan = plan_documents(user_prompt, num_files)

    print(f"✅ Planned {len(plan)} files")

    dataset_folder = os.path.join(
        OUTPUT_DIR,
        company_name.replace(" ", "_")
    )

    os.makedirs(dataset_folder, exist_ok=True)

    generated_docs = []

    def worker(item):
        return generate_document(company_name, item)

    print("\n⚡ Generating documents...")

    with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
        futures = []

        for item in plan:
            futures.append(executor.submit(worker, item))

        for idx, future in enumerate(futures):
            doc = future.result()

            save_document(dataset_folder, doc)
            generated_docs.append(doc)

            print(f"[{idx + 1}/{len(plan)}] Generated: {doc['file_name']}")

    print("\n✅ Dataset generation completed")
    print(f"📂 Saved to: {dataset_folder}")

    print("\nGenerated Files:")
    print("-" * 50)
    for doc in generated_docs:
        print(f"• {doc['file_name']}.txt")
        print(f"• {doc['file_name']}.meta.json")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")

# ============================================================
# OUTPUT STRUCTURE
# ============================================================
# ============================================================
# Streamlit UI section removed for CLI-only script.
# ============================================================
# RUN
# ============================================================
# streamlit run app.py
