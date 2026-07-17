"""
House Interior Generator
-------------------------
A Streamlit app that lets a user pick interior customization options
(door material/color, wall texture/color, bedroom style/color, room type)
from dropdowns, then uses the Hugging Face Inference API to render a
photorealistic preview of that interior.

Run locally:
    pip install -r requirements.txt
    export HF_API_TOKEN="hf_..."      (or put it in .streamlit/secrets.toml)
    streamlit run app.py
"""

import io
import os
from datetime import datetime

import streamlit as st
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError


# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="House Interior Generator",
    page_icon="📐",
    layout="wide",
)

# ----------------------------------------------------------------------
# Design tokens — an architectural "spec sheet" identity: a blueprint-navy
# hero with a faint drafting grid, crisp paper cards with corner tick marks
# (like a detail callout on a drawing), and a cyan highlight pulled from
# blueprint linework rather than a generic accent color.
# ----------------------------------------------------------------------
NAVY = "#0f2a45"
BLUEPRINT_LINE = "#6fa3c4"
PAPER = "#f6f5f0"
INK = "#16212b"
SIGNAL = "#0e94a3"
MUTED = "#5c6b75"

# Reusable corner-tick "detail callout" marks, drawn with layered
# background-gradients so no extra markup is needed on the element.
CORNER_TICKS = f"""
    background-image:
        linear-gradient({INK}, {INK}), linear-gradient({INK}, {INK}),
        linear-gradient({INK}, {INK}), linear-gradient({INK}, {INK}),
        linear-gradient({INK}, {INK}), linear-gradient({INK}, {INK}),
        linear-gradient({INK}, {INK}), linear-gradient({INK}, {INK});
    background-repeat: no-repeat;
    background-size:
        16px 2px, 2px 16px,
        16px 2px, 2px 16px,
        16px 2px, 2px 16px,
        16px 2px, 2px 16px;
    background-position:
        10px 10px, 10px 10px,
        calc(100% - 26px) 10px, calc(100% - 12px) 10px,
        calc(100% - 26px) calc(100% - 12px), calc(100% - 12px) calc(100% - 26px),
        10px calc(100% - 12px), 10px calc(100% - 26px);
"""

CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');

    .stApp {{
        background-color: {PAPER};
    }}
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li {{
        color: {INK};
        font-family: 'Inter', sans-serif;
    }}
    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif;
        color: {INK} !important;
    }}

    /* ---- Hero band ---- */
    .hero-band {{
        background-color: {NAVY};
        background-image:
            linear-gradient(rgba(255,255,255,0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.07) 1px, transparent 1px);
        background-size: 26px 26px;
        border-radius: 6px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 1.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        flex-wrap: wrap;
    }}
    .hero-left {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    .hero-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2rem;
        color: #f6f5f0 !important;
        margin: 0;
        line-height: 1.1;
    }}
    .hero-sub {{
        color: {BLUEPRINT_LINE};
        font-size: 0.95rem;
        margin: 0.35rem 0 0 0;
    }}
    .hero-scale {{
        font-family: 'JetBrains Mono', monospace;
        color: {BLUEPRINT_LINE};
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-align: right;
        white-space: nowrap;
    }}

    /* ---- Section eyebrows inside the spec sheet ---- */
    .section-label {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: {SIGNAL};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.75rem;
        margin: 1.3rem 0 0.5rem 0;
        padding-bottom: 0.35rem;
        border-bottom: 1px dashed {BLUEPRINT_LINE};
    }}
    .section-label:first-of-type {{
        margin-top: 0;
    }}

    /* ---- Spec sheet (form) card ---- */
    div[data-testid="stForm"] {{
        background: {PAPER};
        padding: 1.9rem 2rem 1.5rem 2rem;
        border-radius: 2px;
        border: 1.5px solid {INK};
        {CORNER_TICKS}
    }}
    div[data-testid="stForm"] label p {{
        color: {MUTED} !important;
        font-weight: 600;
        font-size: 0.85rem;
    }}

    /* ---- Preview card (native Streamlit container via key=) ---- */
    div[class*="st-key-preview_card"] {{
        background: {PAPER};
        padding: 1.5rem;
        border-radius: 2px;
        border: 1.5px solid {INK};
        {CORNER_TICKS}
    }}

    /* ---- Dropdowns: crisp, consistent, no baseweb defaults ---- */
    div[data-baseweb="select"] > div {{
        background-color: #ffffff;
        border: 1.5px solid {INK} !important;
        border-radius: 2px;
        color: {INK};
    }}
    div[data-baseweb="select"] * {{
        color: {INK} !important;
    }}
    div[data-baseweb="select"]:focus-within > div {{
        border-color: {SIGNAL} !important;
        box-shadow: 0 0 0 1px {SIGNAL};
    }}
    textarea {{
        color: {INK} !important;
        background-color: #ffffff !important;
        border: 1.5px solid {INK} !important;
        border-radius: 2px !important;
    }}

    /* ---- Buttons ---- */
    .stButton>button, .stFormSubmitButton>button {{
        background-color: {SIGNAL};
        color: #ffffff !important;
        border-radius: 2px;
        border: 1.5px solid {INK};
        padding: 0.65rem 1.4rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 0.85rem;
        width: 100%;
    }}
    .stButton>button:hover, .stFormSubmitButton>button:hover {{
        background-color: {NAVY};
        color: #ffffff !important;
        border-color: {NAVY};
    }}

    /* ---- Info / error banners ---- */
    div[data-testid="stAlert"] {{
        border-radius: 2px;
        border: 1.5px solid {INK};
    }}

    .caption-mono {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: {MUTED};
        letter-spacing: 0.03em;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Option catalogs (edit/extend these freely)
# ----------------------------------------------------------------------
ROOMS = ["Bedroom", "Living Room", "Kitchen", "Bathroom"]

ROOM_FIXTURES = {
    "Bedroom": "a bed with headboard, bedside tables, and a wardrobe",
    "Living Room": "a sofa set, coffee table, and a TV unit",
    "Kitchen": "modular kitchen cabinets, a countertop, and a stove/hob",
    "Bathroom": "a washbasin, shower area, and toilet fixtures",
}

DOOR_MATERIALS = ["Wood", "Teak", "Steel", "Glass", "PVC", "Aluminum"]
DOOR_COLORS = ["Walnut Brown", "Matte Black", "Natural Wood",
               "Charcoal Grey", "White", "Navy Blue"]

WALL_TEXTURES = ["Smooth Paint", "Textured Plaster", "Exposed Brick",
                  "Wood Panel Accent", "Wallpaper", "Stone Cladding"]
WALL_COLORS = ["White", "Beige", "Sage Green", "Charcoal Grey",
               "Pastel Blue", "Terracotta", "Warm Grey"]

DESIGN_STYLES = ["Modern Minimalist", "Scandinavian", "Industrial",
                  "Bohemian", "Luxury Classic", "Coastal", "Contemporary Indian"]
ACCENT_COLORS = ["Ivory", "Blush Pink", "Navy Blue", "Olive Green",
                  "Warm Grey", "Mustard Yellow", "Terracotta"]

FLOORING = ["Wooden Laminate", "Marble", "Vitrified Tiles", "Carpet", "Polished Concrete"]

LIGHTING = ["Warm Ambient", "Bright Daylight", "Cozy Dim", "Studio Bright"]


# ----------------------------------------------------------------------
# Prompt building
# ----------------------------------------------------------------------
def build_prompt(room, door_material, door_color, wall_texture, wall_color,
                  style, accent_color, flooring, lighting, extra_notes):
    fixtures = ROOM_FIXTURES.get(room, "")
    prompt = (
        f"A photorealistic, professionally photographed interior design render of a {room.lower()} "
        f"in an Indian residential home, following an architectural floor plan layout. "
        f"The room includes {fixtures}. "
        f"Overall design style: {style}, with {accent_color.lower()} accent tones. "
        f"Walls have a {wall_texture.lower()} finish painted in {wall_color.lower()}. "
        f"Flooring is {flooring.lower()}. "
        f"The door is made of {door_material.lower()}, finished in {door_color.lower()}. "
        f"Lighting is {lighting.lower()}. "
        f"High resolution, realistic materials, magazine-quality interior photography, "
        f"wide angle, no text or watermarks."
    )
    if extra_notes:
        prompt += f" Additional requirements: {extra_notes.strip()}."
    return prompt


# ----------------------------------------------------------------------
# Image generation
# ----------------------------------------------------------------------
# NOTE: Hugging Face retired the old "api-inference.huggingface.co" URL in
# favor of its newer "Inference Providers" routing. Rather than hard-code a
# provider URL (which can change again), we use Hugging Face's own official
# huggingface_hub client — it always talks to the current routing endpoint.
HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"


def _get_hf_token():
    return os.environ.get("HF_API_TOKEN") or st.secrets.get("HF_API_TOKEN", None)


def generate_image(prompt: str):
    api_key = _get_hf_token()
    if not api_key:
        raise RuntimeError(
            "No Hugging Face API token found. Set the HF_API_TOKEN environment variable, "
            "or add HF_API_TOKEN to .streamlit/secrets.toml."
        )

    client = InferenceClient(api_key=api_key)

    try:
        image = client.text_to_image(prompt, model=HF_MODEL)
    except HfHubHTTPError as e:
        raise RuntimeError(
            f"Hugging Face rejected the request: {e}. "
            "This can happen if the model needs a specific provider, or if your "
            "account doesn't have access to it — try a different model in HF_MODEL."
        ) from e
    except Exception as e:
        raise RuntimeError(f"Couldn't reach Hugging Face: {e}") from e

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# ----------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------
DOOR_MARK_SVG = f"""
<svg width="42" height="42" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 4H44" stroke="{SIGNAL}" stroke-width="3" stroke-linecap="round"/>
  <path d="M4 4V44" stroke="{BLUEPRINT_LINE}" stroke-width="3" stroke-linecap="round"/>
  <path d="M4 44 H28" stroke="{BLUEPRINT_LINE}" stroke-width="3" stroke-linecap="round"/>
  <path d="M28 44 A24 24 0 0 0 4 20" stroke="{SIGNAL}" stroke-width="2" stroke-dasharray="3 3" fill="none"/>
</svg>
"""

st.markdown(
    f'''
    <div class="hero-band">
        <div class="hero-left">
            {DOOR_MARK_SVG}
            <div>
                <h1 class="hero-title">House Interior Generator</h1>
                <p class="hero-sub">Pick your finishes below and render a preview grounded in your floor plan.</p>
            </div>
        </div>
        <div class="hero-scale">SCALE 1:50<br>– – – – – – – –</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    with st.form("interior_form"):
        st.markdown('<div class="section-label">Room</div>', unsafe_allow_html=True)
        room = st.selectbox("Which room are you designing?", ROOMS)

        st.markdown('<div class="section-label">Door</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        door_material = c1.selectbox("Door material", DOOR_MATERIALS)
        door_color = c2.selectbox("Door color", DOOR_COLORS)

        st.markdown('<div class="section-label">Walls</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        wall_texture = c3.selectbox("Wall texture", WALL_TEXTURES)
        wall_color = c4.selectbox("Wall color", WALL_COLORS)

        st.markdown('<div class="section-label">Design &amp; flooring</div>', unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        style = c5.selectbox("Overall design style", DESIGN_STYLES)
        accent_color = c6.selectbox("Accent color", ACCENT_COLORS)

        c7, c8 = st.columns(2)
        flooring = c7.selectbox("Flooring", FLOORING)
        lighting = c8.selectbox("Lighting mood", LIGHTING)

        extra_notes = st.text_area(
            "Anything else? (optional)",
            placeholder="e.g. add a study table, keep it clutter-free, include a balcony view...",
        )

        submitted = st.form_submit_button("Render interior ▸")

with col_result:
    with st.container(key="preview_card"):
        st.markdown('<div class="section-label">Preview</div>', unsafe_allow_html=True)

        if submitted:
            prompt = build_prompt(
                room, door_material, door_color, wall_texture, wall_color,
                style, accent_color, flooring, lighting, extra_notes,
            )
            with st.spinner("Designing your room..."):
                try:
                    image_bytes = generate_image(prompt)
                    st.session_state.history.insert(0, {
                        "image": image_bytes,
                        "prompt": prompt,
                        "room": room,
                        "time": datetime.now().strftime("%H:%M:%S"),
                    })
                except Exception as e:
                    st.error(f"Couldn't generate the image: {e}")

        if st.session_state.history:
            latest = st.session_state.history[0]
            st.image(latest["image"], use_container_width=True)
            st.markdown(
                f'<p class="caption-mono">{latest["room"].upper()} — GENERATED {latest["time"]}</p>',
                unsafe_allow_html=True,
            )
            st.download_button(
                "Download image",
                data=latest["image"],
                file_name=f"interior_{latest['room'].replace(' ', '_').lower()}.png",
                mime="image/png",
            )
            with st.expander("Show generation prompt"):
                st.code(latest["prompt"])
        else:
            st.info("Fill in the form and click **Render interior** to see a preview here.")

# ----------------------------------------------------------------------
# History gallery
# ----------------------------------------------------------------------
if len(st.session_state.history) > 1:
    st.divider()
    st.markdown('<div class="section-label">Previous generations</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, item in enumerate(st.session_state.history[1:9]):
        with cols[i % 4]:
            st.image(item["image"], use_container_width=True, caption=f"{item['room']} ({item['time']})")
