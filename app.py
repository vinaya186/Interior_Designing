"""
House Interior Generator
-------------------------
A Streamlit app that lets a user pick interior customization options
(door material/color, wall texture/color, bedroom style/color, room type)
from dropdowns, then uses OpenAI's image generation API to render a
photorealistic preview of that interior.

Run locally:
    pip install -r requirements.txt
    export OPENAI_API_KEY="sk-..."      (or put it in .streamlit/secrets.toml)
    streamlit run app.py
"""

import os
import base64
import io
from datetime import datetime

import streamlit as st
from openai import OpenAI


# ----------------------------------------------------------------------
# Page setup + styling
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="House Interior Generator",
    page_icon="🏠",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(180deg, #faf7f2 0%, #f3ede3 100%);
    }
    section[data-testid="stSidebar"] {
        background-color: #2b2420;
    }
    section[data-testid="stSidebar"] * {
        color: #f3ede3 !important;
    }
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        color: #2b2420;
    }
    .subtitle {
        color: #6b5f52;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stForm"] {
        background: #ffffff;
        padding: 1.75rem 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
        border: 1px solid #e9e1d4;
    }
    .stButton>button, .stFormSubmitButton>button {
        background-color: #a9744f;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover {
        background-color: #8c5f3e;
        color: white;
    }
    .result-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid #e9e1d4;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Option catalogs (edit/extend these freely)
# ----------------------------------------------------------------------
ROOMS = ["Bedroom", "Kitchen / Living Room", "Bathroom"]

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
    prompt = (
        f"A photorealistic, professionally photographed interior design render of a {room.lower()} "
        f"in an Indian residential home, following an architectural floor plan layout. "
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
def generate_image(prompt: str):
    api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        raise RuntimeError(
            "No OpenAI API key found. Set the OPENAI_API_KEY environment variable, "
            "or add OPENAI_API_KEY to .streamlit/secrets.toml."
        )
    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    b64_data = result.data[0].b64_json
    return base64.b64decode(b64_data)


# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# ----------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------------
st.title("🏠 House Interior Generator")
st.markdown(
    '<p class="subtitle">Pick your finishes below and generate a realistic preview '
    'of how the room could look — based on your floor plan.</p>',
    unsafe_allow_html=True,
)

col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    with st.form("interior_form"):
        st.subheader("Room")
        room = st.selectbox("Which room are you designing?", ROOMS)

        st.subheader("Door")
        c1, c2 = st.columns(2)
        door_material = c1.selectbox("Door material", DOOR_MATERIALS)
        door_color = c2.selectbox("Door color", DOOR_COLORS)

        st.subheader("Walls")
        c3, c4 = st.columns(2)
        wall_texture = c3.selectbox("Wall texture", WALL_TEXTURES)
        wall_color = c4.selectbox("Wall color", WALL_COLORS)

        st.subheader("Design & Flooring")
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
