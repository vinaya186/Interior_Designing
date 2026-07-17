import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Interior Design Layout — Ground Floor Plan",
    page_icon="🏠",
    layout="wide",
)

# ---------------------------------------------------------------------------
# The SVG floor plan (kept as a raw string so it's easy to tweak coordinates,
# colors, or add rooms/furniture later).
# ---------------------------------------------------------------------------
PLAN_SVG = """
<div style="display:flex; justify-content:center;">
<svg id="plan" width="460" height="650" viewBox="0 0 460 650" xmlns="http://www.w3.org/2000/svg"
     style="background:#fff; border-radius:10px; box-shadow:0 8px 24px rgba(43,33,24,0.12); padding:8px;">

  <!-- ============ FLOOR FILLS ============ -->
  <rect x="60" y="50" width="130" height="120" fill="#EFE1D1"/> <!-- Bedroom 1 -->
  <rect x="190" y="50" width="80" height="60" fill="#D7E6E4"/> <!-- Toilet -->
  <rect x="190" y="110" width="80" height="60" fill="#D7E6E4"/> <!-- Bath -->
  <rect x="270" y="50" width="130" height="120" fill="#EFE1D1"/> <!-- Bedroom 2 -->

  <rect x="60" y="170" width="90" height="180" fill="#E8DFC8"/> <!-- Kitchen -->
  <rect x="150" y="170" width="140" height="180" fill="#E3D3BB"/> <!-- TV Lounge -->
  <rect x="290" y="170" width="110" height="180" fill="#EAD9C2"/> <!-- Dining -->

  <rect x="60" y="350" width="110" height="120" fill="#DED2BE"/> <!-- Stair/Lobby -->
  <rect x="170" y="350" width="230" height="120" fill="#DED2BE" opacity="0.55"/> <!-- Entry hall -->

  <rect x="60" y="470" width="140" height="120" fill="#D8D3C8"/> <!-- Car Porch -->
  <rect x="200" y="470" width="200" height="120" fill="#9FBF8F"/> <!-- Garden -->

  <!-- garden texture -->
  <g opacity="0.35" stroke="#6E8F5C" stroke-width="1">
    <path d="M210 480 q5 8 0 16 q-5 8 0 16"/>
    <path d="M225 485 q5 8 0 16 q-5 8 0 16"/>
    <path d="M240 480 q5 8 0 16 q-5 8 0 16"/>
    <path d="M255 490 q5 8 0 16 q-5 8 0 16"/>
    <path d="M355 480 q5 8 0 16 q-5 8 0 16"/>
    <path d="M370 485 q5 8 0 16 q-5 8 0 16"/>
    <path d="M385 480 q5 8 0 16 q-5 8 0 16"/>
  </g>
  <path d="M300 470 L300 590" stroke="#E7DFC9" stroke-width="14" opacity="0.7"/>
  <circle cx="230" cy="540" r="10" fill="#6E8F5C" opacity="0.8"/>
  <circle cx="360" cy="510" r="7" fill="#6E8F5C" opacity="0.8"/>
  <circle cx="330" cy="565" r="6" fill="#6E8F5C" opacity="0.8"/>

  <!-- ============ FURNITURE ============ -->

  <!-- Bedroom 1: bed, wardrobe, nightstand -->
  <g>
    <rect x="72" y="62" width="88" height="70" rx="4" fill="#8B5E3C"/>
    <rect x="76" y="66" width="80" height="18" rx="3" fill="#fff" opacity="0.85"/>
    <rect x="80" y="70" width="16" height="10" rx="2" fill="#C97B4A" opacity="0.7"/>
    <rect x="100" y="70" width="16" height="10" rx="2" fill="#C97B4A" opacity="0.7"/>
    <rect x="72" y="146" width="86" height="20" fill="#6B4A2F"/>
    <rect x="164" y="62" width="16" height="16" fill="#8B5E3C"/>
  </g>

  <!-- Toilet -->
  <g>
    <ellipse cx="210" cy="80" rx="8" ry="10" fill="#fff" stroke="#7A6E60" stroke-width="1"/>
    <rect x="204" y="66" width="12" height="8" fill="#fff" stroke="#7A6E60" stroke-width="1"/>
    <rect x="244" y="64" width="18" height="12" rx="2" fill="#fff" stroke="#7A6E60" stroke-width="1"/>
  </g>

  <!-- Bath -->
  <g>
    <rect x="200" y="122" width="34" height="34" fill="#EAF3F2" stroke="#7A6E60" stroke-width="1"/>
    <circle cx="217" cy="139" r="3" fill="#7A6E60"/>
    <rect x="248" y="122" width="16" height="12" rx="2" fill="#fff" stroke="#7A6E60" stroke-width="1"/>
  </g>

  <!-- Bedroom 2: bed, wardrobe, desk -->
  <g>
    <rect x="310" y="62" width="80" height="70" rx="4" fill="#8B5E3C"/>
    <rect x="314" y="66" width="72" height="18" rx="3" fill="#fff" opacity="0.85"/>
    <rect x="318" y="70" width="16" height="10" rx="2" fill="#C97B4A" opacity="0.7"/>
    <rect x="338" y="70" width="16" height="10" rx="2" fill="#C97B4A" opacity="0.7"/>
    <rect x="280" y="62" width="20" height="80" fill="#6B4A2F"/>
    <rect x="310" y="146" width="40" height="16" fill="#8B5E3C"/>
  </g>

  <!-- Kitchen: counters, stove, sink, fridge -->
  <g>
    <rect x="70" y="180" width="70" height="16" fill="#6B4A2F"/>
    <rect x="70" y="196" width="16" height="80" fill="#6B4A2F"/>
    <rect x="94" y="182" width="18" height="12" fill="#444"/>
    <circle cx="99" cy="188" r="2" fill="#888"/><circle cx="107" cy="188" r="2" fill="#888"/>
    <rect x="120" y="182" width="16" height="12" fill="#CFE4E3" stroke="#7A6E60"/>
    <rect x="72" y="285" width="14" height="34" fill="#D9D3C4" stroke="#7A6E60"/>
  </g>

  <!-- TV Lounge: sofas, coffee table, TV unit, rug -->
  <g>
    <rect x="182" y="222" width="72" height="46" fill="#EDE3D3" opacity="0.7"/>
    <rect x="160" y="200" width="22" height="92" rx="6" fill="#A78B6B"/>
    <rect x="190" y="180" width="72" height="22" rx="6" fill="#A78B6B"/>
    <rect x="196" y="234" width="52" height="24" rx="3" fill="#8B5E3C"/>
    <rect x="178" y="322" width="86" height="14" fill="#6B4A2F"/>
    <rect x="205" y="308" width="32" height="20" fill="#333"/>
  </g>

  <!-- Dining: table, chairs, sideboard -->
  <g>
    <rect x="300" y="182" width="82" height="14" fill="#6B4A2F"/>
    <rect x="316" y="222" width="72" height="52" rx="3" fill="#8B5E3C"/>
    <rect x="322" y="216" width="10" height="8" fill="#A78B6B"/>
    <rect x="340" y="216" width="10" height="8" fill="#A78B6B"/>
    <rect x="358" y="216" width="10" height="8" fill="#A78B6B"/>
    <rect x="322" y="278" width="10" height="8" fill="#A78B6B"/>
    <rect x="340" y="278" width="10" height="8" fill="#A78B6B"/>
    <rect x="358" y="278" width="10" height="8" fill="#A78B6B"/>
  </g>

  <!-- Staircase -->
  <g stroke="#6B4A2F" stroke-width="2">
    <line x1="72" y1="362" x2="132" y2="362"/>
    <line x1="72" y1="372" x2="132" y2="372"/>
    <line x1="72" y1="382" x2="132" y2="382"/>
    <line x1="72" y1="392" x2="132" y2="392"/>
    <line x1="72" y1="402" x2="132" y2="402"/>
    <line x1="72" y1="412" x2="132" y2="412"/>
    <line x1="72" y1="422" x2="132" y2="422"/>
    <line x1="72" y1="432" x2="132" y2="432"/>
    <line x1="72" y1="442" x2="132" y2="442"/>
    <line x1="72" y1="452" x2="132" y2="452"/>
  </g>
  <rect x="146" y="360" width="18" height="30" fill="#8B5E3C"/>

  <!-- Entry hall: bench + planter -->
  <g>
    <rect x="182" y="440" width="46" height="14" rx="4" fill="#A78B6B"/>
    <circle cx="360" cy="448" r="9" fill="#6E8F5C"/>
  </g>

  <!-- Car porch: car + guide lines -->
  <g>
    <rect x="82" y="500" width="94" height="56" rx="10" fill="#8AA1B1"/>
    <rect x="92" y="508" width="74" height="18" rx="4" fill="#C9D6DD"/>
    <circle cx="98" cy="556" r="7" fill="#333"/>
    <circle cx="160" cy="556" r="7" fill="#333"/>
    <line x1="72" y1="480" x2="72" y2="580" stroke="#fff" stroke-dasharray="6 5" opacity="0.6"/>
    <line x1="188" y1="480" x2="188" y2="580" stroke="#fff" stroke-dasharray="6 5" opacity="0.6"/>
  </g>

  <!-- ============ WALLS ============ -->
  <g fill="none" stroke="#2B2118" stroke-width="3.5">
    <rect x="60" y="50" width="340" height="420"/>
    <rect x="60" y="470" width="340" height="120"/>
  </g>
  <g stroke="#2B2118" stroke-width="2">
    <line x1="190" y1="50" x2="190" y2="170"/>
    <line x1="270" y1="50" x2="270" y2="170"/>
    <line x1="190" y1="110" x2="270" y2="110"/>
    <line x1="150" y1="170" x2="150" y2="350"/>
    <line x1="290" y1="170" x2="290" y2="350"/>
    <line x1="60" y1="170" x2="400" y2="170"/>
    <line x1="60" y1="350" x2="400" y2="350"/>
    <line x1="170" y1="350" x2="170" y2="470"/>
    <line x1="200" y1="470" x2="200" y2="590"/>
  </g>

  <!-- ============ LABELS ============ -->
  <text x="125" y="115" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">BEDROOM 1</text>
  <text x="125" y="127" text-anchor="middle" font-size="7.5" fill="#7A6E60">13'-0" x 12'-0"</text>

  <text x="230" y="83" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">TOILET</text>
  <text x="230" y="143" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">BATH</text>

  <text x="335" y="115" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">BEDROOM 2</text>
  <text x="335" y="127" text-anchor="middle" font-size="7.5" fill="#7A6E60">13'-0" x 12'-0"</text>

  <text x="105" y="260" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">KITCHEN</text>
  <text x="105" y="272" text-anchor="middle" font-size="7.5" fill="#7A6E60">9'-0" x 18'-0"</text>

  <text x="220" y="300" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">TV LOUNGE</text>
  <text x="220" y="312" text-anchor="middle" font-size="7.5" fill="#7A6E60">16'-6" x 18'-0"</text>

  <text x="345" y="260" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">DRAWING / DINING</text>
  <text x="345" y="272" text-anchor="middle" font-size="7.5" fill="#7A6E60">16'-0" x 13'-0"</text>

  <text x="115" y="465" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">STAIRCASE / LOBBY</text>

  <text x="130" y="586" text-anchor="middle" font-size="9" font-weight="600" fill="#fff">CAR PORCH</text>
  <text x="130" y="598" text-anchor="middle" font-size="7.5" fill="#eee">14'-0" x 10'-0"</text>

  <text x="300" y="586" text-anchor="middle" font-size="9" font-weight="600" fill="#2B2118">GARDEN</text>
  <text x="300" y="598" text-anchor="middle" font-size="7.5" fill="#7A6E60">13'-6" x 40'-0"</text>

  <!-- North arrow -->
  <g transform="translate(410,60)">
    <line x1="0" y1="18" x2="0" y2="0" stroke="#2B2118" stroke-width="1.5"/>
    <polygon points="0,-6 5,4 -5,4" fill="#2B2118"/>
    <text x="0" y="30" text-anchor="middle" font-size="9" fill="#7A6E60">N</text>
  </g>

</svg>
</div>
"""

# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------
st.title("🏠 Interior Design Layout")
st.caption("GROUND FLOOR PLAN · FURNITURE & ZONING")

col_plan, col_notes = st.columns([2, 1], gap="large")

with col_plan:
    components.html(PLAN_SVG, height=680, scrolling=False)

with col_notes:
    st.subheader("Design Notes")

    rooms = [
        ("🛏️ Bedrooms", "#EFE1D1",
         "Queen bed against the inner wall, full-height wardrobe opposite, "
         "bedside table. Bedroom 2 adds a small study desk. Warm oak "
         "laminate flooring, linen curtains."),
        ("🚿 Toilet & Bath", "#D7E6E4",
         "Anti-skid ceramic tile, wall-hung WC, corner shower with glass "
         "partition, wall-mounted basin to save floor area."),
        ("🍳 Kitchen", "#E8DFC8",
         "L-shaped modular counter along two walls, hob + chimney, sink "
         "under window, tall fridge unit near the entry for easy access."),
        ("🛋️ TV Lounge", "#E3D3BB",
         "L-shaped sectional sofa, low coffee table on a jute rug, "
         "wall-mounted TV unit facing seating — the social hub of the plan."),
        ("🍽️ Drawing / Dining", "#EAD9C2",
         "6-seater dining table centered under a pendant light, low "
         "sideboard for crockery along the entry wall."),
        ("🪜 Lobby & Stair", "#DED2BE",
         "Open-riser staircase, console table with shoe storage at the "
         "entry, statement pendant overhead."),
        ("🌳 Garden & Porch", "#9FBF8F",
         "Lawn strip with a paved path and shrubs; car porch has painted "
         "parking guide lines and space for one vehicle."),
    ]

    for name, color, desc in rooms:
        st.markdown(
            f"""
            <div style="margin-bottom:14px;">
                <div style="font-weight:600; font-size:14px; display:flex; align-items:center; gap:8px;">
                    <span style="width:12px;height:12px;border-radius:3px;background:{color};
                                 display:inline-block;border:1px solid rgba(0,0,0,0.15);"></span>
                    {name}
                </div>
                <div style="font-size:13px; color:#7A6E60; margin-left:20px; line-height:1.4;">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    st.caption(
        "Dimensions are estimated from the source floor plan. Adjust the "
        "coordinates in `PLAN_SVG` inside `app.py` to match exact measurements."
    )
