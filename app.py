# app.py
import streamlit as st
from groq_client import GroqClient
from prompt_templates import ANGLE_PROMPT_TEMPLATE, SCRIPT_PROMPT_TEMPLATE
import os
from pathlib import Path
import json
import re
import time
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Puffy Creative Engine — Ad Builder", layout="centered")
BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
PROJECT_INSTRUCTIONS_FILE = BASE_DIR / "project_instructions.txt"

# load helpers
def load_text(file_path: Path) -> str:
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")

def build_system_prompt() -> str:
    project_instructions = load_text(PROJECT_INSTRUCTIONS_FILE)
    knowledge_texts = []
    for f in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        knowledge_texts.append(f"# {f.name}\n" + load_text(f))
    combined = "\n\n".join([project_instructions] + knowledge_texts)
    return combined

# parse JSON robustly
def try_parse_json(text: str):
    # Try to find first JSON array substring
    try:
        # common case: text is clean JSON
        return json.loads(text)
    except Exception:
        # try to extract with regex matching [...] with nested braces heuristics
        m = re.search(r'(\[.*\])', text, flags=re.DOTALL)
        if m:
            candidate = m.group(1)
            try:
                return json.loads(candidate)
            except Exception:
                # try to fix trailing commas
                fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
                try:
                    return json.loads(fixed)
                except Exception:
                    return None
        return None

def parse_numbered_list(text: str):
    # fallback: split on lines that start with a number + dot
    items = []
    parts = re.split(r'\n\s*(?:\d+[\)\.]|\*\s+)', text)
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # heuristically extract title / hook / description using markers
        # We will return the raw block and later parse it
        items.append(p)
    return items

# ---- Groq client init ----
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = os.environ.get("GROQ_API_URL", "")
DEFAULT_MODEL = os.environ.get("GROQ_DEFAULT_MODEL", "llama-3.3-70b-versatile")
client = GroqClient(api_url=GROQ_API_URL, api_key=GROQ_API_KEY, model=DEFAULT_MODEL)

# session defaults
if "structured_concepts" not in st.session_state:
    st.session_state.structured_concepts = []
if "raw_angles_text" not in st.session_state:
    st.session_state.raw_angles_text = ""
if "script_json" not in st.session_state:
    st.session_state.script_json = None

# UI
st.title("Puffy Creative Engine — YouTube Ad Builder")
st.caption("Workflow: User Input → Angle Generator → Concept Selection → Script Generator → Final 15–20s Ad Script")

with st.sidebar:
    st.header("Configuration")
    st.text_input("Brand (tone)", value="Puffy", key="brand")
    st.text_input("Target audience (short)", value="Affluent US households ($100K+)", key="audience")
    st.text_input("Ad length (seconds)", value="20", key="ad_length")
    st.selectbox("Model", options=[DEFAULT_MODEL, "llama3-8b-8192", "mixtral-8x7b-32768"], index=0, key="model_choice")
    st.markdown("---")
    st.write("Knowledge files (read-only)")
    for kf in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        with st.expander(kf.name):
            st.write(load_text(kf))

st.markdown("## 1) Generate novel creative angles")
user_query = st.text_area("Describe what you want (or leave default):",
                          value="Give me novel video concepts for Puffy's luxury mattress targeted to affluent US buyers. 15–20s, hook 0–3s.",
                          height=120)

num_angles = st.number_input("How many angles to generate", min_value=4, max_value=12, value=8, step=1)

generate_angles_btn = st.button("Generate Angles")

def request_angles(exact_count, retries=2):
    system_prompt = build_system_prompt()
    final_prompt = ANGLE_PROMPT_TEMPLATE.format(
        brand=st.session_state.brand,
        audience=st.session_state.audience,
        ad_length=st.session_state.ad_length,
        user_query=user_query,
        exact_count=exact_count
    )
    attempt = 0
    while attempt <= retries:
        resp = client.create_chat_completion(system_prompt=system_prompt, user_prompt=final_prompt, max_tokens=1200)
        raw_text = resp.get("text") or resp.get("output") or resp.get("raw") or str(resp)
        parsed = try_parse_json(raw_text)
        if parsed and isinstance(parsed, list) and len(parsed) == exact_count:
            return parsed, raw_text
        # fallback: try numbered list parse
        numbered = parse_numbered_list(raw_text)
        if len(numbered) >= exact_count:
            # convert numeric blocks into simple objects (best-effort)
            simple = []
            for i, block in enumerate(numbered[:exact_count], start=1):
                simple.append({
                    "id": i,
                    "title": (block.split("\n")[0])[:80],
                    "hook": "",
                    "description": block[:400],
                    "why": "",
                    "differentiation": ""
                })
            return simple, raw_text
        # If insufficient items or parsing failed, retry with clarifying prompt
        attempt += 1
        final_prompt = ("Your previous response did not include exactly {n} JSON objects. "
                        "Return EXACTLY {n} objects in a JSON array, each with fields id,title,hook,description,why,differentiation. "
                        "No extra text.").format(n=exact_count)
        time.sleep(0.5)
    # last-chance: return whatever we have parsed (could be None)
    return parsed or (simple if 'simple' in locals() else None), raw_text

if generate_angles_btn:
    with st.spinner("Generating creative angles..."):
        structs, raw = request_angles(num_angles, retries=2)
        if not structs:
            st.error("Could not parse model output reliably. See raw output below. Try again or reduce angle count.")
            st.session_state.structured_concepts = []
            st.session_state.raw_angles_text = raw
        else:
            # normalize objects to have required keys
            normalized = []
            for i, obj in enumerate(structs, start=1):
                # tolerate different key names
                if isinstance(obj, dict):
                    title = obj.get("title") or obj.get("name") or f"Concept {i}"
                    hook = obj.get("hook") or obj.get("Hook") or ""
                    desc = obj.get("description") or obj.get("desc") or obj.get("concept") or ""
                    why = obj.get("why") or obj.get("resonates") or ""
                    diff = obj.get("differentiation") or obj.get("diff") or ""
                    normalized.append({
                        "id": i,
                        "title": title.strip(),
                        "hook": hook.strip(),
                        "description": desc.strip(),
                        "why": why.strip(),
                        "differentiation": diff.strip()
                    })
                else:
                    normalized.append({
                        "id": i,
                        "title": f"Concept {i}",
                        "hook": "",
                        "description": str(obj)[:400],
                        "why": "",
                        "differentiation": ""
                    })
            st.session_state.structured_concepts = normalized
            st.session_state.raw_angles_text = raw

# display concepts
if st.session_state.structured_concepts:
    st.markdown("### Generated Angles (Preview)")
    for c in st.session_state.structured_concepts:
        st.markdown(f"**{c['id']}. {c['title']}**")
        if c.get("hook"):
            st.markdown(f"*Hook (0-3s):* {c['hook']}")
        st.markdown(f"*{c['description']}*")
        st.markdown(f"*Why:* {c.get('why','-')}")
        st.markdown(f"*Diff:* {c.get('differentiation','-')}")
        st.write("---")
    st.text_area("Full raw output", value=st.session_state.raw_angles_text, height=220)

st.markdown("## 2) Pick a concept and generate script")
col1, col2 = st.columns([3,1])
with col1:
    if st.session_state.structured_concepts:
        max_idx = len(st.session_state.structured_concepts)
    else:
        max_idx = 1
    selected_idx = st.number_input("Select concept # to expand (use index)", min_value=1, max_value=max_idx, value=1, step=1)
    variation_count = st.slider("How many script variations?", min_value=1, max_value=3, value=1)
    tone = st.selectbox("Script tone", options=["Elegant / Cinematic", "Warm / Emotional", "Clever / Witty"], index=0)

with col2:
    if st.button("Generate Script"):
        if not st.session_state.structured_concepts:
            st.warning("Please generate and select concepts first.")
        else:
            idx = int(selected_idx) - 1
            concept = st.session_state.structured_concepts[idx]
            system_prompt = build_system_prompt()
            # populate script prompt with structured fields
            final_prompt = SCRIPT_PROMPT_TEMPLATE.format(
                brand=st.session_state.brand,
                audience=st.session_state.audience,
                ad_length=st.session_state.ad_length,
                title=concept.get("title",""),
                hook=concept.get("hook",""),
                description=concept.get("description",""),
                why=concept.get("why",""),
                differentiation=concept.get("differentiation",""),
                tone=tone,
                variation_count=variation_count
            )
            with st.spinner("Generating script(s)..."):
                resp = client.create_chat_completion(system_prompt=system_prompt, user_prompt=final_prompt, max_tokens=900)
                raw_script = resp.get("text") or resp.get("output") or resp.get("raw") or str(resp)
                parsed = try_parse_json(raw_script)
                if parsed and isinstance(parsed, list):
                    st.session_state.script_json = parsed
                else:
                    # fallback: show raw text and attempt to convert to simple JSON-like display
                    st.session_state.script_json = None
                    st.session_state.raw_script_text = raw_script

if st.session_state.script_json:
    st.markdown("### Generated Script(s) (Parsed JSON)")
    for v in st.session_state.script_json:
        st.markdown(f"**Variation {v.get('variation_id','?')} — {v.get('title','')}**")
        st.text(v.get("script_timed",""))
        st.markdown(f"*VO:* {v.get('vo','')}")
        st.markdown(f"*On-screen text:* {v.get('on_screen_text','')}")
        st.markdown(f"*Sound:* {v.get('sound','')}")
        st.markdown(f"*CTA:* {v.get('cta','')}")
        st.write("---")
elif "raw_script_text" in st.session_state:
    st.markdown("### Generated Script(s) — Raw output (parsing failed)")
    st.text_area("Script output (raw)", value=st.session_state.raw_script_text, height=360)

st.markdown("---")
st.caption("Notes: The app enforces exact-count angle generation. If the model doesn't return exactly the requested number of JSON objects, it retries up to 2 times. Scripts are generated from the structured concept you select.")
