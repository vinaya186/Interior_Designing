import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Interior Design Layout — Customizable Floor Plan",
    page_icon="🏠",
    layout="wide",
)

# ===========================================================================
# CONSTANTS
# ===========================================================================
PPF = 10          # pixels per foot
MARGIN = 50        # outer margin around the plan
WALL_COLOR = "#2B2118"
DIM_COLOR = "#7A6E60"

DEFAULTS = {
    # row 1
    "bedroom1": {"name": "BEDROOM 1", "L": 13, "W": 12, "color": "#EFE1D1", "type": "bedroom"},
    "toilet":   {"name": "TOILET",    "L": 8,  "W": 6,  "color": "#D7E6E4", "type": "wc"},
    "bath":     {"name": "BATH",      "L": 8,  "W": 6,  "color": "#D7E6E4", "type": "bath"},
    "bedroom2": {"name": "BEDROOM 2", "L": 13, "W": 12, "color": "#EFE1D1", "type": "bedroom"},
    # row 2
    "kitchen":  {"name": "KITCHEN",     "L": 9,  "W": 18, "color": "#E8DFC8", "type": "kitchen"},
    "lounge":   {"name": "LIVING ROOM", "L": 16, "W": 18, "color": "#E3D3BB", "type": "living"},
    "dining":   {"name": "DINING",      "L": 16, "W": 13, "color": "#EAD9C2", "type": "dining"},
    # row 3
    "lobby":     {"name": "HALL", "L": 11, "W": 12, "color": "#DED2BE", "type": "hall"},
    "entryhall": {"name": "ENTRY HALL", "L": 23, "W": 12, "color": "#DED2BE", "type": "hall"},
    # row 4
    "porch":  {"name": "CAR PORCH", "L": 14, "W": 10, "color": "#D8D3C8", "type": "porch"},
    "garden": {"name": "GARDEN",    "L": 20, "W": 12, "color": "#9FBF8F", "type": "garden"},
}

# ===========================================================================
# SIDEBAR — customization form
# ===========================================================================
st.sidebar.header("📐 Customize Room Dimensions")
st.sidebar.caption("Enter length (L) × width (W) in feet for each room. The plan redraws automatically.")

dims = {}
with st.sidebar.expander("🛏️ Bedrooms", expanded=True):
    for key in ["bedroom1", "bedroom2"]:
        d = DEFAULTS[key]
        c1, c2 = st.columns(2)
        L = c1.number_input(f"{d['name']} — L (ft)", 6, 25, d["L"], key=f"{key}_L")
        W = c2.number_input(f"{d['name']} — W (ft)", 6, 25, d["W"], key=f"{key}_W")
        dims[key] = {**d, "L": L, "W": W}

with st.sidebar.expander("🚿 Toilet & Bath"):
    for key in ["toilet", "bath"]:
        d = DEFAULTS[key]
        c1, c2 = st.columns(2)
        L = c1.number_input(f"{d['name']} — L (ft)", 4, 12, d["L"], key=f"{key}_L")
        W = c2.number_input(f"{d['name']} — W (ft)", 4, 12, d["W"], key=f"{key}_W")
        dims[key] = {**d, "L": L, "W": W}

with st.sidebar.expander("🍳 Kitchen & 🍽️ Dining"):
    for key in ["kitchen", "dining"]:
        d = DEFAULTS[key]
        c1, c2 = st.columns(2)
        L = c1.number_input(f"{d['name']} — L (ft)", 6, 25, d["L"], key=f"{key}_L")
        W = c2.number_input(f"{d['name']} — W (ft)", 6, 25, d["W"], key=f"{key}_W")
        dims[key] = {**d, "L": L, "W": W}

with st.sidebar.expander("🛋️ Living Room / Hall"):
    for key in ["lounge", "lobby", "entryhall"]:
        d = DEFAULTS[key]
        c1, c2 = st.columns(2)
        L = c1.number_input(f"{d['name']} — L (ft)", 6, 30, d["L"], key=f"{key}_L")
        W = c2.number_input(f"{d['name']} — W (ft)", 6, 25, d["W"], key=f"{key}_W")
        dims[key] = {**d, "L": L, "W": W}

with st.sidebar.expander("🚗 Porch & 🌳 Garden"):
    for key in ["porch", "garden"]:
        d = DEFAULTS[key]
        c1, c2 = st.columns(2)
        L = c1.number_input(f"{d['name']} — L (ft)", 6, 30, d["L"], key=f"{key}_L")
        W = c2.number_input(f"{d['name']} — W (ft)", 6, 25, d["W"], key=f"{key}_W")
        dims[key] = {**d, "L": L, "W": W}

st.sidebar.divider()
show_dims = st.sidebar.checkbox("Show dimension labels", value=True)
show_doors = st.sidebar.checkbox("Show doors", value=True)
show_windows = st.sidebar.checkbox("Show windows", value=True)


# ===========================================================================
# SVG DRAWING HELPERS
# ===========================================================================
def ft(v):
    """feet -> pixels"""
    return v * PPF


def dim_label(v_ft):
    feet = int(v_ft)
    inches = round((v_ft - feet) * 12)
    return f"{feet}'-{inches}\""


def window_symbol(x1, y1, x2, y2, t=0.5, wlen=None, thickness=6):
    """Draws a window (double parallel lines with a gap) centered at fraction t
    along an axis-aligned wall segment. Returns an SVG snippet."""
    horiz = (y1 == y2)
    length_total = abs(x2 - x1) if horiz else abs(y2 - y1)
    if wlen is None:
        wlen = max(18, min(36, length_total * 0.4))
    if horiz:
        cx = x1 + (x2 - x1) * t
        y = y1
        left, right = cx - wlen / 2, cx + wlen / 2
        return (
            f'<rect x="{left:.1f}" y="{y - thickness/2:.1f}" width="{wlen:.1f}" height="{thickness}" fill="#fff"/>'
            f'<line x1="{left:.1f}" y1="{y - 2:.1f}" x2="{right:.1f}" y2="{y - 2:.1f}" stroke="#5B8FA8" stroke-width="1.5"/>'
            f'<line x1="{left:.1f}" y1="{y + 2:.1f}" x2="{right:.1f}" y2="{y + 2:.1f}" stroke="#5B8FA8" stroke-width="1.5"/>'
        )
    else:
        cy = y1 + (y2 - y1) * t
        x = x1
        top, bottom = cy - wlen / 2, cy + wlen / 2
        return (
            f'<rect x="{x - thickness/2:.1f}" y="{top:.1f}" width="{thickness}" height="{wlen:.1f}" fill="#fff"/>'
            f'<line x1="{x - 2:.1f}" y1="{top:.1f}" x2="{x - 2:.1f}" y2="{bottom:.1f}" stroke="#5B8FA8" stroke-width="1.5"/>'
            f'<line x1="{x + 2:.1f}" y1="{top:.1f}" x2="{x + 2:.1f}" y2="{bottom:.1f}" stroke="#5B8FA8" stroke-width="1.5"/>'
        )


def door_symbol(x1, y1, x2, y2, t=0.5, dlen=None, swing="right", thickness=6):
    """Draws a door (gap + leaf + quarter-circle swing arc) on an axis-aligned wall."""
    horiz = (y1 == y2)
    length_total = abs(x2 - x1) if horiz else abs(y2 - y1)
    if dlen is None:
        dlen = max(22, min(34, length_total * 0.45))
    svg = ""
    if horiz:
        cx = x1 + (x2 - x1) * t
        y = y1
        left, right = cx - dlen / 2, cx + dlen / 2
        svg += f'<rect x="{left:.1f}" y="{y - thickness/2:.1f}" width="{dlen:.1f}" height="{thickness}" fill="#fff"/>'
        if swing == "right":
            hinge_x, hinge_y = left, y
            leaf_x, leaf_y = left, y - dlen
            large_arc, sweep = 0, 1
        else:
            hinge_x, hinge_y = right, y
            leaf_x, leaf_y = right, y - dlen
            large_arc, sweep = 0, 0
        svg += f'<line x1="{hinge_x:.1f}" y1="{hinge_y:.1f}" x2="{leaf_x:.1f}" y2="{leaf_y:.1f}" stroke="{WALL_COLOR}" stroke-width="1.3"/>'
        svg += (f'<path d="M {leaf_x:.1f} {leaf_y:.1f} A {dlen:.1f} {dlen:.1f} 0 {large_arc} {sweep} '
                f'{right if swing=="right" else left:.1f} {y:.1f}" fill="none" stroke="{DIM_COLOR}" '
                f'stroke-width="1" stroke-dasharray="3 2"/>')
    else:
        cy = y1 + (y2 - y1) * t
        x = x1
        top, bottom = cy - dlen / 2, cy + dlen / 2
        svg += f'<rect x="{x - thickness/2:.1f}" y="{top:.1f}" width="{thickness}" height="{dlen:.1f}" fill="#fff"/>'
        if swing == "right":
            hinge_x, hinge_y = x, top
            leaf_x, leaf_y = x + dlen, top
            large_arc, sweep = 0, 0
        else:
            hinge_x, hinge_y = x, bottom
            leaf_x, leaf_y = x + dlen, bottom
            large_arc, sweep = 0, 1
        svg += f'<line x1="{hinge_x:.1f}" y1="{hinge_y:.1f}" x2="{leaf_x:.1f}" y2="{leaf_y:.1f}" stroke="{WALL_COLOR}" stroke-width="1.3"/>'
        svg += (f'<path d="M {leaf_x:.1f} {leaf_y:.1f} A {dlen:.1f} {dlen:.1f} 0 {large_arc} {sweep} '
                f'{x:.1f} {bottom if swing=="right" else top:.1f}" fill="none" stroke="{DIM_COLOR}" '
                f'stroke-width="1" stroke-dasharray="3 2"/>')
    return svg


def furniture_for(room_type, x, y, w, h):
    """Very simple, proportionally scaled furniture placeholders per room type."""
    svg = ""
    if room_type == "bedroom":
        bw, bh = w * 0.62, h * 0.55
        bx, by = x + w * 0.08, y + h * 0.10
        svg += f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" fill="#8B5E3C"/>'
        svg += f'<rect x="{bx+4:.1f}" y="{by+4:.1f}" width="{bw-8:.1f}" height="{bh*0.22:.1f}" rx="3" fill="#fff" opacity="0.85"/>'
        svg += f'<rect x="{x+w*0.74:.1f}" y="{y+h*0.08:.1f}" width="{w*0.18:.1f}" height="{h*0.55:.1f}" fill="#6B4A2F"/>'
    elif room_type == "wc":
        svg += f'<ellipse cx="{x+w*0.4:.1f}" cy="{y+h*0.4:.1f}" rx="{w*0.18:.1f}" ry="{h*0.22:.1f}" fill="#fff" stroke="{DIM_COLOR}" stroke-width="1"/>'
        svg += f'<rect x="{x+w*0.6:.1f}" y="{y+h*0.15:.1f}" width="{w*0.28:.1f}" height="{h*0.2:.1f}" rx="2" fill="#fff" stroke="{DIM_COLOR}" stroke-width="1"/>'
    elif room_type == "bath":
        svg += f'<rect x="{x+w*0.1:.1f}" y="{y+h*0.15:.1f}" width="{w*0.55:.1f}" height="{h*0.6:.1f}" fill="#EAF3F2" stroke="{DIM_COLOR}" stroke-width="1"/>'
        svg += f'<circle cx="{x+w*0.75:.1f}" cy="{y+h*0.3:.1f}" r="3" fill="{DIM_COLOR}"/>'
    elif room_type == "kitchen":
        svg += f'<rect x="{x+w*0.08:.1f}" y="{y+h*0.06:.1f}" width="{w*0.8:.1f}" height="{h*0.1:.1f}" fill="#6B4A2F"/>'
        svg += f'<rect x="{x+w*0.08:.1f}" y="{y+h*0.16:.1f}" width="{w*0.14:.1f}" height="{h*0.68:.1f}" fill="#6B4A2F"/>'
        svg += f'<rect x="{x+w*0.28:.1f}" y="{y+h*0.08:.1f}" width="{w*0.16:.1f}" height="{h*0.08:.1f}" fill="#444"/>'
        svg += f'<rect x="{x+w*0.5:.1f}" y="{y+h*0.08:.1f}" width="{w*0.16:.1f}" height="{h*0.08:.1f}" fill="#CFE4E3" stroke="{DIM_COLOR}"/>'
    elif room_type == "living":
        svg += f'<rect x="{x+w*0.35:.1f}" y="{y+h*0.35:.1f}" width="{w*0.4:.1f}" height="{h*0.35:.1f}" fill="#EDE3D3" opacity="0.7"/>'
        svg += f'<rect x="{x+w*0.1:.1f}" y="{y+h*0.15:.1f}" width="{w*0.16:.1f}" height="{h*0.65:.1f}" rx="6" fill="#A78B6B"/>'
        svg += f'<rect x="{x+w*0.3:.1f}" y="{y+h*0.08:.1f}" width="{w*0.5:.1f}" height="{h*0.16:.1f}" rx="6" fill="#A78B6B"/>'
        svg += f'<rect x="{x+w*0.36:.1f}" y="{y+h*0.45:.1f}" width="{w*0.3:.1f}" height="{h*0.18:.1f}" rx="3" fill="#8B5E3C"/>'
        svg += f'<rect x="{x+w*0.1:.1f}" y="{y+h*0.82:.1f}" width="{w*0.6:.1f}" height="{h*0.1:.1f}" fill="#6B4A2F"/>'
        svg += f'<rect x="{x+w*0.2:.1f}" y="{y+h*0.65:.1f}" width="{w*0.25:.1f}" height="{h*0.15:.1f}" fill="#333"/>'
    elif room_type == "dining":
        svg += f'<rect x="{x+w*0.2:.1f}" y="{y+h*0.3:.1f}" width="{w*0.55:.1f}" height="{h*0.4:.1f}" rx="3" fill="#8B5E3C"/>'
        for fx in (0.24, 0.42, 0.6):
            svg += f'<rect x="{x+w*fx:.1f}" y="{y+h*0.2:.1f}" width="{w*0.08:.1f}" height="{h*0.07:.1f}" fill="#A78B6B"/>'
            svg += f'<rect x="{x+w*fx:.1f}" y="{y+h*0.75:.1f}" width="{w*0.08:.1f}" height="{h*0.07:.1f}" fill="#A78B6B"/>'
    elif room_type == "hall":
        svg += f'<rect x="{x+w*0.1:.1f}" y="{y+h*0.55:.1f}" width="{w*0.3:.1f}" height="{h*0.1:.1f}" rx="4" fill="#A78B6B"/>'
        svg += f'<circle cx="{x+w*0.85:.1f}" cy="{y+h*0.55:.1f}" r="7" fill="#6E8F5C"/>'
        step_y = y + h * 0.15
        while step_y < y + h * 0.5:
            svg += f'<line x1="{x+w*0.08:.1f}" y1="{step_y:.1f}" x2="{x+w*0.4:.1f}" y2="{step_y:.1f}" stroke="{WALL_COLOR}" stroke-width="1.4"/>'
            step_y += 8
    elif room_type == "porch":
        svg += f'<rect x="{x+w*0.15:.1f}" y="{y+h*0.15:.1f}" width="{w*0.7:.1f}" height="{h*0.6:.1f}" rx="10" fill="#8AA1B1"/>'
        svg += f'<rect x="{x+w*0.2:.1f}" y="{y+h*0.2:.1f}" width="{w*0.6:.1f}" height="{h*0.2:.1f}" rx="4" fill="#C9D6DD"/>'
    elif room_type == "garden":
        for gx in (0.2, 0.4, 0.6, 0.8):
            svg += f'<circle cx="{x+w*gx:.1f}" cy="{y+h*0.5:.1f}" r="6" fill="#6E8F5C" opacity="0.8"/>'
        svg += f'<line x1="{x+w*0.5:.1f}" y1="{y+h*0.1:.1f}" x2="{x+w*0.5:.1f}" y2="{y+h*0.9:.1f}" stroke="#E7DFC9" stroke-width="12" opacity="0.6"/>'
    return svg


# ===========================================================================
# LAYOUT ENGINE
# ===========================================================================
def build_row(keys, stack_groups=None):
    """Given ordered simple room keys (and optional stacked sub-groups), return
    row metadata: total L (ft) and total W (ft, i.e. row depth)."""
    stack_groups = stack_groups or {}
    total_L, max_W = 0, 0
    for k in keys:
        if k in stack_groups:
            sub = stack_groups[k]
            group_L = max(dims[s]["L"] for s in sub)
            group_W = sum(dims[s]["W"] for s in sub)
            total_L += group_L
            max_W = max(max_W, group_W)
        else:
            total_L += dims[k]["L"]
            max_W = max(max_W, dims[k]["W"])
    return total_L, max_W


row1_keys = ["bedroom1", "toiletbath", "bedroom2"]
row1_stack = {"toiletbath": ["toilet", "bath"]}
row2_keys = ["kitchen", "lounge", "dining"]
row3_keys = ["lobby", "entryhall"]
row4_keys = ["porch", "garden"]

row1_L, row1_W = build_row(row1_keys, row1_stack)
row2_L, row2_W = build_row(row2_keys)
row3_L, row3_W = build_row(row3_keys)
row4_L, row4_W = build_row(row4_keys)

HOUSE_W = max(row1_L, row2_L, row3_L, row4_L)  # feet — widest row sets house width
row_heights = [row1_W, row2_W, row3_W, row4_W]
HOUSE_H = sum(row_heights)

canvas_w = int(ft(HOUSE_W) + MARGIN * 2)
canvas_h = int(ft(HOUSE_H) + MARGIN * 2)


def layout_row(keys, row_L_ft, y_top_ft, stack_groups=None):
    """Return list of boxes: (key, x_ft, y_ft, w_ft, h_ft) scaled so the row's
    total width fills HOUSE_W, left-aligned to the house."""
    stack_groups = stack_groups or {}
    scale = HOUSE_W / row_L_ft
    boxes = []
    cursor = 0.0
    for k in keys:
        if k in stack_groups:
            sub = stack_groups[k]
            group_L = max(dims[s]["L"] for s in sub) * scale
            sub_y = y_top_ft
            for s in sub:
                h = dims[s]["W"]
                boxes.append((s, cursor, sub_y, group_L, h))
                sub_y += h
            cursor += group_L
        else:
            w = dims[k]["L"] * scale
            h = dims[k]["W"]
            boxes.append((k, cursor, y_top_ft, w, h))
            cursor += w
    return boxes


y_cursor = 0.0
all_boxes = {}
for keys, stacks, h in [
    (row1_keys, row1_stack, row1_W),
    (row2_keys, {}, row2_W),
    (row3_keys, {}, row3_W),
    (row4_keys, {}, row4_W),
]:
    row_L = build_row(keys, stacks)[0]
    for key, x, y, w, hh in layout_row(keys, row_L, y_cursor, stacks):
        all_boxes[key] = (x, y, w, hh)
    y_cursor += h

# ===========================================================================
# BUILD SVG
# ===========================================================================
fills, furniture, walls, openings, labels = [], [], [], [], []

for key, (x_ft, y_ft, w_ft, h_ft) in all_boxes.items():
    meta = dims[key]
    px, py, pw, ph = ft(x_ft) + MARGIN, ft(y_ft) + MARGIN, ft(w_ft), ft(h_ft)
    fills.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="{meta["color"]}"/>')
    furniture.append(furniture_for(meta["type"], px, py, pw, ph))
    labels.append(
        f'<text x="{px+pw/2:.1f}" y="{py+ph/2-4:.1f}" text-anchor="middle" font-size="9" '
        f'font-weight="600" fill="#2B2118">{meta["name"]}</text>'
    )
    if show_dims:
        labels.append(
            f'<text x="{px+pw/2:.1f}" y="{py+ph/2+9:.1f}" text-anchor="middle" font-size="7.5" '
            f'fill="{DIM_COLOR}">{dim_label(meta["L"])} x {dim_label(meta["W"])}</text>'
        )

# ---- Outer walls: one rectangle per row band (keeps the loose-grid character
#      of the original while guaranteeing a clean rectangular outline) ----
y_cursor = 0.0
for h in row_heights:
    x0, y0 = MARGIN, ft(y_cursor) + MARGIN
    w0, h0 = ft(HOUSE_W), ft(h)
    walls.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w0:.1f}" height="{h0:.1f}" '
                 f'fill="none" stroke="{WALL_COLOR}" stroke-width="3"/>')
    y_cursor += h

# ---- Internal partition walls between rooms in each row ----
for keys, stacks in [(row1_keys, row1_stack), (row2_keys, {}), (row3_keys, {}), (row4_keys, {})]:
    for k in keys:
        if k in stacks:
            for s in stacks[k]:
                x_ft, y_ft, w_ft, h_ft = all_boxes[s]
                px, py, pw, ph = ft(x_ft) + MARGIN, ft(y_ft) + MARGIN, ft(w_ft), ft(h_ft)
                walls.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" '
                             f'fill="none" stroke="{WALL_COLOR}" stroke-width="1.6"/>')
        else:
            x_ft, y_ft, w_ft, h_ft = all_boxes[k]
            px, py, pw, ph = ft(x_ft) + MARGIN, ft(y_ft) + MARGIN, ft(w_ft), ft(h_ft)
            walls.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" '
                         f'fill="none" stroke="{WALL_COLOR}" stroke-width="1.6"/>')

# ---- Doors: sensible fixed connections ----
if show_doors:
    def wall_seg(key, side):
        x_ft, y_ft, w_ft, h_ft = all_boxes[key]
        px, py, pw, ph = ft(x_ft) + MARGIN, ft(y_ft) + MARGIN, ft(w_ft), ft(h_ft)
        if side == "bottom":
            return px, py + ph, px + pw, py + ph
        if side == "top":
            return px, py, px + pw, py
        if side == "left":
            return px, py, px, py + ph
        if side == "right":
            return px + pw, py, px + pw, py + ph

    door_plan = [
        ("bedroom1", "bottom", 0.75, "right"),
        ("bedroom2", "bottom", 0.25, "left"),
        ("toilet", "bottom", 0.5, "right"),
        ("bath", "left", 0.5, "left"),
        ("kitchen", "right", 0.5, "right"),
        ("lounge", "bottom", 0.5, "right"),
        ("dining", "left", 0.5, "left"),
        ("entryhall", "bottom", 0.5, "right"),
        ("lobby", "right", 0.5, "left"),
    ]
    for key, side, t, swing in door_plan:
        x1, y1, x2, y2 = wall_seg(key, side)
        openings.append(door_symbol(x1, y1, x2, y2, t=t, swing=swing))

# ---- Windows: on the outer perimeter walls of key rooms ----
if show_windows:
    def outer_wall_seg(key, side):
        x_ft, y_ft, w_ft, h_ft = all_boxes[key]
        px, py, pw, ph = ft(x_ft) + MARGIN, ft(y_ft) + MARGIN, ft(w_ft), ft(h_ft)
        if side == "top":
            return px, py, px + pw, py
        if side == "bottom":
            return px, py + ph, px + pw, py + ph
        if side == "left":
            return px, py, px, py + ph
        if side == "right":
            return px + pw, py, px + pw, py + ph

    window_plan = [
        ("bedroom1", "top", 0.5),
        ("bedroom1", "left", 0.5),
        ("bedroom2", "top", 0.5),
        ("bedroom2", "right", 0.5),
        ("toilet", "top", 0.5),
        ("kitchen", "left", 0.5),
        ("kitchen", "top", 0.5),
        ("lounge", "top", 0.5),
        ("dining", "top", 0.5),
        ("dining", "right", 0.5),
    ]
    for key, side, t in window_plan:
        x1, y1, x2, y2 = outer_wall_seg(key, side)
        openings.append(window_symbol(x1, y1, x2, y2, t=t))

# ---- North arrow ----
na_x, na_y = canvas_w - 40, 30
north_arrow = f'''
<g transform="translate({na_x},{na_y})">
  <line x1="0" y1="18" x2="0" y2="0" stroke="{WALL_COLOR}" stroke-width="1.5"/>
  <polygon points="0,-6 5,4 -5,4" fill="{WALL_COLOR}"/>
  <text x="0" y="30" text-anchor="middle" font-size="9" fill="{DIM_COLOR}">N</text>
</g>'''

PLAN_SVG = f"""
<div style="display:flex; justify-content:center;">
<svg id="plan" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" xmlns="http://www.w3.org/2000/svg"
     style="background:#fff; border-radius:10px; box-shadow:0 8px 24px rgba(43,33,24,0.12); padding:8px;">
  {''.join(fills)}
  {''.join(furniture)}
  {''.join(walls)}
  {''.join(openings)}
  {''.join(labels)}
  {north_arrow}
</svg>
</div>
"""

# ===========================================================================
# PAGE LAYOUT
# ===========================================================================
st.title("🏠 Interior Design Layout")
st.caption("CUSTOM GROUND FLOOR PLAN · DIMENSIONS · DOORS · WINDOWS")

col_plan, col_notes = st.columns([2, 1], gap="large")

with col_plan:
    components.html(PLAN_SVG, height=canvas_h + 40, scrolling=False)
    st.download_button(
        "⬇️ Download plan as SVG",
        data=PLAN_SVG,
        file_name="floor_plan.svg",
        mime="image/svg+xml",
    )

with col_notes:
    st.subheader("Design Notes")

    rooms = [
        ("🛏️ Bedrooms", "#EFE1D1",
         "Bed against the inner wall, wardrobe opposite, door swings inward "
         "from the corridor. Resize either bedroom from the sidebar to see "
         "the plan and door/window positions adjust automatically."),
        ("🚿 Toilet & Bath", "#D7E6E4",
         "Wall-hung WC, corner shower area, small window on the exterior "
         "wall of the toilet for ventilation."),
        ("🍳 Kitchen", "#E8DFC8",
         "L-shaped counter, hob, and sink along two walls with an exterior "
         "window over the sink and a door into the living room."),
        ("🛋️ Living Room", "#E3D3BB",
         "Sofa seating around a coffee table facing a TV unit — the social "
         "hub, connected to the kitchen, dining, and hall."),
        ("🍽️ Dining", "#EAD9C2",
         "Table with chairs, connected to the living room, with a window on "
         "the exterior wall."),
        ("🪜 Hall / Lobby", "#DED2BE",
         "Staircase plus entry hall with a bench and planter; the main "
         "entrance door sits on the exterior wall facing the porch."),
        ("🌳 Garden & Porch", "#9FBF8F",
         "Lawn strip and paved path beside a car porch sized for one "
         "vehicle."),
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
    st.metric("Total built-up width", dim_label(HOUSE_W))
    st.metric("Total built-up depth", dim_label(HOUSE_H))
    st.caption(
        "Adjust any room's L × W in the sidebar — the whole layout, wall "
        "outline, door swings, and window symbols recompute to match."
    )
