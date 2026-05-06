"""Generate UML-style class diagram for the Stock Analyzer.

Outputs:
    class_diagram.png      — embeddable in Word / PDF
    class_diagram.drawio   — editable in https://app.diagrams.net/

Run:
    /Library/Frameworks/Python.framework/Versions/Current/bin/python3 build_diagram.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


# --------------------------------------------------------------------------
# Data: classes shown in the diagram (matches the actual codebase)
# --------------------------------------------------------------------------
CLASSES = {
    "Stock": {
        "stereotype": "class",
        "attrs": [
            "- _symbol: str",
            "- _name: str",
            "- _shares: float",
            "+ DataList: list[DailyData]",
        ],
        "methods": [
            "+ symbol: property (read-only)",
            "+ name: property",
            "+ shares: property (read-only)",
            "+ buy(shares: float)",
            "+ sell(shares: float)",
            "+ add_data(stock_data: DailyData)",
        ],
        "file": "stock_class.py",
    },
    "DailyData": {
        "stereotype": "class",
        "attrs": [
            "- _date: datetime",
            "- _close: float",
            "- _volume: float",
        ],
        "methods": [
            "+ date: property",
            "+ close: property",
            "+ volume: property",
        ],
        "file": "stock_class.py",
    },
    "StockApp": {
        "stereotype": "class",
        "attrs": [
            "+ stock_list: list[Stock]",
            "+ root: Tk",
            "+ stockList: Listbox",
            "+ tabs: ttk.Notebook",
            "+ headingLabel, dailyDataList, stockReport: …",
            "+ addSymbolEntry, addNameEntry, …: Entry",
        ],
        "methods": [
            "+ load() / save()",
            "+ display_stock_data()",
            "+ add_stock() / delete_stock()",
            "+ buy_shares() / sell_shares()",
            "+ scrape_web_data()",
            "+ importCSV_web_data()",
            "+ display_chart()",
        ],
        "file": "stock_GUI.py",
    },
}


# --------------------------------------------------------------------------
# PNG (matplotlib)
# --------------------------------------------------------------------------
def _draw_class_box(ax, x, y, w, h, name, info, color):
    """Render a UML class box at (x, y) with given size and content."""
    # Container box
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.5, edgecolor="#374151",
        facecolor=color,
    )
    ax.add_patch(rect)

    # Compute heights of the three sections
    title_h = 0.55
    n_attr = len(info["attrs"])
    n_meth = len(info["methods"])
    # leave room for file footer
    body_h = h - title_h - 0.35
    attr_h = body_h * (n_attr / max(n_attr + n_meth, 1))
    meth_h = body_h - attr_h

    # Title (class name)
    ax.text(x + w / 2, y + h - title_h / 2, name,
            ha="center", va="center", fontsize=12, fontweight="bold",
            color="#1f2937")

    # Divider 1 (under title)
    ax.plot([x, x + w], [y + h - title_h, y + h - title_h],
            color="#374151", linewidth=1)

    # Attributes
    attr_top = y + h - title_h - 0.08
    line_h = attr_h / max(n_attr, 1)
    for i, a in enumerate(info["attrs"]):
        ax.text(x + 0.10, attr_top - line_h * (i + 0.5), a,
                ha="left", va="center", fontsize=8.2,
                family="monospace", color="#1f2937")

    # Divider 2 (between attrs and methods)
    div2_y = y + h - title_h - attr_h - 0.04
    ax.plot([x, x + w], [div2_y, div2_y], color="#374151", linewidth=1)

    # Methods
    meth_top = div2_y - 0.04
    line_hm = meth_h / max(n_meth, 1)
    for i, m in enumerate(info["methods"]):
        ax.text(x + 0.10, meth_top - line_hm * (i + 0.5), m,
                ha="left", va="center", fontsize=8.2,
                family="monospace", color="#1f2937")

    # File footer
    ax.text(x + w / 2, y + 0.12, f"<<{info['file']}>>",
            ha="center", va="center", fontsize=7.5,
            style="italic", color="#6b7280")


def _draw_inheritance(ax, x_from, y_from, x_to, y_to):
    """Hollow triangle arrow ('inherits from')."""
    arrow = FancyArrowPatch(
        (x_from, y_from), (x_to, y_to),
        arrowstyle="-|>", mutation_scale=22,
        linewidth=1.5, color="#374151",
        shrinkA=4, shrinkB=4,
    )
    ax.add_patch(arrow)


def _draw_composition(ax, x_from, y_from, x_to, y_to, label, lbl_offset=(0, 0)):
    """Open diamond at the container end ('has-a')."""
    arrow = FancyArrowPatch(
        (x_from, y_from), (x_to, y_to),
        arrowstyle="-",
        linewidth=1.5, color="#374151",
        shrinkA=4, shrinkB=4,
    )
    ax.add_patch(arrow)

    # Diamond at the container end (x_from, y_from)
    import numpy as np
    dx, dy = x_to - x_from, y_to - y_from
    length = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / length, dy / length
    px, py = -uy, ux  # perpendicular
    s = 0.13           # diamond size
    p1 = (x_from, y_from)
    p2 = (x_from + ux * s + px * s * 0.55, y_from + uy * s + py * s * 0.55)
    p3 = (x_from + ux * s * 2, y_from + uy * s * 2)
    p4 = (x_from + ux * s - px * s * 0.55, y_from + uy * s - py * s * 0.55)
    diamond = patches.Polygon([p1, p2, p3, p4], closed=True,
                              fill=True, facecolor="white",
                              edgecolor="#374151", linewidth=1.5)
    ax.add_patch(diamond)

    # arrowhead on the contained end
    head = FancyArrowPatch(
        (x_to - ux * 0.05, y_to - uy * 0.05),
        (x_to, y_to),
        arrowstyle="->", mutation_scale=18,
        color="#374151", linewidth=1.5,
    )
    ax.add_patch(head)

    # label
    midx, midy = (x_from + x_to) / 2 + lbl_offset[0], (y_from + y_to) / 2 + lbl_offset[1]
    ax.text(midx, midy, label, ha="center", va="center",
            fontsize=9, color="#1f2937",
            bbox=dict(boxstyle="round,pad=0.25",
                      facecolor="white", edgecolor="#9ca3af",
                      linewidth=0.6))


def render_png(path):
    fig, ax = plt.subplots(figsize=(14, 10), dpi=160)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_aspect("equal")

    # Title
    ax.text(7, 9.65, "Stock Analyzer — UML Class Diagram",
            ha="center", va="center", fontsize=16, fontweight="bold",
            color="#111827")
    ax.text(7, 9.30,
            "IS-A relationships shown with hollow triangles  •  "
            "HAS-A relationships shown with hollow diamonds",
            ha="center", va="center", fontsize=10,
            style="italic", color="#4b5563")

    # ---- 'object' box (top, the inheritance root) ----
    obj_w, obj_h = 3.0, 0.7
    obj_x = 7 - obj_w / 2
    obj_y = 8.10
    rect = patches.FancyBboxPatch(
        (obj_x, obj_y), obj_w, obj_h,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=1.5, edgecolor="#374151",
        facecolor="#f3f4f6",
    )
    ax.add_patch(rect)
    ax.text(7, obj_y + obj_h / 2 + 0.05, "object",
            ha="center", va="center", fontsize=12, fontweight="bold",
            style="italic", color="#1f2937")
    ax.text(7, obj_y + 0.16, "(Python built-in base class)",
            ha="center", va="center", fontsize=8,
            style="italic", color="#6b7280")

    # ---- Three class boxes (Stock | DailyData | StockApp) ----
    box_w, box_h = 4.0, 5.4
    spacing = 0.6
    total_w = box_w * 3 + spacing * 2
    start_x = 7 - total_w / 2
    box_y = 1.3

    positions = {}
    colors = ["#dbeafe", "#dcfce7", "#fef3c7"]   # blue / green / amber
    for i, (name, info) in enumerate(CLASSES.items()):
        bx = start_x + i * (box_w + spacing)
        positions[name] = (bx, box_y, box_w, box_h)
        _draw_class_box(ax, bx, box_y, box_w, box_h, name, info, colors[i])

    # ---- IS-A arrows (each class -> object) ----
    # all aim at the same point on the bottom edge of the object box
    target_x = obj_x + obj_w / 2
    target_y = obj_y - 0.02
    for name, (bx, by, bw, bh) in positions.items():
        x_from = bx + bw / 2
        y_from = by + bh + 0.05
        _draw_inheritance(ax, x_from, y_from, target_x, target_y)

    # ---- HAS-A arrows ----
    # Stock --(DataList: list)--> DailyData (right edge of Stock to left edge of DailyData)
    stock_x, stock_y, stock_w, stock_h = positions["Stock"]
    daily_x, daily_y, daily_w, daily_h = positions["DailyData"]
    sx = stock_x + stock_w
    sy = stock_y + stock_h * 0.55
    dx = daily_x
    dy = daily_y + daily_h * 0.55
    _draw_composition(ax, sx, sy, dx, dy, "DataList\n0..*  HAS-A")

    # StockApp --(stock_list)--> Stock
    # Route through the top of the boxes so the line doesn't go through DailyData.
    app_x, app_y, app_w, app_h = positions["StockApp"]
    sa_x = app_x + app_w * 0.5
    sa_y = app_y + app_h + 0.05
    st_x = stock_x + stock_w * 0.5
    st_y = stock_y + stock_h + 0.05
    # midpoint above both boxes to indicate routing
    mid_y = max(sa_y, st_y) + 0.55

    # draw an L-shaped composition: app top -> up -> left -> down to stock top
    # We'll do it as two segments: a vertical from app, a horizontal across, a
    # vertical down to stock. The diamond is at the source (app).
    import numpy as np
    # diamond at (sa_x, sa_y), pointing up
    s = 0.13
    p1 = (sa_x, sa_y)
    p2 = (sa_x + s * 0.55, sa_y + s)
    p3 = (sa_x, sa_y + s * 2)
    p4 = (sa_x - s * 0.55, sa_y + s)
    diamond = patches.Polygon([p1, p2, p3, p4], closed=True,
                              fill=True, facecolor="white",
                              edgecolor="#374151", linewidth=1.5)
    ax.add_patch(diamond)
    # vertical from diamond up to mid_y
    ax.plot([sa_x, sa_x], [sa_y + s * 2, mid_y],
            color="#374151", linewidth=1.5)
    # horizontal across to above stock
    ax.plot([sa_x, st_x], [mid_y, mid_y],
            color="#374151", linewidth=1.5)
    # vertical down to stock with arrowhead
    head = FancyArrowPatch(
        (st_x, mid_y),
        (st_x, st_y),
        arrowstyle="->", mutation_scale=18,
        color="#374151", linewidth=1.5,
    )
    ax.add_patch(head)
    # label sitting under the horizontal segment to avoid IS-A arrows above
    ax.text((sa_x + st_x) / 2, mid_y - 0.22, "stock_list   0..*  HAS-A",
            ha="center", va="center", fontsize=9, color="#1f2937",
            bbox=dict(boxstyle="round,pad=0.25",
                      facecolor="white", edgecolor="#9ca3af",
                      linewidth=0.6))

    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"PNG saved: {path}")


# --------------------------------------------------------------------------
# draw.io (XML)
# --------------------------------------------------------------------------
def _drawio_class_cell(cell_id, name, info, x, y, parent_id="1"):
    attrs_text = "\n".join(info["attrs"])
    methods_text = "\n".join(info["methods"])
    body = (
        f"<b>{name}</b>"
        "<br/><br/>"
        f"<i>{attrs_text}</i>"
        "<br/><br/>"
        "──"
        "<br/><br/>"
        f"<i>{methods_text}</i>"
        "<br/><br/>"
        f"<font color='#6b7280'>«{info['file']}»</font>"
    )
    return (
        f'<mxCell id="{cell_id}" value="{body}" '
        f'style="rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;'
        f'align=left;spacingLeft=10;spacingTop=8;spacingRight=10;'
        f'fillColor=#dbeafe;strokeColor=#374151;fontFamily=Helvetica;'
        f'fontSize=11" '
        f'vertex="1" parent="{parent_id}">\n'
        f'  <mxGeometry x="{x}" y="{y}" width="280" height="320" as="geometry"/>\n'
        f'</mxCell>'
    )


def _drawio_object_cell(cell_id, x, y, parent_id="1"):
    body = ("<b><i>object</i></b><br/>"
            "<font color='#6b7280' size='1'>(Python built-in base class)</font>")
    return (
        f'<mxCell id="{cell_id}" value="{body}" '
        f'style="rounded=1;whiteSpace=wrap;html=1;align=center;'
        f'fillColor=#f3f4f6;strokeColor=#374151;fontStyle=2;fontSize=12" '
        f'vertex="1" parent="{parent_id}">\n'
        f'  <mxGeometry x="{x}" y="{y}" width="220" height="60" as="geometry"/>\n'
        f'</mxCell>'
    )


def _drawio_inherit(cell_id, src, tgt, parent_id="1"):
    return (
        f'<mxCell id="{cell_id}" style="endArrow=block;endFill=0;'
        f'html=1;strokeColor=#374151;endSize=14" '
        f'edge="1" parent="{parent_id}" source="{src}" target="{tgt}">\n'
        f'  <mxGeometry relative="1" as="geometry"/>\n'
        f'</mxCell>'
    )


def _drawio_composition(cell_id, src, tgt, label, parent_id="1"):
    return (
        f'<mxCell id="{cell_id}" value="{label}" '
        f'style="endArrow=open;startArrow=diamondThin;startFill=0;'
        f'html=1;strokeColor=#374151;endSize=10;startSize=14;'
        f'fontSize=10" '
        f'edge="1" parent="{parent_id}" source="{src}" target="{tgt}">\n'
        f'  <mxGeometry relative="1" as="geometry"/>\n'
        f'</mxCell>'
    )


def render_drawio(path):
    cells = []
    cells.append('<mxCell id="0"/>')
    cells.append('<mxCell id="1" parent="0"/>')

    # object box at top
    cells.append(_drawio_object_cell("obj", 510, 40))

    # Three class boxes
    cells.append(_drawio_class_cell("stock",     "Stock",
                                    CLASSES["Stock"],     60, 240))
    cells.append(_drawio_class_cell("daily",     "DailyData",
                                    CLASSES["DailyData"], 460, 240))
    cells.append(_drawio_class_cell("app",       "StockApp",
                                    CLASSES["StockApp"],  860, 240))

    # IS-A arrows
    cells.append(_drawio_inherit("e_stock_obj", "stock", "obj"))
    cells.append(_drawio_inherit("e_daily_obj", "daily", "obj"))
    cells.append(_drawio_inherit("e_app_obj",   "app",   "obj"))

    # HAS-A arrows
    cells.append(_drawio_composition("e_stock_daily", "stock", "daily",
                                     "DataList&#10;0..*  HAS-A"))
    cells.append(_drawio_composition("e_app_stock",   "app",   "stock",
                                     "stock_list&#10;0..*  HAS-A"))

    inner = "\n      ".join(cells)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<mxfile host="app.diagrams.net">\n'
        '  <diagram name="Stock Analyzer Class Diagram" id="lab2">\n'
        '    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" '
        'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
        'pageScale="1" pageWidth="1300" pageHeight="900" math="0" shadow="0">\n'
        '      <root>\n'
        f'      {inner}\n'
        '      </root>\n'
        '    </mxGraphModel>\n'
        '  </diagram>\n'
        '</mxfile>\n'
    )
    with open(path, "w") as f:
        f.write(xml)
    print(f"draw.io saved: {path}")


# --------------------------------------------------------------------------

if __name__ == "__main__":
    render_png("class_diagram.png")
    render_drawio("class_diagram.drawio")
