import streamlit as st
import requests
import json
import os
import re
import zipfile
import io
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from config import LLM_URL, MODEL

OUTPUT_DIR = "generated_dataset"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# HELPERS
# ============================================================

def sanitize_name(name: str) -> str:
    """Strip path traversal characters — keep only safe filename chars."""
    name = re.sub(r"[^\w\s\-]", "", name)
    return name.strip().replace(" ", "_")


def safe_path(base: str, *parts: str) -> str:
    """Build a path and verify it stays inside base (prevents traversal)."""
    target = os.path.realpath(os.path.join(base, *parts))
    if not target.startswith(os.path.realpath(base)):
        raise ValueError(f"Path traversal detected: {target}")
    return target

# ============================================================
# LLM
# ============================================================

def check_llm_connection() -> bool:
    try:
        r = requests.get(LLM_URL.replace("/v1/chat/completions", "/health"), timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def ask_llm(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": 1200,
    }
    response = requests.post(LLM_URL, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ============================================================
# PLANNER
# ============================================================

def plan_documents(user_prompt: str, num_files: int, category: str) -> list:
    planner_prompt = f"""
You are a dataset planning AI.

Generate a JSON array only.

User Request:
{user_prompt}

Dataset Category: {category}

Create exactly {num_files} files.

Each item must contain:
- file_name (snake_case, no extension)
- document_type
- short_description
- temperature (float 0.0–1.2)

Return valid JSON only.
"""
    raw = ask_llm("You only output valid JSON.", planner_prompt, 0.3)
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

# ============================================================
# GENERATOR
# ============================================================

def generate_document(company_name: str, item: dict, default_temperature: float) -> dict:
    file_name         = sanitize_name(item["file_name"])
    document_type     = item["document_type"]
    short_description = item["short_description"]
    temperature       = item.get("temperature", default_temperature)

    content_prompt = f"""
Create realistic enterprise quality content.

Company Name: {company_name}
Document Type: {document_type}
Description: {short_description}

Requirements:
- realistic and detailed
- production style
- natural language
- no placeholders
- clean formatting
"""
    content = ask_llm("You are an enterprise document generator AI.", content_prompt, temperature)

    return {
        "file_name": file_name,
        "content":   content,
        "meta": {
            "file_name":     file_name,
            "document_type": document_type,
            "company_name":  company_name,
            "created_at":    datetime.now(timezone.utc).isoformat(),
            "temperature":   temperature,
            "source":        "groovy-ai-local-llm",
            "model":         MODEL,
            "word_count":    len(content.split()),
            "tags":          [document_type],
        },
    }

# ============================================================
# SAVE
# ============================================================

def save_document(dataset_folder: str, doc: dict):
    txt_path  = safe_path(dataset_folder, f"{doc['file_name']}.txt")
    json_path = safe_path(dataset_folder, f"{doc['file_name']}.meta.json")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(doc["content"])
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(doc["meta"], f, indent=2)


def build_zip(dataset_folder: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in os.listdir(dataset_folder):
            fpath = safe_path(dataset_folder, fname)
            zf.write(fpath, arcname=fname)
    return buf.getvalue()

# ============================================================
# PAGE
# ============================================================

st.set_page_config(page_title="Groovy AI Dataset Generator", layout="wide")
st.title("🚀 Groovy AI Dataset Generator")
st.caption("Generate enterprise-grade synthetic datasets using your local LLM")

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("🧠 Local LLM")
    online = check_llm_connection()
    st.markdown(f"**Status:** {'🟢 Online' if online else '🔴 Offline'}")
    st.code(f"MODEL: {MODEL}\nURL:   {LLM_URL}")

    st.markdown("---")
    st.subheader("📁 Output Structure")
    st.code("/generated_dataset\n  /Company_Name\n    doc.txt\n    doc.meta.json")

    st.markdown("---")
    st.subheader("⚡ Features")
    st.markdown("""
- Dynamic prompt planning
- Category-aware generation
- Parallel workers
- Path traversal protection
- UTC timestamps
- Word count in metadata
- ZIP download
- Per-file error handling
""")

# ============================================================
# INPUTS
# ============================================================

left, right = st.columns([2, 1])

with left:
    user_prompt = st.text_area(
        "Describe what dataset you want to generate",
        height=220,
        value="Create company docs: about page, founder info, HR policy, privacy policy, terms and conditions, employee handbook, technical architecture, marketing strategy.",
    )

with right:
    st.subheader("⚙️ Settings")

    company_name = st.text_input("Company / Dataset Name", value="NovaByte Technologies")

    category = st.selectbox("Dataset Category", [
        "Enterprise", "Education", "Technical", "Legal", "Healthcare", "Story",
    ])

    num_files = st.slider("Number of Files", 1, 100, 20)

    default_temperature = st.slider("Creativity", 0.0, 1.5, 0.7, step=0.1)

    parallel_workers = st.slider("Parallel Workers", 1, 10, 3)

# ============================================================
# EXAMPLE PROMPTS
# ============================================================

st.divider()
st.subheader("💡 Example Prompts")

examples = [
    "Create 20 company docs: about, founder info, HR policy, privacy policy, terms.",
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

    if not online:
        st.error("LLM server is offline. Check your connection and try again.")
        st.stop()

    safe_company = sanitize_name(company_name)
    dataset_folder = safe_path(OUTPUT_DIR, safe_company)
    os.makedirs(dataset_folder, exist_ok=True)

    try:
        with st.spinner("🧠 Planning documents..."):
            plan = plan_documents(user_prompt, num_files, category)
        st.success(f"✅ Planned {len(plan)} files")
    except Exception as e:
        st.error(f"Planning failed: {e}")
        st.stop()

    progress  = st.progress(0)
    status    = st.empty()
    generated = []
    failed    = []

    def worker(item):
        return generate_document(safe_company, item, default_temperature)

    with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
        futures = [executor.submit(worker, item) for item in plan]

        for idx, future in enumerate(futures):
            try:
                doc = future.result()
                save_document(dataset_folder, doc)
                generated.append(doc)
                status.info(f"[{idx+1}/{len(plan)}] ✅ {doc['file_name']}")
            except Exception as e:
                failed.append({"index": idx + 1, "error": str(e)})
                status.warning(f"[{idx+1}/{len(plan)}] ❌ Failed: {e}")

            progress.progress((idx + 1) / len(plan))

    st.success(f"✅ Done — {len(generated)} generated, {len(failed)} failed")

    if failed:
        with st.expander(f"⚠️ {len(failed)} failed documents"):
            for f in failed:
                st.error(f"#{f['index']} — {f['error']}")

    # ============================================================
    # DOWNLOAD
    # ============================================================

    zip_bytes = build_zip(dataset_folder)
    st.download_button(
        label="⬇️ Download Dataset as ZIP",
        data=zip_bytes,
        file_name=f"{safe_company}_dataset.zip",
        mime="application/zip",
        use_container_width=True,
    )

    # ============================================================
    # PREVIEW
    # ============================================================

    st.divider()
    st.subheader("📂 Generated Files")

    for doc in generated:
        words = doc["meta"]["word_count"]
        with st.expander(f"{doc['file_name']}  ·  {words} words"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.json(doc["meta"])
            with col2:
                st.text_area("Preview", doc["content"][:2000], height=300, label_visibility="collapsed")

    st.info(f"📂 Saved to: {dataset_folder}")
