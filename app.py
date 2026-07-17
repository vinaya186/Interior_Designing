"""
House Interior Generator
-------------------------
A Streamlit app that lets a user pick interior customization options
(door material/color, wall texture/color, bedroom style/color, room type)
from dropdowns, then uses the OpenRouter API to render a
photorealistic preview of that interior.

Run locally:
    pip install -r requirements.txt
    export OPENROUTER_API_KEY="sk-or-..."      (or put it in .streamlit/secrets.toml)
    streamlit run app.py
"""

import base64
import io
import os
from datetime import datetime

import requests
import streamlit as st


# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="House Interior Generator",
    page_icon="🏡",
    layout="wide",
)

# ----------------------------------------------------------------------
# Design tokens — soft pastel palette: lilac-to-blush gradient, white
# cards with pastel borders and gentle shadows, rounded pill buttons.
# ----------------------------------------------------------------------
BG_A = "#F6F0FB"       # pale lavender
BG_B = "#FDF1F4"       # pale blush
CARD_BG = "#FFFFFF"
CARD_BORDER = "#EFE1F6"
INK = "#4A4458"        # soft plum-charcoal (not harsh black)
MUTED = "#8D8299"
LILAC = "#C9A9E9"
PINK = "#F7B8CB"
MINT = "#AEE7DE"

# NOTE ON HTML STRINGS IN THIS FILE:
# Every raw-HTML string passed to st.markdown(..., unsafe_allow_html=True)
# is built with NO leading whitespace on any line. Markdown treats a line
# indented 4+ spaces as a code block (rendered as literal text) even with
# unsafe_allow_html=True, which is what caused the "raw HTML tags shown as
# text" bug — so every block below is written flush-left / concatenated.
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600;700&display=swap');

.stApp {{
background: linear-gradient(160deg, {BG_A} 0%, {BG_B} 100%);
}}
.stApp, .stApp p, .stApp label, .stApp li {{
color: {INK};
font-family: 'Inter', sans-serif;
}}
.stApp span:not([data-testid="stIconMaterial"]) {{
color: {INK};
font-family: 'Inter', sans-serif;
}}
h1, h2, h3, h4 {{
font-family: 'Space Grotesk', sans-serif;
color: {INK} !important;
}}

.hero-band {{
position: relative;
overflow: hidden;
background: linear-gradient(120deg, {LILAC} 0%, {PINK} 100%);
border-radius: 28px;
padding: 2.4rem 2.6rem;
margin-bottom: 1.8rem;
display: flex;
align-items: center;
gap: 1.2rem;
}}
.hero-blob {{
position: absolute;
border-radius: 50%;
background: rgba(255,255,255,0.28);
}}
.hero-blob-1 {{ width: 140px; height: 140px; top: -50px; right: 40px; }}
.hero-blob-2 {{ width: 80px; height: 80px; bottom: -30px; right: 160px; background: rgba(255,255,255,0.18); }}
.hero-title {{
font-family: 'Space Grotesk', sans-serif;
font-weight: 700;
font-size: 2.1rem;
color: #ffffff !important;
margin: 0;
line-height: 1.15;
position: relative;
z-index: 1;
}}
.hero-sub {{
color: #ffffff;
opacity: 0.92;
font-size: 0.98rem;
margin: 0.4rem 0 0 0;
position: relative;
z-index: 1;
}}

.section-pill {{
display: inline-block;
font-weight: 700;
color: {INK};
text-transform: uppercase;
letter-spacing: 0.05em;
font-size: 0.72rem;
padding: 0.3rem 0.8rem;
border-radius: 999px;
margin: 1.1rem 0 0.6rem 0;
}}
.pill-lilac {{ background: #EFE1FA; }}
.pill-pink {{ background: #FDE4EC; }}
.pill-mint {{ background: #DFF6F1; }}

div[data-testid="stForm"] {{
background: {CARD_BG};
padding: 1.9rem 2.1rem 1.6rem 2.1rem;
border-radius: 24px;
border: 1px solid {CARD_BORDER};
box-shadow: 0 10px 30px rgba(201,169,233,0.18);
}}
div[data-testid="stForm"] label p {{
color: {MUTED} !important;
font-weight: 600;
font-size: 0.85rem;
}}

div[class*="st-key-preview_card"] {{
background: {CARD_BG};
padding: 1.6rem;
border-radius: 24px;
border: 1px solid {CARD_BORDER};
box-shadow: 0 10px 30px rgba(201,169,233,0.18);
}}

div[data-baseweb="select"] > div {{
background-color: #FBF7FE;
border: 1.5px solid {CARD_BORDER} !important;
border-radius: 14px;
color: {INK};
}}
div[data-baseweb="select"] * {{
color: {INK} !important;
}}
div[data-baseweb="select"]:focus-within > div {{
border-color: {LILAC} !important;
box-shadow: 0 0 0 2px rgba(201,169,233,0.35);
}}
textarea {{
color: {INK} !important;
background-color: #FBF7FE !important;
border: 1.5px solid {CARD_BORDER} !important;
border-radius: 14px !important;
}}

.stButton>button, .stFormSubmitButton>button {{
background: linear-gradient(120deg, {LILAC} 0%, {PINK} 100%);
color: #ffffff !important;
border-radius: 999px;
border: none;
padding: 0.7rem 1.6rem;
font-family: 'Inter', sans-serif;
font-weight: 700;
letter-spacing: 0.02em;
font-size: 0.9rem;
width: 100%;
box-shadow: 0 6px 16px rgba(201,169,233,0.4);
}}
.stButton>button:hover, .stFormSubmitButton>button:hover {{
filter: brightness(1.05);
color: #ffffff !important;
}}

div[data-testid="stDownloadButton"] button {{
background: #ffffff;
color: {INK} !important;
border-radius: 999px;
border: 1.5px solid {LILAC};
padding: 0.6rem 1.4rem;
font-family: 'Inter', sans-serif;
font-weight: 700;
font-size: 0.88rem;
width: 100%;
}}
div[data-testid="stDownloadButton"] button:hover {{
background: #FBF3FE;
color: {INK} !important;
border-color: {PINK};
}}
div[data-testid="stDownloadButton"] button span:not([data-testid="stIconMaterial"]) {{
color: {INK} !important;
}}

div[data-testid="stExpander"] {{
background: #ffffff;
border: 1px solid {CARD_BORDER};
border-radius: 16px;
overflow: hidden;
}}
div[data-testid="stExpander"] summary {{
color: {INK} !important;
font-weight: 600;
}}
div[data-testid="stExpander"] summary span:not([data-testid="stIconMaterial"]) {{
color: {INK} !important;
}}
div[data-testid="stExpander"] p {{
color: {INK} !important;
}}

div[data-testid="stAlert"] {{
border-radius: 16px;
border: 1px solid {CARD_BORDER};
}}

.caption-soft {{
font-size: 0.8rem;
color: {MUTED};
font-weight: 600;
letter-spacing: 0.02em;
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
# Image generation — via OpenRouter's chat completions endpoint
# ----------------------------------------------------------------------
# OpenRouter doesn't expose a separate "images/generations" endpoint.
# Image-capable models are called through the normal chat completions
# endpoint with `modalities: ["image", "text"]`, and the generated image
# comes back as a base64 data URL inside
# choices[0].message.images[0].image_url.url
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash-image")


def _get_openrouter_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    # st.secrets raises if no secrets.toml exists at all — don't let that
    # crash the app, just treat it as "no key found there either".
    try:
        key = str(st.secrets.get("OPENROUTER_API_KEY", "") or "").strip()
    except Exception:
        key = ""
    return key or None


def generate_image(prompt: str):
    api_key = _get_openrouter_key()
    if not api_key:
        raise RuntimeError(
            "No OpenRouter API key found. Set the OPENROUTER_API_KEY environment variable, "
            "or add OPENROUTER_API_KEY to .streamlit/secrets.toml. "
            "You can create a key at https://openrouter.ai/keys."
        )

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        # Optional but recommended by OpenRouter for attribution/rankings.
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "House Interior Generator",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
    except requests.RequestException as e:
        raise RuntimeError(f"Couldn't reach OpenRouter: {e}") from e

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter rejected the request (HTTP {response.status_code}): {response.text}. "
            f"This can happen if the model '{OPENROUTER_MODEL}' doesn't support image output, "
            "or your OpenRouter account/key doesn't have access to it — try a different model "
            "via the OPENROUTER_MODEL environment variable."
        )

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(f"OpenRouter returned no choices: {data}")

    message = choices[0].get("message", {})
    images = message.get("images", [])
    if not images:
        raise RuntimeError(
            "OpenRouter didn't return an image. The model may only support text output, "
            f"or the request was filtered. Raw response: {data}"
        )

    image_url = images[0].get("image_url", {}).get("url", "")
    if not image_url.startswith("data:image"):
        raise RuntimeError(f"Unexpected image format returned by OpenRouter: {image_url[:80]}...")

    b64_data = image_url.split(",", 1)[1]
    return base64.b64decode(b64_data)


# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# ----------------------------------------------------------------------
# Hero — built as one flush-left concatenated string (no indentation)
# so Markdown never mistakes it for an indented code block.
# ----------------------------------------------------------------------
hero_html = (
    '<div class="hero-band">'
    '<div class="hero-blob hero-blob-1"></div>'
    '<div class="hero-blob hero-blob-2"></div>'
    '<div style="position:relative;z-index:1;">'
    '<h1 class="hero-title">🏡 House Interior Generator</h1>'
    '<p class="hero-sub">Pick your finishes below and render a preview grounded in your floor plan.</p>'
    '</div>'
    '</div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Small diagnostic so it's obvious whether an OpenRouter key was found
# and where it came from — helps debug "Missing Authentication header"
# style errors without ever printing the real key.
# ----------------------------------------------------------------------
with st.sidebar:
    st.caption("OpenRouter connection")
    _env_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    try:
        _secrets_key = str(st.secrets.get("OPENROUTER_API_KEY", "") or "").strip()
    except Exception:
        _secrets_key = ""
    if _env_key:
        st.success(f"Key loaded from environment variable (ends in ...{_env_key[-4:]})")
    elif _secrets_key:
        st.success(f"Key loaded from secrets.toml (ends in ...{_secrets_key[-4:]})")
    else:
        st.warning(
            "No OPENROUTER_API_KEY found in the environment or "
            ".streamlit/secrets.toml. Set it before generating an image."
        )


def section_pill(text, tone="lilac"):
    st.markdown(f'<span class="section-pill pill-{tone}">{text}</span>', unsafe_allow_html=True)


col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    with st.form("interior_form"):
        section_pill("Room", "lilac")
        room = st.selectbox("Which room are you designing?", ROOMS)

        section_pill("Door", "pink")
        c1, c2 = st.columns(2)
        door_material = c1.selectbox("Door material", DOOR_MATERIALS)
        door_color = c2.selectbox("Door color", DOOR_COLORS)

        section_pill("Walls", "mint")
        c3, c4 = st.columns(2)
        wall_texture = c3.selectbox("Wall texture", WALL_TEXTURES)
        wall_color = c4.selectbox("Wall color", WALL_COLORS)

        section_pill("Design &amp; flooring", "lilac")
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

        submitted = st.form_submit_button("✨ Render interior")

with col_result:
    with st.container(key="preview_card"):
        section_pill("Preview", "pink")

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
                f'<p class="caption-soft">{latest["room"].upper()} · GENERATED {latest["time"]}</p>',
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
    section_pill("Previous generations", "lilac")
    cols = st.columns(4)
    for i, item in enumerate(st.session_state.history[1:9]):
        with cols[i % 4]:
            st.image(item["image"], use_container_width=True, caption=f"{item['room']} ({item['time']})")
