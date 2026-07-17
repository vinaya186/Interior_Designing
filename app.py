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
# Page setup + styling
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="House Interior Generator",
    page_icon="🏠",
    layout="wide",
)

TEXT_DARK = "#2b2420"
TEXT_MUTED = "#6b5f52"
ACCENT = "#a9744f"
ACCENT_DARK = "#8c5f3e"
CARD_BG = "#ffffff"
CARD_BORDER = "#e9e1d4"
PAGE_BG_TOP = "#faf7f2"
PAGE_BG_BOTTOM = "#f3ede3"

CUSTOM_CSS = f"""
<style>
    /* Force a consistent palette regardless of the viewer's light/dark
       system setting — Streamlit's theme otherwise leaves headers and
       labels an unreadable pale color on a light card background. */
    .stApp {{
        background: linear-gradient(180deg, {PAGE_BG_TOP} 0%, {PAGE_BG_BOTTOM} 100%);
    }}
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li {{
        color: {TEXT_DARK};
    }}
    h1, h2, h3, h4 {{
        font-family: 'Georgia', serif;
        color: {TEXT_DARK} !important;
    }}
    .hero {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.2rem;
    }}
    .hero-emoji {{
        font-size: 2.4rem;
    }}
    .subtitle {{
        color: {TEXT_MUTED};
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }}
    .section-label {{
        font-weight: 700;
        color: {ACCENT_DARK};
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-size: 0.8rem;
        margin: 1.1rem 0 0.3rem 0;
    }}
    div[data-testid="stForm"] {{
        background: {CARD_BG};
        padding: 1.75rem 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
        border: 1px solid {CARD_BORDER};
    }}
    div[data-testid="stForm"] label p {{
        color: {TEXT_DARK} !important;
        font-weight: 600;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {CARD_BG};
        border-color: {CARD_BORDER};
        color: {TEXT_DARK};
    }}
    div[data-baseweb="select"] * {{
        color: {TEXT_DARK} !important;
    }}
    textarea {{
        color: {TEXT_DARK} !important;
        background-color: {CARD_BG} !important;
    }}
    .stButton>button, .stFormSubmitButton>button {{
        background-color: {ACCENT};
        color: white !important;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        width: 100%;
    }}
    .stButton>button:hover, .stFormSubmitButton>button:hover {{
        background-color: {ACCENT_DARK};
        color: white !important;
    }}
    .result-card {{
        background: {CARD_BG};
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid {CARD_BORDER};
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    }}
    .info-banner {{
        background: #eaf2f8;
        border: 1px solid #cfe3f0;
        color: {TEXT_DARK};
        padding: 1rem 1.2rem;
        border-radius: 12px;
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
# Layout
# ----------------------------------------------------------------------
st.markdown(
    '<div class="hero"><span class="hero-emoji">🏠</span>'
    '<h1 style="margin:0;">House Interior Generator</h1></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="subtitle">Pick your finishes below and generate a realistic preview '
    'of how the room could look — based on your floor plan.</p>',
    unsafe_allow_html=True,
)

col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    with st.form("interior_form"):
        st.markdown('<div class="section-label">🚪 Room</div>', unsafe_allow_html=True)
        room = st.selectbox("Which room are you designing?", ROOMS)

        st.markdown('<div class="section-label">🚪 Door</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        door_material = c1.selectbox("Door material", DOOR_MATERIALS)
        door_color = c2.selectbox("Door color", DOOR_COLORS)

        st.markdown('<div class="section-label">🧱 Walls</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        wall_texture = c3.selectbox("Wall texture", WALL_TEXTURES)
        wall_color = c4.selectbox("Wall color", WALL_COLORS)

        st.markdown('<div class="section-label">🎨 Design & Flooring</div>', unsafe_allow_html=True)
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

        submitted = st.form_submit_button("✨ Generate Interior")

with col_result:
    st.subheader("Preview")

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
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.image(latest["image"], use_container_width=True, caption=f"{latest['room']} — generated at {latest['time']}")
        st.download_button(
            "⬇️ Download image",
            data=latest["image"],
            file_name=f"interior_{latest['room'].replace(' ', '_').lower()}.png",
            mime="image/png",
        )
        with st.expander("Show generation prompt"):
            st.code(latest["prompt"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Fill in the form and click **Generate Interior** to see a preview here.")

# ----------------------------------------------------------------------
# History gallery
# ----------------------------------------------------------------------
if len(st.session_state.history) > 1:
    st.divider()
    st.subheader("Previous generations")
    cols = st.columns(4)
    for i, item in enumerate(st.session_state.history[1:9]):
        with cols[i % 4]:
            st.image(item["image"], use_container_width=True, caption=f"{item['room']} ({item['time']})")
