import streamlit as st
import requests
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# CONFIG
# ============================================================
from config import LLM_URL, MODEL
OUTPUT_DIR = "generated_dataset"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Groovy AI Dataset Generator",
    layout="wide",
)

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
# UI
# ============================================================
st.title("🚀 Groovy AI Dataset Generator")
st.caption("Generate enterprise-grade synthetic datasets using your local LLM")

left, right = st.columns([2, 1])

with left:
    user_prompt = st.text_area(
        "Describe what dataset you want to generate",
        height=220,
        value="Create 20 files for a dummy company docs like about company, founder info, HR/contact details, privacy policy, terms and conditions, employee handbook, technical architecture and marketing strategy.",
    )

with right:
    st.subheader("⚙️ Settings")

    company_name = st.text_input(
        "Company / Dataset Name",
        value="NovaByte Technologies",
    )

    num_files = st.slider(
        "Number of Files",
        1,
        100,
        20,
    )

    default_temperature = st.slider(
        "Creativity",
        0.0,
        1.5,
        0.7,
    )

    parallel_workers = st.slider(
        "Parallel Workers",
        1,
        10,
        3,
    )

    category = st.selectbox(
        "Dataset Type",
        [
            "Enterprise",
            "Education",
            "Technical",
            "Legal",
            "Healthcare",
            "Story",
        ],
    )

# ============================================================
# EXAMPLES
# ============================================================
st.divider()

st.subheader("💡 Example Prompts")

examples = [
    "Create 20 files for a dummy company docs like about company, founder info, HR/contact details, privacy policy and terms.",
    "Create sample stories for teaching 2nd standard students.",
    "Generate startup technical architecture documentation.",
    "Generate HR onboarding documents for a software company.",
]

for example in examples:
    st.code(example)

# ============================================================
# GENERATION
# ============================================================
if st.button("🔥 Generate Dataset", use_container_width=True):

    with st.spinner("Planning documents..."):
        plan = plan_documents(user_prompt, num_files)

    st.success(f"Planned {len(plan)} files")

    dataset_folder = os.path.join(
        OUTPUT_DIR,
        company_name.replace(" ", "_")
    )

    os.makedirs(dataset_folder, exist_ok=True)

    progress = st.progress(0)
    status_box = st.empty()

    generated_docs = []

    def worker(item):
        if "temperature" not in item:
            item["temperature"] = default_temperature

        return generate_document(company_name, item)

    with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
        futures = []

        for item in plan:
            futures.append(executor.submit(worker, item))

        for idx, future in enumerate(futures):
            doc = future.result()

            save_document(dataset_folder, doc)
            generated_docs.append(doc)

            progress.progress((idx + 1) / len(plan))
            status_box.info(f"Generated: {doc['file_name']}")

    st.success("✅ Dataset generation completed")

    # ========================================================
    # OUTPUT PREVIEW
    # ========================================================
    st.divider()

    st.subheader("📂 Generated Files")

    for doc in generated_docs:
        with st.expander(doc["file_name"]):
            st.json(doc["meta"])
            st.text(doc["content"][:1500])

    st.info(f"Dataset saved to: {dataset_folder}")

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("🧠 Local LLM")

    st.code(f'''
MODEL: {MODEL}
URL: {LLM_URL}
''')

    st.markdown("---")

    st.subheader("📁 Output Structure")

    st.code('''
/generated_dataset
    /Company_Name
        company_overview.txt
        company_overview.meta.json
        privacy_policy.txt
        privacy_policy.meta.json
''')

    st.markdown("---")

    st.subheader("⚡ Features")

    st.markdown('''
- Dynamic prompt understanding
- Enterprise document planning
- Parallel generation
- TXT + META JSON export
- Local LLM support
- Multi-category datasets
- Metadata enrichment
- Batch processing
- Scalable architecture
''')

# ============================================================
# RUN
# ============================================================
# streamlit run app.py
